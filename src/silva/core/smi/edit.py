# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from DateTime import DateTime
from AccessControl import getSecurityManager

from megrok import pagetemplate as pt
from five import grok
from zope.traversing.browser import absoluteURL
from zeam.form import silva as silvaforms

from silva.core.interfaces import IVersionedContent
from silva.core.smi.smi import SMIMiddleGroundManager
from silva.core.smi.interfaces import ISMILayer, ISMIExecutorButton
from silva.translations import translate as _

grok.layer(ISMILayer)


class SMIAction(silvaforms.Action):
    """Base for Action.
    """
    tabs = ('tab_edit', 'tab_preview', 'tab_metadata')

    def form_tab_name(self, form):
        return getattr(form.view, 'tab_name', None)

    def can_approve_content(self, form):
        return getSecurityManager().checkPermission(
            'Approve Silva content', form.context)

    def available(self, form):
        return (self.form_tab_name(form) in self.tabs)

    def redirect(self, form):
        url_parts = [absoluteURL(form.context, form.request), 'edit']
        tab_name = self.form_tab_name(form)
        if tab_name:
            url_parts.append(tab_name)
        return form.redirect("/".join(url_parts))


class SMIActionForm(silvaforms.SMIViewletForm):
    grok.baseclass()
    grok.context(IVersionedContent)
    grok.implements(ISMIExecutorButton)
    grok.viewletmanager(SMIMiddleGroundManager)

    postOnly = True


class SMIActionFormTemplate(pt.PageTemplate):
    grok.view(SMIActionForm)


class NewVersion(SMIAction):
    """ This action create a copy of the current version
    """
    description = _(u"work on a new version while the previous stays online: alt-n")
    accesskey = u'n'

    def available(self, form):
        return (SMIAction.available(self, form) and
                (form.context.get_editable() is None))

    def __call__(self, form):
        form.context.create_copy()
        form.context.sec_update_last_author_info()
        form.send_message(
            _(u'New version created.'), type=u"feedback")
        return self.redirect(form)


class WithdrawApprovalRequest(SMIAction):
    """Withdraw approval request.
    """
    description = _(u"withdraw a request for approval: alt-w")
    accesskey = u'w'

    def available(self, form):
        return (SMIAction.available(self, form) and
                not self.can_approve_content(form) and
                bool(form.context.is_version_approval_requested()))

    def __call__(self, form):
        if form.context.get_unapproved_version() is None:
            if form.context.get_public_version() is not None:
                message = _(u"This content is already public.")
            else:
                message = _(u"This content is already approved. "
                            u"You can revoke the approval.")
            form.send_message(message, type="error")
            return self.redirect(form)

        form.context.withdraw_version_approval(
            u"Approval was withdrawn via the edit screen. "
            u"(automatically generated message)")
        form.send_message(
            _(u"Withdrew request for approval."), type="feedback")
        return self.redirect(form)


class RejectApprovalRequest(SMIAction):
    """Withdraw approval request.
    """
    description = _(u"reject a request for approval: alt-w")
    accesskey = u'w'

    def available(self, form):
        return (SMIAction.available(self, form) and
                self.can_approve_content(form) and
                bool(form.context.is_version_approval_requested()))

    def __call__(self, form):
        if form.context.get_unapproved_version() is None:
            if form.context.get_public_version() is not None:
                message = _(u"This content is already public.")
            else:
                message = _(u"This content is already approved. "
                            u"You can revoke the approval.")
            form.send_message(message, type="error")
            return self.redirect(form)

        form.context.reject_version_approval(
            u"Approval was rejected via the edit screen "
            u"(automatically generated message).")
        form.send_message(
            _(u"Rejected request for approval."), type="feedback")
        return self.redirect(form)


class RevokeApproval(SMIAction):
    """Revoke approval.
    """
    description = _(u"un-approve this version in order to edit it: alt-r")
    accesskey = u'r'

    def available(self, form):
        return (SMIAction.available(self, form) and
                bool(form.context.get_approved_version()))

    def __call__(self, form):
        form.context.unapprove_version()
        form.context.sec_update_last_author_info()
        form.send_message(
            _(u'Revoked approval.'), type=u"feedback")
        return self.redirect(form)


class Publish(SMIAction):
    """ Publish the version
    """
    description = _(u"publish this document: alt-p")
    accesskey = u'p'

    def available(self, form):
        return (SMIAction.available(self, form) and
                self.can_approve_content(form) and
                bool(form.context.get_unapproved_version()))

    def __call__(self, form):
        if not form.context.get_unapproved_version():
            # SHORTCUT: To allow approval of closed docs with no
            # new version available first create a new version.
            # This "shortcuts" the workflow.
            # See also edit/Container/tab_status_approve.py
            if form.context.is_version_published():
                form.send_message(
                    _("There is no unapproved version to approve."),
                    type=u'error')
                return form.redirect(self.next_url(form))
            form.context.create_copy()

        form.context.set_unapproved_version_publication_datetime(DateTime())
        form.context.approve_version()
        form.send_message(_(u"Version approved."), type=u"feedback")
        return self.redirect(form)


class SMIVersionActionForm(SMIActionForm):
    """ Button form to create a new Version
    """
    grok.order(20)

    prefix = 'version_actions'
    actions = silvaforms.Actions(
        Publish(_(u'publish now')),
        WithdrawApprovalRequest(_(u'withdraw request')),
        RejectApprovalRequest(_(u'reject request')),
        RevokeApproval(_(u'revoke approval')),
        NewVersion(_(u'new version')))
