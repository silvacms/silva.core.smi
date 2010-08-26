# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager

from five import grok
from silva.core.interfaces import ISilvaObject
from silva.core.services.interfaces import IMemberService
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zope import schema, interface
from zope.component import getUtility
from silva.core.interfaces.adapters import ILanguageProvider
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder


@grok.provider(IContextSourceBinder)
def language_source(context):
    langs = [
        SimpleTerm(
            value=None,
            token='none',
            title=_(u'Use browser language setting'))]
    language = ILanguageProvider(context.REQUEST)
    for lang in language.getAvailableLanguages():
        langs.append(SimpleTerm(
                value=lang, token=lang, title=language.getLanguageName(lang)))
    return SimpleVocabulary(langs)


class IUserInfo(interface.Interface):
    userid = schema.TextLine(
        title=_(u"user identifier"),
        description=_(
            u"Identifier used to authenticate. Cannot be modified."),
        readonly=True,
        required=False)
    fullname = schema.TextLine(
        title=_(u"fullname"),
        description=_(u"Fullname of the user"),
        required=True)
    email = schema.TextLine(
        title=_(u"email address"),
        description=_(u"Contact email address"),
        required=True)
    language = schema.Choice(
        title=_(u"preferred language"),
        description=_(u"Silva interface language"),
        source=language_source,
        required=True)


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
            return getattr(self.content, 'set_' + key)(value)
        if key == 'language':
            return self.language.setPreferredLanguage(value)


class UserInfo(silvaforms.RESTForm):
    grok.context(ISilvaObject)
    grok.name('userinfo')

    label = _(u"User information")
    fields = silvaforms.Fields(IUserInfo)
    ignoreContent = False
    actions = silvaforms.Actions(silvaforms.EditAction())

    def getContentData(self):
        service = getUtility(IMemberService)
        member = service.get_member(getSecurityManager().getUser().getId())
        return UserDataManager(member, self.request)
