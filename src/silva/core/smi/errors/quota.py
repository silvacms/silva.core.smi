# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core.views import views as silvaviews
from zope.traversing.browser import absoluteURL

from Acquisition import aq_parent
from Products.Silva.mangle import Bytes
from Products.Silva.Publication import OverQuotaException


class OverQuotaErrorPage(silvaviews.Page):
    """ Page to render broken references errors.

    It redirects to break references form if the user as the necessary rights to
    break references.
    """
    grok.context(OverQuotaException)
    grok.name('error.html')
    grok.template('error')

    tab_name = 'tab_edit'

    def update(self):
        self.exceeding_size = Bytes(self.context.error.args[0])
        self.next_url = absoluteURL(aq_parent(self.context), self.request) + '/edit'
