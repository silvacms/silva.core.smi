# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized
from zope.interface import implements

from silva.core.layout.interfaces import ISMILayer
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

# 404 page

class ErrorPage(silvaviews.Page):
    silvaconf.context(INotFound)
    silvaconf.name('error.html')
    silvaconf.layer(ISMILayer)


# Unauthorized page

class UnauthorizedPage(silvaviews.Page):
    silvaconf.context(IUnauthorized)
    silvaconf.name('error.html')
    silvaconf.layer(ISMILayer)

