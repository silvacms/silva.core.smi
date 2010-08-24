# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from DateTime import DateTime

from five import grok
from zope.traversing.browser import absoluteURL
from zeam.form.base import Action, Actions
from zeam.form.silva.form import SMIViewletForm

from silva.core.interfaces import IVersionedContent
from silva.core.smi.smi import SMIMiddleGroundManager
from silva.core.smi.interfaces import ISMILayer, ISMIExecutorButton
from silva.translations import translate as _

grok.layer(ISMILayer)


class SMIAction(Action):
    """Base for Action.
    """
    tabs = ('tab_edit', 'tab_preview', 'tab_metadata')

    def form_tab_name(self, form):
        return getattr(form.view, 'tab_name', None)

    def available(self, form):
        return (self.form_tab_name(form) in self.tabs)

    def redirect(self, form):
        url_parts = [absoluteURL(form.context, form.request), 'edit']
        tab_name = self.form_tab_name(form)
        if tab_name:
            url_parts.append(tab_name)
        return form.redirect("/".join(url_parts))


class MakeCopy(SMIAction):
    """ This action create a copy of the current version
    """
    description = _(u"work on a new version while the previous stays online: alt-n")

    def available(self, form):
        return (SMIAction.available(self, form) and
                (form.context.get_editable() is None))

    def __call__(self, form):
        form.context.create_copy()
        form.context.sec_update_last_author_info()
        form.send_message(
            _(u'New version created.'), type=u"feedback")
        return self.redirect(form)


class Publish(SMIAction):
    """ Publish the version
    """
    description = _(u"publish this document: alt-p")

    def available(self, form):
        return  (SMIAction.available(self, form) and
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


class SMINewVersionForm(SMIViewletForm):
    """ Button form to create a new Version
    """
    grok.context(IVersionedContent)
    grok.implements(ISMIExecutorButton)
    grok.viewletmanager(SMIMiddleGroundManager)

    prefix = 'new_version'
    postOnly = True
    actions = Actions(
        MakeCopy(_(u'new version'), identifier='make_copy'))
    accesskey = u'n'


class SMIPublishForm(SMIViewletForm):
    grok.context(IVersionedContent)
    grok.implements(ISMIExecutorButton)
    grok.viewletmanager(SMIMiddleGroundManager)
    grok.order(20)

    prefix = 'publish'
    postOnly = True
    actions = Actions(
        Publish(_(u'publish now'), identifier='publish'))

    accesskey = u'p'
