# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi.interfaces import ISMIExecutorButton, \
    IFormsEditorSupport, IKupuEditorSupport
from silva.core.smi import smi
from silva.core import interfaces
from silva.translations import translate as _

from five import grok

grok.view(smi.EditTab)


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


class KupuEditorButton(VersionedEditButton):
    grok.context(IKupuEditorSupport)
    grok.order(10)

    tab = 'tab_edit?editor=kupu'
    label = _(u"kupu editor")
    help = _(u"edit with the kupu editor: alt-(")
    accesskey = '('

    @property
    def selected(self):
        return self.request.get('editor',None)=='kupu'


class FormsEditorButton(VersionedEditButton):
    grok.context(IFormsEditorSupport)
    grok.order(20)

    tab = 'tab_edit?editor=forms_editor'
    label = _(u"forms editor")
    help = _(u"edit with the forms editor: alt-)")
    accesskey = ')'

    @property
    def selected(self):
        return self.request.get('editor',None)=='forms_editor'
