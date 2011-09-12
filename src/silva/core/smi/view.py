# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import IViewableObject
from silva.translations import translate as _
from silva.ui.menu import LinkMenuItem, ViewMenu


class DisplayMenu(LinkMenuItem):
    grok.adapts(ViewMenu, IViewableObject)
    grok.order(20)
    name = _('View')
    description = _(u'view content in a new window')
    accesskey = u';'

    def get_url(self, context, request):
        return absoluteURL(context, request)
