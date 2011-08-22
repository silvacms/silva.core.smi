# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager
from AccessControl.User import nobody

from five import grok
from silva.core.interfaces import ISilvaObject
from silva.core.interfaces.adapters import ILanguageProvider
from silva.core.interfaces.auth import IEditableMember
from silva.core.services.interfaces import IMemberService
from silva.translations import translate as _
from z3c.schema.email import RFC822MailAddress
from zeam.form import silva as silvaforms
from zope import schema, interface
from zope.component import getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zExceptions import Unauthorized


from silva.pas.base.interfaces import IFormFieldFactory

@grok.provider(IContextSourceBinder)
def language_source(context):
    langs = [
        SimpleTerm(
            value=None,
            token='none',
            title=_(u'Use browser language setting'))]
    languages = ILanguageProvider(context.REQUEST)
    codes = languages.getAvailableLanguages()
    # If the current language is not in the available list, we
    # still add it in order to prevent vocabularies to fail
    preferred = languages.getPreferredLanguage()
    if preferred not in codes:
        codes.append(preferred)
    codes.sort()
    for lang in codes:
        langs.append(SimpleTerm(
                value=lang, token=lang, title=languages.getLanguageName(lang)))
    return SimpleVocabulary(langs)


class IUserInfo(interface.Interface):
    userid = schema.TextLine(
        title=_(u"user identifier"),
        description=_(
            u"identifier used to authenticate"),
        required=False)
    fullname = schema.TextLine(
        title=_(u"fullname"),
        description=_(u"user full name"),
        required=True)
    email = RFC822MailAddress(
        title=_(u"email address"),
        description=_(u"contact email address"),
        required=True)
    language = schema.Choice(
        title=_(u"preferred language"),
        description=_(u"language to use the for Silva interface"),
        source=language_source,
        required=False)
    avatar = RFC822MailAddress(
        title=_('gravatar email address'),
        description=_(u"create your globally recognized avatar at gravatar.com"),
        required=False)


class UserDataManager(silvaforms.ObjectDataManager):

    def __init__(self, content, request):
        super(UserDataManager, self).__init__(content)
        self.language = ILanguageProvider(request)

    def get(self, key):
        if key in ('userid', 'email', 'fullname', 'avatar'):
            return getattr(self.content, key)()
        if key == 'language':
            return self.language.getPreferredLanguage()
        raise KeyError(key)

    def set(self, key, value):
        if key in ('email', 'fullname', 'avatar'):
            return getattr(self.content, 'set_' + key)(value)
        if key == 'language':
            return self.language.setPreferredLanguage(value)

class SimpleUserInfoFieldsFactory(grok.Adapter):
    """Factory for returning the silvaforms.Fields schema for standard
       silva Simple Members (this is the default schema)"""
    grok.implements(IFormFieldFactory)
    grok.context(IEditableMember)
    
    def get_fields(self):
        fields = silvaforms.Fields(IUserInfo)
        fields['userid'].mode = silvaforms.DISPLAY
        return fields

class UserInfo(silvaforms.RESTPopupForm):
    grok.context(ISilvaObject)
    grok.name('userinfo')

    label = _(u"user settings")
    ignoreContent = False
    actions = silvaforms.Actions(
        silvaforms.EditAction(),
        silvaforms.CancelAction())
    
    def get_fields_for_member(self, member):
        """different members may have different schema, or different
           requirements on schema fields (i.e. some may be readonly), 
           so defer to a silvaformfield factory for this"""
        return I
    
    def processForm(self):
        """bah!  RestPopupForms DO NOT have an update() method like other
           zeam form types do.  processForm is called before anything else,
           so override it here to do some field cleanup and such"""
        service = getUtility(IMemberService)
        user = getSecurityManager().getUser()
        if user == nobody:
            raise Unauthorized()
        self.member = service.get_member(user.getId())
        #different member types may have a different schema
        self.fields = IFormFieldFactory(self.member).get_fields()
        return super(UserInfo, self).processForm()

    def getContentData(self):
        return UserDataManager(self.member, self.request)
