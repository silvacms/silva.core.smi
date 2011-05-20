# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import queryUtility
from zope.component.interfaces import IFactory

from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IContainer
from silva.translations import translate as _
from silva.ui.rest import Screen, REST
from silva.ui.menu import ExpendableMenuItem, ContentMenu


class Adding(REST):
    grok.adapts(Screen, IContainer)
    grok.name('adding')
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
        return super(Adding, self).publishTraverse(request, name)


class AddMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IContainer)
    grok.order(15)
    grok.require('silva.ChangeSilvaContent')
    name = _('Add')
    screen = Adding

    def get_submenu_items(self):
        entries = []
        path = self.identifier()
        for addable in IAddableContents(self.content).get_authorized_addables():
            entries.append({
                    'name': addable,
                    'screen': '/'.join((path, addable))})
        return entries
