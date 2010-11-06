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
from silva.core.interfaces import IAccessSecurity, IAuthorizationManager
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

    label = _(u"manage access to content")
    description = _(u"This screen lets you authorize or revoke access "
                    u"to this item and all content it contains.")


class LookupUserPopupAction(silvaforms.PopupAction):
    title = _(u"lookup users...")
    description = _(u"search for users to assign them roles: alt-l")
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

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.send_message(
                _(u"Sorry, there were errors."),
                type="error")
            return silvaforms.FAILURE
        username = data['user'].strip()
        if len(username) < 2:
            form.send_message(
                _(u"The search input is too short. "
                  u"Please enter two or more characters."),
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
                _(u"Found ${count} users: ${users}.",
                  mapping={'count': len(new_users),
                           'users': u', '.join(new_users)}),
                type="feedback")
        else:
            form.send_message(
                _(u"No matching users were found."),
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
    description = _(u"Search for users to assign them roles. Enter as least "
                    u"two characters. Looukup entire "
                    u"names to limit the number of results.")
    fields = silvaforms.Fields(ILookupUserSchema)
    actions = silvaforms.Actions(
        LookupUserAction(),
        silvaforms.CancelAction())


class UserRole(silvaforms.SMISubFormGroup):
    grok.context(ISilvaObject)
    grok.order(20)
    grok.view(AccessTab)

    #label = _(u'manage users roles')
    #description = _(u"Find, add and remove roles for users.")


class IGrantRoleSchema(interface.Interface):
    """A role for a user.
    """
    role = schema.Choice(
        title=_(u"role to grant:"),
        source=role_vocabulary,
        required=True)


class GrantAccessAction(silvaforms.Action):

    title = _(u"grant role")
    description = _(u"grant the selected role to selected users(s)")

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
                   'username': authorization.identifier}
        try:
            if authorization.grant(role):
                form.send_message(
                    _('Role "${role}" granted to user "${username}".',
                      mapping=mapping),
                    type="feedback")
            else:
                form.send_message(
                    _('User "${username}" already has the role "${role}".',
                      mapping=mapping),
                    type="error")
        except UnauthorizedRoleAssignement:
            form.send_message(
                _(u'Sorry, you are not allowed to remove the role "${role}" '
                  u'from user "${userid}".',
                  mapping=mapping),
                type="error")
        return silvaforms.SUCCESS


class RevokeAccessAction(silvaforms.Action):
    grok.implements(IRemoverAction)

    title = _(u"revoke role")
    description=_(u"revoke the role of selected user(s)")

    def available(self, form):
        return reduce(
            operator.or_,
            [False] + map(lambda l: l.getContent().local_role is not None,
                          form.lines))

    def __call__(self, form, authorization, line):
        try:
            role = authorization.local_role
            username = authorization.identifier
            if authorization.revoke():
                form.send_message(
                    _(u'Removed role "${role}" from user "${username}".',
                      mapping={'role': role,
                               'username': username}),
                    type="feedback")
            else:
                form.send_message(
                    _(u'User "${username}" doesn\'t have any local role.',
                      mapping={'username': username}),
                    type="error")
        except UnauthorizedRoleAssignement, error:
            form.send_message(
                _(u'Sorry, you are not allowed to remove the role "${role}" '
                  u'from user "${userid}".',
                  mapping={'role': error.args[0],
                           'userid': error.args[1]}),
                type="error")
        return silvaforms.SUCCESS


class IUserAuthorization(interface.Interface):

    identifier = schema.TextLine(
        title=_(u"username"))
    acquired_role = schema.Choice(
        title=_(u"role defined above"),
        source=role_vocabulary,
        required=False)
    local_role = schema.Choice(
        title=_(u"role defined here"),
        source=role_vocabulary,
        required=False)


class UserAccessForm(silvaforms.SMISubTableForm):
    """Form to give/revoke access to users.
    """
    grok.context(ISilvaObject)
    grok.order(20)
    grok.view(UserRole)

    label = _(u"user roles")
    emptyDescription = _(u'No roles have been assigned.')
    ignoreContent = False
    ignoreRequest = True
    mode = silvaforms.DISPLAY
    fields = silvaforms.Fields(IGrantRoleSchema)
    fields['role'].mode = silvaforms.INPUT
    fields['role'].ignoreRequest = False
    fields['role'].ignoreContent = True
    fields['role'].available = lambda form: len(form.lines) != 0
    tableFields = silvaforms.Fields(IUserAuthorization)
    tableFields['identifier'].mode = 'silva.icon'
    tableActions = silvaforms.TableActions(
        RevokeAccessAction(),
        GrantAccessAction())

    def getItems(self):
        access = IAuthorizationManager(self.context)
        authorizations = access.get_defined_authorizations().items()
        authorizations.sort(key=operator.itemgetter(0))
        return filter(lambda auth: auth.type == 'user',
                      map(operator.itemgetter(1), authorizations))


class LookupUserResultForm(UserAccessForm):
    """Form to give/revoke access to users.
    """
    grok.order(10)

    label = _(u"user clipboard")
    emptyDescription = _(u'In order to assign roles to users, first lookup '
                         u'users so they\'re listed on this user clipboard. '
                         u'Then assign the users roles. Any users on the '
                         u'clipboard will remain here when you move to other '
                         u'areas of the site.')
    actions = silvaforms.Actions(LookupUserPopupAction())
    tableActions = silvaforms.TableActions(GrantAccessAction())

    @CachedProperty
    def store(self):
        return SessionStore(self.request)

    def getItems(self):
        user_ids = self.store.get(USER_STORE_KEY, set())
        if user_ids:
            access = IAuthorizationManager(self.context)
            authorizations = access.get_authorizations(user_ids).items()
            authorizations.sort(key=operator.itemgetter(0))
            return filter(lambda auth: auth.type == 'user',
                          map(operator.itemgetter(1), authorizations))
        return []

    @silvaforms.action(
        _(u"clear clipboard"),
        description=_(u"clear the user clipboard"),
        available=lambda form: len(form.lines) != 0,
        implements=IRemoverAction)
    def clear(self):
        self.store.set(USER_STORE_KEY, set())



class IAccessMinimumRoleSchema(interface.Interface):
    """A role for a user.
    """
    acquired = schema.Bool(
        title=_(u"is the role acquired from above?"),
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
                    u"content on this and lower levels.")
    ignoreRequest = True
    ignoreContent = False
    dataManager = silvaforms.makeAdaptiveDataManager(IAccessSecurity)
    fields = silvaforms.Fields(IAccessMinimumRoleSchema)
    fields['acquired'].mode = silvaforms.DISPLAY

    @silvaforms.action(
        _(u"acquire restriction"),
        description=_(u"set the access restriction to acquire its "
                      u"setting from the parent container."),
        available=lambda form: not form.getContent().is_acquired(),
        implements=IRemoverAction)
    def acquire(self):
        access = self.getContentData().getContent()
        if access.is_acquired():
            self.send_message(
                _(u"The minimum role setting was already acquired."),
                type="error")
        else:
            access.set_acquired()
            self.send_message(
                _(u"Now acquiring the minimum role setting."),
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
                _(u'The minimum required role to access this content '
                  u'has been set to "${role}".',
                  mapping=dict(role=role)),
                type=u"feedback")
        else:
            access.set_acquired()
            self.send_message(
                _(u"The minimum required role to access this"
                  "content is acquired."),
                type=u"feedback")
        return silvaforms.SUCCESS
