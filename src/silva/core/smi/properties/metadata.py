from five import grok

from silva.core.interfaces import ISilvaObject, IVersionedContent
from silva.core.views import views as silvaviews
from silva.core.smi import smi
from silva.core.smi import interfaces

grok.layer(interfaces.ISMILayer)


class PropertiesTab(smi.SMIPage):
    """ Properties tab allows metadata editing.
    """
    grok.context(ISilvaObject)
    grok.name('tab_metadata')
    grok.implements(interfaces.IPropertiesTab, interfaces.ISMITabIndex)
    tab = 'properties'

    def update(self):
        pass


class MetadataViewletManager(silvaviews.ViewletManager):
    """Viewlet manager to hold Metadata viewlets
    """
    grok.context(ISilvaObject)
    grok.name('metadatainfo')

    def filter(self, viewlets):
        results = []
        for name, viewlet in \
                super(MetadataViewletManager, self).filter(viewlets):
            if not viewlet.available():
                continue
            results.append((name, viewlet,))
        return results


class MetadataViewlet(silvaviews.Viewlet):
    grok.baseclass()
    grok.viewletmanager(MetadataViewletManager)

    def available(self):
        return False


class MetadataEditViewlet(MetadataViewlet):
    grok.baseclass()
    grok.template('metadataeditviewlet')


class MetadataReadOnlyViewlet(MetadataViewlet):
    grok.baseclass()
    grok.template('metadatareadonlyviewlet')


class EditableMetadataViewlet(MetadataEditViewlet):
    """Metadata of the editable version.
    """
    grok.context(IVersionedContent)

    def update(self):
        self.content = self.context.get_editable()

    def available(self):
        self.context.get_unapproved_version()


class PreviewableMetadataViewlet(MetadataEditViewlet):
    """metadata of previewable version.
    """
    grok.context(IVersionedContent)

    def update(self):
        self.content = self.context.get_previewable()

    def available(self):
        return self.context.get_unapproved_version()


class ViewableMetadataViewlet(MetadataReadOnlyViewlet):
    """metadata of the viewable version
    """
    grok.context(IVersionedContent)

    def update(self):
        self.content = self.context.get_viewable()

    def available(self):
        return self.context.get_public_version()


class LastClosedMetadataViewlet(MetadataEditViewlet):
    """Metadata of the last closed version
    """
    grok.context(IVersionedContent)

    def update(self):
        self.content = self.context.get_last_closed()

    def available(self):
        return not self.context.get_next_version() and \
            not self.context.get_public_version()


class NonVersionedContentMetadataViewlet(MetadataEditViewlet):
    """Metadata for non versioned content
    """
    grok.context(ISilvaObject)

    def update(self):
        self.content = self.context

    def available(self):
        return not IVersionedContent.providedBy(self.context)


