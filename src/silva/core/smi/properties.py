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
    grok.order(50)

    tab = 'tab_addables'
    label = _(u"addables")
    help = _(u"change the addables allowed in this publication: alt-d")
    accesskey = 'd'


class SettingsButton(smi.SMIMiddleGroundButton):
    grok.order(10)

    tab = 'tab_settings'
    label = _(u"settings")
    help = _(u"various settings: alt-e")
    accesskey = 'e'


class LocalSiteButton(smi.SMIMiddleGroundButton):
    grok.context(interfaces.IPublication)
    grok.require('zope2.ViewManagementScreens')
    grok.order(70)

    tab = 'tab_localsite'
    label = _(u"local site")
    help = _(u"local site")

    def available(self):
        return not interfaces.IRoot.providedBy(self.context)


class SubscriptionButton(smi.SMIMiddleGroundButton):
    grok.order(110)

    tab = 'tab_subscriptions'
    label = _(u"subscriptions")
    help = _(u"manage subscriptions: alt-u")
    accesskey = "u"

    def available(self):
        return (interfaces.ISubscribable(self.context, None) is not None and
                self.context.service_subscriptions.subscriptionsEnabled())
