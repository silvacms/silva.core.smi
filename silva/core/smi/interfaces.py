# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope.interface import Attribute, Interface

from silva.core import conf as silvaconf
from silva.core.layout.interfaces import ICustomizableLayer
from silva.core.views.interfaces import ISMITab, IViewlet, IViewletManager


class ISMILayer(ICustomizableLayer):
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

