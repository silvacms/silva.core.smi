from five import grok
from silva.core.interfaces import IRoot, IPublication
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

    path = u''

    @property
    def target_url(self):
        return "%s/%s" % (self.context.absolute_url(), self.path,)

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
    grok.name(u'menu_edit')
    path = u'edit'

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
    path = u''

    def available(self):
        return True

    @property
    def selected(self):
        return False

    @property
    def target_url(self):
        return u'%s/%s' % (self.viewletmanager.target_url, self.path,)


class SMITopMenuItem(SMIMenuItem):
    """ SMI top menu item base class
    """
    grok.baseclass()
    template = grok.PageTemplate(
        filename='smi_templates/smitopmenuitem.pt')

    accesskey = u''
    uplink_accesskey = u''
    toplink_accesskey = u''

    @property
    def root_url(self):
        return self.layout.root_url()

    @property
    def up_image_src(self):
        if IPublication.providedBy(self.context):
            return '%s/up_publication.gif' % self.layout.resource_base_url()
        return '%s/up_tree.gif' % self.layout.resource_base_url()

    @property
    def selected(self):
        return self.request.URL.endswith(self.path)

    @property
    def active(self):
        return self.request.URL.endswith(self.path)

    @property
    def item_class_name(self):
        return self.selected and \
            (self.active and 'recede' or 'selected') \
            or ''

    @property
    def title(self):
        return self.name

    @property
    def up_level_url(self):
        return '%s/up_level.gif' % self.layout.resource_base_url()

    @property
    def uplink_url(self):
        if not IRoot.providedBy(self.context):
            return "%s/edit/%s" % (
                self.context.aq_parent.absolute_url(),
                self.path)
        return None

    @property
    def toplink_url(self):
        if not IRoot.providedBy(self.context):
            return "%s/edit/%s" % (
                self.context.aq_parent.get_publication().absolute_url(),
                self.path)
        return None

    @property
    def toplink_title(self):
        return _('up to top of publication: alt-${key}',
                    mapping={'key': self.toplink_accesskey})

    @property
    def uplink_title(self):
        return _('up a level: alt-${key}',
                    mapping={'key': self.uplink_accesskey})


class SMIEditMenuItem(SMITopMenuItem):
    """ Base class for items of menu_edit
    """
    grok.baseclass()
    grok.viewletmanager(SMIEditMenu)


class SMIEditEditMenuItem(SMIEditMenuItem):
    """ Edit tab of the edit menu
    """
    name = _(u'edit')
    path = u'tab_edit'


class SMIEditPreviewMenuItem(SMIEditMenuItem):
    """ Preview tab of the edit menu
    """
    name = _(u'preview')
    path = u'tab_preview'


