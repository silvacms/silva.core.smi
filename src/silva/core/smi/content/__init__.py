# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.ui.interfaces import IUIScreen
from silva.core.interfaces import IContent, INonPublishable
from silva.translations import translate as _
from silva.ui.menu import ExpendableMenuItem, MenuItem, ContentMenu
from zeam.form import silva as silvaforms
from zope.interface import classImplements


class IEditScreen(IUIScreen):
    """Marker used to mark edit tab.
    """


class ContentEditMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IContent)
    grok.order(10)
    name = _('Edit')
    screen = 'content'
    interface = IEditScreen


class NonPublishableEditMenu(MenuItem):
    grok.adapts(ContentMenu, INonPublishable)
    grok.order(10)
    name = _(u'Edit')
    screen = 'content'
    interface = IEditScreen


classImplements(silvaforms.SMIEditForm, IEditScreen)







