# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.traversing.browser import absoluteURL

from Acquisition import aq_parent

from silva.core.interfaces import IRoot, IPublication
from silva.core.smi import interfaces
from silva.core.smi.interfaces import ISMIMenu, ISMIMenuItem, ISMITabIndex
from silva.core.views import views as silvaviews
from silva.translations import translate as _


class SMIMenu(silvaviews.ContentProvider):
    """ Base menu
    """
    grok.baseclass()
    grok.implements(ISMIMenu)

    path = u''

    @property
    def target_url(self):
        return "%s/%s" % (absoluteURL(self.context, self.request), self.path)

    def filter(self, viewlets):
        results = []
        for name, viewlet in viewlets:
            if not viewlet.available():
                continue
            results.append((name, viewlet,))
        return results


class SMITopMenu(SMIMenu):
    """ SMI main menu base class
    """
    grok.baseclass()
    template = grok.PageTemplate(
        filename='smi_templates/smitopmenu.pt')


class SMIEditMenu(SMITopMenu):
    """ Menu for the edit tab
    """
    grok.name(u'smimenutabs')
    path = u'edit'

    def selected(self):
        False


class SMIMenuItem(silvaviews.Viewlet):
    """ Base menu item
    """
    grok.baseclass()
    grok.viewletmanager(SMIMenu)
    grok.implements(ISMIMenuItem)
    grok.order(100)

    name = u''
    path = u''

    def available(self):
        return True

    @property
    def selected(self):
        return False

    @property
    def target_url(self):
        return u'%s/%s' % (self.viewletmanager.target_url, self.path,)


class SMITopMenuItem(SMIMenuItem):
    """ SMI top menu item base class
    """
    grok.baseclass()
    template = grok.PageTemplate(
        filename='smi_templates/smitopmenuitem.pt')

    tab = None
    accesskey = u''
    uplink_accesskey = u''
    toplink_accesskey = u''

    @property
    def selected(self):
        return self.tab is not None and self.tab.providedBy(self.view)

    @property
    def active(self):
        return self.selected and ISMITabIndex.providedBy(self.view)

    @property
    def css_class(self):
        return self.selected and \
            (self.active and 'selected' or 'recede') \
            or ''

    @property
    def up_image_src(self):
        if IPublication.providedBy(self.context):
            self.layout.static['up_publication.gif']()
        return self.layout.static['up_tree.gif']()

    @property
    def title(self):
        return self.name

    @property
    def toplink_url(self):
        if not IRoot.providedBy(self.context):
            publication = aq_parent(self.context).get_publication()
            return "%s/edit/%s" % (
                absoluteURL(publication, self.request), self.path)
        return None

    @property
    def toplink_title(self):
        return _('up to top of publication: alt-${key}',
                    mapping={'key': self.toplink_accesskey})

    @property
    def uplink_url(self):
        if not IRoot.providedBy(self.context):
            parent = aq_parent(self.context)
            return "%s/edit/%s" % (
                absoluteURL(parent, self.request), self.path)
        return None

    @property
    def uplink_title(self):
        return _('up a level: alt-${key}',
                    mapping={'key': self.uplink_accesskey})


class SMIEditMenuItem(SMITopMenuItem):
    """ Base class for items of menu_edit
    """
    grok.baseclass()
    grok.viewletmanager(SMIEditMenu)
    grok.order(1)


class SMIEditEditMenuItem(SMIEditMenuItem):
    """ Edit tab of the edit menu
    """
    name = _(u'edit')
    path = u'tab_edit'
    tab = interfaces.IEditTab
    grok.order(10)


class SMIEditPreviewMenuItem(SMIEditMenuItem):
    """ Preview tab of the edit menu
    """
    name = _(u'preview')
    path = u'tab_preview'
    tab = interfaces.IPreviewTab
    grok.order(20)


class SMIEditPropertiesMenuItem(SMIEditMenuItem):
    """ Properties tab of the edit menu
    """
    name = _(u'properties')
    path = u'tab_metadata'
    tab = interfaces.IPropertiesTab
    grok.order(30)


class SMIEditAccessMenuItem(SMIEditMenuItem):
    """ Access tab of the edit menu
    """
    name = _(u'access')
    path = u'tab_access'
    tab = interfaces.IAccessTab
    grok.order(40)


class SMIEditPublishMenuItem(SMIEditMenuItem):
    """ Publish tab of the edit menu
    """
    name = _(u'publish')
    path = u'tab_status'
    tab = interfaces.IPublishTab
    grok.order(50)
