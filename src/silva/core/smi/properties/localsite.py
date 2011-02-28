# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from zope.cachedescriptors.property import CachedProperty
from five import grok

from silva.ui.menu import SettingsMenuItem
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction
from silva.translations import translate as _
from silva.core.interfaces import IPublication, IRoot, ISiteManager


class LocalSiteMenu(SettingsMenuItem):
    grok.context(IPublication)
    grok.order(100)
    name = _(u'Local site')
    action = 'localsite'


class ManageLocalSite(silvaforms.SMIForm):
    """This form let enable (or disable) a Publication as a local
    site.
    """
    grok.context(IPublication)
    grok.name('silva.ui.localsite')
    grok.require('zope2.ViewManagementScreens')

    label = _(u"Local site")
    description = _(u"Here you can enable/disable a local site (or subsite). "
                    u"By making a local site, you will be able to add "
                    u"local services to the publication. Those services "
                    u"will only affect elements inside that publication.")

    @CachedProperty
    def manager(self):
        return ISiteManager(self.context)

    def can_be_a_local_site(self):
        return IPublication.providedBy(self.context) and \
            not self.manager.isSite()

    @silvaforms.action(
        _("make local site"),
        identifier="make_site",
        available=lambda form: form.can_be_a_local_site())
    def make_site(self):
        try:
            self.manager.makeSite()
        except ValueError, e:
            self.send_message(str(e), type=u"error")
            return silvaforms.FAILURE
        else:
            self.send_message(_("Local site activated."), type=u"feedback")
            return silvaforms.SUCCESS

    def can_be_normal_again(self):
        return IPublication.providedBy(self.context) and \
            self.manager.isSite() and \
            not IRoot.providedBy(self.context)

    @silvaforms.action(
        _("remove local site"),
        identifier="delete_site",
        available=lambda form: form.can_be_normal_again(),
        implements=IRemoverAction)
    def delete_site(self):
        try:
            self.manager.deleteSite()
        except ValueError, e:
            self.send_message(str(e), type=u"error")
            return silvaforms.FAILURE
        else:
            self.send_message(_("Local site deactivated."), type=u"feedback")
            return silvaforms.SUCCESS

