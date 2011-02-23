from five import grok
from zope import component

from silva.core.interfaces import ISilvaObject, IVersionedContent, IContainer
from silva.core.smi import interfaces

from zeam.form import silva as silvaforms

from Products.Silva.icon import get_icon_url
from Products.Silva.adapters.security import is_role_greater_or_equal
from Products.SilvaMetadata.interfaces import IMetadataService

from silva.translations import translate as _

grok.layer(interfaces.ISMILayer)


class PropertiesTab(silvaforms.SMIComposedForm):
    """ Properties tab allows metadata editing.
    """
    grok.context(ISilvaObject)
    grok.name('tab_metadata')
    grok.implements(interfaces.IPropertiesTab, interfaces.ISMITabIndex)
    tab = 'properties'
    tab_name = 'tab_metadata'


class MetadataFormGroup(silvaforms.SMISubFormGroup):
    """Form group that holds metadata forms.
    """
    grok.context(ISilvaObject)
    grok.view(PropertiesTab)
    grok.order(10)
    # metadata category filter
    category = ''
    title = _('properties of')


class BindingCache(object):

    def __init__(self, binding):
        self.binding = binding
        self.clear()

    def clear(self):
        self._cache = {}

    def get_bound_element(self, set_name, element_name):
        id = (set_name, element_name)
        element = self._cache.get(id)
        if element is not None:
            return element
        self._cache[id]= element = \
            self.binding.getElement(set_name, element_name)
        return element


class MetadataForm(silvaforms.SMISubForm):
    grok.baseclass()
    grok.context(ISilvaObject)
    grok.view(MetadataFormGroup)
    grok.template('metadataform')
    grok.require('zope2.ManageProperties')

    title = ''

    @property
    def edit(self):
        return self.mode == silvaforms.INPUT

    def available(self):
        return False

    def default_namespace(self):
        parent = super(MetadataForm, self).default_namespace()
        parent['content'] = self.getContent()
        return parent

    def update(self):
        if not self.available():
            return
        if not self.title:
            self.title = self.parent.title
        self.category = self.parent.category
        self.metadata_service = component.getUtility(IMetadataService)
        self.binding = self.metadata_service.getMetadata(self.getContent())
        self.binding_cache = BindingCache(self.binding)
        self.aquired_items = self.binding.listAcquired()
        self.user_roles = self.context.sec_get_all_roles()
        self.errors = False
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
            return self.getContent().can_set_title()
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


class MetadataEditForm(MetadataForm):
    grok.baseclass()
    grok.view(MetadataFormGroup)
    edit = True

    def __init__(self, context, parent, request):
        super(MetadataEditForm, self).__init__(context, parent, request)
        # Prefix is set by grokker and we need to extend it because sometimes
        # when need to use several instances of the same form.
        if self.parent.category:
            self.prefix += '-' + self.parent.category

    @silvaforms.action(_('save'),
        identifier='save-metadata')
    def save(self):
        self.errors = self.binding.setValuesFromRequest(
            self.request, reindex=1)
        if self.errors:
            self.send_message(_(
            'The data that was submitted did not '
            'validate properly.  Please adjust '
            'the form values and submit again.'), type='error')
            return silvaforms.FAILURE
        else:
            self.send_message(_('Metadata saved.'), type='feedback')
            return silvaforms.SUCCESS


class MetadataReadOnlyForm(MetadataForm):
    grok.baseclass()
    grok.view(MetadataFormGroup)
    mode = silvaforms.DISPLAY
    edit = False

    def is_element_editable(self, set_name, element_name):
        return False


class EditableMetadataForm(MetadataEditForm):
    """Metadata of the editable version.
    """
    grok.context(IVersionedContent)
    grok.view(MetadataFormGroup)
    grok.order(10)

    def getContent(self):
        return self.context.get_editable()

    def available(self):
        return bool(self.context.get_unapproved_version())


class PreviewableMetadataForm(MetadataEditForm):
    """metadata of previewable version.
    """
    grok.context(IVersionedContent)
    grok.view(MetadataFormGroup)
    grok.order(20)
    title = _('properties for approved version of')

    def getContent(self):
        return self.context.get_previewable()

    def available(self):
        return bool(self.context.get_approved_version())


class ViewableMetadataForm(MetadataReadOnlyForm):
    """metadata of the viewable version
    """
    grok.context(IVersionedContent)
    grok.order(30)
    title = _('properties for public version of')

    def getContent(self):
        return self.context.get_viewable()

    def available(self):
        return bool(self.context.get_public_version())


class LastClosedMetadataForm(MetadataReadOnlyForm):
    """Metadata of the last closed version
    """
    grok.context(IVersionedContent)
    grok.order(30)
    title = _('properties for closed version of')

    def getContent(self):
        return self.context.get_last_closed()

    def available(self):
        return bool(not self.context.get_next_version() and \
            not self.context.get_public_version())


class NonVersionedContentMetadataForm(MetadataEditForm):
    """Metadata for non versioned content
    """
    grok.context(ISilvaObject)
    grok.order(40)

    def getContent(self):
        return self.context

    def available(self):
        return not IVersionedContent.providedBy(self.context)


