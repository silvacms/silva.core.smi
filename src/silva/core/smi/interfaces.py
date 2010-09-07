# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope import schema
from zope.interface import Attribute, Interface, directlyProvides
from zope.contentprovider.interfaces import ITALNamespaceData

from grokcore.view.interfaces import IGrokView

from silva.core import conf as silvaconf
from silva.core.layout.interfaces import ICustomizableLayer
from silva.core.views.interfaces import INonCachedLayer
from silva.core.views.interfaces import IViewlet, IViewletManager


class ISMIView(IGrokView):
    """A view in SMI.
    """

class ISMILayer(ICustomizableLayer, INonCachedLayer):
    """Layer for SMI.
    """
    silvaconf.resource('jquery-1.3.2.js')
    silvaconf.resource('jquery-ui-1.7.3.custom.min.js')
    silvaconf.resource('jquery-ui-i18n.js')
    silvaconf.resource('smi.js')

    silvaconf.resource('jquery-ui-1.7.3.custom.css')
    silvaconf.resource('smi.css')


class ISMIButtonManager(IViewletManager):
    """Where SMI (middleground) buttons apprears.
    """


class ISMIButton(IViewlet):
    """A button which appears at the top of the management tab.
    """

    def available():
        """Is that button available ?
        """


class ISMIBasicButton(ISMIButton):
    """Basic link-o-button.
    """
    label = Attribute("Label of the button")
    tab = Attribute("Where do that button links to")
    accesskey = Attribute("Access Key")
    help = Attribute("Description of that tab")



class ISMIRemoteButton(ISMIBasicButton):
    """Button that open a popup form.
    """
    label = Attribute("Label of the button")
    action = Attribute("What action the popup does trigger")
    accesskey = Attribute("Access Key")
    help = Attribute("Description of that tab")


class ISMIExecutorButton(ISMIButton):
    """This button execute an action.
    """


class ISMIMenu(IViewletManager):
    """ Interface for menu of the SMI
    """


class ISMIMenuItem(IViewlet):
    """ Interface for menu items
    """

    name = Attribute('menu item name')
    position = Attribute('order attribute')

    def available():
        """ returns whether the menu item should be displayed
        """


class IMessageProvider(Interface):
    """ This interfaces allow to get the message varialbles declare in
    the template into the content provider that provides this interface.
    """
    message = schema.Text(
        title=u"notification message for the user",
        required=False)

    message_type = schema.TextLine(
        title=u"notification type",
        required=False)

    no_empty_feedback = schema.Bool(
        title=u"omit feedback space if there is no messages",
        required=False,
        default=False)

directlyProvides(IMessageProvider, ITALNamespaceData)


class ISMINavigationOff(Interface):
    """ View implementing this interface won't display navigation
    """


# XXX ISMIView and ISMITab should be the same ?
class ISMITab(IGrokView):
    """A tab in SMI.
    """


class ISMITabIndex(IGrokView):
    """A view that is an index of a tab in SMI.
    """


class IPublicationAwareTab(ISMITab):
    """Tabs where publication like tasks are done.
    """


class IEditionAwareTab(IPublicationAwareTab):
    """Tabs where edition like tasks are done.
    """


class IAccessTab(ISMITab):
    """Access tab.
    """


class IPropertiesTab(IEditionAwareTab):
    """Properties tab.
    """


class IPreviewTab(IEditionAwareTab):
    """Preview tab.
    """


class IPublishTab(IPublicationAwareTab):
    """Publish tab.
    """


class IEditTab(IEditionAwareTab):
    """Edit tab.
    """


class IEditTabIndex(IEditTab, ISMITabIndex):
    """Edit tab index: edit form.
    """


class IAddingTab(IEditTab, ISMINavigationOff):
    """Adding tab.
    """
    __name__ = Attribute("Content type of the added content")
