# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime

from five import grok
from zope import schema, interface
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

from DateTime import DateTime
from AccessControl.security import checkPermission

from silva.core.interfaces import IContainer
from silva.core.interfaces import IVersioning, IVersionedContent
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import VersioningError
from silva.core.smi.content.publish import Publish, IPublicationFields
from silva.translations import translate as _
from zeam.form import autofields
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction, IDefaultAction
from zeam.form.silva.interfaces import IRESTCloseOnSuccessAction
from zeam.form.ztk.actions import EditAction


class IPublicationInformation(interface.Interface):
    publication_datetime = schema.Datetime(
        title=_('Publication time'),
        required=True)
    expiration_datetime = schema.Datetime(
        title=_('Expiration time'),
        description=_('Empty indicates no expiration.'),
        required=False)

    @interface.invariant
    def check_publication_expiration(data):
        if data.expiration_datetime:
            if data.expiration_datetime < data.publication_datetime:
                raise interface.Invalid(
                    _(u"Expiration datetime cannot be before publication."))


class VersionedContentPublicationInformation(grok.Adapter):
    grok.context(IVersionedContent)
    grok.implements(IPublicationInformation)

    @apply
    def expiration_datetime():

        def getter(self):
            return self.context.get_unapproved_version_expiration_datetime()

        def setter(self, datetime):
            if datetime is None:
                return
            self.context.set_unapproved_version_expiration_datetime(
                DateTime(datetime))

        return property(getter, setter)

    @apply
    def publication_datetime():

        def getter(self):
            value = self.context.get_unapproved_version_publication_datetime()
            if value is None:
                # This will make sure we have the default value
                raise KeyError('publication_datetime')
            return value

        def setter(self, datetime):
            self.context.set_unapproved_version_publication_datetime(
                DateTime(datetime))

        return property(getter, setter)


class ContainerPublicationInformation(grok.Adapter):
    grok.context(IContainer)
    grok.implements(IPublicationInformation)

    @property
    def expiration_datetime(self):
        return None

    @property
    def publication_datetime(self):
        return None


class IPublicationMessage(interface.Interface):
    message = schema.Text(
        title=_('Message'),
        description=_('This message will remain visible in the status'
                      ' screen for other authors and editors.'),
        default=u'',
        required=False)


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
        data, errors = form.extractData()
        if errors:
            return silvaforms.FAILURE

        content_data = form.getContentData()
        content = content_data.getContent()

        self.applyData(form, content_data, data)
        return self.execute(form, content, data)


class RequestApprovalAction(PublicationAction):
    title = _('Request approval')

    def execute(self, form, content, data):
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(
                content).request_approval(message)
        except VersioningError as e:
            form.send_message(e.reason(), type='error')
            return silvaforms.FAILURE
        form.send_message(_("Approval requested."), type='feedback')
        return silvaforms.SUCCESS


class RequestApprovalForm(silvaforms.SMISubForm):
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(20)
    fields = autofields.FieldsCollector(IPublicationFields)
    actions = silvaforms.Actions(RequestApprovalAction())
    ignoreContent = False
    ignoreRequest = False

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
        # Date from the form should already be set (see PublicationAction)
        try:
            IPublicationWorkflow(form.context).publish()
        except VersioningError as e:
            form.send_message(e.reason(), type='error')
            return silvaforms.FAILURE
        form.send_message(_("Version published."), type='feedback')
        return silvaforms.SUCCESS


class ApproveAction(PublicationAction):
    title = _('Approve for future')

    def available(self, form):
        return bool(
            checkPermission('silva.ApproveSilvaContent', form.context) and
            form.context.get_unapproved_version())

    def execute(self, form, content, data):
        # Date from the form should already be set (see PublicationAction)
        try:
            IPublicationWorkflow(form.context).approve()
        except VersioningError as e:
            form.send_message(e.reason(), type='error')
            return silvaforms.FAILURE
        form.send_message(_("Version approved."), type='feedback')
        return silvaforms.SUCCESS


class PublicationForm(silvaforms.SMISubForm):
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(20)

    fields = autofields.FieldsCollector(IPublicationFields)
    dataManager = autofields.FieldsDataManager()
    actions = silvaforms.Actions(
        ApproveAction(identifier='approve'),
        PublishAction(identifier='publish-now'))
    ignoreContent = False
    ignoreRequest = False

    label = _('Publish new version')

    def available(self):
        return bool(
            checkPermission('silva.ApproveSilvaContent', self.context) and
            self.context.get_unapproved_version())


class DefaultRequestApprovalFields(autofields.AutoFields):
    autofields.group(IPublicationFields)
    autofields.order(10)
    fields = silvaforms.Fields(IPublicationInformation)
    fields['publication_datetime'].defaultValue = lambda f: datetime.now()


class MultiApproveAction(EditAction):
    grok.implements(IDefaultAction, IRESTCloseOnSuccessAction)
    title = _(u"Approve")

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return silvaforms.FAILURE

        get_content = getUtility(IIntIds).getObject
        count = 0
        for id in form.request.form.get('form.prefix.contents', []):
            content = get_content(int(id))
            try:
                self.applyData(form, form.dataManager(content), data)
                IPublicationWorkflow(content).approve()
            except VersioningError as e:
                form.send_message(e.reason(), type='error')
            else:
                count +=1
        if count:
            form.send_message(
                _("${count} version(s) approved.", mapping={'count': count}),
                type='feedback')
            return silvaforms.SUCCESS
        return silvaforms.FAILURE


class ApproveForFuturePopupForm(silvaforms.RESTPopupForm):
    grok.context(IContainer)
    grok.name('silva.core.smi.approveforfuture')

    fields = autofields.FieldsCollector(IPublicationFields)
    dataManager = autofields.FieldsDataManager()
    actions = silvaforms.Actions(silvaforms.CancelAction(),
                                 MultiApproveAction(identifier='approve'))

    label = _('Approve content for future')
    description = _(u'Approve selected content for the future')
    ignoreContent = True
    ignoreRequest = False


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


class IWithdrawalMessage(interface.Interface):
    message = schema.Text(title=_('Add message on withdrawal'),
            description=_('The message may be viewed by local users.'),
            default=u'',
            required=False)


class WithdrawApprovalRequestForm(PendingApprovalRequestForm):
    fields = silvaforms.Fields(IWithdrawalMessage)
    label = _('Withdraw request')

    def available(self):
        if checkPermission('silva.ApproveSilvaContent', self.context):
            return False
        return super(WithdrawApprovalRequestForm, self).available()

    @silvaforms.action(
        _('Withdraw approval request'),
        identifier='withdraw')
    def withdraw(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(self.context).withdraw_request(message)
        except VersioningError as e:
            self.send_message(e.reason(), type='error')
            return silvaforms.FAILURE
        self.send_message('Withdrew request for approval', type='feedback')
        return silvaforms.SUCCESS


class IRejectionMessage(interface.Interface):
    message = schema.Text(title=_('Add message on rejection'),
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

    @silvaforms.action(
        _('Reject approval request'),
        identifier='reject')
    def reject(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(self.context).reject_request(message)
        except VersioningError as e:
            self.send_message(e.reason(), type='error')
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

    @silvaforms.action(
        _('Close published version'),
        identifier='close',
        implements=IRemoverAction)
    def close(self):
        try:
            IPublicationWorkflow(self.context).close()
        except VersioningError as e:
            self.send_message(e.reason(), type='error')
            return silvaforms.FAILURE
        return silvaforms.SUCCESS


