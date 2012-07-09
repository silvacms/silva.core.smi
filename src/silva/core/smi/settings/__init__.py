# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import Acquisition

from five import grok
from silva.ui.menu import ContentMenu, ExpendableMenuItem
from silva.ui.rest import Screen
from silva.core.interfaces import ISilvaObject
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class AcquisitionMethod(Acquisition.Explicit):
    """This class let you have an acquisition context on a method.
    """
    # for Formulamerde.
    def __init__(self, parent, method_name):
        self.parent = parent
        self.method_name = method_name

    def __call__(self, *args, **kwargs):
        instance = self.parent.aq_inner
        method = getattr(instance, self.method_name)
        return method(*args, **kwargs)


class Settings(silvaforms.SMIComposedForm):
    grok.adapts(Screen, ISilvaObject)
    grok.name('settings')

    label = _('Settings')

    def get_wanted_quota_validator(self):
        # for Formulamerde crap.
        return AcquisitionMethod(self.context, 'validate_wanted_quota')

    get_wanted_quota_validator__roles__ = None



class SettingsMenu(ExpendableMenuItem):
    grok.adapts(ContentMenu, ISilvaObject)
    grok.order(80)
    name = _('Settings')
    screen = Settings

