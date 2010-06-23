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
from silva.core.interfaces import ISilvaObject, IVersionedContent
from silva.core.smi import interfaces
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.core.messages.interfaces import IMessageService


class SMIView(silvaviews.SilvaGrokView):
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


class SMIHTTPHeaders(HTTPResponseHeaders):
    """Define HTTP-headers for SMI pages. By default we don't want to
    cache.
    """
    grok.adapts(interfaces.ISMILayer, ISilvaObject)

    def cache_headers(self):
        self.disable_cache()


class SMILayout(silvaviews.Layout):
    """ Layout for SMI.
    """
    grok.context(Interface)
    grok.layer(interfaces.ISMILayer)

    def root_url(self):
        if not hasattr(self, '_root_url'):
            self._root_url = self.context.get_root_url()
        return self._root_url

    def resource_base_url(self):
        return '%s/++resource++silva.core.smi' % self.root_url()

    def view_name(self):
        return self.view.__name__


class SMIHeader(silvaviews.ContentProvider):
    grok.context(Interface)
    grok.name('header')
    grok.layer(interfaces.ISMILayer)


class SMIFooter(silvaviews.ContentProvider):
    grok.context(Interface)
    grok.name('footer')
    grok.layer(interfaces.ISMILayer)

    def username(self):
        return self._get_user().name

    def _get_user(self):
        gsm = getSecurityManager()
        return gsm.getUser()

    def get_metadata(self, element_name, set_name='silvaextra'):
        if not hasattr(self, '_service_metadata'):
            self._service_metadata = self.context.service_metadata
        content = self.context
        if IVersionedContent.providedBy(self.context):
            content = self.context.get_viewable()
        if content:
            try:
                return self._service_metadata.getMetadataValue(
                    content, set_name, element_name)
            except (AttributeError, KeyError,) as e:
                return u''
        return u''

    def contact_name(self):
        return self.get_metadata('contactname')

    def contact_email(self):
        return self.get_metadata('contactemail')

    def email_url(self):
        email = self.contact_email()
        if email:
            return "mailto:%s" % quote(email)
        return ''

    def logout_url(self):
        return mangle.urlencode(
            self.context.absolute_url() + '/service_members/logout',
            came_from=self.context.get_publication().absolute_url())

    def get_user_role(self):
        return '/'.join(self.context.sec_get_all_roles())

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

class AccessTab(SMITab):
    """Access
    """
    grok.implements(interfaces.IAccessTab)
    grok.name('tab_access')
    grok.baseclass()


class DummyAccessTab(AccessTab):

    grok.template('smitab')
    grok.name('tab_access_extra')
    tab_name = 'tab_access'


class PropertiesTab(SMITab):
    """Properties
    """
    grok.implements(interfaces.IPropertiesTab)
    grok.name('tab_metadata')
    grok.baseclass()


class DummyPropertiesTab(PropertiesTab):

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


class EditTab(SMITab):
    """Edit
    """
    grok.implements(interfaces.IEditTab)
    grok.name('tab_edit')
    grok.baseclass()


class DummyEditTab(EditTab):

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

    message = u''
    message_type = u''

    def messages(self):
        if self.request.response.getStatus() == 302:
            return []
        if hasattr(self, '_messages'):
            return self._messages
        service = getUtility(IMessageService)
        self._messages = service.receive_all(self.request)
        if self.message:
            self._messages.insert(0, (self.message_type, self.message,))
        return self._messages

    def message_class(self, namespace):
        return namespace == 'error' and 'fixed-alert' or 'fixed-feedback'
