# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.cachedescriptors.property import CachedProperty
from zope.i18n import translate

from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

from silva.core.smi import interfaces

silvaconf.templatedir('templates')

class SMITab(silvaviews.SMIView):
    """A SMI Tab.
    """

    silvaconf.baseclass()


# For the moment tabs are not registered. Dummy tabs are used instead
# to register components to, they will become the real tab when we
# will switch from Silva views to that system completly.

class AccessTab(SMITab):
    """Access
    """

    silvaconf.implements(interfaces.IAccessTab)
    silvaconf.name('tab_access')
    silvaconf.baseclass()


class DummyAccessTab(AccessTab):

    silvaconf.template('smitab')
    silvaconf.name('tab_access_extra')
    tab_name = 'tab_access'


class PropertiesTab(SMITab):
    """Properties
    """

    silvaconf.implements(interfaces.IPropertiesTab)
    silvaconf.name('tab_metadata')
    silvaconf.baseclass()


class DummyPropertiesTab(PropertiesTab):

    silvaconf.template('smitab')
    silvaconf.name('tab_metadata_extra')
    tab_name = 'tab_metadata'


class PreviewTab(SMITab):
    """Preview
    """

    silvaconf.implements(interfaces.IPreviewTab)
    silvaconf.name('tab_preview')
    silvaconf.baseclass()


class DummyPreviewTab(PreviewTab):

    silvaconf.template('smitab')
    silvaconf.name('tab_preview_extra')
    tab_name = 'tab_preview'


class EditTab(SMITab):
    """Edit
    """

    silvaconf.implements(interfaces.IEditTab)
    silvaconf.name('tab_edit')
    silvaconf.baseclass()


class DummyEditTab(EditTab):

    silvaconf.template('smitab')
    silvaconf.name('tab_edit_extra')
    tab_name = 'tab_edit'


class SMIMiddleGroundManager(silvaviews.ViewletManager):
    """Middleground macro.
    """

    silvaconf.view(silvaviews.SMIView)

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

    silvaconf.viewletmanager(SMIMiddleGroundManager)
    silvaconf.template('smibutton')
    silvaconf.baseclass()

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

