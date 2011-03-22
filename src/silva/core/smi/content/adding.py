# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import queryUtility
from zope.component.interfaces import IFactory

from zExceptions import NotFound

from infrae.rest import REST
from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IContainer
from silva.translations import translate as _
from silva.ui.menu import ExpendableMenuItem, ContentMenu


class AddMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IContainer)
    grok.order(15)
    name = _('Add')
    screen = 'adding'

    def get_submenu_items(self):
        entries = []
        for addable in IAddableContents(self.content).get_authorized_addables():
            entries.append({
                    'name': addable,
                    'screen': '/'.join((self.screen, addable))})
        return entries


class Adding(REST):
    grok.context(IContainer)
    grok.name('silva.ui.adding')
    grok.require('silva.ChangeSilvaContent')

    def publishTraverse(self, request, name):
        addables = IAddableContents(self.context).get_container_addables()
        if name in addables:
            factory = queryUtility(IFactory, name=name)
            if factory is not None:
                factory = factory(self.context, request)
                # Set parent for security check.
                factory.__name__ = '/'.join((self.__name__, name))
                factory.__parent__ = self
                return factory
        raise NotFound(name)


