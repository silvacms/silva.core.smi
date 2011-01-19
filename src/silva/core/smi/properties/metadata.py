from five import grok
from zope import component

from silva.core.interfaces import ISilvaObject, IVersionedContent, IContainer
from silva.core.views import views as silvaviews
from silva.core.smi import smi
from silva.core.smi import interfaces

from Products.Silva.icon import get_icon_url
from Products.Silva.adapters.security import is_role_greater_or_equal
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.translations import translate as _

grok.layer(interfaces.ISMILayer)


class PropertiesTab(smi.SMIPage):
    """ Properties tab allows metadata editing.
    """
    grok.context(ISilvaObject)
    grok.name('tab_metadata')
    grok.implements(interfaces.IPropertiesTab, interfaces.ISMITabIndex)
    tab = 'properties'

    def update(self):
        super(PropertiesTab, self).update()
        self.errors = False
        if self.request.method == 'POST' and \
                self.request.form.get('save_metadata'):
            self.save()

    def save(self):
        metadata_service = component.getUtility(IMetadataService)
        binding = metadata_service.getMetadata(self.context.get_editable())

        self.errors = binding.setValuesFromRequest(self.request, reindex=1)
        if self.errors:
            self.send_message(_(
            'The data that was submitted did not validate properly.  Please adjust '
            'the form values and submit again.'), type='error')
        else:
            self.send_message(_('Metadata saved.'), type='feedback')


class MetadataViewletManager(silvaviews.ViewletManager):
    """Viewlet manager to hold Metadata viewlets
    """
    grok.context(ISilvaObject)
    grok.name('metadatainfo')

    def filter(self, viewlets):
        results = []
        for name, viewlet in \
                super(MetadataViewletManager, self).filter(viewlets):
            if not viewlet.available():
                continue
            results.append((name, viewlet,))
        return results


class BindingCache(object):

    def __init__(self, binding):
        self.binding = binding
        self._cache = {}

    def get_bound_element(self, set_name, element_name):
        id = (set_name, element_name)
        element = self._cache.get(id)
        if element is not None:
            return element
        self._cache[id]= element = \
            self.binding.getElement(set_name, element_name)
        return element


class MetadataViewlet(silvaviews.Viewlet):
    grok.baseclass()
    grok.viewletmanager(MetadataViewletManager)
    grok.template('metadataviewlet')

    category = ''
    title = _('properties of')
    form_name = 'form'
    edit = True

    def available(self):
        return False

    def update(self):
        self.metadata_service = component.getUtility(IMetadataService)
        self.binding = self.metadata_service.getMetadata(self.content)
        self.binding_cache = BindingCache(self.binding)
        self.aquired_items = self.binding.listAcquired()
        self.user_roles = self.context.sec_get_all_roles()
        self.errors = self.view.errors
        self.set_names = self.binding.getSetNames(category=self.category)
        self.is_container = IContainer.providedBy(self.context)

    def get_icon_url(self):
        return get_icon_url(self.context, self.request)

    def get_set_title(self, set_name):
        return self.binding.getSet(set_name).getTitle() or set_name

    def get_element_names(self, set_name):
        return self.binding.getElementNames(set_name, mode='view')

    def get_element_title(self, set_name, element_name):
        bound_element = \
            self.binding_cache.get_bound_element(set_name, element_name)
        return bound_element.Title()

    def get_element_description(self, set_name, element_name):
        bound_element = \
            self.binding_cache.get_bound_element(set_name, element_name)
        return bound_element.Description()

    def is_element_required(self, set_name, element_name):
        bound_element = \
            self.binding_cache.get_bound_element(set_name, element_name)
        return bound_element.isRequired()

    def is_element_hidden(self, set_name, element_name):
        bound_element = \
            self.binding_cache.get_bound_element(set_name, element_name)
        return bool(bound_element.field.get_value('hidden'))

    def is_element_acquireable(self, set_name, element_name):
        bound_element = \
            self.binding_cache.get_bound_element(set_name, element_name)
        return bound_element.isAcquireable()

    def is_element_editable(self, set_name, element_name):
        at_least_author = [role for role in self.user_roles
                           if is_role_greater_or_equal(role, 'Author')]
        if not at_least_author:
            return False
        # XXX: hack - this check should go in the element's guard
        if set_name == 'silva-content':
            return self.content.can_set_title()
        return self.binding.isEditable(set_name, element_name)

    def is_element_acquired(self, set_name, element_name):
        if (set_name, element_name) in self.aquired_items:
            return True
        return False

    def render_element(self, set_name, element_name):
        if self.is_element_editable(set_name, element_name):
            if self.errors:
                return self.binding.renderElementEdit(
                    set_name, element_name, self.request)
            else:
                return self.binding.renderElementEdit(set_name, element_name)
        return self.binding.renderElementView(set_name, element_name)

    def render_element_view(self, set_name, element_name):
        return self.binding.renderElementView(set_name, element_name)

    def html_id(self, set_name, element_name):
        bound_element = \
            self.binding_cache.get_bound_element(set_name, element_name)
        return getattr(bound_element.field, 'html_id', None)

    def is_allowed(self, set_name):
        minimal_role = self.binding.getSet(set_name).getMinimalRole()
        if not minimal_role:
            return True
        for role in self.user_roles:
            if is_role_greater_or_equal(role, minimal_role):
                return True
        return False


class MetadataEditViewlet(MetadataViewlet):
    grok.baseclass()


class MetadataReadOnlyViewlet(MetadataViewlet):
    grok.baseclass()

    edit = False

    def is_element_editable(self, set_name, element_name):
        return False


class EditableMetadataViewlet(MetadataEditViewlet):
    """Metadata of the editable version.
    """
    grok.context(IVersionedContent)

    def update(self):
        self.content = self.context.get_editable()
        super(EditableMetadataViewlet, self).update()

    def available(self):
        return self.context.get_unapproved_version()


class PreviewableMetadataViewlet(MetadataEditViewlet):
    """metadata of previewable version.
    """
    grok.context(IVersionedContent)
    title = _('properties for approved version of')

    def update(self):
        self.content = self.context.get_previewable()
        super(PreviewableMetadataViewlet, self).update()

    def available(self):
        return self.context.get_approved_version()


class ViewableMetadataViewlet(MetadataReadOnlyViewlet):
    """metadata of the viewable version
    """
    grok.context(IVersionedContent)
    title = _('properties for public version of')

    def update(self):
        self.content = self.context.get_viewable()
        super(ViewableMetadataViewlet, self).update()

    def available(self):
        return self.context.get_public_version()


class LastClosedMetadataViewlet(MetadataReadOnlyViewlet):
    """Metadata of the last closed version
    """
    grok.context(IVersionedContent)
    title = _('properties for closed version of')

    def update(self):
        self.content = self.context.get_last_closed()
        super(LastClosedMetadataViewlet, self).update()

    def available(self):
        return not self.context.get_next_version() and \
            not self.context.get_public_version()


class NonVersionedContentMetadataViewlet(MetadataEditViewlet):
    """Metadata for non versioned content
    """
    grok.context(ISilvaObject)

    def update(self):
        self.content = self.context
        super(NonVersionedContentMetadataViewlet, self).update()

    def available(self):
        return not IVersionedContent.providedBy(self.context)


