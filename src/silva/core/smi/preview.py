# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.interfaces import IDirectlyRendered
from silva.core.interfaces import ISilvaObject
from silva.core.views.interfaces import ISilvaURL
from silva.translations import translate as _
from silva.ui.menu import ViewMenuItem
from silva.ui.rest.base import PageREST
from zope.component import getMultiAdapter


class PreviewMenu(ViewMenuItem):
    grok.context(ISilvaObject)
    grok.order(10)
    name = _('Preview')
    action = 'preview'


class Preview(PageREST):
    grok.context(ISilvaObject)
    grok.name('silva.ui.preview')
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        return {"ifaces": ["preview"],
                "html_url": getMultiAdapter((self.context, self.request), ISilvaURL).preview()}


class DirectlyRenderedPreview(PageREST):
    grok.context(IDirectlyRendered)
    grok.name('silva.ui.preview')
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        return {"ifaces": ["preview"],
                "html": self.context.preview()}
