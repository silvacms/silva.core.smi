# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from Products.Silva.mangle import Bytes
from Products.Silva.Publication import OverQuotaException
from silva.ui.rest.errors import ErrorREST
from silva.translations import translate as _


class OverQuotaError(ErrorREST):
    """ Over quota error.
    """
    grok.context(OverQuotaException)

    title = _(u'Over Quota')

    def update(self):
        self.exceeding_size = Bytes(self.context.error.args[0])
