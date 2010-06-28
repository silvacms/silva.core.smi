# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.skinnable import applySkin
from zope.traversing.interfaces import ITraversable

from silva.core.interfaces import IPublication
from silva.core.smi.interfaces import ISMILayer
from silva.core.views.traverser import UseParentByAcquisition
from silva.core.layout.traverser import SET_SKIN_ALLOWED_FLAG


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
        if self.request.get(SET_SKIN_ALLOWED_FLAG, True):
            applySkin(self.request, ISMILayer)
            # Prevent skin modification after
            self.request[SET_SKIN_ALLOWED_FLAG] = False
        if name:
            self.request.other['SILVA_SMI_NAME'] = name
        return UseParentByAcquisition()
