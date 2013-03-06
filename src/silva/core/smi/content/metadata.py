# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import bisect

from five import grok
from zope.component import getUtility, getMultiAdapter
from zope.cachedescriptors.property import CachedProperty

from silva.core.interfaces import IIconResolver, IAuthorizationManager
from silva.core.interfaces import ISilvaObject, IVersion, IVersionedObject
from silva.core.references.interfaces import IReferenceService
from silva.core.services.interfaces import IMetadataService
from silva.core.views import views as silvaviews
from silva.core.views.interfaces import IContentURL
from silva.translations import translate as _
from silva.ui.menu import ContentMenu, MenuItem
from silva.ui.rest import Screen
from zeam.form import silva as silvaforms

from Products.Silva.Security.management import is_role_greater_or_equal


class Properties(silvaforms.SMIComposedForm):
    """ Properties tab allows metadata editing.
    """
    grok.adapts(Screen, ISilvaObject)
    grok.name('properties')
    grok.require('silva.ChangeSilvaContent')
    label = _('Properties')


class PropertiesMenu(MenuItem):
    grok.adapts(ContentMenu, ISilvaObject)
    grok.order(20)
    grok.require('silva.ChangeSilvaContent')
    name = _('Properties')
    screen = Properties


class MetadataFormGroup(silvaforms.SMISubFormGroup):
    """Form group that holds metadata forms.
    """
    grok.context(ISilvaObject)
    grok.view(Properties)
    grok.order(10)
    # metadata category filter
    category = ''


class BindingCache(object):

    def __init__(self, binding):
        self.binding = binding
        self.clear()

    def clear(self):
        self._cache = {}

    def get_element(self, set_name, element_name):
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

    label = _('Editable item properties')

    @CachedProperty
    def binding(self):
        service = getUtility(IMetadataService)
        return service.getMetadata(self.getContent())

    def available(self):
        if self.binding is None:
            return False
        return len(self.binding.getSetNames(category=self.parent.category)) != 0

    def update(self):
        if not self.available():
            return
        self.category = self.parent.category
        self.binding_cache = BindingCache(self.binding)
        self.aquired_items = self.binding.listAcquired()
        self.user_role = IAuthorizationManager(self.context).get_user_role()
        self.errors = False
        self.set_names = self.binding.getSetNames(category=self.category)

    def get_set_title(self, set_name):
        return self.binding.getSet(set_name).getTitle() or set_name

    def get_element_names(self, set_name):
        return self.binding.getElementNames(set_name, mode='view')

    def get_element_title(self, set_name, element_name):
        element = self.binding_cache.get_element(set_name, element_name)
        return element.Title()

    def get_element_description(self, set_name, element_name):
        element = self.binding_cache.get_element(set_name, element_name)
        return element.Description()

    def is_element_required(self, set_name, element_name):
        element = self.binding_cache.get_element(set_name, element_name)
        return element.isRequired()

    def is_element_hidden(self, set_name, element_name):
        element = self.binding_cache.get_element(set_name, element_name)
        return bool(element.field.get_value('hidden'))

    def is_element_acquireable(self, set_name, element_name):
        element = self.binding_cache.get_element(set_name, element_name)
        return element.isAcquireable()

    def is_element_editable(self, set_name, element_name):
        if not is_role_greater_or_equal(self.user_role, 'Author'):
            return False
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
        element = self.binding_cache.get_element(set_name, element_name)
        return getattr(element.field, 'html_id', None)

    def is_allowed(self, set_name):
        minimal_role = self.binding.getSet(set_name).getMinimalRole()
        if not minimal_role:
            return True
        if is_role_greater_or_equal(self.user_role, minimal_role):
            return True
        return False


class MetadataEditForm(MetadataForm):
    grok.baseclass()
    grok.view(MetadataFormGroup)
    actions = silvaforms.Actions(silvaforms.CancelAction())

    def __init__(self, context, parent, request):
        super(MetadataEditForm, self).__init__(context, parent, request)
        # Prefix is set by grokker and we need to extend it because sometimes
        # when need to use several instances of the same form.
        if self.parent.category:
            self.prefix += '-' + self.parent.category

    @silvaforms.action(
        _('Save changes'),
        implements=silvaforms.IDefaultAction,
        available=lambda form: not form.binding.read_only,
        accesskey='ctrl+s')
    def save(self):
        self.errors = self.binding.setValuesFromRequest(
            self.request, reindex=1)
        if self.errors:
            self.send_message(_(
            'The data that was submitted did not '
            'validate properly.  Please adjust '
            'the form values and submit again.'), type='error')
            return silvaforms.FAILURE
        self.send_message(_('Metadata saved.'), type='feedback')
        return silvaforms.SUCCESS


class MetadataReadOnlyForm(MetadataForm):
    grok.baseclass()
    grok.view(MetadataFormGroup)
    mode = silvaforms.DISPLAY
    actions = silvaforms.Actions(silvaforms.CancelAction())

    def is_element_editable(self, set_name, element_name):
        return False


class EditableMetadataForm(MetadataEditForm):
    """Metadata of the editable version.
    """
    grok.context(IVersionedObject)
    grok.view(MetadataFormGroup)
    grok.order(10)

    def getContent(self):
        return self.context.get_editable()

    def available(self):
        return (bool(self.context.get_unapproved_version()) and
                super(EditableMetadataForm, self).available())


class PreviewableMetadataForm(MetadataEditForm):
    """metadata of previewable version.
    """
    grok.context(IVersionedObject)
    grok.view(MetadataFormGroup)
    grok.order(20)
    label = _('Approved version item properties')

    def getContent(self):
        return self.context.get_previewable()

    def available(self):
        return (bool(self.context.get_approved_version()) and
                super(PreviewableMetadataForm, self).available())


class ViewableMetadataForm(MetadataReadOnlyForm):
    """metadata of the viewable version
    """
    grok.context(IVersionedObject)
    grok.order(30)
    label = _('Public version item properties')

    def getContent(self):
        return self.context.get_viewable()

    def available(self):
        return (bool(self.context.get_public_version()) and
                super(ViewableMetadataForm, self).available())


class LastClosedMetadataForm(MetadataReadOnlyForm):
    """Metadata of the last closed version
    """
    grok.context(IVersionedObject)
    grok.order(30)
    label = _('Last closed version item properties')

    def getContent(self):
        version_id = self.context.get_last_closed_version()
        if version_id is None:
            return None
        return self.context._getOb(version_id)

    def available(self):
        return (not bool(self.context.get_next_version()) and
                not bool(self.context.get_public_version()) and
                super(LastClosedMetadataForm, self).available())


class NonVersionedContentMetadataForm(MetadataEditForm):
    """Metadata for non versioned content
    """
    grok.context(ISilvaObject)
    grok.order(40)

    def getContent(self):
        return self.context

    def available(self):
        return (not IVersionedObject.providedBy(self.context) and
                super(NonVersionedContentMetadataForm, self).available())


class ContentReferencedBy(silvaviews.Viewlet):
    """Report reference usage of this publishable
    """
    grok.template('contentreferencedby')
    grok.context(ISilvaObject)
    grok.view(Properties)
    grok.viewletmanager(silvaforms.SMIFormPortlets)

    def update(self):
        references = {}
        service = getUtility(IReferenceService)
        get_icon = IIconResolver(self.request).get_tag
        for reference in service.get_references_to(self.context):
            source = reference.source
            source_versions = []
            if IVersion.providedBy(source):
                source_versions.append(source.id)
                source = source.get_silva_object()

            url = getMultiAdapter((source, self.request), IContentURL)
            edit_url = str(url) + '/edit'
            if edit_url in references and source_versions:
                previous_versions = references[edit_url]['versions']
                if previous_versions[-1] > source_versions[0]:
                    bisect.insort_right(
                        previous_versions, source_versions[0])
                    continue
                else:
                    source_versions = previous_versions + source_versions

            source_title = source.get_title_or_id()
            references[edit_url] = {
                'title': source_title,
                'path': self.view.get_content_path(source),
                'icon': get_icon(source),
                'versions': source_versions}

        self.references = references.values()
        self.references.sort(key=lambda info: info['title'].lower())

        for info in self.references:
            if info['versions']:
                info['title'] += ' (' + ', '.join(info['versions']) + ')'


