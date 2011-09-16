# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

import re
import lxml.html.diff

from five import grok
from zope.interface import Interface
from zope.interface import alsoProvides
from zope import schema
from zope.component import getMultiAdapter
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.Silva.Versioning import VersioningError
from silva.core.interfaces import IVersion, IVersionManager
from silva.core.interfaces import IVersionedContent
from silva.core.interfaces import IPublicationWorkflow
from silva.core.smi.content.publish import Publish
from silva.translations import translate as _
from silva.ui.rest import RedirectToPage
from silva.ui.rest import PageREST
from silva.core.views.interfaces import IPreviewLayer
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction


@apply
def version_status_vocabulary():
    terms = [
        SimpleTerm(value="unapproved", title=_(u"Unapproved")),
        SimpleTerm(value="approved", title=_(u"Approved")),
        SimpleTerm(value="published", title=_(u"Published")),
        SimpleTerm(value="last_closed", title=_(u"Last closed")),
        SimpleTerm(value="closed", title=_(u"Closed"))]
    return SimpleVocabulary(terms)


class IPublicationStatusInfo(Interface):
    id = schema.TextLine(
        title=_(u'Version'))
    modification_time = schema.Datetime(
        title=_('Modification time'))
    publication_time = schema.Datetime(
        title=_('Publication time'))
    expiration_time = schema.Datetime(
        title=_('Expiration time'))
    last_author = schema.TextLine(
        title=_('Last author'))
    version_status = schema.Choice(
        title=_('Version status'),
        source=version_status_vocabulary)


class PublicationStatusInfo(grok.Adapter):
    grok.context(IVersion)
    grok.provides(IPublicationStatusInfo)

    def __init__(self, context):
        self.context = context
        self.manager = IVersionManager(self.context)

    @property
    def id(self):
        return self.context.getId()

    @property
    def modification_time(self):
        dt = self.manager.get_modification_datetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def publication_time(self):
        dt = self.manager.get_publication_datetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def expiration_time(self):
        dt = self.manager.get_expiration_datetime()
        if dt is not None:
            return dt.asdatetime()

    @property
    def last_author(self):
        author = self.manager.get_last_author()
        if author is not None:
            return author.fullname()

    @property
    def version_status(self):
        return self.manager.get_status()

    def delete(self):
        return self.manager.delete()

    def copy_for_editing(self):
        return self.manager.make_editable()


class CopyForEditingAction(silvaforms.Action):
    """Copy a version to use as new editable version.
    """
    title = _('Copy for editing')
    description = _('create a new editable version of '
                    'the selected old one')

    def __call__(self, form, selected, deselected):
        if len(selected) != 1:
            form.send_message(
                _(u"Please select one version to copy."),
                type='error')
            return silvaforms.FAILURE
        content = selected[0].getContentData().getContent()
        try:
            content.copy_for_editing()
        except VersioningError as e:
            form.send_message(e.reason(), type='error')
            return silvaforms.FAILURE
        form.send_message(
            _("Reverted to previous version."),
            type='feedback')
        return silvaforms.SUCCESS


class ViewVersionAction(silvaforms.Action):
    """Preview a particular version.
    """
    title = _('View')
    description = _('view this particular version')

    def __call__(self, form, selected, deselected):
        if len(selected) != 1:
            form.send_message(
                _(u"Please select one version to view it."),
                type='error')
            return silvaforms.FAILURE
        version_id = selected[0].getContentData().getContent().id
        raise RedirectToPage(form.context, 'publish/view/%s' % version_id)


class ViewVersionScreen(PageREST):
    grok.adapts(Publish, IVersionedContent)
    grok.require('silva.ReadSilvaContent')
    grok.name('view')

    def __init__(self, *args):
        super(ViewVersionScreen, self).__init__(*args)
        self.__version = None

    def publishTraverse(self, request, name):
        match = re.compile('^(\d+)$').match(name)
        if match:
            version = self.context._getOb(match.group(1), None)
            if IVersion.providedBy(version):
                self.__version = version
                alsoProvides(self.request, IPreviewLayer)
                return self
        return super(ViewVersionScreen, self).publishTraverse(request, name)

    def payload(self):
        assert self.__version is not None
        view = getMultiAdapter(
            (self.context, self.request), name='content.html')
        view.version = self.__version
        return {"ifaces": ["preview"],
                "html": view()}


class CompareVersionAction(silvaforms.Action):
    """Compare two different versions.
    """
    title = _('Compare')
    descripton = _('select and compare two different versions')

    def __call__(self, form, selected, deselected):
        if len(selected) != 2:
            form.send_message(
                _(u"Select exactly two different versions to compare them."),
                type='error')
            return silvaforms.FAILURE
        id1 = selected[0].getContentData().getContent().id
        id2 = selected[1].getContentData().getContent().id
        raise RedirectToPage(form.context, 'publish/compare/%s-%s' % (id1, id2))


class CompareVersionScreen(PageREST):
    """Screen to compare two versions
    """
    grok.adapts(Publish, IVersionedContent)
    grok.require('silva.ReadSilvaContent')
    grok.name('compare')

    def __init__(self, *args):
        super(CompareVersionScreen, self).__init__(*args)
        self.__version1 = None
        self.__version2 = None

    def publishTraverse(self, request, name):
        match = re.compile('^(\d+)-(\d+)$').match(name)
        if match:
            version1 = self.context._getOb(match.group(1), None)
            version2 = self.context._getOb(match.group(2), None)
            if IVersion.providedBy(version1) and IVersion.providedBy(version2):
                self.__version1 = version1
                self.__version2 = version2
                alsoProvides(self.request, IPreviewLayer)
                return self
        return super(CompareVersionScreen, self).publishTraverse(request, name)

    def payload(self):
        assert self.__version1 is not None
        assert self.__version2 is not None

        version1_view = getMultiAdapter(
            (self.context, self.request), name='content.html')
        version1_view.content = self.__version1
        version1_html = version1_view()

        version2_view = getMultiAdapter(
            (self.context, self.request), name='content.html')
        version2_view.content = self.__version2
        version2_html = version2_view()

        return {"ifaces": ["preview"],
                "html": lxml.html.diff.htmldiff(version2_html, version1_html)}


class DeleteVersionAction(silvaforms.Action):
    """Permanently remove version.
    """
    grok.implements(IRemoverAction)
    title = _("Delete")
    description = _("there's no undo")

    def __call__(self, form, selected, deselected):
        if not len(deselected):
            form.send_message(
                _(u"Cannot delete all versions."),
                type='error')
            return silvaforms.FAILURE
        if not len(selected):
            form.send_message(
                _(u"No version selected, nothing deleted."),
                type='error')
            return silvaforms.FAILURE
        for line in selected:
            try:
                line.getContentData().getContent().delete()
            except VersioningError as e:
                form.send_message(e.reason(), type='error')
        form.send_message(_(u"Version(s) deleted."), type='feedback')
        return silvaforms.SUCCESS


class PublicationStatusTableForm(silvaforms.SMISubTableForm):
    """ Manage versions.
    """
    grok.context(IVersionedContent)
    grok.view(Publish)
    grok.order(30)

    label = _(u"Manage versions")
    mode = silvaforms.DISPLAY

    ignoreRequest = True
    ignoreContent = False

    batchSize = 10
    batchItemFactory = IPublicationStatusInfo

    tableFields = silvaforms.Fields(IPublicationStatusInfo)
    tableActions = silvaforms.TableMultiActions(
        DeleteVersionAction(identifier='delete'),
        CopyForEditingAction(identifier='copy'),
        ViewVersionAction(identifier='view'),
        CompareVersionAction(identifier='compare'))

    def getItems(self):
        versions = IPublicationWorkflow(self.context).get_versions(False)
        versions.sort(key=lambda v: int(v.getId()), reverse=True)
        return versions
