# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope import schema
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from silva.ui.menu import MenuItem
from silva.core.smi.settings import SettingsMenu, Settings
from silva.core.interfaces import ISilvaObject
from silva.core.layout.interfaces import IMarkManager
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction


class CustomizationMenu(MenuItem):
    grok.adapts(SettingsMenu, ISilvaObject)
    grok.order(100)
    grok.require('silva.ManageSilvaContent')
    name = _(u'Customization')
    screen = 'customization'


class ManageCustomizeMarker(silvaforms.SMIComposedForm):
    """This form lets you add and remove customization markers for the
    current content.
    """
    grok.adapts(Settings, ISilvaObject)
    grok.name('customization')
    grok.require('silva.ManageSilvaContent')

    label = _(u"Customization markers")
    description = _(u"This screen lets you tag content with markers "
                    u"which can alter how content is displayed.")

# Forms to mark objects


def interfaceTerm(interface):
    """Create a vocabulary term to represent an interface.
    """
    title = interface.__doc__
    if '\n' in title:
        title = title.split('\n', 1)[0].strip()
    if not title:
        title = interface.__identifier__
    return SimpleTerm(token=interface.__identifier__,
                      value=interface,
                      title=title)


@grok.provider(IContextSourceBinder)
def usedInterfacesForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary(
        [interfaceTerm(interface)
         for interface in manager.usedInterfaces])


@grok.provider(IContextSourceBinder)
def usedMarkersForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary(
        [interfaceTerm(interface)
         for interface in manager.usedMarkers])


@grok.provider(IContextSourceBinder)
def availableMarkersForContent(context):
    manager = IMarkManager(context)
    return SimpleVocabulary(
        [interfaceTerm(interface)
         for interface in manager.availableMarkers])


class IDisplayUsedInterfaces(Interface):

    usedInterface = schema.Set(
        title=_(u"used interfaces"),
        value_type=schema.Choice(
            source=usedInterfacesForContent),
        required=False)


class IRemoveCustomizationMarker(Interface):

    usedMarkers = schema.Set(
        title=_(u"used markers"),
        value_type=schema.Choice(
            source=usedMarkersForContent))


class IAddCustomizationMarker(Interface):

    availablesMarkers = schema.Set(
        title=_(u"available markers"),
        value_type=schema.Choice(
            source=availableMarkersForContent))


class ContentInterfaces(grok.Adapter):
    grok.context(ISilvaObject)
    grok.provides(IDisplayUsedInterfaces)

    @property
    def usedInterface(self):
        manager = IMarkManager(self.context)
        return manager.usedInterfaces


class DisplayUsedInterfaces(silvaforms.SMISubForm):
     grok.view(ManageCustomizeMarker)
     grok.order(10)
     grok.context(ISilvaObject)

     label = _(u"Interfaces in use which affect the rendering of content")
     fields = silvaforms.Fields(IDisplayUsedInterfaces)
     mode = silvaforms.DISPLAY
     dataManager = silvaforms.makeAdaptiveDataManager(IDisplayUsedInterfaces)
     ignoreContent = False
     ignoreRequest = True


class AddCustomizationMarker(silvaforms.SMISubForm):
    grok.view(ManageCustomizeMarker)
    grok.order(20)
    grok.context(ISilvaObject)

    label = _(u"Add a marker to alter the rendering")
    fields = silvaforms.Fields(IAddCustomizationMarker)

    def available(self):
        markerField = self.fields['availablesMarkers']
        return len(markerField.valueField.getChoices(self.context))

    @silvaforms.action(
        _(u"Add marker"),
        description=_(u"mark the content with the selected marker(s)"))
    def add(self):
        values, errors = self.extractData()
        if not values.get('availablesMarkers', None):
            self.send_message(_(u"You need to select a marker."), type=u"error")
            return silvaforms.FAILURE

        manager = IMarkManager(self.context)
        for value in values['availablesMarkers']:
            manager.addMarker(value)
        self.send_message(_(u"Marker added."), type=u"feedback")
        return silvaforms.SUCCESS


class RemoveCustomizationMarker(silvaforms.SMISubForm):
    grok.view(ManageCustomizeMarker)
    grok.order(30)
    grok.context(ISilvaObject)

    label = _(u"Remove a marker")
    fields = silvaforms.Fields(IRemoveCustomizationMarker)

    def available(self):
        markerField = self.fields['usedMarkers']
        return len(markerField.valueField.getChoices(self.context))

    @silvaforms.action(
        _(u"Remove"),
        description=_(u"remove the selected marker(s) from the content"),
        implements=IRemoverAction)
    def remove(self):
        values, errors = self.extractData()
        if not values.get('usedMarkers', None):
            self.send_message(_(u"You need to select a marker."), type=u"error")
            return silvaforms.FAILURE

        manager = IMarkManager(self.context)
        for value in values['usedMarkers']:
            manager.removeMarker(value)
        self.send_message(_(u"Marker removed."), type=u"feedback")
        return silvaforms.SUCCESS


