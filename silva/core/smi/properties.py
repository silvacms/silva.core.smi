# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi.interfaces import ISMIExecutorButton
from silva.core.smi import smi
from silva.core import conf as silvaconf

from Products.Silva.i18n import translate as _
from Products.Silva import interfaces
from Products.Silva.adapters.interfaces import ISubscribable

silvaconf.templatedir('templates')
silvaconf.view(smi.PropertiesTab)

class AddablesButton(smi.SMIButton):

    silvaconf.context(interfaces.IPublication)
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


class SubscriptionButton(smi.SMIButton):

    silvaconf.order(110)

    tab = 'tab_subscriptions'
    label = _(u"subscriptions")
    help = _(u"manage subscriptions: alt-u")
    accesskey = "u"

    def available(self):
        return ISubscribable(self.context, None) is not None


class PublishNowButton(smi.SMIButton):

    silvaconf.context(interfaces.IVersionedContent)
    silvaconf.implements(ISMIExecutorButton)
    silvaconf.order(20)

    label = _(u"publish now")
    help = _(u"publish this document: alt-p")
    accesskey = 'p'

    @property
    def tab(self):
        return 'quick_publish?return_to=%s' % self.view.tab_name

    def available(self):
        return bool(self.context.get_unapproved_version())
