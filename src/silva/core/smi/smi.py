# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from urllib import quote

from Acquisition import aq_parent
from AccessControl import getSecurityManager
from Products.Silva import mangle

from five import grok
from grokcore.view.meta.views import default_view_name
from infrae import rest
from megrok.chameleon.components import ChameleonPageTemplate
from silva.core.interfaces import ISilvaObject, IAuthorizationManager
from silva.core.layout.interfaces import IMetadata
from silva.core.messages.interfaces import IMessageService
from silva.core.messages.service import Message
from silva.core.smi import interfaces
from silva.core.views import views as silvaviews
from silva.core.views.absoluteurl import AbsoluteURL
from silva.core.views.interfaces import IVirtualSite
from silva.translations import translate as _
from zope.cachedescriptors.property import CachedProperty
from zope.component import getUtility, getMultiAdapter
from zope.i18n import translate
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.interface import Interface
from zope.traversing.browser import absoluteURL



class SMIAbsoluteURL(AbsoluteURL):
    """Support URL computation on SMI pages/views/forms.
    """

    def url(self, preview=False):
        path = list(aq_parent(self.context).getPhysicalPath())
        # Insert back the 'edit' element. We don't care about preview here.
        path.extend(['edit', self.context.tab_name])
        return self.request.physicalPathToURL(path)


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
        return None

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

    tab = _('contents')

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
        langs = IUserPreferredLanguages(self.request).getPreferredLanguages()
        self.lang = langs[0] if langs else 'en'
        self.metadata = IMetadata(self.context)
        self.root_url = IVirtualSite(self.request).get_root_url()
        self.tab_name = getattr(self.view, 'tab_name', self.view.__name__)


class SMIFavicon(silvaviews.ContentProvider):
    grok.context(Interface)
    grok.name('favicon')
    grok.layer(interfaces.ISMILayer)

    @property
    def favicon_url(self):
        return self.static['silvacon.ico']


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

        authorization = IAuthorizationManager(self.context).get_authorization()
        self.username = authorization.identifier
        self.role = authorization.role

    def logout_url(self):
        return mangle.urlencode(
            self.context.absolute_url() + '/service_members/logout',
            came_from=self.context.get_publication().absolute_url())

    def can_request_role(self):
        return self.context.service_members.allow_authentication_requests()


class SMIPathBar(silvaviews.ContentProvider):
    grok.context(Interface)
    grok.name('smipathbar')
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


class SMIMiddleGroundManager(silvaviews.ViewletManager):
    """Middleground macro.
    """
    grok.context(Interface)
    grok.layer(interfaces.ISMILayer)

    @CachedProperty
    def buttons(self):
        return [viewlet for viewlet in self.viewlets if
                ((not interfaces.ISMIExecutorButton.providedBy(viewlet))
                 and viewlet.available())]

    @CachedProperty
    def executors(self):
        return [viewlet for viewlet in self.viewlets if
                (interfaces.ISMIExecutorButton.providedBy(viewlet)
                 and viewlet.available())]


class SMIMiddleGroundButton(silvaviews.Viewlet):
    """A button.
    """
    grok.baseclass()
    grok.layer(interfaces.ISMILayer)
    grok.viewletmanager(SMIMiddleGroundManager)
    grok.implements(interfaces.ISMIBasicButton)

    template = ChameleonPageTemplate(filename='smi_templates/smibutton.cpt')

    label = None
    tab = None
    help = None
    accesskey = None

    def url(self):
        return ''.join(
            (absoluteURL(self.context, self.request), '/edit/', self.tab))

    def formatedLabel(self):
        return translate(self.label, context=self.request) + '...'

    def available(self):
        return True

    @property
    def selected(self):
        return self.request.URL.endswith(self.tab)


# BBB
SMIButton = SMIMiddleGroundButton


class SMIMiddleGroundRemoteButton(silvaviews.Viewlet):
    """A button.
    """
    grok.baseclass()
    grok.layer(interfaces.ISMILayer)
    grok.viewletmanager(SMIMiddleGroundManager)
    grok.implements(interfaces.ISMIRemoteButton)

    template = ChameleonPageTemplate(
        filename='smi_templates/smiremotebutton.cpt')

    label = None
    action = None
    help = None
    accesskey = None

    def url(self):
        return ''.join(
            (absoluteURL(self.context, self.request), '/++rest++', self.action))

    def available(self):
        return True


class SMIPortletManager(silvaviews.ViewletManager):
    """Third SMI column manager.
    """
    grok.view(Interface)


class SMIMessages(silvaviews.ContentProvider):
    """ Messages display
    """
    grok.context(Interface)
    grok.view(Interface)
    grok.layer(Interface)
    grok.implements(interfaces.IMessageProvider)

    message = None
    message_type = None
    no_empty_feedback = False

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
        self.no_empty_feedback = (
            self.no_empty_feedback and not len(self.messages))

    def css_class(self, message):
        if message.namespace == 'error':
            return 'fixed-alert'
        return 'fixed-feedback'

