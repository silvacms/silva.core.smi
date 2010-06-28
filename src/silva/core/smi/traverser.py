# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import ITraversable

from silva.core.interfaces import IPublication
from silva.core.smi.interfaces import ISMILayer
from silva.core.views.traverser import UseParentByAcquisition


class SMITraversable(grok.MultiAdapter):
    """Traverser to display versioned contents in SMI preview.

    Add the preview layer on the request if needed.
    """
    grok.adapts(IPublication, IBrowserRequest)
    grok.implements(ITraversable)
    grok.name('edit')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, remaining):
        if not ISMILayer.providedBy(self.request):
            alsoProvides(self.request, ISMILayer)
        if name:
            self.request.other['SILVA_SMI_NAME'] = name
        return UseParentByAcquisition()
