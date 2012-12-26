# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getMultiAdapter, getUtility

from silva.core.interfaces import IViewableObject
from silva.core.views.interfaces import ISilvaURL
from silva.translations import translate as _
from silva.ui.interfaces import IUIService
from silva.ui.menu import LinkMenuItem, ViewMenu


class DisplayMenu(LinkMenuItem):
    grok.adapts(ViewMenu, IViewableObject)
    grok.order(20)
    name = _('View')
    description = _(u'View the published item in a new tab or window.')
    accesskey = u';'

    def get_url(self, context, request):
        service = getUtility(IUIService)
        url = getMultiAdapter(
            (context, request),
            ISilvaURL).url(host=service.public_url or None)
        return url
