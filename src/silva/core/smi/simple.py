# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import Interface

from silva.core.smi.smi import SMILayout
from silva.core.smi import interfaces
from silva.core.views.httpheaders import HTTPResponseHeaders
from infrae.layout import ILayout, layout


class ISimpleSMILayout(ILayout):
    """ Interface for simple SMI layout
    """


class SimpleSMILayout(SMILayout):
    """ Layout for SMI.
    """
    grok.implements(ISimpleSMILayout)
    grok.template('simplesmilayout')
    layout(ISimpleSMILayout)


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
