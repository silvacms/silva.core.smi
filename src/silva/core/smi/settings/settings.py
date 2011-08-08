# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface
from zope import schema
from zope.traversing.browser import absoluteURL
from zeam.form import silva as silvaforms

from silva.core import interfaces
from silva.core.smi.content.metadata import MetadataFormGroup
from silva.core.smi.settings import SettingsMenu, Settings
from silva.translations import translate as _
from silva.ui.menu import MenuItem

import Acquisition
from Products.Silva import mangle


class AcquisitionMethod(Acquisition.Explicit):
    """This class let you have an acquisition context on a method.
    """
    # for Formulamerde.
    def __init__(self, parent, method_name):
        self.parent = parent
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        instance = self.parent.aq_inner
        method = getattr(instance, self.method_name)
        return method(*args, **kwargs)


class OtherSettings(silvaforms.SMIComposedForm):
    """Settings tab.
    """
    grok.adapts(Settings, interfaces.IContainer)
    grok.name('settings')
    grok.require('silva.ManageSilvaContent')
    label = _("Settings")

    def get_wanted_quota_validator(self):
        # for Formulamerde crap.
        return AcquisitionMethod(self.context, 'validate_wanted_quota')

    get_wanted_quota_validator__roles__ = None


class OtherSettingsMenu(MenuItem):
    grok.adapts(SettingsMenu, interfaces.IContainer)
    grok.order(10)
    grok.require('silva.ManageSilvaContent')
    name = _(u'Settings')
    screen = OtherSettings


class ConvertToFolderAction(silvaforms.Action):
    title = _('Convert to folder')
    description = _('Change container to a folder')
    accesskey = 'ctrl+f'

    def available(self, form):
        return interfaces.IGhostFolder.providedBy(form.context) or \
            interfaces.IPublication.providedBy(form.context)

    def __call__(self, form):
        form.context.to_folder()
        # XXX needed ?
        form.context.sec_update_last_author_info()
        form.send_message(_("Changed into folder"), type="feedback")
        return silvaforms.SUCCESS


class ConvertToPublicationAction(silvaforms.Action):
    title = _('Convert to publication')
    description = _('Change container to a publication')
    accesskey = 'ctrl+p'

    def available(self, form):
        return not interfaces.IPublication.providedBy(form.context)

    def __call__(self, form):
        form.context.to_publication()
        form.context.sec_update_last_author_info()
        form.send_message(_("Changed into publication"), type="feedback")
        return silvaforms.SUCCESS


class ConvertToForm(silvaforms.SMISubForm):
    grok.context(interfaces.IContainer)
    # XXX set it for real
    grok.require('silva.ManageSilvaContent')
    grok.view(OtherSettings)
    grok.order(10)
    actions = silvaforms.Actions(ConvertToPublicationAction(),
        ConvertToFolderAction())
    label = _('Container type')

    def available(self):
        if interfaces.IRoot.providedBy(self.context):
            return False
        return super(ConvertToForm, self).available()

    def update(self):
        if interfaces.IGhostFolder.providedBy(self.context):
            self.description = _('This Ghost Folder can be converted'
                ' to a normal Publication or Folder. All ghosted content'
                ' will be duplicated and can then be edited.')
        elif interfaces.IPublication.providedBy(self.context):
            self.description = _('This Silva Publication can be converted'
                                 ' to a Silva Folder')
        else:
            self.description = _('This Silva Folder can be converted'
                                 ' to a Publication')

class IActivateFeedsSchema(Interface):
    allow = schema.Bool(title=_('Allow feeds'),
        description=_('Check to provide an Atom / RSS '
                      'feed from this container.'))
    atom_url = schema.URI(title=_(u"Atom feed URL"), required=False)
    rss_url = schema.URI(title=_(u"RSS feed URL"), required=False)


def get_feeds_status(form):
    return bool(form.context.allow_feeds())

def get_feed_url(name):

    def get_url(form):
        return '/'.join((absoluteURL(form.context, form.request), name),)

    return get_url


class FeedsForm(silvaforms.SMISubForm):
    grok.context(interfaces.IContainer)
    grok.view(OtherSettings)
    grok.order(30)
    grok.require('silva.ManageSilvaContent')

    fields = silvaforms.Fields(IActivateFeedsSchema)
    fields['allow'].defaultValue = get_feeds_status
    fields['atom_url'].mode = silvaforms.DISPLAY
    fields['atom_url'].defaultValue = get_feed_url('atom.xml')
    fields['rss_url'].mode = silvaforms.DISPLAY
    fields['rss_url'].defaultValue = get_feed_url('rss.xml')

    ignoreContent = True
    ignoreRequest = False

    label = _('Atom/rss feeds')

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


class IQuotaSchema(Interface):
    size = schema.TextLine(title=_('Space used in this folder'))


def get_used_space(form):
    return mangle.Bytes(form.context.used_space)


class QuotaForm(silvaforms.SMISubForm):
    grok.context(interfaces.IContainer)
    grok.view(OtherSettings)
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
    grok.context(interfaces.IContainer)
    grok.order(50)
    grok.view(OtherSettings)
    category = 'settings'
    label = _('Generic Settings')


