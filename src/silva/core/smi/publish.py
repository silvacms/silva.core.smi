from five import grok
from zope.interface import Interface
from zope import schema

from AccessControl import getSecurityManager

from silva.core.smi import interfaces
from silva.core import interfaces as silvainterfaces
from zeam.form import silva as silvaforms
from zeam.form import autofields
from zeam.form.ztk.actions import EditAction
from silva.translations import translate as _


grok.layer(interfaces.ISMILayer)


# XXX move this somewhere else

class PublicationWorkflowError(StandardError):
    """Base class for allow workflow errors.
    """


class IPublicationWorkflow(Interface):
    """ Define api to manage publication of silva objects.

    All the following methods may raise a PublicationWorkflowError.
    They all return True/False on Success/Failure.
    """

    def request_approval(message,
            publication_datetime,
            expiration_datetime=None,
            **extras):
        """Issue a request for approval from an author.
        """

    def withdraw_request(message, **extras):
        """ Withdraw a previous request for approval.
        """

    def reject_request(message, **extras):
        """ Reject a request for approval.
        """


class PublishTab(silvaforms.SMIComposedForm):
    """Publish tab.
    """
    grok.context(silvainterfaces.ISilvaObject)
    grok.require('silva.ChangeSilvaContent')
    grok.implements(interfaces.IPublishTab, interfaces.ISMITabIndex)
    grok.name('tab_status')
    tab = 'publish'

    label = _('properties')


class IRequestApprovalFields(Interface):
    """ Interface to register autofields for request approval
    """


class IPublicationInformation(Interface):
    publication_datetime = schema.Datetime(
        title=_('publication time'), required=True)
    expiration_datetime = schema.Datetime(
        title=_('expiration time'),
        description=_('Empty indicates no expiration.'),
        required=False)


class IPublicationMessage(Interface):
    message = schema.Text(title=_('message'),
            description=_('This message will remain visible in the status'
                          ' screen for other authors and editors.'),
            required=False)


class VersionPublication(grok.Adapter):
    grok.context(silvainterfaces.IVersioning)
    grok.implements(IPublicationInformation)

    def get_expiration_datetime(self):
        return self.context.get_unapproved_version_expiration_datetime()

    def set_expiration_datetime(self, datetime):
        self.context.set_unapproved_version_expiration_datetime(
            datetime)

    def get_publication_datetime(self):
        return self.context.get_unapproved_version_publication_datetime()

    def set_publication_datetime(self, datetime):
        self.context.set_unapproved_version_publication_datetime(
            datetime)

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


class VersionedContentPublicationWorkflow(grok.Adapter):
    grok.context(silvainterfaces.IVersionedContent)
    grok.implements(IPublicationWorkflow)

    def request_approval(self, message):
        # XXX add checkout publication datetime
        if self.context.get_unapproved_version() is None:
            raise PublicationWorkflowError(
                _('There is no unapproved version.'))
        if self.context.is_version_approval_requested():
            raise PublicationWorkflowError(
                _('Approval has already been requested.'))
        self.context.request_version_approval(message)
        return True

    def _check_withdraw_or_reject(self):
        if self.context.get_unapproved_version() is None:
            if self.context.get_public_version() is not None:
                raise PublicationWorkflowError(
                    _("This content is already public."))
            else:
                raise PublicationWorkflowError(
                    _("This content is already approved."))
        if not self.context.is_version_approval_requested():
            raise PublicationWorkflowError(
                _("No request for approval is pending for this content."))

    def withdraw_request(self, message):
        self._check_withdraw_or_reject()
        self.context.withdraw_version_approval(message)
        return True

    def reject_request(self, message):
        self._check_withdraw_or_reject()
        self.context.reject_version_approval(message)
        return True


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

    title = _('request approval')

    def execute(self, form, content, data):
        message = data.getWithDefault('message')
        try:
            IPublicationWorkflow(content).request_approval(message)
        except PublicationWorkflowError as e:
            form.send_message(e.message, type='error')
            return silvaforms.FAILURE
        form.send_message(_("Approval requested."), type='feedback')
        return silvaforms.SUCCESS


class RequestApprovalForm(silvaforms.SMISubForm):
    grok.context(silvainterfaces.IVersionedContent)
    grok.require('silva.ChangeSilvaContent')
    grok.view(PublishTab)
    grok.order(10)
    fields = autofields.FieldsCollector(IRequestApprovalFields)
    actions = silvaforms.Actions(RequestApprovalAction())

    label = _('request approval for new version')

    def available(self):
        """ This form do not show if there is no unapproved version or if
        the current user can directly approve the content
        """
        security_manager = getSecurityManager()
        if security_manager.checkPermission(
                'Approve Silva content', self.context):
            return False
        return bool(self.context.get_unapproved_version()) and \
            not self.context.is_version_approval_requested()


class DefaultRequestApprovalFields(autofields.AutoFields):
    autofields.group(IRequestApprovalFields)
    autofields.order(0)
    # XXX this shouldn't be needed but SMISubFrom doesn't seem to provide
    # zope.browser.interfaces.IBrowserView which is default requirement
    grok.view(RequestApprovalForm)
    fields = silvaforms.Fields(IPublicationInformation, IPublicationMessage)


