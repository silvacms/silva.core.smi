# -*- coding: utf-8 -*-

from five import grok
from zope.interface import Interface
from zope import schema
from DateTime import DateTime
from datetime import datetime
from AccessControl.security import checkPermission

from Products.Silva.Versioning import VersioningError
from silva.core.interfaces import IVersion, IVersionManager, IContainer
from silva.core.interfaces import IVersioning, IVersionedContent
from silva.core.interfaces import IPublicationWorkflow, PublicationWorkflowError
from silva.core.smi.widgets.zeamform import PublicationStatus
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from silva.ui.menu import ContentMenu, MenuItem
from silva.ui.rest import Screen
from zeam.form import autofields
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction
from zeam.form.ztk.actions import EditAction
from zeam.form.base import makeAdaptiveDataManager

# TODO
# - messages
# - prevent multiple copy
# - compare
# - throw events ?


class Publish(silvaforms.SMIComposedForm):
    """Publish tab.
    """
    grok.adapts(Screen, IVersionedContent)
    grok.require('silva.ChangeSilvaContent')
    grok.name('publish')

    label = _('Publication')


class PublishMenu(MenuItem):
    grok.adapts(ContentMenu, IVersionedContent)
    grok.require('silva.ChangeSilvaContent')
    grok.order(30)
    name = _('Publish')

    screen = Publish


class PublicationInfo(silvaviews.Viewlet):
    """Portlet giving information about the publication status.
    """
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.viewletmanager(silvaforms.SMIFormPortlets)

    def update(self):
        formatter = self.request.locale.dates.getFormatter('dateTime')
        convert = lambda d: d is not None and formatter.format(d.asdatetime()) or None
        self.publication_date = convert(
            self.context.get_public_version_publication_datetime())
        self.expiration_date = convert(
            self.context.get_public_version_expiration_datetime())
        self.have_unapproved = self.context.get_unapproved_version() != None
        self.have_next = self.context.get_next_version() != None
        self.have_closed = self.context.get_last_closed_version() != None
        self.have_approved = self.context.is_approved()
        self.have_published = self.context.is_published()
        self.may_approve = checkPermission('silva.ApproveSilvaContent', self.context)
        self.may_change = checkPermission('silva.ChangeSilvaContent', self.context)


class IPublicationFields(Interface):
    """ Interface to register autofields for request approval
    """


class IPublicationInformation(Interface):
    publication_datetime = schema.Datetime(
        title=_('Publication time'), required=True)
    expiration_datetime = schema.Datetime(
        title=_('Expiration time'),
        description=_('Empty indicates no expiration.'),
        required=False)


class IPublicationMessage(Interface):
    message = schema.Text(title=_('message'),
            description=_('This message will remain visible in the status'
                          ' screen for other authors and editors.'),
            default=u'',
            required=False)


class VersionPublication(grok.Adapter):
    grok.context(IVersionedContent)
    grok.implements(IPublicationFields)

    def get_expiration_datetime(self):
        return self.context.get_unapproved_version_expiration_datetime()

    def set_expiration_datetime(self, datetime):
        self.context.set_unapproved_version_expiration_datetime(
            DateTime(datetime))

    def get_publication_datetime(self):
        return self.context.get_unapproved_version_publication_datetime()

    def set_publication_datetime(self, datetime):
        self.context.set_unapproved_version_publication_datetime(
            DateTime(datetime))

    expiration_datetime = property(
        get_expiration_datetime, set_expiration_datetime)
    publication_datetime = property(
        get_publication_datetime, set_publication_datetime)


class MessagePublication(object):
    grok.context(IVersioning)
    grok.implements(IPublicationMessage)

    def get_message(self):
        return None

    def set_message(self):
        pass

    message = property(get_message, set_message)


class PublicationAction(EditAction):
    """An author request approval for a content.
    """

    def __call__(self, form):
        content_data = form.getContentData()
        content = content_data.getContent()

        data, errors = form.extractData()
        if errors:
            return silvaforms.FAILURE

        self.applyData(form, content_data, data)
        return self.execute(form, content, data)


class RequestApprovalAction(PublicationAction):

    title = _('Request approval')

    def execute(self, form, content, data):
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(
                content).request_approval(message)
        except PublicationWorkflowError as e:
            form.send_message(e.message, type='error')
            return silvaforms.FAILURE
        form.send_message(_("Approval requested."), type='feedback')
        return silvaforms.SUCCESS


class RequestApprovalForm(silvaforms.SMISubForm):
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(20)
    fields = autofields.FieldsCollector(IPublicationFields)
    actions = silvaforms.Actions(RequestApprovalAction())

    label = _('Request approval for new version')

    def available(self):
        """ This form do not show if there is no unapproved version or if
        the current user can directly approve the content
        """
        if checkPermission('silva.ApproveSilvaContent', self.context):
            return False
        return bool(self.context.get_unapproved_version()) and \
            not self.context.is_approval_requested()


class PublishAction(PublicationAction):

    title = _('Publish now')

    def available(self, form):
        return bool(
            checkPermission('silva.ApproveSilvaContent', form.context) and
            form.context.get_unapproved_version())

    def execute(self, form, content, data):
        try:
            IPublicationWorkflow(form.context).approve()
        except PublicationWorkflowError as e:
            form.send_message(e.message, type='error')
            return silvaforms.FAILURE
        form.send_message(_("approved."), type='feedback')
        return silvaforms.SUCCESS


class ApproveAction(PublicationAction):

    title = _('Approve for future')

    def available(self, form):
        return bool(
            checkPermission('silva.ApproveSilvaContent', form.context) and
            form.context.get_unapproved_version())

    def execute(self, form, content, data):
        try:
            # XXX approve here should take the publication datetime but doesnt !
            IPublicationWorkflow(form.context).approve(
                time=data.get('publication_datetime'))
        except PublicationWorkflowError as e:
            form.send_message(e.message, type='error')
            return silvaforms.FAILURE
        form.send_message(_("approved."), type='feedback')
        return silvaforms.SUCCESS


class PublicationForm(silvaforms.SMISubForm):
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(20)

    dataManager = makeAdaptiveDataManager(IPublicationFields)

    fields = autofields.FieldsCollector(IPublicationFields)
    actions = silvaforms.Actions(
        ApproveAction(identifier='approve'),
        PublishAction(identifier='publish-now'))

    label = _('Publish new version')

    def available(self):
        return bool(
            checkPermission('silva.ApproveSilvaContent', self.context) and
            self.context.get_unapproved_version())


class ApproveForFuturePopupForm(silvaforms.RESTPopupForm):
    grok.context(IContainer)
    grok.name('silva.core.smi.approveforfuture')

    fields = autofields.FieldsCollector(IPublicationFields)
    actions = silvaforms.Actions(silvaforms.CancelAction())

    label = _('Approve for future new version')


class DefaultRequestApprovalFields(autofields.AutoFields):
    autofields.group(IPublicationFields)
    autofields.order(10)
    fields = silvaforms.Fields(IPublicationInformation)
    fields['publication_datetime'].defaultValue = lambda d: datetime.now()


class RequestApprovalMessage(autofields.AutoFields):
    autofields.group(IPublicationFields)
    autofields.order(20)
    grok.view(RequestApprovalForm)
    fields = silvaforms.Fields(IPublicationMessage)


class PendingApprovalRequestForm(silvaforms.SMISubForm):
    grok.baseclass()
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(20)

    def available(self):
        """ This form do not show if there is no pending approval version or if
        the current user can directly approve the content
        """
        return bool(self.context.get_unapproved_version()) and \
            self.context.is_approval_requested()


class IWithdrawalMessage(Interface):
    message = schema.Text(title=_('add message on withdrawal'),
            description=_('The message may be viewed by local users.'),
            default=u'',
            required=False)


class WithdrawApprovalRequestForm(PendingApprovalRequestForm):
    fields = silvaforms.Fields(IWithdrawalMessage)
    label = _('withdraw request')

    def available(self):
        if checkPermission('silva.ApproveSilvaContent', self.context):
            return False
        return super(WithdrawApprovalRequestForm, self).available()

    @silvaforms.action(_('Withdraw approval request'),
        identifier='withdraw')
    def withdraw(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(self.context).withdraw_request(message)
        except PublicationWorkflowError as e:
            self.send_message(e.message, type='error')
            return silvaforms.FAILURE
        self.send_message('Withdrew request for approval', type='feedback')
        return silvaforms.SUCCESS


class IRejectionMessage(Interface):
    message = schema.Text(title=_('add message on rejection'),
            description=_('The message may be viewed by local users.'),
            default=u'',
            required=False)


class RejectApprovalRequestForm(PendingApprovalRequestForm):
    """ Reject approval from an author by and editor.
    """
    fields = silvaforms.Fields(IRejectionMessage)
    label = _('Reject request')

    def available(self):
        return checkPermission('silva.ApproveSilvaContent', self.context) \
            and super(RejectApprovalRequestForm, self).available()

    @silvaforms.action(_('Reject approval request'),
        identifier='reject')
    def reject(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(self.context).reject_request(message)
        except PublicationWorkflowError as e:
            self.send_message(e.message, type='error')
            return silvaforms.FAILURE
        self.send_message('Rejected request for approval', type='feedback')
        return silvaforms.SUCCESS


class ManualCloseForm(silvaforms.SMISubForm):
    """ Close the public version.
    """
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(30)

    label = _('Manual close')
    description = _('If necessary, the published version of this '
        'content can be manually closed (taken offline). '
        'It will also be removed from the public index.')

    def available(self):
        return checkPermission('silva.ApproveSilvaContent', self.context) and \
            self.context.get_public_version() is not None

    @silvaforms.action(_('Close published version'),
        identifier='close',
        implements=IRemoverAction)
    def close(self):
        try:
            IPublicationWorkflow(self.context).close()
        except PublicationWorkflowError as e:
            self.send_message(e.message, type='error')
            return silvaforms.FAILURE


# sort the versions, order approved, unapproved, published, closed
def sort_versions(a, b):
    # XXX This is fast. awsome.
    ast = IVersionManager(a).get_status()
    bst = IVersionManager(b).get_status()
    order = ['unapproved', 'approved', 'published', 'last_closed', 'closed']
    ret = cmp(order.index(ast), order.index(bst))
    if ret == 0:
        try:
            ret = cmp(int(b.id), int(a.id))
        except ValueError:
            # non-int id(s)
            ret = cmp(b.id, a.id)
    return ret


class IPublicationStatusInfo(Interface):
    modification_time = schema.Datetime(title=_('Modification time'))
    publication_time = schema.Datetime(title=_('Publication time'))
    expiration_time = schema.Datetime(title=_('Expiration time'))
    last_author = schema.TextLine(title=_('Last author'))
    version_status = PublicationStatus(title=_('Version status'))


class PublicationStatusInfo(grok.Adapter):
    grok.context(IVersion)
    grok.provides(IPublicationStatusInfo)

    def __init__(self, context):
        self.context = context
        self.manager = IVersionManager(self.context)

    @property
    def modification_time(self):
        dt = self.manager.get_modification_datetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def publication_time(self):
        dt = self.manager.get_publication_datetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def expiration_time(self):
        dt = self.manager.get_expiration_datetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def last_author(self):
        author = self.manager.get_last_author()
        if author is not None:
            return author.fullname()

    @property
    def version_status(self):
        return self.manager.get_status()

    def delete(self):
        return self.manager.delete()

    def copy_for_editing(self):
        return self.manager.make_editable()

# XXX : TODO...
# class Compare(silvaforms.Action):
#     pass


class CopyForEditingAction(silvaforms.Action):
    """ copy a version to use as new editable version
    """
    title = _('Copy for editing')
    description = _('create a new editable version of '
                    'the selected old one')
    def __call__(self, form, content, line):
        try:
            content.copy_for_editing()
            form.send_message(
                _("Reverted to previous version."), type='feedback')
            return silvaforms.SUCCESS
        except VersioningError as e:
            form.send_message(e.reason(), type='error')
            return silvaforms.FAILURE


class DeleteVersionAction(silvaforms.Action):
    """ permanently remove version
    """
    grok.implements(IRemoverAction)
    title = _("Delete")
    description = _("there's no undo")

    def __call__(self, form, content, line):
        try:
            content.delete()
            form.send_message(
                _('Deleted version'),
                type='feedback')
            return silvaforms.SUCCESS
        except VersioningError as e:
            form.send_message(e.reason(), type='error')
            return silvaforms.FAILURE


class PublicationStatusTableForm(silvaforms.SMISubTableForm):
    """ Manage versions.
    """
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(30)

    label = _(u"Manage versions")
    mode = silvaforms.DISPLAY

    ignoreRequest = True
    ignoreContent = False

    tableFields = silvaforms.Fields(IPublicationStatusInfo)
    tableActions = silvaforms.TableActions(
        DeleteVersionAction(identifier='delete'),
        CopyForEditingAction(identifier='copy'))

    def getItems(self):
        versions = IPublicationWorkflow(self.context).get_versions(False)
        versions.sort(sort_versions)
        return [IPublicationStatusInfo(v) for v in versions]
