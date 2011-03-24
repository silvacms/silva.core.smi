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
from silva.ui.rest import Screen, PageWithTemplateREST
from silva.ui.menu import ExpendableMenuItem, ContentMenu

from Products.Silva.ExtensionRegistry import extensionRegistry


class Adding(PageWithTemplateREST):
    grok.adapts(Screen, IContainer)
    grok.name('adding')
    grok.require('silva.ChangeSilvaContent')

    def update(self):
        self.addables = []
        for addable in IAddableContents(self.context).get_container_addables():
            info = extensionRegistry.get_addable(addable)
            self.addables.append({'name': addable,
                                  'screen': '/'.join(('adding', addable)),
                                  'description': info['doc']})

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
    name = _('Add')
    screen = Adding

    def get_submenu_items(self):
        entries = []
        path = grok.name.bind().get(self.screen)
        for addable in IAddableContents(self.content).get_authorized_addables():
            entries.append({
                    'name': addable,
                    'screen': '/'.join((path, addable))})
        return entries
