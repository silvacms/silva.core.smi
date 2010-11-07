# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import urllib

from Products.Silva.icon import get_meta_type_icon, get_icon_url
from Products.Silva.ExtensionRegistry import extensionRegistry as registry
from zExceptions import Redirect, BadRequest

from five import grok
from silva.core.interfaces import (IContainer,
    ISilvaObject, IRoot)
from silva.core.smi.interfaces import (ISMILayer,
    ISMITabIndex, ISMINavigationOff)
from silva.core.views import views as silvaviews
from silva.core.smi import smi as silvasmi
from silva.core.smi.interfaces import IAddingTab, IEditTab, IPublicationAwareTab
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zope import schema, interface
from zope.component import queryUtility
from zope.component.interfaces import IFactory
from zope.interface import Interface
from zope.publisher.browser import applySkin
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.traversing.browser import absoluteURL

grok.layer(ISMILayer)


@grok.provider(IContextSourceBinder)
def silva_content_types(context):
    contents = [SimpleTerm(value=None, token='none', title=_('select:'))]
    for addable in context.get_silva_addables():
        contents.append(SimpleTerm(
                value=addable['name'],
                token=addable['name'],
                title=addable['name']))
    return SimpleVocabulary(contents)


class INewContent(interface.Interface):
    position = schema.Int(
        title=_(u"Content position"),
        default=0,
        required=False)
    content = schema.Choice(
        title=_(u"Content type"),
        description=_("Select a new content to add"),
        source=silva_content_types,
        required=False)


class SMIContainerActionForm(silvasmi.SMIMiddleGroundActionForm):
    """ Button form to create a new Version
    """
    grok.view(IPublicationAwareTab)
    grok.context(IContainer)
    grok.order(20)

    fields = silvaforms.Fields(INewContent)
    fields['position'].mode = silvaforms.HIDDEN
    prefix = 'md.container'
    ignoreContent = False

    def getContentData(self):
        # We edit ourselves, to get the default value (which dependent
        # of the selected view).
        return self.dataManager(self)

    @property
    def content(self):
        if IAddingTab.providedBy(self.view):
            return self.view.__name__
        return None

    @property
    def position(self):
        if 'addform.options.position' in self.request.form:
            try:
                return int(self.request.form['addform.options.position'])
            except ValueError:
                pass
        return None

    @silvaforms.action(
        _(u"new..."),
        identifier="new",
        description=_(u"add a new item"))
    def new(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        url = [absoluteURL(self.context, self.request), 'edit', '+']
        if data['content'] is not silvaforms.NO_VALUE and data['content']:
            url.append(data['content'])
        url = '/'.join(url)
        if data.getDefault('position'):
            url += '?' + urllib.urlencode(
                {'addform.options.position': str(data['position'])})
        self.redirect(url)
        return silvaforms.SUCCESS


class PortletAddDescription(silvaviews.Viewlet):
    grok.viewletmanager(silvasmi.SMIPortletManager)
    grok.order(0)
    grok.view(IAddingTab)

    def update(self):
        addable = registry.get_addable(self.view.__name__)
        self.icon = get_meta_type_icon(self.view.__name__)
        self.title = addable.get('name')
        self.description = addable.get('doc')


class AddingView(silvasmi.SMIPage):
    grok.name('+')
    grok.context(Interface)
    grok.require('silva.ChangeSilvaContent')
    grok.layer(Interface)
    grok.implements(IEditTab)

    def __init__(self, context, request):
        # Due to bugs in traversing, 'edit' is not called. so set back
        # what is done there.
        context = context.get_container()
        applySkin(request, ISMILayer)
        super(AddingView, self).__init__(context, request)

    def publishTraverse(self, request, name):
        if name in self.context.get_silva_addables_allowed_in_container():
            factory = queryUtility(IFactory, name=name)
            if factory is not None:
                return factory(self.context, request)
        raise Redirect(
            '/'.join([absoluteURL(self.context, request), 'edit', '+']))

    def update(self):
        self.addables = []
        self.icon = get_meta_type_icon(self.context.meta_type)
        add_url = [absoluteURL(self.context, self.request), 'edit', '+']
        for addable in self.context.get_silva_addables():
            meta_type = addable['name']
            self.addables.append(
                {'icon': get_meta_type_icon(meta_type),
                 'name': meta_type,
                 'title': _(u"Create a ${addable_name}",
                            mapping={'addable_name': meta_type}),
                 'url': '/'.join(add_url + [meta_type]),
                 'description': addable['doc']})


class SMIContainerEditTab(silvasmi.SMIPage):
    """ Container listing for the smi
    """
    grok.context(IContainer)
    grok.implements(IEditTab, ISMITabIndex, ISMINavigationOff)
    grok.name('tab_edit')
    tab = 'edit'

    def update(self):
        if not IRoot.providedBy(self.context):
            # redirect to root url with browser hash tag
            # http://silva/folder/edit -> http://silva/edit#browser/folder
            root = self.context.get_root()
            root_path = root.getPhysicalPath()
            context_path = self.context.getPhysicalPath()
            if context_path[:len(root_path)] == root_path:
                root_url = absoluteURL(root, self.request)
                path = "/".join(context_path[len(root_path):])
                url = "%s/edit#browse/%s" % (root_url,
                                             path)
                raise Redirect(url)
            raise BadRequest('invalid path')


class SMIContainerListing(silvasmi.SMIView):
    """ Container listing view
    """
    grok.context(IContainer)
    grok.name('containerlisting')

    def update(self):
        self.items = self._get_items()

    def get_item_class(self, item):
        html_classes = ['container-listing-item',
                        self._get_meta_type_class(item)]
        if IContainer.providedBy(item):
            html_classes.append('container-listing-item-is-container')
        return " ".join(html_classes)

    def _get_items(self):
        default = self.context.get_default()
        if default is not None:
            yield default
        for item in self.context.get_ordered_publishables():
            yield item

    def _get_meta_type_class(self, item):
        return 'container-listing-item-' + \
            item.meta_type.lower().replace(' ', '-')


class SMIContainerListingItem(silvasmi.SMIView):
    """ List item view for container listings
    """
    grok.context(ISilvaObject)
    grok.name('containerlistingitem')

    @property
    def icon_url(self):
        return get_icon_url(self.context, self.request)

    @property
    def title_link_url(self):
        base = self._normalize_path(self.request.get('browse', None))
        return "#browse%s%s" % (base, self.context.id)

    def _normalize_path(self, path):
        if not path:
            return '/'
        if path.startswith('/'):
            path = path[1:]
        if path.endswith('/'):
            path = path[:-1]

        components = path.split('/')
        result = []

        for component in components:
            if component == '..' and len(result) > 0:
                result.pop()
            else:
                result.append(component)

        return '/' + '/'.join(result) + '/'

    @property
    def id_link_url(self):
        return "#"
