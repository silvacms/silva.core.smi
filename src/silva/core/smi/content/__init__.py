# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.interfaces import IContent, INonPublishable
from silva.translations import translate as _
from silva.ui.menu import MenuItem, ContentMenu
from zeam.form import silva as silvaforms
from zope.interface import Interface, classImplements


class IEditTab(Interface):
    """Marker used to mark edit tab.
    """


class ContentEditMenu(MenuItem):
    grok.adapts(ContentMenu, IContent)
    grok.order(10)
    name = _('Edit')
    screen = 'content'
    interface = IEditTab


class NonPublishableEditMenu(MenuItem):
    grok.adapts(ContentMenu, INonPublishable)
    grok.order(10)
    name = _(u'Edit')
    screen = 'content'
    interface = IEditTab


classImplements(silvaforms.SMIEditForm, IEditTab)







