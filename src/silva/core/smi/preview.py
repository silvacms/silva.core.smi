# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface
from zope.component import getMultiAdapter, getUtility

from silva.core.interfaces import IViewableObject, IDirectlyRendered
from silva.core.views.interfaces import ISilvaURL
from silva.translations import translate as _
from silva.ui.interfaces import IJSView, IUIService
from silva.ui.interfaces import IUIScreen
from silva.ui.menu import ViewMenu, MenuItem
from silva.ui.rest import PageREST, Screen


class PreviewJSView(grok.MultiAdapter):
    """Preview JSView.
    """
    grok.provides(IJSView)
    grok.adapts(Interface, Interface)
    grok.name('content-preview')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, screen):
        service = getUtility(IUIService)
        url = getMultiAdapter(
            (self.context, self.request),
            ISilvaURL).url(preview=True, host=service.preview_url or None)
        return {"ifaces": ["preview"],
                "html_url": url}


class DirectlyRenderedPreview(grok.MultiAdapter):
    """Preview JSView for directly rendered contents.
    """
    grok.provides(IJSView)
    grok.adapts(IDirectlyRendered, Interface)
    grok.name('content-preview')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, screen):
        view = getMultiAdapter(
            (self.context, self.request),
            name='content.html')
        return {"ifaces": ["preview"],
                "html": view()}


class IPreviewScreen(IUIScreen):
    """Marker used to mark edit tab.
    """


class Preview(PageREST):
    grok.adapts(Screen, IViewableObject)
    grok.implements(IPreviewScreen)
    grok.name('preview')
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        view = getMultiAdapter(
            (self.context, self.request),
            IJSView,
            name='content-preview')
        return view(self)


class PreviewMenu(MenuItem):
    grok.adapts(ViewMenu, IViewableObject)
    grok.order(10)
    name = _('Preview')
    description = _(u'Preview this item within the management interface.')
    screen = 'preview'
    interface = IPreviewScreen
