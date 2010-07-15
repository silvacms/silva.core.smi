# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import Interface

from silva.core.smi import interfaces
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from infrae.layout import ILayout, layout


class ISimpleSMILayout(ILayout):
    """ Interface for simple SMI layout
    """


class SimpleSMILayout(silvaviews.Layout):
    """ Layout for SMI.
    """
    grok.context(Interface)
    grok.layer(interfaces.ISMILayer)
    grok.implements(ISimpleSMILayout)
    grok.template('simplesmilayout')
    layout(ISimpleSMILayout)

    def update(self):
        self.root_url = self.context.get_root_url()
        self.view_name = ''


class ErrorSMILayout(SimpleSMILayout):
    grok.context(Exception)


class SMIHTTPHeaders(HTTPResponseHeaders):
    """Define HTTP-headers for SMI pages. By default we don't want to
    cache.
    """
    grok.adapts(interfaces.ISMILayer, Interface)

    def cache_headers(self):
        self.disable_cache()


class ErrorHTTPHeaders(SMIHTTPHeaders):
    grok.adapts(interfaces.ISMILayer, Exception)

