# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from megrok.chameleon.components import ChameleonPageTemplate

from Products.Silva.mangle import Bytes
from Products.Silva.Publication import OverQuotaException
from silva.ui.rest.errors import ErrorREST


class OverQuotaError(ErrorREST):
    """ Over quota error.
    """
    grok.context(OverQuotaException)

    message_template = ChameleonPageTemplate('templates/quota.cpt')

    def update(self):
        self.exceeding_size = Bytes(self.context.error.args[0])
