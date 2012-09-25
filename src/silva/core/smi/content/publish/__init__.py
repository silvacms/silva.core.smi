# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt


from five import grok
from zope.interface import Interface
from silva.core.interfaces import IVersionedObject
from silva.translations import translate as _
from silva.ui.menu import ContentMenu, ExpendableMenuItem
from silva.ui.rest import Screen
from zeam.form import silva as silvaforms


class Publish(silvaforms.SMIComposedForm):
    """Publish tab.
    """
    grok.adapts(Screen, IVersionedObject)
    grok.require('silva.ChangeSilvaContent')
    grok.name('publish')

    label = _('Publication')


class PublishMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, IVersionedObject)
    grok.require('silva.ChangeSilvaContent')
    grok.order(30)
    name = _('Publish')

    screen = Publish


class IPublicationFields(Interface):
    """ Interface to register autofields for request approval
    """
