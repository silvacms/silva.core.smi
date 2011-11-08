# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import zipfile

from five import grok
from zope import schema
from zope.interface import Interface

from silva.core.conf import schema as silvaschema
from silva.core.interfaces import IContainer
from silva.core.interfaces import IZipFileImporter, IArchiveFileImporter
from silva.core.smi.content.container import Container, ContainerMenu
from silva.translations import translate as _
from silva.ui.menu import MenuItem
from zeam.form import silva as silvaforms


class IImportFields(Interface):
    """Import form description.
    """
    archive = silvaschema.Bytes(
        title=_("File to upload"),
        description=_(u"Locate a zip file containing Assets "
                      u"or a zip file created by a Silva full media export."),
        required=True)
    asset_title = schema.TextLine(
        title=_(u"Title for assets"),
        description=_(u"Set a title for all Assets created from the contents "
                      u"of a zip file with Assets."),
        default=u'',
        required=False)
    sub_directories = schema.Bool(
        title=_(u"Subdirectories"),
        description=_(u"Recreate the subdirectory structure of a zip file "
                      u"with Assets by adding Silva Folders."),
        default=False,
        required=False)
    replace = schema.Bool(
        title=_(u"Replace content"),
        description=_(u"Replace Content Objects with the Objects from "
                      u"the import when they have the same ids "
                      u"(Note: they will be replaced *even* when published)."),
        default=False,
        required=False)


class ImportForm(silvaforms.SMIForm):
    """Import the content of a file in Silva.
    """
    grok.adapts(Container, IContainer)
    grok.name('import')
    grok.require('silva.ManageSilvaContentSettings')

    label = _(u"Import and extract ZIP archive")
    fields = silvaforms.Fields(IImportFields)
    fields['archive'].fileNotSetLabel = _(
        u"Click the Upload button to select a file to import.")
    fields['archive'].fileSetLabel = _(
        u"Click the Upload button to replace the current file with a new file.")
    actions = silvaforms.Actions(silvaforms.CancelAction())

    @silvaforms.action(
        _(u"Import"),
        description=_(u"upload and import file"),
        implements=silvaforms.IDefaultAction,
        factory=silvaforms.ExtractedDecoratedAction,
        accesskey='ctrl+i')
    def import_file(self, data):
        importer = IZipFileImporter(self.context)
        try:
            if importer.isFullmediaArchive(data['archive']):
                imported, failures = importer.importFromZip(
                    data['archive'],
                    self.request,
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
                    _('Imported ${succeeded}.',
                      mapping={'succeeded': ', '.join(imported)}),
                    type=u"feedback")
            if failures:
                self.send_message(
                    _('Could not import: ${failed}.',
                      mapping={'failed': ', '.join(failures)}),
                    type=u"error")


class ImportMenu(MenuItem):
    grok.adapts(ContainerMenu, IContainer)
    grok.order(80)
    grok.require('silva.ManageSilvaContentSettings')
    name = _(u'Import')

    screen = ImportForm
