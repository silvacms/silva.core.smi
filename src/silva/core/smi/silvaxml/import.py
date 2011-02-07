# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import zipfile

from five import grok
from silva.core.conf import schema as silvaschema
from silva.core.interfaces import IContainer
from silva.core.interfaces import IZipFileImporter, IArchiveFileImporter
from silva.core.smi import smi as silvasmi
from silva.core.smi.interfaces import IPublishTab, IPublicationAwareTab
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.silva.form import ExtractedDecoratedAction
from zope import schema
from zope.interface import Interface


class IImportFields(Interface):
    """Import form description.
    """
    archive = silvaschema.Bytes(
        title=_("file to upload"),
        description=_(u"Locate a zip file containing Assets "
                      u"or a zip file created by a Silva full media export."),
        required=True)
    asset_title = schema.TextLine(
        title=_(u"title for assets"),
        description=_(u"Set a title for all Assets created from the contents "
                      u"of a zip file with Assets."),
        default=u'',
        required=False)
    sub_directories = schema.Bool(
        title=_(u"subdirectories"),
        description=_(u"Recreate the subdirectory structure of a zip file "
                      u"with Assets by adding Silva Folders."),
        default=False,
        required=False)
    replace = schema.Bool(
        title=_(u"replace content"),
        description=_(u"Replace Content Objects with the Objects from "
                      u"the import when they have the same ids "
                      u"(Note: they will be replaced *even* when published)."),
        default=False,
        required=False)


class ImportForm(silvaforms.SMIForm):
    """Import the content of a file in Silva.
    """
    grok.name('tab_edit_import')
    grok.require('silva.ManageSilvaContentSettings')
    grok.context(IContainer)
    grok.implements(IPublishTab)

    tab = 'edit'

    label = _(u"import and extract zip archive")
    fields = silvaforms.Fields(IImportFields)
    actions = silvaforms.Actions(silvaforms.CancelAction())

    @silvaforms.action(
        _(u"import"),
        description=_(u"upload and import file"),
        factory=ExtractedDecoratedAction)
    def import_file(self, data):
        importer = IZipFileImporter(self.context)
        try:
            if importer.isFullmediaArchive(data['archive']):
                imported, failures = importer.importFromZip(
                    data['archive'],
                    data.getDefault('replace'))
            else:
                importer = IArchiveFileImporter(self.context)
                imported, failures = importer.importArchive(
                    data['archive'],
                    data.getDefault('asset_title'),
                    data.getDefault('sub_directories'),
                    data.getDefault('replace'))
        except zipfile.BadZipfile as error:
            self.send_message(
                _('Invalid file: ${error}', mapping={'error': str(error)}),
                type=u"error")
        else:
            if imported:
                self.send_message(
                    _('added ${succeeded}',
                      mapping={'succeeded': ', '.join(imported)}),
                    type=u"feedback")
            if failures:
                self.send_message(
                    _('could not add: ${failed}',
                      mapping={'failed': ', '.join(failures)}),
                    type=u"error")


class ImportButton(silvasmi.SMIMiddleGroundButton):
    grok.context(IContainer)
    grok.order(200)
    grok.require('silva.ManageSilvaContentSettings')
    grok.view(IPublicationAwareTab)

    tab = 'tab_edit_import'
    label = _(u"import")
    help = _(u"import xml data or a zip file: alt-i")
    accesskey = 'i'


class ExportButton(silvasmi.SMIMiddleGroundButton):
    grok.context(IContainer)
    grok.order(210)
    grok.require('silva.ManageSilvaContentSettings')
    grok.view(IPublicationAwareTab)

    tab = 'tab_status_export'
    label = _(u"export")
    help = _(u"export to xml or other: alt-e")
    accesskey = 'e'
