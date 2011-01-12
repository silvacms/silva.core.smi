from five import grok

from zope.interface import Interface
from zope import schema
from silva.core.interfaces import IContainer, IRoot
from silva.core.smi.interfaces import IPropertiesTab
from zeam.form import silva as silvaforms
from silva.translations import translate as _


from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

@grok.provider(IContextSourceBinder)
def addables_content_types(context):
    addables = context.get_silva_addables_all()
    entries = []
    for addable in addables:
        entries.append(SimpleTerm(value=addable,
                                  token=addable,
                                  title=addable))
    return SimpleVocabulary(entries)

def default_content_types(form):
    return form.context.get_silva_addables_allowed_in_container()

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


class AddablesTab(silvaforms.SMIForm):
    """Control addables for silva containers.
    """
    grok.context(IContainer)
    grok.implements(IPropertiesTab)
    grok.name('tab_addables')
    grok.require('silva.ManageSilvaContentSettings')

    tab = 'properties'
    label = _(u"addable settings")
    fields = silvaforms.Fields(IAddablesSchema)
    fields['acquire'].defaultValue = acquire_addables
    fields['addables'].defaultValue = default_content_types
    ignoreContent=True
    ignoreRequest=False

    def update(self):
        if IRoot.providedBy(self.context):
            self.fields['acquire'].mode = silvaforms.DISPLAY
        else:
            self.fields['acquire'].mode = silvaforms.INPUT

    @silvaforms.action(_(u'save addables settings'),
        description=_(u'save addable settings for this publication: alt-a'),
        accesskey=u'a')
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

