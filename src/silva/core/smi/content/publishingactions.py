# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager

from five import grok
from zope.component import getUtility

from silva.core.interfaces import IVersionedContent
from silva.core.interfaces import IPublicationWorkflow
from silva.core.interfaces import PublicationError
from silva.core.messages.interfaces import IMessageService
from silva.translations import translate as _
from silva.ui.rest import UIREST
from silva.ui.menu import ActionMenu, MenuItem
from silva.ui.rest.exceptions import RESTRedirectHandler


class PublicationMenuItem(MenuItem):
    """Base menu item for publication actions.
    """
    grok.baseclass()
    grok.adapts(ActionMenu, IVersionedContent)
    grok.require('silva.ChangeSilvaContent')

    def can_approve_content(self):
        sm = getSecurityManager()
        return sm.checkPermission('Approve Silva content', self.content)


class PublicationAction(UIREST):
    grok.baseclass()
    grok.context(IVersionedContent)
    grok.require('silva.ChangeSilvaContent')

    def process(self, workflow):
        raise NotImplementedError

    def send_notification(self, message, type="feedback"):
        service = getUtility(IMessageService)
        service.send(message, self.request, namespace=type)

    def POST(self):
        self.workflow = IPublicationWorkflow(self.context)
        try:
            self.process()
        except PublicationError as error:
            # Notify failure.
            self.send_notification(error.reason, type="error")
            return self.json_response({
                'ifaces': ['notifications'],
                'notifications': self.get_notifications()})

        # Refresh screen on success
        return RESTRedirectHandler(
            'silva.ui/' + self.request.form.get('screen', 'content'),
            True).publish(self)


class NewVersionMenu(PublicationMenuItem):
    grok.order(100)

    name = _(u'New version')
    description = _(u'Work on a new version while the previous stays online.')
    action = 'newversion'
    accesskey = u'n'
    icon = 'document'

    def available(self):
        return (self.content.get_editable() is None and
                self.content.get_approved_version() is None)


class NewVersionAction(PublicationAction):
    grok.name('silva.ui.actions.newversion')

    def process(self):
        self.workflow.new_version()
        self.send_notification(_(u'New version created.'))


class RequestApprovalMenu(PublicationMenuItem):
    grok.order(10)

    name = _(u'Request approval')
    description = _(u'Request approval for immediate publication.')
    action = 'requestapproval'
    accesskey = u'r'
    icon = 'check'

    def available(self):
        return bool(not self.can_approve_content() and
                    self.content.get_unapproved_version() is not None and
                    not self.content.is_approval_requested())


class RequestApprovalAction(PublicationAction):
    grok.name('silva.ui.actions.requestapproval')

    def process(self):
        self.workflow.request_approval()
        self.send_notification(
            _(u"Approval requested for immediate publication."))


class WithdrawApprovalRequestMenu(PublicationMenuItem):
    grok.order(40)

    name = _(u'Withdraw request')
    description = _(u'Withdraw a request for approval.')
    action = 'withdrawrequest'
    accesskey = u'w'
    icon = 'close'

    def available(self):
        return bool(not self.can_approve_content() and
                    self.content.is_approval_requested())


class WithdrawApprovalRequestAction(PublicationAction):
    grok.name('silva.ui.actions.withdrawrequest')

    def process(self):
        self.workflow.withdraw_request()
        self.send_notification(_(u"Withdrew request for approval."))


class RejectApprovalRequestMenu(PublicationMenuItem):
    grok.order(80)

    name = _(u'Reject request')
    description = _(u'reject a request for approval')
    action = 'rejectrequest'
    accesskey = u'w'
    icon = 'close'

    def available(self):
        return bool(self.can_approve_content() and
                    self.content.is_approval_requested())


class RejectApprovalRequestAction(PublicationAction):
    grok.name('silva.ui.actions.rejectrequest')

    def process(self):
        self.workflow.reject_request()
        self.send_notification(_(u"Rejected request for approval."))


class RevokeApprovalMenu(PublicationMenuItem):
    grok.order(81)

    name = _(u'Revoke approval')
    description = _(u'Un-approve this version in order to edit it.')
    action = 'revokeapproval'
    accesskey = u'r'
    icon = 'cancel'

    def available(self):
        return bool(self.content.get_approved_version())


class RevokeApprovalAction(PublicationAction):
    grok.name('silva.ui.actions.revokeapproval')

    def process(self):
        self.workflow.revoke_approval()
        self.send_notification(_(u'Revoked approval.'))


class PublishMenu(PublicationMenuItem):
    grok.order(10)

    name = _(u'Publish now')
    description = _(u'Publish now this content.')
    action = 'publish'
    accesskey = u'p'
    icon = 'check'

    def available(self):
        return bool(self.can_approve_content() and
                    self.content.get_unapproved_version())


class PublishAction(PublicationAction):
    grok.name('silva.ui.actions.publish')

    def process(self):
        self.workflow.publish()
        self.send_notification(_(u"Version published."))


