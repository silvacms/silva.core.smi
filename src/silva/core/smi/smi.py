# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from urllib import quote

from five import grok
from zope.interface import Interface
from zope.component import getUtility
from zope.cachedescriptors.property import CachedProperty
from zope.i18n import translate

from grokcore.view.meta.views import default_view_name

from AccessControl import getSecurityManager
from Products.Silva import mangle

from silva.core.conf.utils import getSilvaViewFor
from silva.core.interfaces import ISilvaObject, IUserAccessSecurity
from silva.core.layout.interfaces import IMetadata
from silva.core.smi import interfaces
from silva.core.views import views as silvaviews
from silva.core.messages.interfaces import IMessageService
from silva.core.messages.service import Message


class SMIView(silvaviews.HTTPHeaderView, grok.View):
    """A view in SMI.
    """
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.implements(interfaces.ISMIView)

    vein = 'contents'

    def _silvaView(self):
        # Lookup the correct Silva edit view so forms are able to use
        # silva macros.
        context = self.request['model']
        return getSilvaViewFor(self.context, 'edit', context)

    @property
    def tab_name(self):
        return grok.name.bind().get(self, default=default_view_name)

    @property
    def active_tab(self):
        tab_class = None
        for base in self.__class__.__bases__:
            if interfaces.ISMITab.implementedBy(base):
                tab_class = base
        if tab_class:
            name = grok.name.bind()
            return name.get(tab_class, default=default_view_name)
        return 'tab_edit'

    def __call__(self, **kwargs):
        return super(SMIView, self).__call__()

    def namespace(self):
        # This add to the template namespace global variable used in
        # Zope 2 and Silva templates.  Here should be bind at the
        # correct place in the Silva view registry so you should be
        # able to use silva macro in your templates.
        view = self._silvaView()
        return {'here': view,
                'user': getSecurityManager().getUser(),
                'container': self.request['model'],}


class SMIPage(silvaviews.Page):
    """Page for SMI.
    """
    grok.baseclass()
    grok.layer(interfaces.ISMILayer)

    tab = 'contents'

    @property
    def tab_name(self):
        return grok.name.bind().get(self, default=default_view_name)

    def send_message(self, message, type=u""):
        service = getUtility(IMessageService)
        service.send(message, self.request, namespace=type)


class SMILayout(silvaviews.Layout):
    """ Layout for SMI.
    """
    grok.context(Interface)
    grok.layer(interfaces.ISMILayer)

    def update(self):
        self.metadata = IMetadata(self.context)
        self.root_url = self.context.get_root_url()
        self.view_name = self.view.__name__
        self.have_navigation = not interfaces.ISMINavigationOff.providedBy(
            self.view)
        self.viewport_css_class = 'viewport'
        if self.have_navigation:
            self.viewport_css_class += ' viewport-with-navigation'


class SMIHeader(silvaviews.ContentProvider):
    grok.context(Interface)
    grok.name('header')
    grok.layer(interfaces.ISMILayer)


class SMIFooter(silvaviews.ContentProvider):
    grok.context(Interface)
    grok.name('footer')
    grok.layer(interfaces.ISMILayer)

    def update(self):
        metadata = self.layout.metadata['silva-extra']
        self.contact_name = metadata['contactname']
        self.contact_email = metadata['contactemail']
        self.contact_email_url = None
        if self.contact_email:
            self.contact_email_url = "mailto:%s" % quote(self.contact_email)

        authorization = IUserAccessSecurity(
            self.context).get_user_authorization()
        self.username = authorization.username
        self.role = authorization.role

    def logout_url(self):
        return mangle.urlencode(
            self.context.absolute_url() + '/service_members/logout',
            came_from=self.context.get_publication().absolute_url())

    def can_request_role(self):
        return self.context.service_members.allow_authentication_requests()


class SMIPathBar(silvaviews.ContentProvider):
    grok.context(Interface)
    grok.name('path_bar')
    grok.layer(interfaces.ISMILayer)

    def is_manager(self):
        user = getSecurityManager().getUser()
        return user.has_role(['Manager'], object=self.context)

    def zmi_url(self):
        return self.view.url(name='manage_main')


class SMITab(SMIView):
    """A SMI Tab.
    """
    grok.baseclass()


# For the moment tabs are not registered. Dummy tabs are used instead
# to register components to, they will become the real tab when we
# will switch from Silva views to that system completly.


class DummyPropertiesTab(SMITab):
    grok.implements(interfaces.IPropertiesTab)
    grok.template('smitab')
    grok.name('tab_metadata_extra')
    tab_name = 'tab_metadata'


class PreviewTab(SMITab):
    """Preview
    """
    grok.implements(interfaces.IPreviewTab)
    grok.name('tab_preview')
    grok.baseclass()


class DummyPreviewTab(PreviewTab):

    grok.template('smitab')
    grok.name('tab_preview_extra')
    tab_name = 'tab_preview'


class DummyEditTab(SMITab):
    grok.implements(interfaces.IEditTab)
    grok.template('smitab')
    grok.name('tab_edit_extra')
    tab_name = 'tab_edit'


class SMIMiddleGroundManager(silvaviews.ViewletManager):
    """Middleground macro.
    """
    grok.context(Interface)
    grok.layer(interfaces.ISMILayer)

    @CachedProperty
    def buttons(self):
        return (viewlet for viewlet in self.viewlets if \
                    not interfaces.ISMISpecialButton.providedBy(viewlet) \
                    and viewlet.available())

    @CachedProperty
    def executors(self):
        return (viewlet for viewlet in self.viewlets if \
                    interfaces.ISMIExecutorButton.providedBy(viewlet) \
                    and viewlet.available())


class SMIButton(silvaviews.Viewlet):
    """A button.
    """
    grok.baseclass()
    grok.layer(interfaces.ISMILayer)
    grok.viewletmanager(SMIMiddleGroundManager)

    template = grok.PageTemplate(filename='smi_templates/smibutton.pt')

    label = None
    tab = None
    help = None
    accesskey = None

    def formatedLabel(self):
        if interfaces.ISMISpecialButton.providedBy(self):
            return self.label
        return translate(self.label, context=self.request) + '...'

    def available(self):
        return True

    @property
    def selected(self):
        return self.request.URL.endswith(self.tab)


class SMIMessages(silvaviews.ContentProvider):
    """ Messages display
    """
    grok.context(Interface)
    grok.view(Interface)
    grok.layer(interfaces.ISMILayer)
    grok.implements(interfaces.IMessageProvider)

    message = None
    message_type = None

    def update(self):
        if self.request.response.getStatus() == 302:
            self.messages = []
        service = getUtility(IMessageService)
        messages = service.receive_all(self.request)
        if self.message:
            messages.insert(0, Message(self.message, self.message_type))
        self.messages = map(
            lambda m: {'text': unicode(m), 'css_class': self.css_class(m)},
            messages)

    def css_class(self, message):
        if message.namespace == 'error':
            return 'fixed-alert'
        return 'fixed-feedback'
