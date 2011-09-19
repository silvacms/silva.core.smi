from five import grok

from zope.interface import Interface
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import IRoot, IContainer, IVersionedContent
from silva.core.smi import interfaces
from silva.core.views import views as silvaviews
from Products.Silva.icon import get_icon_url


class SMINavCommon(object):
    """ Mixin for navigation content providers
    """
    @property
    def tree_root(self):
        if not hasattr(self, '_tree_root'):
            self._tree_root = self.context.get_publication()
        return self._tree_root


class SMINoNavigation(silvaviews.ContentProvider):
    grok.layer(interfaces.ISMILayer)
    grok.name('sminavigation')
    grok.view(interfaces.ISMINavigationOff)

    def render(self):
        return u''


class SMINoNavigationForContainer(SMINoNavigation):
    grok.context(IContainer)


class SMINavigation(silvaviews.ContentProvider, SMINavCommon):
    """ Main content provider for navigation
    """
    grok.name('sminavigation')
    grok.layer(interfaces.ISMILayer)
    grok.view(Interface)

    def update(self):
        self.context_url = absoluteURL(self.context, self.request)
        self.is_root = IRoot.providedBy(self.tree_root)

    def up_url(self):
        return '%s/../edit/%s' % (self.context_url, self.view.tab_name,)

    def top_url(self):
        return '%s/edit/%s' % (self.layout.root_url, self.view.tab_name,)

    def top_image_src(self):
        return self.layout.static['up_publication.gif']()


class SMINavigationListingForContainer(silvaviews.ContentProvider):
    """ Content Provider for listing of container
    """
    grok.context(IContainer)
    grok.name('navigation_listing')
    grok.layer(interfaces.ISMILayer)

    def render(self):
        return self.context.service_sidebar.render(
            self.context, self.view.tab_name, request=self.request)


class SMINavigationListingForNonContainer(
    silvaviews.ContentProvider, SMINavCommon):
    """ Content provider for listing of non-container
    """
    grok.name('navigation_listing')
    grok.layer(interfaces.ISMILayer)

    def update(self):
        self.content_type = self.context.meta_type.startswith('Silva ') and \
            self.context.meta_type[6:].lower() or \
            self.context.meta_type

    def items(self):
        default_doc_list = self.default_document() and \
            [self.default_document()] or []
        return default_doc_list + \
            self.context.get_ordered_publishables() + \
            self.context.get_non_publishables()

    def get_item_tab_url(self, item):
        return "%s/edit/%s" % (item.absolute_url(), self.view.tab_name,)

    def get_icon_url(self, item):
        return get_icon_url(item, self.request)

    def get_item_title(self, item):
        return item.get_title() or item.id

    def get_item_class(self, item):
        if item == self.context:
            return u'selected'
        return u'unselected'

    def should_link_to_tab_status(self, item):
        return IVersionedContent.providedBy(item) or \
            IContainer.providedBy(item)

    @property
    def container(self):
        if not hasattr(self, '_container'):
            self._container = self.context.get_container()
        return self._container

    def container_icon_url(self):
        return get_icon_url(self.container, self.request)

    def container_title(self):
        return self.container.get_short_title_editable() or self.container.id

    def container_url(self):
        return self.container.absolute_url()

    def container_tab_url(self):
        tab_name = getattr(self.view, 'tab_name', 'tab_edit')
        return u"%s/edit/%s" % (self.container_url(), tab_name,)

    def default_document(self):
        if not hasattr(self, '_default_document'):
            self._default_document = self.context.get_default()
        return self._default_document
