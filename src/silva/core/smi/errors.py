# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.smi import interfaces
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders


class SMILayout(silvaviews.Layout):
    """ Layout for SMI.
    """
    grok.context(Exception)
    grok.layer(interfaces.ISMILayer)

    def update(self):
        self.root_url = self.context.get_root_url()
        self.view_name = ''


class SMIHTTPHeaders(HTTPResponseHeaders):
    """Define HTTP-headers for SMI pages. By default we don't want to
    cache.
    """
    grok.adapts(interfaces.ISMILayer, Exception)

    def cache_headers(self):
        self.disable_cache()
