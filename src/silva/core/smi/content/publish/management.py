# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime

from five import grok
from zope import schema, interface
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from DateTime import DateTime
from AccessControl.security import checkPermission

from silva.core.interfaces import IContainer
from silva.core.interfaces import IVersioning, IVersionedObject
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import IRequestForApprovalStatus
from silva.core.interfaces.errors import VersioningError
from silva.core.smi.content.publish import Publish, IPublicationFields
from silva.translations import translate as _

from zeam.form import autofields
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction
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


class VersionedObjectPublicationInformation(grok.Adapter):
    grok.context(IVersionedObject)
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
        raise KeyError('expiration_datetime')

    @property
    def publication_datetime(self):
        raise KeyError('publication_datetime')


class ApprovalForms(silvaforms.SMISubFormGroup):
    grok.context(IVersionedObject)
    grok.view(Publish)
    grok.order(10)

    def available(self):
        if self.context.is_published() or self.context.is_approved():
            return False
        return super(ApprovalForms, self).available()


class PublicationAction(EditAction):
    """An author request approval for a content.
    """

    def create_unapproved_version(self, content):
        if not content.get_unapproved_version():
            content.create_copy()

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return silvaforms.FAILURE

        content_data = form.getContentData()
        content = content_data.getContent()
        self.create_unapproved_version(content)

        self.applyData(form, content_data, data)
        return self.execute(form, content, data)


class RequestApprovalAction(PublicationAction):
    title = _('Request approval')

    def execute(self, form, content, data):
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(content).request_approval(message)
        except VersioningError as e:
            form.send_message(e.reason, type='error')
            return silvaforms.FAILURE
        form.send_message(_(u"Approval requested."), type='feedback')
        return silvaforms.SUCCESS


class RequestApprovalForm(silvaforms.SMISubForm):
    grok.context(IVersionedObject)
    grok.view(ApprovalForms)
    grok.order(20)

    label = _('Request approval for new version')
    fields = autofields.FieldsCollector(IPublicationFields)
    actions = silvaforms.Actions(RequestApprovalAction())
    ignoreContent = False
    ignoreRequest = False

    def available(self):
        """ This form do not show if there is no unapproved version or if
        the current user can directly approve the content
        """
        if checkPermission('silva.ApproveSilvaContent', self.context):
            return False
        return not self.context.is_approval_requested()


class PublishAction(PublicationAction):
    title = _('Publish now')

    def available(self, form):
        return bool(checkPermission('silva.ApproveSilvaContent', form.context))

    def execute(self, form, content, data):
        # Date from the form should already be set (see PublicationAction)
        try:
            IPublicationWorkflow(form.context).publish()
        except VersioningError as e:
            form.send_message(e.reason, type='error')
            return silvaforms.FAILURE
        form.send_message(_(u"Version published."), type='feedback')
        return silvaforms.SUCCESS


class ApproveAction(PublicationAction):
    title = _('Approve for future')

    def available(self, form):
        return bool(checkPermission('silva.ApproveSilvaContent', form.context))

    def execute(self, form, content, data):
        # Date from the form should already be set (see PublicationAction)
        try:
            IPublicationWorkflow(form.context).approve()
        except VersioningError as e:
            form.send_message(e.reason, type='error')
            return silvaforms.FAILURE
        form.send_message(_(u"Version approved."), type='feedback')
        return silvaforms.SUCCESS


class PublicationForm(silvaforms.SMISubForm):
    grok.context(IVersionedObject)
    grok.view(ApprovalForms)
    grok.order(20)

    fields = autofields.FieldsCollector(IPublicationFields)
    dataManager = autofields.FieldsDataManager()
    actions = silvaforms.Actions(
        ApproveAction(identifier='approve'),
        PublishAction(identifier='publish-now'))
    ignoreContent = False
    ignoreRequest = False

    label = _(u'Publish new version')

    def available(self):
        return bool(checkPermission('silva.ApproveSilvaContent', self.context))


approval_status_vocabulary = SimpleVocabulary([
        SimpleTerm(value='request', title=_(u'Request publication')),
        SimpleTerm(value='reject', title=_(u'Reject publication')),
        SimpleTerm(value='withdraw', title=_(u'Withdraw publication')),
        SimpleTerm(value='approve', title=_(u'Approve publication'))])


class IRequestForApprovalStatusMessage(interface.Interface):
    user_id = schema.TextLine(title=u"User")
    date = schema.Datetime(title=u"Date")
    message = schema.Text(title=u"Message")
    status = schema.Choice(title=u"Action", source=approval_status_vocabulary)

class RequestForApprovalStatusDisplayForm(silvaforms.SMISubTableForm):
    grok.context(IVersionedObject)
    grok.view(ApprovalForms)
    grok.order(50)

    label = _(u"Request approval history")
    tableFields = silvaforms.Fields(IRequestForApprovalStatusMessage)
    mode = silvaforms.DISPLAY
    ignoreContent = False
    ignoreRequest = True
    emptyDescription = _(u"There is no history.")
    batchSize = 5

    def widgetsByKey(self, line):
        result = {}
        for key in line.keys():
            result[key.split('.')[-1]] = line[key]
        return result

    def getItems(self):
        version_id = self.context.get_unapproved_version()
        if version_id is None:
            version_id = self.context.get_last_closed_version()
        version = self.context._getOb(version_id)
        messages = list(IRequestForApprovalStatus(version).messages)
        messages.reverse()
        return messages


class DefaultRequestApprovalFields(autofields.AutoFields):
    autofields.group(IPublicationFields)
    autofields.order(10)
    fields = silvaforms.Fields(IPublicationInformation)
    fields['publication_datetime'].defaultValue = lambda f: datetime.now()
    fields['publication_datetime'].required = lambda f: checkPermission(
        'silva.ApproveSilvaContent', f.context)


class IRequestApprovalMessage(interface.Interface):
    message = schema.Text(
        title=_(u'Message'),
        description=_(u'This message will remain visible in the status'
                      u' screen for other authors and editors.'),
        default=u'',
        required=False)


class RequestApprovalMessagePublication(object):
    grok.context(IVersioning)
    grok.implements(IRequestApprovalMessage)

    def get_message(self):
        return None

    def set_message(self):
        pass

    message = property(get_message, set_message)


class RequestApprovalMessageFields(autofields.AutoFields):
    autofields.group(IPublicationFields)
    autofields.order(20)
    grok.view(RequestApprovalForm)
    fields = silvaforms.Fields(IRequestApprovalMessage)


class PendingApprovalRequestForm(silvaforms.SMISubForm):
    grok.baseclass()
    grok.context(IVersionedObject)
    grok.view(ApprovalForms)
    grok.order(30)

    def available(self):
        """ This form do not show if there is no pending approval version or if
        the current user can directly approve the content
        """
        return self.context.is_approval_requested()


class IWithdrawalMessage(interface.Interface):
    message = schema.Text(title=_('Add message on withdrawal'),
            description=_('The message may be viewed by local users.'),
            default=u'',
            required=False)


class WithdrawApprovalRequestForm(PendingApprovalRequestForm):
    fields = silvaforms.Fields(IWithdrawalMessage)
    label = _(u'Withdraw approval request')

    def available(self):
        if checkPermission('silva.ApproveSilvaContent', self.context):
            return False
        return super(WithdrawApprovalRequestForm, self).available()

    @silvaforms.action(
        _(u'Withdraw approval request'),
        identifier='withdraw')
    def withdraw(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(self.context).withdraw_request(message)
        except VersioningError as e:
            self.send_message(e.reason, type='error')
            return silvaforms.FAILURE
        self.send_message('Withdrew request for approval', type='feedback')
        return silvaforms.SUCCESS


class IRejectionMessage(interface.Interface):
    message = schema.Text(title=_(u'Add message on rejection'),
            description=_(u'The message may be viewed by local users.'),
            default=u'',
            required=False)


class RejectApprovalRequestForm(PendingApprovalRequestForm):
    """ Reject approval from an author by and editor.
    """
    fields = silvaforms.Fields(IRejectionMessage)
    label = _(u'Reject approval request')

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
            self.send_message(e.reason, type='error')
            return silvaforms.FAILURE
        self.send_message('Rejected request for approval', type='feedback')
        return silvaforms.SUCCESS


class ManualCloseForm(silvaforms.SMISubForm):
    """ Close the public version.
    """
    grok.context(IVersionedObject)
    grok.view(Publish)
    grok.order(40)

    label = _(u'Manual close')
    description = _(u'If necessary, the published version of this '
        u'content can be manually closed (taken offline). '
        u'It will also be removed from the public index.')

    def available(self):
        return checkPermission('silva.ApproveSilvaContent', self.context) and \
            self.context.get_public_version() is not None

    @silvaforms.action(
        _(u'Close published version'),
        identifier='close',
        implements=IRemoverAction)
    def close(self):
        try:
            IPublicationWorkflow(self.context).close()
        except VersioningError as e:
            self.send_message(e.reason, type='error')
            return silvaforms.FAILURE
        return silvaforms.SUCCESS


