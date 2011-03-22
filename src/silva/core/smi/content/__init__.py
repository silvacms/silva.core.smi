# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.interfaces import IContent
from silva.core.interfaces import INonPublishable
from silva.translations import translate as _
from silva.ui.menu import MenuItem, ContentMenu


class EditMenu(MenuItem):
    grok.adapts(ContentMenu, IContent)
    grok.order(10)
    name = _('Edit')
    screen = 'content'


class EditAssetMenu(MenuItem):
    grok.adapts(ContentMenu, INonPublishable)
    grok.order(10)
    name = _(u'Edit')
    screen = 'content'






