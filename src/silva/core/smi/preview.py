# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from silva.core.smi.smi import SMIPage
from silva.core.interfaces import IDirectlyRendered
from silva.translations import translate as _


class PreviewTab(SMIPage):
    """Preview tab for non-publishable content in Silva.
    """
    grok.context(IDirectlyRendered)
    grok.name('tab_preview')
    grok.require('silva.ReadSilvaContent')

    tab = _('preview')

    def render(self):
        return self.context.preview()
