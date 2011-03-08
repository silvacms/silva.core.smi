# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from silva.ui.menu import ExpendableContentMenuItem
from silva.translations import translate as _
from silva.core.interfaces import IContainer


class XMLMenu(ExpendableContentMenuItem):
    grok.context(IContainer)
    grok.order(20)
    name = _(u'XML')

