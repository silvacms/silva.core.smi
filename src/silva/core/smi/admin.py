
from Acquisition import aq_parent

from five import grok
from silva.core.interfaces import IContainer, IRoot
from silva.core.interfaces import IIconResolver, ISiteManager
from silva.core.interfaces import ISilvaConfigurableService
from silva.translations import translate as _
from silva.ui import rest
from silva.ui.menu import MenuItem

from .userinfo import UserSettingsMenu


class ConfigurationScreen(rest.PageWithTemplateREST):
    grok.adapts(rest.Screen, IContainer)
    grok.name('admin')
    grok.require('zope2.ViewManagementScreens')

    def get_menu_title(self):
        return _("Site Configuration")

    def get_services(self, container):
        services = []
        for candidate in container.objectValues():
            if ISilvaConfigurableService.providedBy(candidate):
                # We assume service icons are URLs
                services.append({
                        'name': candidate.meta_type,
                        'icon': self.get_icon(candidate),
                        'path': self.get_content_path(candidate)})
        return sorted(services, key=lambda i: i['name'].lower())

    def update(self):
        self.get_icon = IIconResolver(self.request).get_tag
        self.main_services = self.get_services(self.context.get_root())
        self.local_services = None
        container = self.context.get_publication()
        while not IRoot.providedBy(container):
            if ISiteManager(container).is_site():
                self.local_services = self.get_services(container)
                break
            container = aq_parent(container).get_publication()


class ConfiguationMenu(MenuItem):
    grok.adapts(UserSettingsMenu, IContainer)
    grok.order(10)
    grok.require('zope2.ViewManagementScreens')
    name = _('Site Preferences')
    icon = 'configuration'
    screen = ConfigurationScreen
