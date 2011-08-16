# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.traversing.browser import absoluteURL

from Products.Silva.Versioning import VersioningError
from silva.core.interfaces import IVersion, IVersionManager
from silva.core.interfaces import IVersionedContent
from silva.core.interfaces import IPublicationWorkflow
from silva.core.smi.content.publish import Publish
from silva.translations import translate as _
from silva.ui.rest import RedirectToContentPreview, RedirectToPreview
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IRemoverAction

# TODO
# - messages

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
                _(u"Select only one copy to copy it for editing."),
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
                _(u"Select only one version to view it."),
                type='error')
            return silvaforms.FAILURE
        version = selected[0].getContentData().getContent().context
        raise RedirectToContentPreview(version)


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
        id1 = selected[0].getContentData().getContent().context.getId()
        id2 = selected[1].getContentData().getContent().context.getId()
        raise RedirectToPreview(
            absoluteURL(form.context, form.request) +
            '/compare_versions.html?version1=%s&version2=%s' % (id1, id2))


class DeleteVersionAction(silvaforms.Action):
    """Permanently remove version.
    """
    grok.implements(IRemoverAction)
    title = _("Delete")
    description = _("there's no undo")

    def __call__(self, form, content, line):
        try:
            content.delete()
        except VersioningError as e:
            form.send_message(e.reason(), type='error')
            return silvaforms.FAILURE
        form.send_message(_(u"Deleted version"), type='feedback')
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
    batchFactory = IPublicationStatusInfo

    tableFields = silvaforms.Fields(IPublicationStatusInfo)
    tableActions = silvaforms.CompoundActions(
        silvaforms.TableActions(
            DeleteVersionAction(identifier='delete')),
        silvaforms.TableMultiActions(
            CopyForEditingAction(identifier='copy'),
            ViewVersionAction(identifier='view'),
            CompareVersionAction(identifier='compare')))

    def getItems(self):
        versions = IPublicationWorkflow(self.context).get_versions(False)
        versions.sort(key=lambda v: int(v.getId()), reverse=True)
        return versions
