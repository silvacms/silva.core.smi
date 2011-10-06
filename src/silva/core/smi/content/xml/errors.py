# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.interfaces.errors import ExternalReferenceError
from silva.translations import translate as _
from silva.core.views.views import Page


class ExternalReferenceErrorPage(Page):
    """ Page to render broken references errors.

    It redirects to break references form if the user as the necessary rights to
    break references.
    """
    grok.context(ExternalReferenceError)
    grok.name('error.html')

    title = _('External reference exported')

    def update(self):
        self.origin = self.content.error.content.get_silva_object()
        self.target = self.content.error.target.get_silva_object()
        self.exported = self.content.error.exported.get_silva_object()
