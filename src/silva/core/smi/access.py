# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

from five import grok

from silva.core.smi import smi
from silva.core.smi.interfaces import IAccessTab, ISMITabIndex
from silva.core.interfaces import ISilvaObject, IUserAccessSecurity
from silva.core.interfaces import IUserAuthorization
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class AccessTab(silvaforms.SMIComposedForm):
    """Control access to Silva.
    """
    grok.context(ISilvaObject)
    grok.implements(IAccessTab, ISMITabIndex)
    grok.name('tab_access')
    grok.require('silva.ChangeSilvaAccess')

    tab = 'access'

    label = _(u"manage access to Silva content")
    description = _(u"This screen let you authorize or cancel access "
                    u"to this content and content below it.")


class UserAccessForm(silvaforms.SMISubTableForm):
    """Form to give/revoke access to users.
    """
    grok.context(ISilvaObject)
    grok.order(10)
    grok.view(AccessTab)

    label = _(u"user roles")
    fields = silvaforms.Fields(IUserAuthorization)
    ignoreContent = False
    mode = silvaforms.DISPLAY

    def getItems(self):
        values = IUserAccessSecurity(self.context).getAuthorizations().items()
        values.sort(key=operator.itemgetter(0))
        return map(operator.itemgetter(1), values)

    @silvaforms.action(_(u"revoke"), category='tableActions')
    def revoke(self):
        self.status = "Dude, you lost in the ware"

class AccessPermissionForm(silvaforms.SMISubForm):
    """Form to manage default permission needed to see the current
    content.
    """
    grok.context(ISilvaObject)
    grok.order(30)
    grok.view(AccessTab)

    label = _(u"public view access restrictions")
    description = _(u"Setting an access restriction here affects "
                    u"contents on this and lower levels.")


class LookupUserButton(smi.SMIButton):
    grok.view(AccessTab)
    grok.order(10)

    tab = 'lookup'
    help = _(u"lookup users: alt-l")
    accesskey = 'l'
    style = 'float:right'

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
