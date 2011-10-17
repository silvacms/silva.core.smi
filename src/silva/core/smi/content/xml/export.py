# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime
import mimetypes

from five import grok
from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder

from silva.core.interfaces import IContainer, IContentExporterRegistry
from silva.core.smi.content.container import ContainerMenu, Container
from silva.translations import translate as _
from silva.ui.menu import MenuItem
from silva.ui.rest import ContentException
from zeam.form import silva as silvaforms

from Products.Silva.silvaxml import xmlexport
from zExceptions import BadRequest


@grok.provider(IContextSourceBinder)
def export_formats(context):
    return getUtility(IContentExporterRegistry).list(context)

def default_format(form):
    exporters = getUtility(IContentExporterRegistry).list(form.context)
    if len(exporters) > 0:
        return list(exporters)[0].token


class IExportFields(Interface):
    include_sub_publications = schema.Bool(
        title=_(u"Include sub publications?"),
        description=_(u"Check to export all sub publications. "),
        default=False,
        required=False)

    export_newest_version_only = schema.Bool(
        title=_(u"Export only newest versions?"),
        description=_(u"If not checked all versions are exported."),
        default=True,
        required=False)

    export_format = schema.Choice(
        source=export_formats,
        title=_(u"Select an export format"),
        description=_(u"Select the format which will be used for the export."))


class ExportAction(silvaforms.LinkAction):
    grok.implements(silvaforms.IDefaultAction)

    title = _(u"Export")
    description = _(u"export content")
    accesskey = 'ctrl+e'

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            raise BadRequest('invalid export parameters')

        settings = xmlexport.ExportSettings()
        settings.setWithSubPublications(
            data.getWithDefault('include_sub_publications'))
        settings.setLastVersion(
            data.getWithDefault('export_newest_version_only'))

        exporter = getUtility(IContentExporterRegistry).get(
            form.context, data.getWithDefault('export_format'))
        filename = '%s_export_%s.%s' % (
            form.context.id,
            datetime.now().strftime("%Y-%m-%d"),
            exporter.extension)
        output = exporter.export(settings)

        content_type, content_encoding = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'
        response = form.request.response
        response.setHeader('Content-Type', content_type)
        if content_encoding:
            response.setHeader('Content-Encoding', content_encoding)
        response.setHeader(
            'Content-Disposition', 'attachment;filename=%s' % filename)
        raise ContentException(output)


class ExportForm(silvaforms.SMIForm):
    """Export form for containers.
    """
    grok.adapts(Container, IContainer)
    grok.require('silva.ManageSilvaContentSettings')
    grok.name('export')

    label = _(u"Export")

    fields = silvaforms.Fields(IExportFields)
    fields['export_format'].mode = 'radio'
    fields['export_format'].defaultValue = default_format
    actions = silvaforms.Actions(silvaforms.CancelAction(), ExportAction())

    postOnly = False
    ignoreContent=True
    ignoreRequest=False


class ExportMenu(MenuItem):
    grok.adapts(ContainerMenu, IContainer)
    grok.order(81)
    grok.require('silva.ManageSilvaContentSettings')

    name = _(u'Export')
    screen = ExportForm


