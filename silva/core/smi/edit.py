# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi.interfaces import ISMIExecutorButton, \
    IFormsEditorSupport, IKupuEditorSupport
from silva.core.smi import smi
from silva.core import conf as silvaconf

from Products.Silva.i18n import translate as _
from silva.core import interfaces
from Products.SilvaDocument.interfaces import IDocument


silvaconf.view(smi.EditTab)


class VersionedEditButton(smi.SMIButton):

    silvaconf.context(interfaces.IVersionedContent)
    silvaconf.baseclass()

    def available(self):
        return bool(self.context.get_unapproved_version())


class PublishNowButton(VersionedEditButton):

    silvaconf.implements(ISMIExecutorButton)
    silvaconf.order(20)

    label = _(u"publish now")
    help = _(u"publish this document: alt-p")
    accesskey = 'p'

    @property
    def tab(self):
        return 'quick_publish?return_to=%s' % self.view.tab_name


class KupuEditorButton(VersionedEditButton):
    silvaconf.context(IKupuEditorSupport)
    silvaconf.order(10)

    tab = 'tab_edit?editor=kupu'
    label = _(u"kupu editor")
    help = _(u"edit with the kupu editor: alt-(")
    accesskey = '('

    @property
    def selected(self):
        return self.request.get('editor',None)=='kupu'

class FormsEditorButton(VersionedEditButton):
    silvaconf.context(IFormsEditorSupport)
    silvaconf.order(20)

    tab = 'tab_edit?editor=forms_editor'
    label = _(u"forms editor")
    help = _(u"edit with the forms editor: alt-)")
    accesskey = ')'
    
    @property
    def selected(self):
        return self.request.get('editor',None)=='forms_editor'
