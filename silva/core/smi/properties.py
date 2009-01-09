# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi import smi, edit
from silva.core import conf as silvaconf

from Products.Silva.i18n import translate as _
from Products.Silva import interfaces

silvaconf.templatedir('templates')
silvaconf.view(smi.PropertiesTab)

class AddablesButton(smi.SMIButton):

    silvaconf.context(interfaces.IContainer)
    silvaconf.order(50)

    tab = 'tab_addables'
    label = _(u"addables")
    help = _(u"change the addables allowed in this publication: alt-d")
    accesskey = 'd'


class SettingsButton(smi.SMIButton):

    silvaconf.order(10)

    tab = 'tab_settings'
    label = _(u"settings")
    help = _(u"various settings: alt-e")
    accesskey = 'e'


class LocalSiteButton(smi.SMIButton):

    silvaconf.context(interfaces.IPublication)
    silvaconf.require('zope2.ViewManagementScreens')
    silvaconf.order(70)

    tab = 'tab_localsite'
    label = _(u"local site")
    help = _(u"local site")


class SubscriptionButton(smi.SMIButton):

    silvaconf.order(110)

    tab = 'tab_subscriptions'
    label = _(u"subscriptions")
    help = _(u"manage subscriptions: alt-u")
    accesskey = "u"

    def available(self):
        return (interfaces.ISubscribable(self.context, None) is not None and
                self.context.service_subscriptions.subscriptionsEnabled())


class PublishNowButton(edit.PublishNowButton):
    pass



