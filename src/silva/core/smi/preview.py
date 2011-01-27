# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getMultiAdapter

from silva.core.views.interfaces import ISilvaURL
from silva.core.smi.smi import SMIPage
from silva.core.interfaces import IDirectlyRendered, ISilvaObject
from silva.translations import translate as _

from silva.core.smi.interfaces import ISMILayer


grok.templatedir('smi_templates')
grok.layer(ISMILayer)


class PreviewTab(SMIPage):
    """Preview tab for non-publishable content in Silva.
    """
    grok.context(IDirectlyRendered)
    grok.name('tab_preview')
    grok.require('silva.ReadSilvaContent')

    tab = _('preview')

    def render(self):
        return self.context.preview()


class PreviewFrameset(grok.View):
    grok.context(ISilvaObject)
    grok.name('previewframeset')

    rows = '52px,*'

    @property
    def preview_url(self):
        url = getMultiAdapter((self.context, self.request), ISilvaURL)
        return url.preview()
