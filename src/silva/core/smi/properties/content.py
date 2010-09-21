# $Id$
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
from five import grok

from silva.core import interfaces
from silva.core.smi import smi
from silva.core.smi.interfaces import IPropertiesTab
from silva.translations import translate as _


grok.view(IPropertiesTab)


class AddablesButton(smi.SMIMiddleGroundButton):
    grok.context(interfaces.IContainer)
    grok.require('silva.ManageSilvaContentSettings')
    grok.order(50)

    tab = 'tab_addables'
    label = _(u"addables")
    help = _(u"change the addables allowed in this publication: alt-d")
    accesskey = 'd'


class SettingsButton(smi.SMIMiddleGroundButton):
    grok.order(10)
    grok.require('silva.ManageSilvaContent')

    tab = 'tab_settings'
    label = _(u"settings")
    help = _(u"various settings: alt-e")
    accesskey = 'e'


class LocalSiteButton(smi.SMIMiddleGroundButton):
    grok.context(interfaces.IPublication)
    grok.order(70)
    grok.require('zope2.ViewManagementScreens')

    tab = 'tab_localsite'
    label = _(u"local site")
    help = _(u"local site")

    def available(self):
        return not interfaces.IRoot.providedBy(self.context)

