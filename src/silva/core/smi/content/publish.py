# -*- coding: utf-8 -*-

from five import grok
from zope.interface import Interface
from zope import schema
from DateTime import DateTime
from datetime import datetime
from AccessControl.security import checkPermission

from Products.Silva.Versioning import VersioningError
from silva.core import interfaces as silvainterfaces
from silva.core.smi.widgets.zeamform import PublicationStatus
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from silva.ui.menu import ContentMenu, MenuItem
from zeam.form import autofields
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction
from zeam.form.ztk.actions import EditAction

# TODO
# - messages
# - prevent multiple copy
# - compare
# - throw events ?


class PublishTabMenu(MenuItem):
    grok.adapts(ContentMenu, silvainterfaces.IVersionedContent)
    grok.require('silva.ChangeSilvaContent')
    grok.order(30)
    name = _('Publish')
    screen = 'publish'


class PublishTab(silvaforms.SMIComposedForm):
    """Publish tab.
    """
    grok.context(silvainterfaces.IVersionedContent)
    grok.require('silva.ChangeSilvaContent')
    grok.name('silva.ui.publish')

    label = _('Publication')


class PublicationInfo(silvaviews.Viewlet):
    grok.context(silvainterfaces.IVersionedContent)
    grok.view(PublishTab)
    grok.viewletmanager(silvaforms.SMIFormPortlets)

    def update(self):
        formatter = self.request.locale.dates.getFormatter('dateTime')
        convert = lambda d: d is not None and formatter.format(d.asdatetime()) or None
        self.publication_date = convert(
            self.context.get_public_version_publication_datetime())
        self.expiration_date = convert(
            self.context.get_public_version_expiration_datetime())


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
    grok.context(silvainterfaces.IVersioning)
    grok.implements(IPublicationInformation)

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
        get_publication_datetime, set_expiration_datetime)


class MessagePublication(object):
    grok.context(silvainterfaces.IVersioning)
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
            silvainterfaces.IPublicationWorkflow(
                content).request_approval(message)
        except silvainterfaces.PublicationWorkflowError as e:
            form.send_message(e.message, type='error')
            return silvaforms.FAILURE
        form.send_message(_("Approval requested."), type='feedback')
        return silvaforms.SUCCESS


class RequestApprovalForm(silvaforms.SMISubForm):
    grok.context(silvainterfaces.IVersionedContent)
    grok.view(PublishTab)
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
            not self.context.is_version_approval_requested()


class Publish(PublicationAction):

    title = _('Publish now')

    def available(self, form):
        return bool(
            checkPermission('silva.ApproveSilvaContent', form.context) and
            form.context.get_unapproved_version())

    def execute(self, form, content, data):
        try:
            silvainterfaces.IPublicationWorkflow(content).approve()
        except silvainterfaces.PublicationWorkflowError as e:
            form.send_message(e.message, type='error')
            return silvaforms.FAILURE
        form.send_message(_("approved."), type='feedback')
        return silvaforms.SUCCESS


class Approve(PublicationAction):

    title = _('Approve for future')

    def available(self, form):
        return bool(
            checkPermission('silva.ApproveSilvaContent', form.context) and
            form.context.get_unapproved_version())

    def execute(self, form, content, data):
        try:
            # XXX approve here should take the publication datetime but doesnt !
            silvainterfaces.IPublicationWorkflow(content).approve()
        except silvainterfaces.PublicationWorkflowError as e:
            form.send_message(e.message, type='error')
            return silvaforms.FAILURE
        form.send_message(_("approved."), type='feedback')
        return silvaforms.SUCCESS


class PublicationForm(silvaforms.SMISubForm):
    grok.context(silvainterfaces.IVersionedContent)
    grok.view(PublishTab)
    grok.order(20)
    fields = autofields.FieldsCollector(IPublicationFields)
    actions = silvaforms.Actions(
        Approve(identifier='approve'),
        Publish(identifier='publish-now'))

    label = _('Publish new version')

    def available(self):
        return bool(
            checkPermission('silva.ApproveSilvaContent', self.context) and
            self.context.get_unapproved_version())


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
    grok.context(silvainterfaces.IVersionedContent)
    grok.view(PublishTab)
    grok.order(20)

    def available(self):
        """ This form do not show if there is no pending approval version or if
        the current user can directly approve the content
        """
        return bool(self.context.get_unapproved_version()) and \
            self.context.is_version_approval_requested()


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
            silvainterfaces.IPublicationWorkflow(self.context).withdraw_request(message)
        except silvainterfaces.PublicationWorkflowError as e:
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
            silvainterfaces.IPublicationWorkflow(
                self.context).reject_request(message)
        except silvainterfaces.PublicationWorkflowError as e:
            self.send_message(e.message, type='error')
            return silvaforms.FAILURE
        self.send_message('Rejected request for approval', type='feedback')
        return silvaforms.SUCCESS


class ManualCloseForm(silvaforms.SMISubForm):
    """ Close the public version.
    """
    grok.context(silvainterfaces.IVersionedContent)
    grok.view(PublishTab)
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
            silvainterfaces.IPublicationWorkflow(self.context).close()
        except silvainterfaces.PublicationWorkflowError as e:
            self.send_message(e.message, type='error')
            return silvaforms.FAILURE


# sort the versions, order approved, unapproved, published, closed
def sort_versions(a, b):
    ast = a.version_status()
    bst = b.version_status()
    order = ['unapproved', 'approved', 'public', 'last_closed', 'closed']
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
    grok.context(silvainterfaces.IVersion)
    grok.provides(IPublicationStatusInfo)

    def __init__(self, context):
        self.context = context
        self.versioned_content = self.context.get_content()
        self.version_manager = silvainterfaces.IVersionManagement(
            self.context.get_content())

    @property
    def modification_time(self):
        dt = self.version_manager.getVersionModificationTime(self.context.id)
        if dt is not None:
            return dt.asdatetime()

    @property
    def publication_time(self):
        dt = self.version_manager.getVersionPublicationTime(self.context.id)
        if dt is not None:
            return dt.asdatetime()

    @property
    def expiration_time(self):
        dt = self.version_manager.getVersionExpirationTime(self.context.id).asdatetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def last_author(self):
        author = self.version_manager.getVersionLastAuthorInfo(self.context.id)
        if author is not None:
            return author.fullname()

    @property
    def version_status(self):
        return self.version_manager.getVersionStatus(self.context.id)

    def delete_version(self):
        return self.version_manager.deleteVersions([self.context.id])

    def copy_version_for_editing(self):
        return self.version_manager.revertPreviousToEditable(self.context.id)

# XXX : TODO...
# class Compare(silvaforms.Action):
#     pass


class CopyForEditing(silvaforms.Action):
    """ copy a version to use as new editable version
    """
    title = _('Copy for editing')
    description = _('create a new editable version of '
                    'the selected old one')
    accesskey = 'f'

    def __call__(self, form, content, line):
        try:
            content.copy_version_for_editing()
            form.send_message(
                _("Reverted to previous version."), type='feedback')
            return silvaforms.SUCCESS
        except VersioningError as e:
            form.send_message(unicode(e), type='error')
            return silvaforms.FAILURE


class DeleteVersion(silvaforms.Action):
    """ permanently remove version
    """
    grok.implements(IRemoverAction)
    title = _("Delete")
    description = _("there's no undo")

    def __call__(self, form, content, line):
        try:
            status = silvaforms.SUCCESS
            for id, error in content.delete_version():
                if error:
                    form.send_message(
                        _('could not delete ${id}: ${error}',
                            mapping={'id': id, 'error': error}),
                        type='error')
                    status = silvaforms.FAILURE
                else:
                    form.send_message(_('deleted ${id}',
                        mapping={'id': id}), type='feedback')
            return status
        except VersioningError as e:
            form.send_message(unicode(e), type='error')
            return silvaforms.FAILURE


class PublicationStatusTableForm(silvaforms.SMISubTableForm):
    """ Manage versions.
    """
    grok.context(silvainterfaces.IVersionedContent)
    grok.view(PublishTab)
    grok.order(30)

    label = _(u"Manage versions")
    mode = silvaforms.DISPLAY

    ignoreRequest = True
    ignoreContent = False

    tableFields = silvaforms.Fields(IPublicationStatusInfo)
    tableActions = silvaforms.TableActions(
        DeleteVersion(identifier='delete'),
        CopyForEditing(identifier='copy'))

    def getItems(self):
        version_manager = silvainterfaces.IVersionManagement(self.context)
        versions = version_manager.getVersions(False)
        versions.sort(sort_versions)
        return [IPublicationStatusInfo(v) for v in versions]
