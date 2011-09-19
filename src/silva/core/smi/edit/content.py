# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

from DateTime import DateTime
from AccessControl import getSecurityManager

from five import grok
from silva.core.interfaces import IVersionable
from silva.core.smi import smi as silvasmi
from silva.core.smi.interfaces import (ISMILayer,
    IPublicationAwareTab, IPreviewTab)
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zope.traversing.browser import absoluteURL

grok.layer(ISMILayer)


class SMIAction(silvaforms.Action):
    """Base for Action.
    """
    grok.view(IPublicationAwareTab)

    def can_approve_content(self, form):
        sm = getSecurityManager()
        return sm.checkPermission('Approve Silva content', form.context)

    def send_editor_messages(self):
        service_messages = getattr(self.context, 'service_messages', None)
        if service_messages is not None:
            service_messages.send_pending_messages()

    def redirect(self, form):
        url_parts = [absoluteURL(form.context, form.request), 'edit']
        tab_name = getattr(form, 'tab_name', None)

        # XXX workaround problem with preview frames.
        view = getattr(form, 'view', form)
        if IPreviewTab.providedBy(view):
            tab_name = 'tab_preview'

        if tab_name:
            url_parts.append(tab_name)
        return form.redirect("/".join(url_parts))


class NewVersion(SMIAction):
    """ This action create a copy of the current version
    """
    description = _(u"work on a new version while the previous stays online: alt-n")
    accesskey = u'n'

    def available(self, form):
        return form.context.get_editable() is None

    def __call__(self, form):
        form.context.create_copy()
        form.context.sec_update_last_author_info()
        form.send_message(
            _(u'New version created.'), type=u"feedback")
        return self.redirect(form)


class RequestApproval(SMIAction):
    """Request approval for immediate publication.
    """
    description = _(u"request approval for immediate publication: alt-r")
    accesskey = u'r'

    def available(self, form):
        return bool(not self.can_approve_content(form) and
                    form.context.get_unapproved_version() is not None and
                    not form.context.is_version_approval_requested())

    def __call__(self, form):
        message = None
        if form.context.get_unapproved_version() is None:
            message = _(u"There is no unapproved version.")
        if form.context.is_version_approval_requested():
            message= _(u"Approval has already been requested.")
        if message is not None:
            form.send_message(message, type="error")
            return self.redirect(form)

        form.context.set_unapproved_version_publication_datetime(DateTime())
        form.context.request_version_approval(
            u"Request immediate publication of this content. ")
        form.send_message(
            _(u"Approval requested for immediate publication."),
            type="feedback")
        self.send_editor_messages()
        return self.redirect(form)


class WithdrawApprovalRequest(SMIAction):
    """Withdraw approval request.
    """
    description = _(u"withdraw a request for approval: alt-w")
    accesskey = u'w'

    def available(self, form):
        return bool(not self.can_approve_content(form) and
                    form.context.is_version_approval_requested())

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
        self.send_editor_messages()
        return self.redirect(form)


class RejectApprovalRequest(SMIAction):
    """Withdraw approval request.
    """
    description = _(u"reject a request for approval: alt-w")
    accesskey = u'w'

    def available(self, form):
        return bool(self.can_approve_content(form) and
                    form.context.is_version_approval_requested())

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
        self.send_editor_messages()
        return self.redirect(form)


class RevokeApproval(SMIAction):
    """Revoke approval.
    """
    description = _(u"un-approve this version in order to edit it: alt-r")
    accesskey = u'r'

    def available(self, form):
        return bool(form.context.get_approved_version())

    def __call__(self, form):
        form.context.unapprove_version()
        form.context.sec_update_last_author_info()
        form.send_message(
            _(u'Revoked approval.'), type=u"feedback")
        self.send_editor_messages()
        return self.redirect(form)


class Publish(SMIAction):
    """ Publish the version
    """
    description = _(u"publish this document: alt-p")
    accesskey = u'p'

    def available(self, form):
        return bool(self.can_approve_content(form) and
                    form.context.get_unapproved_version())

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
                return self.redirect(form)
            form.context.create_copy()

        form.context.set_unapproved_version_publication_datetime(DateTime())
        form.context.approve_version()
        form.send_message(_(u"Version approved."), type=u"feedback")
        self.send_editor_messages()
        return self.redirect(form)


class SMIVersionActionForm(silvasmi.SMIMiddleGroundActionForm):
    """ Button form to create a new Version
    """
    grok.context(IVersionable)
    grok.order(20)

    prefix = 'md.version'
    actions = silvaforms.Actions(
        RequestApproval(_(u"request approval")),
        Publish(_(u'publish now')),
        WithdrawApprovalRequest(_(u'withdraw request')),
        RejectApprovalRequest(_(u'reject request')),
        RevokeApproval(_(u'revoke approval')),
        NewVersion(_(u'new version')))

    def available(self):
        return reduce(
            operator.or_,
            [False] + map(lambda a: a.available(self), self.actions))
