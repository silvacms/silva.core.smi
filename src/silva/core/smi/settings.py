from five import grok

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope import component
from zope.interface import Interface
from zope import schema


from zeam.form import silva as silvaforms
from silva.core import interfaces as silvainterfaces
from silva.core.smi import interfaces
from silva.translations import translate as _
from Products.Silva.transform.interfaces import IRendererRegistry
from Products.Silva import mangle


class TabSettings(silvaforms.SMIComposedForm):
    """Settings tab.
    """
    grok.context(silvainterfaces.ISilvaObject)
    grok.name('tab_settings')
    grok.implements(interfaces.IPropertiesTab)
    tab = 'settings'
    label = _("settings")
    description = _("")


class ConvertToFolderAction(silvaforms.Action):
    title = _('convert to folder')
    accesskey = 'f'
    description = _('change container type to a folder: alt-f')

    def available(self, form):
        return silvainterfaces.IGhostFolder.providedBy(form.context) or \
            silvainterfaces.IPublication.providedBy(form.context)

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
        silvainterfaces.IPublication.providedBy('')
        return not silvainterfaces.IPublication.providedBy(form.context)

    def __call__(self, form):
        form.context.to_publication()
        form.context.sec_update_last_author_info()
        form.send_message(_("Changed into publication"), type="feedback")
        return silvaforms.SUCCESS


class ConvertToForm(silvaforms.SMISubForm):
    grok.context(silvainterfaces.IContainer)
    # XXX set it for real
    grok.require('silva.ChangeSilvaContent')
    grok.view(TabSettings)
    grok.order(10)
    actions = silvaforms.Actions(ConvertToPublicationAction(),
        ConvertToFolderAction())
    label = _('container type')

    def update(self):
        if silvainterfaces.IGhostFolder.providedBy(self.context):
            self.description = _('This Ghost Folder can be converted'
                ' to a normal Publication or Folder. All ghosted content'
                ' will be duplicated and can then be edited.')
        elif silvainterfaces.IPublication.providedBy(self.context):
            self.description = _('This Silva Publication can be converted'
                                 ' to a Silva Folder')
        else:
            self.description = _('This Silva Folder can be converted'
                                 ' to a Publication')


@grok.provider(IContextSourceBinder)
def renderers(context):
    registry = component.queryUtility(IRendererRegistry) or \
        context.service_renderer_registry
    renderers = []
    for name in registry.getFormRenderersList(context.meta_type):
        renderers.append(SimpleTerm(title=name, value=name, token=name))
    return SimpleVocabulary(renderers)

RENDERER_DEFAULT = '(Default)'

def selected_renderer(form):
    editable = form.context.get_editable()
    if editable:
        return editable.get_renderer_name() or RENDERER_DEFAULT
    return RENDERER_DEFAULT


class IRendererShema(Interface):
    renderer = schema.Choice(source=renderers,
        title=_('renderer'),
        description=_('Select a renderer to render this content.'))


class RendererForm(silvaforms.SMISubForm):
    grok.context(silvainterfaces.ISilvaObject)
    grok.view(TabSettings)
    grok.order(20)
    fields = silvaforms.Fields(IRendererShema)
    fields['renderer'].defaultValue = selected_renderer
    ignoreContent = True
    ignoreRequest = False

    def available(self):
        return bool(self.context.get_editable())

    @silvaforms.action(_('change renderer'),
        identifier='renderer',
        description=_('change renderer: alt-c'),
        accesskey='c')
    def change_renderer(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        editable = self.context.get_editable()
        editable.set_renderer_name(data.getWithDefault('renderer'))
        self.send_message(_('Renderer setting saved.'), type='feedback')
        return silvaforms.SUCCESS


class IActivateFeedsSchema(Interface):
    feeds = schema.Bool(title=_('allow feeds'),
        description=_('Check to provide an Atom / RSS '
                      'feed from this container.'))


def get_feeds_status(form):
    return bool(form.context.allow_feeds())

# XXX : this should display url to feeds somewhere. but there is no
# possibility to put some html in there except overriding template.
class ActivateFeedsForm(silvaforms.SMISubForm):
    grok.context(silvainterfaces.IContainer)
    grok.view(TabSettings)
    grok.order(30)

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
    grok.context(silvainterfaces.IContainer)
    grok.view(TabSettings)
    grok.order(40)

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


class MetadataForm(silvaforms.SMISubForm):
    grok.context(silvainterfaces.ISilvaObject)
    grok.order(50)

    def available(self):
        pass



