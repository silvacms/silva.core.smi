# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from zope.publisher.interfaces import INotFound
from zope.security.interfaces import IUnauthorized

from silva.core.layout.interfaces import ISMILayer
from silva.core.views import views as silvaviews

# 404 page

class ErrorPage(silvaviews.Page):
    grok.context(INotFound)
    grok.name('error.html')
    grok.layer(ISMILayer)


# Unauthorized page

class UnauthorizedPage(silvaviews.Page):
    grok.context(IUnauthorized)
    grok.name('error.html')
    grok.layer(ISMILayer)

