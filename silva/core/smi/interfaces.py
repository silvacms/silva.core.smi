# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope.interface import Attribute, Interface

from silva.core.views.interfaces import ISMIView, IViewlet, IViewletManager

class ISMITab(ISMIView):
    """A management tab in Silva management interface.
    """

    tab_name = Attribute("Name of the current tab.")


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

    def available():
        """Is that button available ?
        """

    label = Attribute("Label of the button")
    tab = Attribute("Where do that button links to")
    accesskey = Attribute("Access Key")
    help = Attribute("Description of that tab")


class ISMISpecialButton(Interface):
    """A special button.
    """


class ISMIExecutorButton(ISMIButton, ISMISpecialButton):
    """This button execute an action.
    """

