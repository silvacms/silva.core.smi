# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager

from five import grok
from silva.core.interfaces import IVersionedContent
from silva.translations import translate as _
from silva.ui.menu import ActionMenuItem


class PublicationMenuItem(ActionMenuItem):
    """Base menu item for publication actions.
    """
    grok.baseclass()
    grok.context(IVersionedContent)

    def can_approve_content(self):
        sm = getSecurityManager()
        return sm.checkPermission('Approve Silva content', self.context)


class NewVersionMenu(PublicationMenuItem):
    grok.order(100)

    name = _(u'New version')
    description = _(u'work on a new version while the previous stays online')
    action = 'newversion'

    def available(self):
        return self.context.get_editable() is None


class RequestApprovalMenu(PublicationMenuItem):
    grok.order(10)

    name = _(u'Request Approval')
    description = _(u'request approval for immediate publication')
    action = 'requestapproval'

    def available(self):
        return bool(not self.can_approve_content() and
                    self.context.get_unapproved_version() is not None and
                    not self.context.is_version_approval_requested())


class WithdrawApprovalRequest(PublicationMenuItem):
    grok.order(40)

    name = _(u'Withdraw Request')
    description = _(u'withdraw a request for approval')
    action = 'withdrawapproval'

    def available(self):
        return bool(not self.can_approve_content() and
                    self.context.is_version_approval_requested())


class RejectApprovalRequest(PublicationMenuItem):
    grok.order(80)

    name = _(u'Reject Request')
    description = _(u'reject a request for approval')
    action = 'rejectapproval'

    def available(self):
        return bool(self.can_approve_content() and
                    self.context.is_version_approval_requested())


class RevokeApproval(PublicationMenuItem):
    grok.order(81)

    name = _(u'Revoke Approval')
    description = _(u'un-approve this version in order to edit it')
    action = 'revokeapproval'

    def available(self):
        return bool(self.context.get_approved_version())


class Publish(PublicationMenuItem):
    grok.order(10)

    name = _(u'Publish Now')
    description = _(u'publish now this content')
    action = 'publish'

    def available(self):
        return bool(self.can_approve_content() and
                    self.context.get_unapproved_version())


# class NewVersion(SMIAction):
#     """ This action create a copy of the current version
#     """
#     accesskey = u'n'

#     def __call__(self, form):
#         form.context.create_copy()
#         form.context.sec_update_last_author_info()
#         form.send_message(
#             _(u'New version created.'), type=u"feedback")
#         return self.redirect(form)


# class RequestApproval(SMIAction):
#     """Request approval for immediate publication.
#     """
#     accesskey = u'r'

#     def __call__(self, form):
#         message = None
#         if form.context.get_unapproved_version() is None:
#             message = _(u"There is no unapproved version.")
#         if form.context.is_version_approval_requested():
#             message= _(u"Approval has already been requested.")
#         if message is not None:
#             form.send_message(message, type="error")
#             return self.redirect(form)

#         form.context.set_unapproved_version_publication_datetime(DateTime())
#         form.context.request_version_approval(
#             u"Request immediate publication of this content. ")
#         form.send_message(
#             _(u"Approval requested for immediate publication."),
#             type="feedback")
#         return self.redirect(form)


# class WithdrawApprovalRequest(SMIAction):
#     """Withdraw approval request.
#     """
#     accesskey = u'w'

#     def __call__(self, form):
#         if form.context.get_unapproved_version() is None:
#             if form.context.get_public_version() is not None:
#                 message = _(u"This content is already public.")
#             else:
#                 message = _(u"This content is already approved. "
#                             u"You can revoke the approval.")
#             form.send_message(message, type="error")
#             return self.redirect(form)

#         form.context.withdraw_version_approval(
#             u"Approval was withdrawn via the edit screen. "
#             u"(automatically generated message)")
#         form.send_message(
#             _(u"Withdrew request for approval."), type="feedback")
#         return self.redirect(form)


# class RejectApprovalRequest(SMIAction):
#     """Withdraw approval request.
#     """
#     accesskey = u'w'

#     def __call__(self, form):
#         if form.context.get_unapproved_version() is None:
#             if form.context.get_public_version() is not None:
#                 message = _(u"This content is already public.")
#             else:
#                 message = _(u"This content is already approved. "
#                             u"You can revoke the approval.")
#             form.send_message(message, type="error")
#             return self.redirect(form)

#         form.context.reject_version_approval(
#             u"Approval was rejected via the edit screen "
#             u"(automatically generated message).")
#         form.send_message(
#             _(u"Rejected request for approval."), type="feedback")
#         return self.redirect(form)


# class RevokeApproval(SMIAction):
#     """Revoke approval.
#     """
#     accesskey = u'r'

#     def __call__(self, form):
#         form.context.unapprove_version()
#         form.context.sec_update_last_author_info()
#         form.send_message(
#             _(u'Revoked approval.'), type=u"feedback")
#         return self.redirect(form)


# class Publish(SMIAction):
#     """ Publish the version
#     """
#     accesskey = u'p'

#     def __call__(self, form):
#         if not form.context.get_unapproved_version():
#             # SHORTCUT: To allow approval of closed docs with no
#             # new version available first create a new version.
#             # This "shortcuts" the workflow.
#             # See also edit/Container/tab_status_approve.py
#             if form.context.is_version_published():
#                 form.send_message(
#                     _("There is no unapproved version to approve."),
#                     type=u'error')
#                 return self.redirect(form)
#             form.context.create_copy()

#         form.context.set_unapproved_version_publication_datetime(DateTime())
#         form.context.approve_version()
#         form.send_message(_(u"Version approved."), type=u"feedback")
#         return self.redirect(form)
