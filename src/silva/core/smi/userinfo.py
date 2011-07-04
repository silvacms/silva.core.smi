# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager

from five import grok
from silva.core.interfaces import ISilvaObject, IEditableMember
from silva.core.interfaces.adapters import ILanguageProvider
from silva.core.services.interfaces import IMemberService
from silva.translations import translate as _
from z3c.schema.email import RFC822MailAddress
from zeam.form import silva as silvaforms
from zope import schema, interface
from zope.component import getUtility
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


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
        title=_(u"User identifier"),
        description=_(
            u"identifier used to authenticate"),
        required=False)
    fullname = schema.TextLine(
        title=_(u"Fullname"),
        description=_(u"user full name"),
        required=True)
    email = RFC822MailAddress(
        title=_(u"Email address"),
        description=_(u"contact email address"),
        required=True)
    language = schema.Choice(
        title=_(u"Preferred language"),
        description=_(u"language to use the for Silva interface"),
        source=language_source,
        required=False)


class UserDataManager(silvaforms.ObjectDataManager):

    def __init__(self, content, request):
        super(UserDataManager, self).__init__(content)
        self.language = ILanguageProvider(request)

    def get(self, key):
        if key in ('userid', 'email', 'fullname'):
            return getattr(self.content, key)()
        if key == 'language':
            return self.language.getPreferredLanguage()
        raise KeyError(key)

    def set(self, key, value):
        if key in ('email', 'fullname'):
            if IEditableMember.providedBy(self.content):
                return getattr(self.content, 'set_' + key)(value)
        if key == 'language':
            return self.language.setPreferredLanguage(value)


class UserInfo(silvaforms.RESTPopupForm):
    grok.context(ISilvaObject)
    grok.name('silva.core.smi.userpreferences')

    label = _(u"User preferences")
    fields = silvaforms.Fields(IUserInfo)
    fields['userid'].mode = silvaforms.DISPLAY
    ignoreContent = False
    actions = silvaforms.Actions(
        silvaforms.CancelAction(),
        silvaforms.EditAction())

    def update(self):
        service = getUtility(IMemberService)
        member = service.get_member(getSecurityManager().getUser().getId())
        if not IEditableMember.providedBy(member):
            self.fields['fullname'].mode = silvaforms.DISPLAY
            self.fields['email'].mode = silvaforms.DISPLAY
        self.user = UserDataManager(member, self.request)

    def getContentData(self):
        return self.user
