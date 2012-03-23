# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope import schema
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from silva.core.interfaces import ISilvaObject, IVersionedContent, IVersion
from silva.core.layout.interfaces import IMarkManager
from silva.core.smi.interfaces import IPropertiesTab
from silva.core.smi.smi import SMIButton
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction

import makers

## This module extends the Customization Tab to support VersionedContent. (VC)
## VC's should have their markers on the Version (similar to how metadata
## is stored).  The forms are on the VersionedContent, so their grok.context
## is IVersionedContent.  Since we're actually operating on the desired version
## (be it editable, viewable, or closed), in the forms __init__ we switch 
## context to the version, BEFORE calling super.  The "before" part is important
## as in the case of the two DisplayForms

class VersionInterfaces(makers.ContentInterfaces):
    grok.context(IVersion)
    
    @property
    def usedInterface(self):
        manager = IMarkManager(self.context)
        return manager.usedInterfaces


class VersionMarkers(grok.Adapter):
    grok.context(IVersion)
    grok.provides(makers.IUsedMarkers)
    
    @property
    def usedMarkers(self):
        manager = IMarkManager(self.context)
        return manager.usedMarkers


class DisplayUsedInterfaces(makers.DisplayUsedInterfaces):
    grok.context(IVersionedContent)

    
    def __init__(self, context, parent, request):
        """Override context, we want the version instead of the 
           VersionedContent.  We override the context, rather than use a
           custom dataManager, because the super's code uses self.context
           for things.  Using a custom data manager will not change
           the availability.
           
           Any version will do, the aim is to get the interfaces used by the
           version
        """
        c = context.get_previewable()
        super(DisplayUsedInterfaces, self).__init__(c, parent, request)


class DisplayUsedMarkersViewable(silvaforms.SMISubForm):
    """Displays the used markers for the published or closed version
    """
    grok.view(makers.ManageCustomizeMarker)
    grok.order(50)
    grok.context(IVersionedContent)
    
    label = _(u"markers on the viewable or closed version")
    fields = silvaforms.Fields(makers.IUsedMarkers)
    mode = silvaforms.DISPLAY
    ignoreContent = False
    dataManager = silvaforms.makeAdaptiveDataManager(makers.IUsedMarkers)
    
    def __init__(self, context, parent, request):
        """Sets self.version to be the published or closed version
        """
        self.version = context.get_viewable()
        if not self.version:
            self.version = context.get_last_closed()
        if not self.version:
            self.version = context.get_editable()
        if self.version:
            context = self.version
            
        super(DisplayUsedMarkersViewable, self).__init__(context, parent, request)
            
    def available(self):
        if not self.version:
            return False
        markerField = self.fields['usedMarkers']
        return len(markerField.valueField.getChoices(self.version))


class AddCustomizationMarker(makers.AddCustomizationMarker):
    """Like DisplayUsedInterfaces, switch the content to the editable version.
    """
    grok.context(IVersionedContent)
    label = _(u"add a marker to editable version to alter the rendering")
    
    def __init__(self, context, parent, request):
        """Override context, we want the version instead of the 
           VersionedContent.  We override the context, rather than use a
           custom dataManager, because the super's code uses self.context
           for things.  Using a custom data manager will not change
           the availability, and the 'add' handler uses self.context.
        """
        self.version = context.get_editable()
        #only switch self.context if there is an editable version
        if self.version:
            context = self.version
        super(AddCustomizationMarker, self).__init__(context, parent, request)
            
    def available(self):
        if not self.version:
            return False
        return super(AddCustomizationMarker, self).available()


class RemoveCustomizationMarker(makers.RemoveCustomizationMarker):
    """Remove Marker for Versioned Content -- removes the marker from
       the editable version.
    """
    grok.context(IVersionedContent)
    label = _(u"remove a marker from the editable version")
    
    def __init__(self, context, parent, request):
        """Override context, we want the version instead of the 
           VersionedContent.  We override the context, rather than use a
           custom dataManager, because the super's code uses self.context
           for things.  Using a custom data manager will not change
           the availability, and the 'remove' handler uses self.context.
        """
        self.version = context.get_editable()
        #only switch self.context if there is an editable version
        if self.version:
            context = self.version
        super(RemoveCustomizationMarker, self).__init__(context, parent, request)
            
    def available(self):
        if not self.version:
            return False
        return super(RemoveCustomizationMarker, self).available()

    