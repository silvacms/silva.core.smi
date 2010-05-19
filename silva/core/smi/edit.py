# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi.interfaces import ISMIExecutorButton
from silva.core.smi import smi
from silva.core import interfaces
from silva.translations import translate as _

from five import grok


# grok.view(smi.EditTab)
grok.templatedir('smi_templates')


class VersionedEditButton(smi.SMIButton):

    grok.context(interfaces.IVersionedContent)
    grok.baseclass()

    def available(self):
        return bool(self.context.get_unapproved_version())


class PublishNowButton(VersionedEditButton):

    grok.implements(ISMIExecutorButton)
    grok.order(20)

    label = _(u"publish now")
    help = _(u"publish this document: alt-p")
    accesskey = 'p'

    @property
    def tab(self):
        return 'quick_publish?return_to=%s' % self.view.tab_name

