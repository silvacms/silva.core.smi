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
from silva.core.interfaces import IUserAuthorization
from silva.core.interfaces import role_vocabulary, authenticated_role_vocabulary
from silva.core.services.interfaces import IMemberService
from silva.core.cache.store import SessionStore
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import (
    IRESTCloseOnSuccessAction, IRESTRefreshAction, IRemoverAction)

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


class LookupUserPopupAction(silvaforms.PopupAction):
    title = _(u"lookup users")
    description = _(u"look for users to assign roles: alt-l")
    action = 'smi-lookupuser'
    accesskey = u'l'


class ILookupUserSchema(interface.Interface):
    """Lookup a new user
    """
    user = schema.TextLine(
        title=_(u"username"),
        description=_(u"username or part of the username to lookup"),
        required=True)


class LookupUserAction(silvaforms.Action):
    grok.implements(IRESTCloseOnSuccessAction, IRESTRefreshAction)
    refresh = 'form-userrole'

    title = _(u"lookup user")
    description = _(u"look for users in order to assign them roles")

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.send_message(
                _(u"There were errors."),
                type="error")
            return silvaforms.FAILURE
        username = data['user'].strip()
        if len(username) < 2:
            form.send_message(
                _(u"Search input is too short. "
                  u"Please supply more characters"),
                type="error")
            return silvaforms.FAILURE

        service = component.getUtility(IMemberService)

        store = SessionStore(form.request)
        users = set()
        new_users = set()
        for member in service.find_members(username, location=form.context):
            userid = member.userid()
            users.add(userid)
            new_users.add(userid)
        if new_users:
            users = store.get(USER_STORE_KEY, set()).union(users)
            store.set(USER_STORE_KEY, users)
            form.send_message(
                _(u"Found ${count} users: ${users}",
                  mapping={'count': len(new_users),
                           'users': u', '.join(new_users)}),
                type="feedback")
        else:
            form.send_message(
                _(u"No matching users"),
                type="error")
            return silvaforms.FAILURE
        return silvaforms.SUCCESS


class LookupUserForm(silvaforms.RESTPopupForm):
    """Form to manage default permission needed to see the current
    content.
    """
    grok.name('smi-lookupuser')
    grok.context(ISilvaObject)

    label = _(u"lookup users")
    description = _(u"Lookup new user to give them roles.")
    fields = silvaforms.Fields(ILookupUserSchema)
    actions = silvaforms.Actions(
        LookupUserAction(),
        silvaforms.CancelAction())


class UserRole(silvaforms.SMISubFormGroup):
    grok.context(ISilvaObject)
    grok.order(20)
    grok.view(AccessTab)

    #label = _(u'manage users roles')
    #description = _(u"find, add and remove roles to users")


class IGrantRole(interface.Interface):
    """A role for a user.
    """
    role = schema.Choice(
        title=_(u"role to grant"),
        source=role_vocabulary,
        required=True)


class GrantAccessAction(silvaforms.Action):

    title = _(u"grant role")
    description = _(u"grant selected role to selected users(s)")

    def available(self, form):
        return len(form.lines) != 0

    def __call__(self, form, authorization, line):
        data, errors = form.extractData(form.fields)
        if errors:
            return silvaforms.FAILURE
        role = data['role']
        if not role:
            return form.revoke(authorization, line)
        mapping = {'role': role,
                   'username': authorization.username}
        try:
            if authorization.grant(role):
                form.send_message(
                    _('Role "${role}" granted to user "${username}"',
                      mapping=mapping),
                    type="feedback")
            else:
                form.send_message(
                    _('User "${username}" already have role "${role}"',
                      mapping=mapping),
                    type="error")
        except UnauthorizedRoleAssignement:
            form.send_message(
                _(u'You are not allowed to remove role "${role}" '
                  u'from user "${userid}"',
                  mapping=mapping),
                type="error")
        return silvaforms.SUCCESS


class RevokeAccessAction(silvaforms.Action):
    grok.implements(IRemoverAction)

    title = _(u"revoke role")
    description=_(u"revoke roles of selected user(s)")

    def available(self, form):
        return reduce(
            operator.or_,
            [False] + map(lambda l: l.getContent().local_role is not None,
                          form.lines))

    def __call__(self, form, authorization, line):
        try:
            role = authorization.local_role
            username = authorization.username
            if authorization.revoke():
                form.send_message(
                    _('Removed role "${role}" from user "${username}"',
                      mapping={'role': role,
                               'username': username}),
                    type="feedback")
            else:
                form.send_message(
                    _('User "${username}" doesn\'t have any local role',
                      mapping={'username': username}),
                    type="error")
        except UnauthorizedRoleAssignement, error:
            form.send_message(
                _(u'You are not allowed to remove role "${role}" '
                  u'from user "${userid}"',
                  mapping={'role': error.args[0],
                           'userid': error.args[1]}),
                type="error")
        return silvaforms.SUCCESS


class UserAccessForm(silvaforms.SMISubTableForm):
    """Form to give/revoke access to users.
    """
    grok.context(ISilvaObject)
    grok.order(20)
    grok.view(UserRole)

    label = _(u"user roles")
    ignoreContent = False
    ignoreRequest = True
    mode = silvaforms.DISPLAY
    fields = silvaforms.Fields(IGrantRole)
    fields['role'].mode = silvaforms.INPUT
    fields['role'].ignoreRequest = False
    fields['role'].ignoreContent = True
    fields['role'].available = lambda form: len(form.lines) != 0
    tableFields = silvaforms.Fields(IUserAuthorization)
    tableFields['username'].mode = 'silva.icon'
    tableActions = silvaforms.TableActions(
        RevokeAccessAction(),
        GrantAccessAction())

    def getItems(self):
        access = IUserAccessSecurity(self.context)
        authorizations = access.get_defined_authorizations().items()
        authorizations.sort(key=operator.itemgetter(0))
        return map(operator.itemgetter(1), authorizations)


class LookupUserResultForm(UserAccessForm):
    """Form to give/revoke access to users.
    """
    grok.order(10)

    emptyDescription = _(u"Search for users to assign them roles.")
    label = _(u"user clipboard")
    tableActions = silvaforms.TableActions(
        GrantAccessAction(),
        LookupUserPopupAction())

    @CachedProperty
    def store(self):
        return SessionStore(self.request)

    def getUserIds(self):
        return self.store.get(USER_STORE_KEY, set())

    def getItems(self):
        user_ids = self.getUserIds()
        if user_ids:
            access = IUserAccessSecurity(self.context)
            authorizations = access.get_users_authorization(user_ids).items()
            authorizations.sort(key=operator.itemgetter(0))
            return map(operator.itemgetter(1), authorizations)
        return []

    @silvaforms.action(
        _(u"clear clipboard"),
        description=_(u"clear user clipboard"),
        available=lambda form: len(form.lines) != 0,
        implements=IRemoverAction)
    def clear(self):
        self.store.set(USER_STORE_KEY, set())



class IAccessMinimumRole(interface.Interface):
    """A role for a user.
    """
    acquired = schema.Bool(
        title=_(u"is role acquired ?"),
        description=_(u"acquire the minimum role from the parent content"),
        required=False)
    minimum_role = schema.Choice(
        title=_(u"minimum role"),
        description=_(u"minimum required role needed to access this content"),
        source=authenticated_role_vocabulary,
        required=False)


class AccessPermissionForm(silvaforms.SMISubForm):
    """Form to manage default permission needed to see the current
    content.
    """
    grok.context(ISilvaObject)
    grok.order(100)
    grok.view(AccessTab)

    label = _(u"public view access restriction")
    description = _(u"Setting an access restriction here affects "
                    u"contents on this and lower levels.")
    ignoreRequest = True
    ignoreContent = False
    dataManager = silvaforms.makeAdaptiveDataManager(IAccessSecurity)
    fields = silvaforms.Fields(IAccessMinimumRole)
    fields['acquired'].mode = silvaforms.DISPLAY

    @silvaforms.action(
        _(u"acquire restriction"),
        description=_(u"set access restriction to acquire its "
                      u"settings from the parent"),
        available=lambda form: not form.getContent().is_acquired(),
        implements=IRemoverAction)
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

    @silvaforms.action(
        _(u"set restriction"),
        description=_(
            u"restrict access to this content to the selected role"))
    def restrict(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        role = data['minimum_role']
        access = self.getContent()
        if role:
            access.set_minimum_role(role)
            self.send_message(
                _(u'minimum required role to access this content '
                  u'set to "${role}"',
                  mapping=dict(role=role)),
                type=u"feedback")
        else:
            access.set_acquired()
            self.send_message(
                _(u"minimum required role to access this content acquired"),
                type=u"feedback")
        return silvaforms.SUCCESS
