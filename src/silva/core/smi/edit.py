from five import grok
from zope.interface import Interface
from zeam.form.base import Action, Actions
from zeam.form.base.widgets import ActionWidget
from zeam.form.silva.form import SMIViewletForm

from silva.core.views import views as silvaviews
from silva.core.interfaces import IVersionedContent
from silva.core.smi.smi import SMIMiddleGroundManager
from silva.core.smi.interfaces import (
    ISMILayer, ISMIExecutorButton, ISMISpecialButton)
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.i18nmessageid import MessageFactory
from DateTime import DateTime


_ = MessageFactory('silva')

grok.templatedir('smi_templates')
grok.layer(ISMILayer)


class MakeCopy(Action):
    """ This action create a copy of the current version
    """
    def available(self, form):
        return form.context.get_editable() is None

    def __call__(self, form):
        if form.request.method.lower() == 'post':
            form.context.sec_update_last_author_info()
            form.context.create_copy()
            form.send_message(_(u'A new working copy has been created'),
                              type=u"feedback")
        form.redirect("%s/edit" % form.context.absolute_url())


class Publish(Action):
    """ Publish the version
    """
    tabs = ('tab_edit', 'tab_preview',)

    def available(self, form):
        if hasattr(form.view, 'tab_name') and \
                form.view.tab_name not in self.tabs:
            return False
        return bool(form.context.get_unapproved_version())

    def __call__(self, form):
        if not form.context.get_unapproved_version():
            # SHORTCUT: To allow approval of closed docs with no
            # new version available first create a new version.
            # This "shortcuts" the workflow.
            # See also edit/Container/tab_status_approve.py
            if form.context.is_version_published():
                # error
                message=_("There is no unapproved version to approve.")
                form.send_message(message, type=u'error')
                return form.redirect(self.next_url(form))
            form.context.create_copy()

        form.context.set_unapproved_version_publication_datetime(DateTime())
        form.context.approve_version()
        form.send_message(_(u"Version approved."), type=u"feedback")
        return form.redirect(self.next_url(form))

    def next_url(self, form):
        if hasattr(form.view, 'tab_name'):
            return "%s/edit/%s" % \
                (form.context.absolute_url(), form.view.tab_name,)
        return "%s/edit" % form.context.absolute_url()


class SMIVersionManagement(silvaviews.ContentProvider):
    """ Content provider for new version bar
    """


class SMINewVersionForm(SMIViewletForm):
    """ Button form to create a new Version
    """
    grok.context(IVersionedContent)
    grok.viewletmanager(SMIVersionManagement)
    prefix = 'newversionform'
    actions = Actions(
        MakeCopy(_(u'New version'), identifier='make_copy'))


class SMIMakeCopyWidget(ActionWidget):
    grok.adapts(MakeCopy, SMINewVersionForm, Interface)


class SMIPublishForm(SMIViewletForm):
    grok.context(IVersionedContent)
    grok.implements(ISMIExecutorButton)
    grok.viewletmanager(SMIMiddleGroundManager)
    grok.order(20)

    prefix = 'publishform'
    actions = Actions(
        Publish(_(u'publish now'), identifier='publish'))

    help = _(u"publish this document: alt-p")
    accesskey = 'p'


