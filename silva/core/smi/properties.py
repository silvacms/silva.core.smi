# $Id$
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl import getSecurityManager

from five import grok

from silva.core import interfaces
from silva.core.smi import smi, edit
from silva.translations import translate as _


grok.view(smi.PropertiesTab)


class AddablesButton(smi.SMIButton):

    grok.context(interfaces.IContainer)
    grok.order(50)

    tab = 'tab_addables'
    label = _(u"addables")
    help = _(u"change the addables allowed in this publication: alt-d")
    accesskey = 'd'


class SettingsButton(smi.SMIButton):

    grok.order(10)

    tab = 'tab_settings'
    label = _(u"settings")
    help = _(u"various settings: alt-e")
    accesskey = 'e'


class LocalSiteButton(smi.SMIButton):

    grok.context(interfaces.IPublication)
    grok.require('zope2.ViewManagementScreens')
    grok.order(70)

    tab = 'tab_localsite'
    label = _(u"local site")
    help = _(u"local site")

    def available(self):
        return not interfaces.IRoot.providedBy(self.context)


class SubscriptionButton(smi.SMIButton):

    grok.order(110)

    tab = 'tab_subscriptions'
    label = _(u"subscriptions")
    help = _(u"manage subscriptions: alt-u")
    accesskey = "u"

    def available(self):
        # XXX Later on there is a permission. There is no such thing
        # here. Improvise with this crappy API.
        userid = getSecurityManager().getUser().getId()
        roles = self.context.sec_get_roles_for_userid(userid) + \
            self.context.sec_get_all_roles(userid)
        if not ('Editor' in roles or 'ChiefEditor' in roles or 'Manager' in roles):
            return False
        return (interfaces.ISubscribable(self.context, None) is not None and
                self.context.service_subscriptions.subscriptionsEnabled())


class PublishNowButton(edit.PublishNowButton):
    pass



