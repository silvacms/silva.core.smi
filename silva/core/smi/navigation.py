from five import grok

from silva.core.interfaces import (IRoot, IPublication, IContainer,
    IVersionedContent)
from silva.core.smi import interfaces

from silva.core.views import views as silvaviews
from Products.Silva.adapters.virtualhosting import getVirtualHostingAdapter
from Products.Silva.icon import get_icon_url


grok.templatedir('smi_templates')


class SMINavCommon(object):
    """ Mixin for navigation content providers
    """
    @property
    def tree_root(self):
        if not hasattr(self, '_tree_root'):
            self._tree_root = self.context.get_publication()
            adapter = getVirtualHostingAdapter(self._tree_root)
            if adapter.containsVirtualRoot():
                self._tree_root = adapter.getVirtualRoot()
        return self._tree_root


class SMINavigation(silvaviews.ContentProvider, SMINavCommon):
    """ Main content provider for navigation
    """
    grok.name('navigation')
    grok.layer(interfaces.ISMILayer)

    @property
    def context_url(self):
        if not hasattr(self, '_context_url'):
            self._context_url = self.context.absolute_url()
        return self._context_url

    def is_root(self):
        return IRoot.providedBy(self.tree_root)

    def up_url(self):
        return '%s/../edit/%s' % (self.context_url, self.view.__name__,)

    def top_url(self):
        return '%s/edit/%s' % (self.layout.root_url(), self.view.__name__,)

    def top_image_src(self):
        if IPublication.providedBy(self.tree_root):
            return '%s/up_tree.gif' % self.layout.resource_base_url()
        return '%s/up_publication.gif' % self.layout.resource_base_url()


class SMINavigationListing(silvaviews.ContentProvider, SMINavCommon):
    """ Base class for listings of navigation
    """
    grok.baseclass()

    def get_item_tab_url(self, item):
        return "%s/edit/%s" % (item.absolute_url(), self.view.tab_name,)

    def get_icon_url(self, item):
        return get_icon_url(item, self.request)

    def get_item_title(self, item):
        return item.title or item.id

    def get_item_class(self, item):
        if item == self.context:
            return u'selected'
        return u'unselected'

    def should_link_to_tab_status(self, item):
        return IVersionedContent.providedBy(item) or \
            IContainer.providedBy(item)


class SMINavigationListingForContainer(SMINavigationListing):
    """ Content Provider for listing of container
    """
    grok.context(IContainer)
    grok.name('navigation_listing')
    grok.layer(interfaces.ISMILayer)

    def items(self):
        return self.tree_root.get_container_tree()


class SMINavigationListingForNonContainer(SMINavigationListing):
    """ Content provider for listing of non-container
    """
    grok.name('navigation_listing')
    grok.layer(interfaces.ISMILayer)

    def items(self):
        default_doc_list = self.default_document and \
            [self.default_document] or []
        return default_doc_list + \
            self.context.get_ordered_publishables() + \
            self.context.get_non_publishables()

    @property
    def container(self):
        if not hasattr(self, '_container'):
            self._container = self.context.get_container()
        return self._container

    @property
    def container_icon_url(self):
        return get_icon_url(self.container, self.request)

    @property
    def container_title(self):
        return self.container.get_short_title_editable() or container.id

    @property
    def container_url(self):
        return self.container.absolute_url()

    @property
    def container_tab_url(self):
        return "%s/edit/%s" % (self.container_url, self.view.tab_name,)

    @property
    def gentype(self):
        return self.context.meta_type.startswith('Silva ') and \
            self.context.meta_type[6:].lower() or \
            self.context.meta_type

    @property
    def default_document(self):
        if not hasattr(self, '_default_document'):
            self._default_document = self.context.get_default()
        return self._default_document


