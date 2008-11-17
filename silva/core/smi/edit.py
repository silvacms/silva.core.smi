# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.smi import properties
from silva.core.smi import smi
from silva.core import conf as silvaconf

from Products.Silva.i18n import translate as _
from Products.Silva import interfaces
from Products.SilvaDocument.interfaces import IDocument

silvaconf.templatedir('templates')
silvaconf.view(smi.EditTab)

class PublishNowButton(properties.PublishNowButton):

    silvaconf.context(interfaces.IVersionedContent)


class KupuEditorButton(smi.SMIButton):
    silvaconf.context(IDocument)
    silvaconf.order(10)

    tab = 'tab_edit?editor=kupu'
    label = _(u"kupu editor")
    help = _(u"edit with the kupu editor: alt-(")
    accesskey = '('


class FormsEditorButton(smi.SMIButton):
    silvaconf.context(IDocument)
    silvaconf.order(20)

    tab = 'tab_edit?editor=forms_editor'
    label = _(u"forms editor...")
    help = _(u"edit with the forms editor: alt-)")
    accesskey = ')'


