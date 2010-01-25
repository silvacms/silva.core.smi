# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core import interfaces
from silva.core.smi import smi
from silva.translations import translate as _


grok.view(smi.AccessTab)


class GroupAdminButton(smi.SMIButton):

    grok.context(interfaces.IContainer)
    grok.order(50)

    tab = 'tab_access_groups'
    label = _(u"groups admin")
    help = _(u"groups administration: alt-g")
    accesskey = 'g'


    def available(self):
        # Berk.
        return self.context.sec_groups_enabled() and \
            hasattr(self.context, 'service_groups')


class LookupUserButton(smi.SMIButton):

    grok.order(10)

    tab = 'lookup'
    help = _(u"lookup users: alt-l")
    accesskey = 'l'

    @property
    def selected(self):
        # XXX hack  for the moment.  Should have something  nicer when
        # every view will be a real view.
        path = self.request.PATH_TRANSLATED.split('/')
        return path[-1].startswith('lookup_ui')

    @property
    def label(self):
        if self.context.sec_can_find_users():
            return _(u"add users")
        return _(u"lookup users")
