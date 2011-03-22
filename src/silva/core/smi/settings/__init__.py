# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.ui.menu import ContentMenu, ExpendableMenuItem
from silva.core.interfaces import ISilvaObject
from silva.translations import translate as _


class SettingsMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, ISilvaObject)
    grok.order(80)
    name = _('Settings')

