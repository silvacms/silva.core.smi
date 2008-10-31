# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.cachedescriptors.property import CachedProperty

from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

from silva.core.smi import interfaces

silvaconf.templatedir('templates')

class SMITab(silvaviews.SMIView):
    """A SMI Tab.
    """

    silvaconf.template('smitab')
    silvaconf.baseclass()


class AccessTab(SMITab):
    """Access
    """

    silvaconf.implements(interfaces.IAccessTab)
    silvaconf.name('tab_access_extra')

    tab_name = 'tab_access'


class PropertiesTab(SMITab):
    """Properties
    """

    silvaconf.implements(interfaces.IPropertiesTab)
    silvaconf.name('tab_properties_extra')

    tab_name = 'tab_metadata'


class PreviewTab(SMITab):
    """Preview
    """

    silvaconf.implements(interfaces.IPreviewTab)
    silvaconf.name('tab_preview_extra')

    tab_name = 'tab_preview'


class EditTab(SMITab):
    """Edit
    """

    silvaconf.implements(interfaces.IEditTab)
    silvaconf.name('tab_edit_extra')

    tab_name = 'tab_edit'


class SMIMiddleGroundManager(silvaviews.ViewletManager):
    """Middleground macro.
    """

    silvaconf.view(SMITab)

    @CachedProperty
    def buttons(self):
        return (viewlet for viewlet in self.viewlets if \
                    not interfaces.ISMISpecialButton.providedBy(viewlet))

    @CachedProperty
    def executors(self):
        return (viewlet for viewlet in self.viewlets if \
                    interfaces.ISMIExecutorButton.providedBy(viewlet))


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

    def available(self):
        return True

    @property
    def selected(self):
        return self.request.URL.endswith(self.tab)

