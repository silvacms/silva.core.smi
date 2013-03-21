# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl.security import checkPermission

from five import grok
from zope.interface import Interface
from zope import schema
from zope.traversing.browser import absoluteURL
from zope.cachedescriptors.property import Lazy

from silva.core.interfaces import IContainer, IPublication, IRoot
from silva.core.interfaces import ISilvaObject, IGhostFolder
from silva.core.interfaces.adapters import ISiteManager
from silva.core.smi.content.metadata import MetadataFormGroup
from silva.core.smi.settings import Settings
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction

from Products.Silva import mangle


class ConvertToFolderAction(silvaforms.Action):
    title = _('Convert to folder')
    description = _('Change container to a folder')
    accesskey = 'ctrl+f'

    def available(self, form):
        return (IGhostFolder.providedBy(form.context) or
                (IPublication.providedBy(form.context) and
                 not form.manager.is_site()))

    def __call__(self, form):
        form.context.to_folder()
        form.send_message(_("Changed into folder."), type="feedback")
        return silvaforms.SUCCESS


class ConvertToPublicationAction(silvaforms.Action):
    title = _('Convert to publication')
    description = _('Change container to a publication')
    accesskey = 'ctrl+p'

    def available(self, form):
        return not IPublication.providedBy(form.context)

    def __call__(self, form):
        form.context.to_publication()
        form.send_message(_("Changed into publication."), type="feedback")
        return silvaforms.SUCCESS


class MakeLocalSiteAction(silvaforms.Action):
    title = _("Make local site")

    def available(self, form):
        return (IPublication.providedBy(form.context) and
                not form.manager.is_site())

    def __call__(self, form):
        try:
            form.manager.make_site()
        except ValueError as error:
            form.send_message(str(error), type=u"error")
            return silvaforms.FAILURE
        else:
            form.send_message(_("Local site activated."), type=u"feedback")
            return silvaforms.SUCCESS


class RemoveLocalSiteAction(silvaforms.Action):
    grok.implements(IRemoverAction)
    title = _("Remove local site")

    def available(self, form):
        return (IPublication.providedBy(form.context) and
                form.manager.is_site())

    def __call__(self, form):
        try:
            form.manager.delete_site()
        except ValueError as error:
            form.send_message(str(error), type=u"error")
            return silvaforms.FAILURE
        else:
            form.send_message(_("Local site deactivated."), type=u"feedback")
            return silvaforms.SUCCESS


class ConvertToForm(silvaforms.SMISubForm):
    grok.context(IContainer)
    grok.require('silva.ManageSilvaContent')
    grok.view(Settings)
    grok.order(10)
    actions = silvaforms.Actions(
        ConvertToPublicationAction(),
        ConvertToFolderAction(),
        MakeLocalSiteAction(),
        RemoveLocalSiteAction())
    label = _('Container type')

    def available(self):
        if IRoot.providedBy(self.context):
            return False
        if not checkPermission('silva.ManageSilvaContent', self.context):
            return False
        return super(ConvertToForm, self).available()

    @Lazy
    def manager(self):
        return ISiteManager(self.context)

    @Lazy
    def description(self):
        if IGhostFolder.providedBy(self.context):
            return _(u'This Ghost Folder can be converted '
                     u'to a normal Publication or Folder. All ghosted content '
                     u'will be duplicated and can then be edited.')
        elif IPublication.providedBy(self.context):
            if self.manager.is_site():
                return _(u"This Silva Publication is a local site. You need to "
                         u"remove any local service, and the local site before "
                         u"you can convert it to a Silva Folder.")
            return _(u'This Silva Publication can be converted '
                     u'to a Silva Folder, or can become a local site.')
        return _(u'This Silva Folder can be converted '
                 u'to a Publication.')


class IActivateFeedsSchema(Interface):
    allow = schema.Bool(
        title=_('Allow feeds'),
        description=_('Check to provide an Atom / RSS '
                      'feed from this container.'))


class FeedsForm(silvaforms.SMISubForm):
    grok.context(IContainer)
    grok.view(Settings)
    grok.order(30)
    grok.require('silva.ManageSilvaContent')

    fields = silvaforms.Fields(IActivateFeedsSchema)
    fields['allow'].defaultValue = lambda f: bool(f.context.allow_feeds())

    ignoreContent = True
    ignoreRequest = False

    label = _('Atom/rss feeds')

    def available(self):
        if not checkPermission('silva.ManageSilvaContent', self.context):
            return False
        return super(FeedsForm, self).available()

    @silvaforms.action(_('Change feed settings'),
        identifier='activatefeeds',
        description=_('change feed settings'))
    def activate_feeds(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        self.context.set_allow_feeds(data.getWithDefault('allow'))
        self.send_message(_('Feed settings saved.'), type='feedback')
        return silvaforms.SUCCESS


class FeedsInformation(silvaviews.Viewlet):
    grok.context(IContainer)
    grok.order(10)
    grok.view(Settings)
    grok.viewletmanager(silvaforms.SMIFormPortlets)

    def update(self):
        self.activated = self.context.allow_feeds()
        self.url = absoluteURL(self.context, self.request)



class IQuotaSchema(Interface):
    size = schema.TextLine(title=_('Space used in this folder'))


def get_used_space(form):
    return mangle.Bytes(form.context.used_space)


class QuotaForm(silvaforms.SMISubForm):
    grok.context(IContainer)
    grok.view(Settings)
    grok.order(40)
    grok.require('silva.ManageSilvaContentSettings')

    fields = silvaforms.Fields(IQuotaSchema)
    fields['size'].defaultValue = get_used_space
    fields['size'].mode = silvaforms.DISPLAY

    # read-only
    ignoreContent = True
    ignoreRequest = True

    label = _('Used space')

    def available(self):
        return bool(
            self.context.service_extensions.get_quota_subsystem_status())

    def update(self):
        if self.available():
            self.description = \
                _('The quota for this area is set to ${quota} MB.',
                mapping={'quota': self.context.get_current_quota()})


class SettingsMetadataForm(MetadataFormGroup):
    grok.context(ISilvaObject)
    grok.order(50)
    grok.view(Settings)
    category = 'settings'
    label = _('Generic Settings')


