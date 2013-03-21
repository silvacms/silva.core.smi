
from five import grok
from zope.interface import Interface
from zope import schema

from silva.core.interfaces import IHTTPHeadersSettings
from silva.core.interfaces import ISilvaObject
from silva.core.smi.settings import SettingsMenu, Settings
from silva.translations import translate as _
from silva.ui.menu import MenuItem
from zeam.form import silva as silvaforms


class IHTTPHeadersSettingsFields(Interface):

    http_disable_cache = schema.Bool(
        title=_(u'Prevent item from ever being cached'),
        description=_(u'Add headers to prevent HTTP proxies to cache item.'),
        required=False,
        default=False)
    http_max_age = schema.Int(
        title=_(u'Maximum caching time'),
        description=_(u'If the item is cached, this is the maximum time '
                      u'in seconds it can be cached by an HTTP proxy. '
                      u'Minimal time is 30 seconds.'),
        default=84600,
        min=30,
        required=True)
    http_last_modified = schema.Bool(
        title=_(u'Include a Last-Modified header in the response'),
        description=_(
            u'This information is used to control the caching '
            u'of an item. If not specified, an HTTP proxy will fetch '
            u'the item as often as possible.'),
        required=False,
        default=True)


def cache_not_disabled(form):
    return not form.getContent().http_disable_cache


class HTTPHeadersSettingsForm(silvaforms.SMIForm):
    grok.adapts(Settings, ISilvaObject)
    grok.require('silva.ManageSilvaContentSettings')

    label = _('HTTP Caching settings')
    fields = silvaforms.Fields(IHTTPHeadersSettingsFields)
    fields['http_max_age'].available = cache_not_disabled
    actions = silvaforms.Actions(
        silvaforms.CancelAction(),
        silvaforms.EditAction())
    ignoreRequest = False
    ignoreContent = False

    def update(self):
        self.setContentData(IHTTPHeadersSettings(self.context, None))


class CachingMenu(MenuItem):
    grok.adapts(SettingsMenu, ISilvaObject)
    grok.order(10000)
    grok.require('silva.ManageSilvaContentSettings')
    name = _(u'HTTP Caching')
    screen = HTTPHeadersSettingsForm

    def available(self):
        return IHTTPHeadersSettings(self.content, None) is not None
