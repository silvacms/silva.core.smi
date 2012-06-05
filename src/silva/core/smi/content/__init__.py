# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import classImplements
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from silva.core import conf as silvaconf
from silva.core.interfaces import IContent, INonPublishable
from silva.translations import translate as _
from silva.ui.interfaces import IUIScreen
from silva.ui.menu import ExpendableMenuItem, ContentMenu
from zeam.form import silva as silvaforms


class IEditScreen(IUIScreen):
    """Marker used to mark edit tab.
    """

# We cannot do it with one unique class, because of Container

class EditMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, INonPublishable)
    grok.order(10)
    name = _('Edit')
    screen = 'content'
    interface = IEditScreen


class ContentEditMenu(EditMenu):
    grok.adapts(ContentMenu, IContent)


classImplements(silvaforms.SMIEditForm, IEditScreen)


class ICompareResources(IDefaultBrowserLayer):
    silvaconf.resource('compare.css')
