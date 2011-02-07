# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Acquisition import aq_parent

from five import grok
from infrae.layout import ILayout, layout
from silva.core.interfaces import ISilvaObject
from silva.core.smi import interfaces
from silva.core.smi.smi import SMILayout
from silva.core.views.httpheaders import HTTPResponseHeaders
from zope.interface import Interface


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

    def __init__(self, request, context):
        while not ISilvaObject.providedBy(context):
            context = aq_parent(context)
        super(ErrorSMILayout, self).__init__(request, context)


class SMIHTTPHeaders(HTTPResponseHeaders):
    """Define HTTP-headers for SMI pages. By default we don't want to
    cache.
    """
    grok.adapts(interfaces.ISMILayer, Interface)

    def cache_headers(self):
        self.disable_cache()


class ErrorHTTPHeaders(SMIHTTPHeaders):
    grok.adapts(interfaces.ISMILayer, Exception)
