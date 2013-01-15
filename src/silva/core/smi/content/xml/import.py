# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import zipfile
import uuid

from five import grok
from zope import schema
from zope.event import notify
from zope.interface import Interface
from zope.component import getUtility
from zope.lifecycleevent import ObjectModifiedEvent

from silva.core.references.interfaces import IReferenceService
from silva.core.conf import schema as silvaschema
from silva.core.interfaces import IContainer, IVersion
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
        description=_(u"Locate a zip file containing assets "
                      u"or a zip file created by a Silva full media export."),
        required=True)
    asset_title = schema.TextLine(
        title=_(u"Title for assets"),
        description=_(u"Set a title for all assets created from the items "
                      u"of a zip file with assets."),
        default=u'',
        required=False)
    sub_directories = schema.Bool(
        title=_(u"Subdirectories"),
        description=_(u"Recreate the subdirectory structure of a zip file "
                      u"with assets by adding folders."),
        default=False,
        required=False)
    replace = schema.Bool(
        title=_(u"Replace items"),
        description=_(u"Replace items with the ones from the import file "
                      u"when they have the same ids (Note: they will be "
                      u"replaced *even* when published)."),
        default=False,
        required=False)


def make_import_log(context, importer, identifier='import_log'):
    # All of this need improvements
    log = context._getOb(identifier, None)
    if log is None:
        factory = context.manage_addProduct['silva.app.document']
        factory.manage_addDocument(identifier, 'Import log')
        log = context._getOb(identifier)
    version = log.get_editable()
    service = getUtility(IReferenceService)

    html = ['<h2> Import inside {0}</h2><ul>'.format(
            importer.root.get_title_or_id())]
    for reason, content in importer.getProblems():
        if IVersion.providedBy(content):
            content = content.get_silva_object()
        tag = unicode(uuid.uuid1())
        reference = service.new_reference(version, name=u"body link")
        reference.set_target(content)
        reference.add_tag(tag)
        html.extend(['<li><a class="link" reference="{0}">'.format(tag),
                     content.get_title_or_id(), '</a>: ',
                     reason, '</li>'])
    html.append('</ul>')
    version.body.save_raw_text(''.join(html) + unicode(version.body))
    notify(ObjectModifiedEvent(version))


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
        # This need improvements and refactoing
        importer = IZipFileImporter(self.context)
        try:
            if importer.isFullmediaArchive(data['archive']):
                importer = importer.importFromZip(
                    data['archive'],
                    self.request,
                    data.getDefault('replace'))
                make_import_log(self.context, importer)
                problems = importer.getProblems()
                if len(problems):
                    self.send_message(
                        _(u'Import is successful, but there are '
                          u'${many} problem(s).',
                          mapping={'many': len(problems)}),
                        type=u"error")
                else:
                    self.send_message(
                        _(u"Import succeeded."),
                        type=u"feedback")
            else:
                importer = IArchiveFileImporter(self.context)
                imported, failures = importer.importArchive(
                    data['archive'],
                    data.getDefault('asset_title'),
                    data.getDefault('sub_directories'),
                    data.getDefault('replace'))
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
        except zipfile.BadZipfile as error:
            self.send_message(
                _('Invalid import file: ${error}.',
                  mapping={'error': str(error)}),
                type=u"error")


class ImportMenu(MenuItem):
    grok.adapts(ContainerMenu, IContainer)
    grok.order(80)
    grok.require('silva.ManageSilvaContentSettings')
    name = _(u'Import')

    screen = ImportForm
