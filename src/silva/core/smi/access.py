# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

from five import grok
from zope.cachedescriptors.property import CachedProperty
from zope import interface, schema, component

from Products.Silva.Security import UnauthorizedRoleAssignement

from silva.core.smi.interfaces import IAccessTab, ISMITabIndex
from silva.core.interfaces import ISilvaObject
from silva.core.interfaces import IAccessSecurity, IUserAccessSecurity
from silva.core.interfaces import IUserAuthorization, role_vocabulary
from silva.core.interfaces import IMemberService
from silva.core.cache.store import ClientStore
from silva.translations import translate as _
from zeam.form import silva as silvaforms

USER_STORE_KEY = 'lookup user'


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


class ILookupUser(interface.Interface):
    """Lookup a new user
    """
    user = schema.TextLine(
        title=_(u"username"),
        description=_(u"username or part of the username to lookup"),
        required=True)


class LookupForm(silvaforms.SMISubForm):
    """Form to manage default permission needed to see the current
    content.
    """
    grok.context(ISilvaObject)
    grok.order(5)
    grok.view(AccessTab)

    label = _(u"lookup users")
    description = _(u"Lookup new user to give them roles.")
    fields = silvaforms.Fields(ILookupUser)

    @silvaforms.action(_(u"lookup user"))
    def lookup(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        username = data['user'].strip()
        if len(username) < 2:
            self.send_message(
                _(u"Search input is too short. "
                  u"Please supply more characters"),
                type="error")
            return silvaforms.FAILURE

        service = component.getUtility(IMemberService)

        store = ClientStore(self.request)
        users = set()
        for member in service.find_members(username, location=self.context):
            users.add(member.userid())
        if users:
            users = store.get(USER_STORE_KEY, set()).union(users)
            store.set(USER_STORE_KEY, users)
            self.send_message(
                _(u"Found ${count} users: ${users}",
                  mapping={'count': len(users),
                           'users': u', '.join(users)}),
                type="feedback")
        else:
            self.send_message(
                _(u"No matching users"),
                type="error")
        return silvaforms.SUCCESS


class IGrantRole(interface.Interface):
    """A role for a user.
    """
    role = schema.Choice(
        title=_(u"role to grant"),
        source=role_vocabulary,
        required=True)


class UserAccessForm(silvaforms.SMISubTableForm):
    """Form to give/revoke access to users.
    """
    grok.context(ISilvaObject)
    grok.order(10)
    grok.view(AccessTab)

    label = _(u"user roles")
    ignoreContent = False
    ignoreRequest = True
    mode = silvaforms.DISPLAY
    fields = silvaforms.Fields(IGrantRole)
    fields['role'].mode = silvaforms.INPUT
    fields['role'].ignoreRequest = False
    fields['role'].ignoreContent = True
    tableFields = silvaforms.Fields(IUserAuthorization)
    tableFields['username'].mode = 'silva.icon'
    tableActions = silvaforms.TableActions()

    def getItems(self):
        access = IUserAccessSecurity(self.context)
        authorizations = access.get_authorizations().items()
        authorizations.sort(key=operator.itemgetter(0))
        return map(operator.itemgetter(1), authorizations)

    @silvaforms.action(_(u"revoke role"), category='tableActions')
    def revoke(self, authorization, line):
        try:
            if authorization.revoke():
                self.send_message(
                    _('Removed role "${role}" from user "${username}"',
                      mapping={'role': authorization.local_role,
                               'username': authorization.username}),
                    type="feedback")
            else:
                self.send_message(
                    _('User "${username}" doesn\'t have any local role',
                      mapping={'username': authorization.username}),
                    type="error")
        except UnauthorizedRoleAssignement, error:
            self.send_message(
                _(u'You are not allowed to remove role "${role}" '
                  u'from user "${userid}"',
                  mapping={'role': error.args[0],
                           'userid': error.args[1]}),
                type="error")
        return silvaforms.SUCCESS

    @silvaforms.action(_(u"grant role"), category='tableActions')
    def grant(self, authorization, line):
        data, errors = self.extractData(self.fields)
        if errors:
            return silvaforms.FAILURE
        role = data['role']
        if not role:
            return self.revoke(authorization, line)
        mapping = {'role': role,
                   'username': authorization.username}
        try:
            if authorization.grant(role):
                self.send_message(
                    _('Role "${role}" granted to user "${username}"',
                      mapping=mapping),
                    type="feedback")
            else:
                self.send_message(
                    _('User "${username}" already have role "${role}"',
                      mapping=mapping),
                    type="feedback")
        except UnauthorizedRoleAssignement:
            self.send_message(
                _(u'You are not allowed to remove role "${role}" '
                  u'from user "${userid}"',
                  mapping=mapping),
                type="error")
        return silvaforms.SUCCESS


class LookupResultForm(UserAccessForm):
    """Form to give/revoke access to users.
    """
    grok.order(6)

    label = _(u"lookup results")
    tableActions = silvaforms.TableActions()

    @CachedProperty
    def store(self):
        return ClientStore(self.request)

    def getUserIds(self):
        return self.store.get(USER_STORE_KEY, set())

    def available(self):
        return len(self.getUserIds()) != 0

    def getItems(self):
        user_ids = self.getUserIds()
        access = IUserAccessSecurity(self.context)
        authorizations = access.get_users_authorization(user_ids).items()
        authorizations.sort(key=operator.itemgetter(0))
        return map(operator.itemgetter(1), authorizations)

    @silvaforms.action(_(u"grant role"), category='tableActions')
    def grant(self, authorization, line):
        super(LookupResultForm, self).grant(authorization, line)

    @silvaforms.action(_(u"clear result"))
    def clear(self):
        self.store.set(USER_STORE_KEY, set())



class IGrantRole(interface.Interface):
    """A role for a user.
    """
    acquired = schema.Bool(
        title=_(u"is role acquired ?"),
        description=_(u"acquire the minimum role from the parent content"),
        readonly=True,
        required=False)
    role = schema.Choice(
        title=_(u"minimum role"),
        description=_(u"minimum required role needed to access this content"),
        source=role_vocabulary,
        required=False)


class AccessPermissionForm(silvaforms.SMISubForm):
    """Form to manage default permission needed to see the current
    content.
    """
    grok.context(ISilvaObject)
    grok.order(30)
    grok.view(AccessTab)

    label = _(u"public view access restriction")
    description = _(u"Setting an access restriction here affects "
                    u"contents on this and lower levels.")
    ignoreRequest = True
    ignoreContent = False
    dataManager = silvaforms.makeAdaptiveDataManager(IAccessSecurity)
    fields = silvaforms.Fields(IGrantRole)

    @silvaforms.action(_(u"acquire restriction"))
    def acquire(self):
        access = self.getContentData().getContent()
        if access.is_acquired():
            self.send_message(
                _(u"Minimum role setting was already acquired"),
                type="error")
        else:
            access.set_acquired()
            self.send_message(
                _(u"Acquiring minimum role setting"),
                type="feedback")
        return silvaforms.SUCCESS

    @silvaforms.action(_(u"set restriction"))
    def restrict(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        role = data['role']
        access = self.getContentData().getContent()
        if role:
            access.set_minimum_role(role)
        else:
            access.set_acquired()
        return silvaforms.SUCCESS
