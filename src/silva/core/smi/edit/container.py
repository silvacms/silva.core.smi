# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.icon import get_meta_type_icon
from Products.Silva.ExtensionRegistry import extensionRegistry as registry

from five import grok
from silva.core.interfaces import IContainer
from silva.core.views import views as silvaviews
from silva.core.smi import smi as silvasmi
from silva.core.smi.interfaces import ISMILayer, IAddingTab
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


class ImportButton(silvasmi.SMIMiddleGroundButton):
    grok.context(IContainer)
    grok.require('silva.ChangeSilvaContent')
    grok.order(50)

    tab = 'tab_edit_import'
    label = _(u"import")
    help = _(u"import xml data or a zip file: alt-i")
    accesskey = 'i'


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
        required=False)
    content = schema.Choice(
        title=_(u"Content type"),
        description=_("Select a new content to add"),
        source=silva_content_types,
        required=False)


class SMIContainerActionForm(silvasmi.SMIMiddleGroundActionForm):
    """ Button form to create a new Version
    """
    grok.context(IContainer)
    grok.order(20)

    fields = silvaforms.Fields(INewContent)
    fields['position'].mode = silvaforms.HIDDEN
    prefix = 'md.container'
    ignoreContent = False

    def __init__(self, *args):
        super(SMIContainerActionForm, self).__init__(*args)
        # We edit ourselves, to get the default value (which dependent
        # of the selected view).
        self.setContentData(self)

    @property
    def content(self):
        if IAddingTab.providedBy(self.view):
            return self.view.__name__
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
        if data['content']:
            url.append(data['content'])
        self.redirect('/'.join(url))
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

    def __init__(self, context, request):
        # Due to bugs in traversing, 'edit' is not called. so set back
        # what is done there.
        context = context.get_container()
        applySkin(request, ISMILayer)
        super(AddingView, self).__init__(context, request)

    def publishTraverse(self, request, name):
        # XXX validate name
        factory = queryUtility(IFactory, name=name)
        if factory is not None:
            return factory(self.context, request)
        return super(AddingView, self).publishTraverse(request, name)

    def update(self):
        self.addables = []
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