
from five import grok
from zope.interface import Interface
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from infrae.rest import RESTWithTemplate
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.smi.userinfo import UserSettingsMenu
from silva.fanstatic import need
from silva.translations import translate as _
from silva.ui.menu import LinkMenuItem
from silva.ui.rest.helper import ResourcesProvider


class IAboutResources(IDefaultBrowserLayer):
    silvaconf.resource('about.css')


class About(RESTWithTemplate):
    grok.context(ISilvaObject)
    grok.name('silva.core.smi.about')

    def GET(self):
        root = self.context.get_root()
        self.version = root.get_silva_software_version()
        need(IAboutResources)
        data = {
            'content': {
                'ifaces': ['text-overlay'],
                'html': self.template.render(self)
            }}
        ResourcesProvider(self, self.request)(self, data)
        return self.json_response(data)


class AboutMenu(LinkMenuItem):
    grok.adapts(UserSettingsMenu, Interface)
    grok.order(10)
    name = _('About')
    icon = 'about'
    trigger = 'text-overlay'

    def get_url(self, context, request):
        return '{0}/++rest++silva.core.smi.about'.format(
            absoluteURL(context, request))
