# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core.interfaces import IContainer, IRoot, IAddableContents
from silva.translations import translate as _
from silva.ui.menu import MenuItem
from silva.core.smi.settings import SettingsMenu, Settings
from zeam.form import silva as silvaforms
from zope import schema
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


@grok.provider(IContextSourceBinder)
def addables_content_types(context):
    addables = IAddableContents(context).get_all_addables()
    entries = []
    for addable in addables:
        entries.append(SimpleTerm(value=addable,
                                  token=addable,
                                  title=addable))
    return SimpleVocabulary(entries)

def default_content_types(form):
    return IAddableContents(form.context).get_container_addables()

def acquire_addables(form):
    return form.context.is_silva_addables_acquired()


class IAddablesSchema(Interface):
    acquire = schema.Bool(
        title=_(u"acquire"),
        description=_(u"If checked, inherit the addables from above. "
                      u"Uncheck this to change the allowed addables below."),
        required=False,
        default=True)
    addables = schema.Set(
        title=_(u"addables"),
        description=_(u"If 'acquire' is not checked, these settings will "
                      u"determine the items allowed in this publication. "
                      u"Otherwise the addables are acquired from the "
                      u"publication above."),
        required=False,
        value_type=schema.Choice(source=addables_content_types))


class AddablesForm(silvaforms.SMIForm):
    """Control addables for silva containers.
    """
    grok.adapts(Settings, IContainer)
    grok.name('addables')
    grok.require('silva.ManageSilvaContentSettings')

    label = _(u"Addable settings")
    fields = silvaforms.Fields(IAddablesSchema)
    fields['acquire'].defaultValue = acquire_addables
    fields['addables'].defaultValue = default_content_types
    actions = silvaforms.Actions(silvaforms.CancelAction())
    ignoreContent=True
    ignoreRequest=True

    def update(self):
        if IRoot.providedBy(self.context):
            self.fields['acquire'].mode = silvaforms.DISPLAY
        else:
            self.fields['acquire'].mode = silvaforms.INPUT

    @silvaforms.action(
        _(u'Save addables settings'),
        description=_(u'save addable settings for this publication'),
        implements=silvaforms.IDefaultAction,
        accesskey='ctrl+s')
    def save_changes(self):
        data, errors = self.extractData()
        currently_acquired = self.context.is_silva_addables_acquired()
        will_be_acquired = data.getWithDefault('acquire')
        if will_be_acquired and currently_acquired:
            self.send_message(
                _(u"Addable settings have not changed and remain acquired."),
                type=u"error")
            return silvaforms.FAILURE

        if will_be_acquired:
            self.send_message(
                _(u"Addable settings are now aquired."), type=u"feedback")
            self.context.set_silva_addables_allowed_in_container(None)
        else:
            self.send_message(
                _(u"Changes to addables content types saved."),
                type=u"feedback")
            self.context.set_silva_addables_allowed_in_container(
                data.getWithDefault('addables'))

        return silvaforms.SUCCESS


class AddablesMenu(MenuItem):
    grok.adapts(SettingsMenu, IContainer)
    grok.order(50)
    grok.require('silva.ManageSilvaContentSettings')
    name = _(u'Addables')
    screen = AddablesForm

