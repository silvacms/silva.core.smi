# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface
from zope import schema
from zeam.form import silva as silvaforms
from silva.ui.menu import SettingsMenuItem
from silva.core import interfaces
from silva.core.smi.properties.metadata import MetadataFormGroup
from silva.translations import translate as _

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


class SettingsMenu(SettingsMenuItem):
    grok.context(interfaces.ISilvaObject)
    grok.order(10)
    name = _(u'Settings')
    screen = 'settings'


class TabSettings(silvaforms.SMIComposedForm):
    """Settings tab.
    """
    grok.context(interfaces.ISilvaObject)
    grok.name('silva.ui.settings')
    grok.require('silva.ManageSilvaContent')
    label = _("settings")

    def get_wanted_quota_validator(self):
        # for Formulamerde crap.
        return AcquisitionMethod(self.context, 'validate_wanted_quota')

    get_wanted_quota_validator__roles__ = None


class ConvertToFolderAction(silvaforms.Action):
    title = _('convert to folder')
    accesskey = 'f'
    description = _('change container type to a folder: alt-f')

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
    title = _('convert to publication')
    accesskey = 'p'
    description = _('change container type to a publication: alt-p')

    def available(self, form):
        interfaces.IPublication.providedBy('')
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
    grok.view(TabSettings)
    grok.order(10)
    actions = silvaforms.Actions(ConvertToPublicationAction(),
        ConvertToFolderAction())
    label = _('container type')

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
    feeds = schema.Bool(title=_('allow feeds'),
        description=_('Check to provide an Atom / RSS '
                      'feed from this container.'))


def get_feeds_status(form):
    return bool(form.context.allow_feeds())

# XXX : this should display url to feeds somewhere. but there is no
# possibility to put some html in there except overriding template.
class ActivateFeedsForm(silvaforms.SMISubForm):
    grok.context(interfaces.IContainer)
    grok.view(TabSettings)
    grok.order(30)
    grok.require('silva.ManageSilvaContent')

    fields = silvaforms.Fields(IActivateFeedsSchema)
    fields['feeds'].defaultValue = get_feeds_status

    ignoreContent = True
    ignoreRequest = False

    label = _('atom/rss feeds')

    @silvaforms.action(_('change feed settings'),
        identifier='activatefeeds',
        description=_('change feed settings: alt-f'),
        accesskey='f')
    def activate_feeds(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        self.context.set_allow_feeds(data.getWithDefault('feeds'))
        self.send_message(_('Feed settings saved.'), type='feedback')
        return silvaforms.SUCCESS


class IQuotaSchema(Interface):
    size = schema.TextLine(title=_('space used in this folder'))


def get_used_space(form):
    return mangle.Bytes(form.context.used_space)


class QuotaForm(silvaforms.SMISubForm):
    grok.context(interfaces.IContainer)
    grok.view(TabSettings)
    grok.order(40)
    grok.require('silva.ManageSilvaContentSettings')

    fields = silvaforms.Fields(IQuotaSchema)
    fields['size'].defaultValue = get_used_space
    fields['size'].mode = silvaforms.DISPLAY

    # read-only
    ignoreContent = True
    ignoreRequest = True

    label = _('used space')

    def available(self):
        return bool(
            self.context.service_extensions.get_quota_subsystem_status())

    def update(self):
        if self.available():
            self.description = \
                _('The quota for this area is set to ${quota} MB.',
                mapping={'quota': self.context.get_current_quota()})


class LayoutMetadataForm(MetadataFormGroup):
    grok.context(interfaces.ISilvaObject)
    grok.order(50)
    grok.view(TabSettings)
    category = 'layout'
    title = _('layout settings of')


class SettingsMetadataForm(MetadataFormGroup):
    grok.context(interfaces.ISilvaObject)
    grok.order(50)
    grok.view(TabSettings)
    category = 'settings'
    title = _('settings of')


