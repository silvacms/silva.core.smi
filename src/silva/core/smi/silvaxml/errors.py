# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.translations import translate as _
from silva.ui.rest.errors import ErrorREST
from Products.Silva.silvaxml.xmlexport import ExternalReferenceError


class ExternalReferenceErrorPage(ErrorREST):
    """ Page to render broken references errors.

    It redirects to break references form if the user as the necessary rights to
    break references.
    """
    grok.context(ExternalReferenceError)

    title = _('External reference exported')

    def update(self):
        origin, target, exported = self.context.error.args
        self.origin = origin.get_silva_object()
        self.target = target.get_silva_object()
        self.exported = exported.get_silva_object()
