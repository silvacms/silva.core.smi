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

# XXX ISMIView and ISMITab should be the same ?
class ISMITab(IGrokView):
    """A tab in SMI.
    """


class ISMITabIndex(IGrokView):
    """A view that is an index of a tab in SMI.
    """


class ISMILayer(ICustomizableLayer, INonCachedLayer):
    """Layer for SMI.
    """
    silvaconf.resource('jquery-1.3.2.js')
    silvaconf.resource('jquery-ui-1.7.2.js')

    silvaconf.resource('jquery-ui-1.7.2.css')
    silvaconf.resource('smi.css')


class IAccessTab(ISMITab):
    """Access tab.
    """


class IPropertiesTab(ISMITab):
    """Properties tab.
    """


class IPreviewTab(ISMITab):
    """Preview tab.
    """

class IPublishTab(ISMITab):
    """Publish tab.
    """


class IEditTab(ISMITab):
    """Edit tab.
    """


class ISMIButtonManager(IViewletManager):
    """Where SMI button apprears.
    """


class ISMIButton(IViewlet):
    """A button which appears at the top of the management tab.
    """
    label = Attribute("Label of the button")
    tab = Attribute("Where do that button links to")
    accesskey = Attribute("Access Key")
    help = Attribute("Description of that tab")

    def available():
        """Is that button available ?
        """


class ISMISpecialButton(Interface):
    """A special button.
    """


class ISMIExecutorButton(ISMIButton, ISMISpecialButton):
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
