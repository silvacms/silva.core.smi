# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import Interface
from zope.cachedescriptors.property import CachedProperty
from zope.i18n import translate

from silva.core.smi import interfaces
from silva.core.views import views as silvaviews


class SMILayout(silvaviews.Layout):
    """ Layout for SMI.
    """
    grok.context(Interface)
    grok.layer(interfaces.ISMILayer)


class SMITab(silvaviews.SMIView):
    """A SMI Tab.
    """

    grok.baseclass()


# For the moment tabs are not registered. Dummy tabs are used instead
# to register components to, they will become the real tab when we
# will switch from Silva views to that system completly.

class AccessTab(SMITab):
    """Access
    """

    grok.implements(interfaces.IAccessTab)
    grok.name('tab_access')
    grok.baseclass()


class DummyAccessTab(AccessTab):

    grok.template('smitab')
    grok.name('tab_access_extra')
    tab_name = 'tab_access'


class PropertiesTab(SMITab):
    """Properties
    """

    grok.implements(interfaces.IPropertiesTab)
    grok.name('tab_metadata')
    grok.baseclass()


class DummyPropertiesTab(PropertiesTab):

    grok.template('smitab')
    grok.name('tab_metadata_extra')
    tab_name = 'tab_metadata'


class PreviewTab(SMITab):
    """Preview
    """

    grok.implements(interfaces.IPreviewTab)
    grok.name('tab_preview')
    grok.baseclass()


class DummyPreviewTab(PreviewTab):

    grok.template('smitab')
    grok.name('tab_preview_extra')
    tab_name = 'tab_preview'


class EditTab(SMITab):
    """Edit
    """

    grok.implements(interfaces.IEditTab)
    grok.name('tab_edit')
    grok.baseclass()


class DummyEditTab(EditTab):

    grok.template('smitab')
    grok.name('tab_edit_extra')
    tab_name = 'tab_edit'


class SMIMiddleGroundManager(silvaviews.ViewletManager):
    """Middleground macro.
    """
    grok.layer(interfaces.ISMILayer)
    grok.view(silvaviews.SMIView)

    @CachedProperty
    def buttons(self):
        return (viewlet for viewlet in self.viewlets if \
                    not interfaces.ISMISpecialButton.providedBy(viewlet) \
                    and viewlet.available())

    @CachedProperty
    def executors(self):
        return (viewlet for viewlet in self.viewlets if \
                    interfaces.ISMIExecutorButton.providedBy(viewlet) \
                    and viewlet.available())


class SMIButton(silvaviews.Viewlet):
    """A button.
    """
    grok.baseclass()
    grok.layer(interfaces.ISMILayer)
    grok.viewletmanager(SMIMiddleGroundManager)

    template = grok.PageTemplate(filename='templates/smibutton.pt')

    label = None
    tab = None
    help = None
    accesskey = None

    def formatedLabel(self):
        if interfaces.ISMISpecialButton.providedBy(self):
            return self.label
        return translate(self.label, context=self.request) + '...'

    def available(self):
        return True

    @property
    def selected(self):
        return self.request.URL.endswith(self.tab)

