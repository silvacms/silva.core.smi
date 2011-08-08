# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.component import queryUtility
from zope.component.interfaces import IFactory
from zExceptions import NotFound

from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IContainer
from silva.translations import translate as _
from silva.ui.rest import Screen, REST
from silva.ui.menu import ExpendableMenuItem, ContentMenu
from silva.ui.interfaces import IMenuItem


class Adding(REST):
    grok.adapts(Screen, IContainer)
    grok.name('adding')
    grok.require('silva.ChangeSilvaContent')

    def publishTraverse(self, request, name):
        addables = IAddableContents(self.context).get_container_addables()
        if name in addables:
            factory = queryUtility(IFactory, name=name)
            if factory is not None:
                form = factory(self.context, request)
                # Set parent for security check.
                form.__name__ = '/'.join((self.__name__, name))
                form.__parent__ = self
                return form
        # If it is not addable, it is not an addable.
        raise NotFound(name)


class AddableMenuItem(object):
    """A Addable MenuItem
    """
    grok.implements(IMenuItem)

    def __init__(self, addable):
        self.name = addable

    def available(self):
        return True

    def describe(self, page, path, actives):
        info = {'name': self.name,
                'screen': '/'.join((path, self.name))}
        if actives and actives[0].__name__ == info['screen']:
            info['active'] = True
        return info


class AddMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IContainer)
    grok.order(15)
    grok.require('silva.ChangeSilvaContent')
    name = _('Add')
    screen = Adding

    def get_submenu_items(self):
        return map(AddableMenuItem, IAddableContents(self.content).get_authorized_addables())
