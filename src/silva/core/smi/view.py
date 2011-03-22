# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import ISilvaObject
from silva.translations import translate as _
from silva.ui.menu import MenuItem, ViewMenu
from silva.ui.rest import UIREST


class DisplayMenu(MenuItem):
    grok.adapts(ViewMenu, ISilvaObject)
    grok.order(20)
    name = _('View')
    description = _(u'view content in a new window')
    action = 'view'


class ViewREST(UIREST):
    grok.name('silva.ui.actions.view')
    grok.context(ISilvaObject)

    def POST(self):
        data = {'ifaces': ['view'],
                'url': absoluteURL(self.context, self.request)}
        return self.json_response(data)
