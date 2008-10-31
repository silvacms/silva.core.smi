# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi import smi
from silva.core import conf as silvaconf

from Products.Silva.i18n import translate as _
from Products.Silva import interfaces

silvaconf.templatedir('templates')
silvaconf.view(smi.AccessTab)

class GroupAdminButton(smi.SMIButton):

    silvaconf.context(interfaces.IContainer)
    silvaconf.order(50)

    tab = 'tab_access_groups'
    label = _(u"groups admin")
    help = _(u"groups administration: alt-g")
    accesskey = 'g'


    def available(self):
        # Berk.
        return self.context.sec_groups_enabled() and \
            hasattr(self.context, 'service_groups')

class LookupUserButton(smi.SMIButton):

    silvaconf.order(10)

    tab = 'lookup'
    help = _(u"lookup users: alt-l")
    accesskey = 'l'

    @property
    def label(self):
        if self.context.sec_can_find_users():
            return _(u"add users")
        return _(u"lookup users")
