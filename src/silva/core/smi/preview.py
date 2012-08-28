# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.interfaces import IDirectlyRendered
from silva.core.interfaces import IViewableObject
from silva.core.views.interfaces import ISilvaURL
from silva.translations import translate as _
from silva.ui.menu import ViewMenu, MenuItem
from silva.ui.rest import PageREST, Screen
from silva.ui.interfaces import IUIScreen
from zope.component import getMultiAdapter


class IPreviewScreen(IUIScreen):
    """Marker used to mark edit tab.
    """


class Preview(PageREST):
    grok.adapts(Screen, IViewableObject)
    grok.implements(IPreviewScreen)
    grok.name('preview')
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        url = getMultiAdapter((self.context, self.request), ISilvaURL).preview()
        return {"ifaces": ["preview"],
                "html_url": url}


class DirectlyRenderedPreview(PageREST):
    grok.adapts(Screen, IDirectlyRendered)
    grok.implements(IPreviewScreen)
    grok.name('preview')
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        content = getMultiAdapter(
            (self.context, self.request), name='content.html')
        return {"ifaces": ["preview"],
                "html": content()}


class PreviewMenu(MenuItem):
    grok.adapts(ViewMenu, IViewableObject)
    grok.order(10)
    name = _('Preview')
    description = _(u'view item while staying in the admin interface')
    screen = 'preview'
    interface = IPreviewScreen
