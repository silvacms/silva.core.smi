# -*- coding: utf-8 -*-
# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized
from zope.interface import implements

from silva.core.layout.interfaces import ISMILayer
from silva.core.views.interfaces import ITemplate
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

# 404 page

class IErrorPage(ITemplate):
    pass

class ErrorPage(silvaviews.Template):
    silvaconf.context(INotFound)
    silvaconf.name('error.html')
    silvaconf.layer(ISMILayer)

    implements(IErrorPage)

    def __call__(self):
        # FIXME: Why do I get a redirect and notfound in /edit ?
        self.update()
        return self.template.render(self)

# Unauthorized page

class IUnauthorizedPage(ITemplate):
    pass

class UnauthorizedPage(silvaviews.Template):
    silvaconf.context(IUnauthorized)
    silvaconf.name('error.html')
    silvaconf.layer(ISMILayer)

    implements(IUnauthorizedPage)

