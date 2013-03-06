# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.ui.menu import ContentMenu, ExpendableMenuItem
from silva.ui.rest import Screen
from silva.core.interfaces import ISilvaObject
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class Settings(silvaforms.SMIComposedForm):
    grok.adapts(Screen, ISilvaObject)
    grok.require('silva.ChangeSilvaContent')
    grok.name('settings')

    label = _('Settings')



class SettingsMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, ISilvaObject)
    grok.require('silva.ChangeSilvaContent')
    grok.order(80)
    name = _('Settings')
    screen = Settings

