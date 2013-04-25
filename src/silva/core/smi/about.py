
from five import grok
from zope.interface import Interface
from zope.traversing.browser import absoluteURL

from infrae.rest import RESTWithTemplate
from silva.core.interfaces import ISilvaObject
from silva.ui.menu import LinkMenuItem
from silva.translations import translate as _
from silva.core.smi.userinfo import UserSettingsMenu


class About(RESTWithTemplate):
    grok.context(ISilvaObject)
    grok.name('silva.core.smi.about')

    def GET(self):
        self.silva_version = (self.context.get_root()
                              .get_silva_software_version())
        return self.json_response({
            'content': {
                'ifaces': ['text-overlay'],
                'html': self.template.render(self)
            }})


class AboutMenu(LinkMenuItem):
    grok.adapts(UserSettingsMenu, Interface)
    grok.order(10)
    name = _('About')
    icon = 'about'
    trigger = 'text-overlay'

    def get_url(self, context, request):
        return '{0}/++rest++silva.core.smi.about'.format(
            absoluteURL(context, request))
