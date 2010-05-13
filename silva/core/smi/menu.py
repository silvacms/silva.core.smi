from five import grok
from silva.core.views import views as silvaviews
from silva.core.smi.interfaces import ISMIMenu, ISMIMenuItem
from AccessControl import getSecurityManager
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('smi')


class SMIMenu(silvaviews.ContentProvider):
    """ Base menu
    """
    grok.baseclass()
    grok.implements(ISMIMenu)

    def filter(self, viewlets):
        results = []
        for name, viewlet in viewlets:
            if not self._check_permission(viewlet):
                continue
            if not viewlet.available():
                continue
            results.append((name, viewlet,))
        return results

    def _check_permission(self, viewlet):
        if viewlet.permission:
            if not hasattr(self, '_security_manager'):
                self._security_manager = getSecurityManager()
            return self._security_manager.checkPermission(
                viewlet.permission, self.context)
        return True


class SMITopMenu(SMIMenu):
    """ SMI main menu base class
    """
    grok.baseclass()
    template = grok.PageTemplate(
        filename='smi_templates/smitopmenu.pt')


class SMIEditMenu(SMITopMenu):
    """ Menu for the edit tab
    """
    grok.name('menu_edit')

    def selected(self):
        False


class SMIMenuItem(silvaviews.Viewlet):
    """ Base menu item
    """
    grok.baseclass()
    grok.viewletmanager(SMIMenu)
    grok.implements(ISMIMenuItem)

    name = u''
    permission = u''

    def available(self):
        return True

    def selected(self):
        return False


class SMITopMenuItem(SMIMenuItem):
    """ SMI top menu item base class
    """
    grok.baseclass()
    template = grok.PageTemplate(
        filename='smi_templates/smitopmenuitem.pt')

    accesskey = u''
    uplink_url = u''
    uplink_title = u''
    toplink_url = u''

    @property
    def root_url(self):
        if not hasattr(self, '_root_url'):
            self._root_url = self.context.get_root_url()
        return self._root_url

    @property
    def up_image_src(self):
        if self.publication == self.context:
            return '%s/globals/up_publication.gif' % self.root_url
        return '%s/globals/up_tree.gif' % root_url

    def is_selected(self):
        return False

    def is_active(self):
        return False

    def item_class_name(self):
        return self.is_selected() and \
            (self.is_active() and 'recede' or 'selected') \
            or ''

    @property
    def url(self):
        return u'%s/%s' % (self.root_url, self.name,)

    @property
    def title(self):
        return self.name

    @property
    def up_level_url(self):
        return '%s/globals/up_level.gif' % self.root_url


class SMIEditMenuItem(SMITopMenuItem):
    """ Base class for items of menu_edit
    """
    grok.baseclass()
    grok.viewletmanager(SMIEditMenu)


class SMIEditEditMenuItem(SMIEditMenuItem):
    """ Edit tab of the edit menu
    """
    name = _(u'edit')


class SMIEditPreviewMenuItem(SMIEditMenuItem):
    """ Preview tab of the edit menu
    """
    name = _(u'preview')


