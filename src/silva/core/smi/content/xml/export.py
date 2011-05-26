# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime
import mimetypes
import urllib

from five import grok
from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder

from silva.core.interfaces import IContainer, IContentExporterRegistry
from silva.core.smi.content.container import ContainerMenu, Container
from silva.translations import translate as _
from silva.ui.menu import MenuItem
from silva.ui.rest import REST, RedirectToUrl
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
        title=_(u"include sub publications?"),
        description=_(u"Check to export all sub publications. "),
        default=False,
        required=False)

    export_newest_version_only = schema.Bool(
        title=_(u"export only newest versions?"),
        description=_(u"If not checked all versions are exported."),
        default=True,
        required=False)

    export_format = schema.Choice(
        source=export_formats,
        title=_(u"select an export format"),
        description=_(u"Select the format which will be used for the export."))


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
    actions = silvaforms.Actions(silvaforms.CancelAction())

    postOnly = False
    ignoreContent=True
    ignoreRequest=False

    @silvaforms.action(title=_(u"Export"),
        description=_(u"export as an zip archive"))
    def export(self):
        data, errors = self.extractData()
        if len(errors) == 0:
            url = self.url() + '/++rest++silva.ui/content/export/download'
            query_string = "?" + urllib.urlencode(self.request.form)
            raise RedirectToUrl(url + query_string)
        return silvaforms.FAILURE


class ExportMenu(MenuItem):
    grok.adapts(ContainerMenu, IContainer)
    grok.order(81)
    grok.require('silva.ManageSilvaContentSettings')

    name = _(u'Export')
    screen = ExportForm


class ExportDownload(REST):
    grok.adapts(ExportForm, IContainer)
    grok.require('silva.ManageSilvaContentSettings')
    grok.name('download')

    def update(self):
        form = self.__parent__
        data, errors = form.extractData()
        if len(errors) > 0:
            raise BadRequest('invalid export parameters')
        settings = xmlexport.ExportSettings()
        settings.setWithSubPublications(
            data.getWithDefault('include_sub_publications'))
        settings.setLastVersion(
            data.getWithDefault('export_newest_version_only'))

        exporter = getUtility(IContentExporterRegistry).get(
            self.context, data.getWithDefault('export_format'))
        self.filename = '%s_export_%s.%s' % (
            form.context.id,
            datetime.now().strftime("%Y-%m-%d"),
            exporter.extension)
        self.output = exporter.export(settings)

    def GET(self):
        self.update()
        content_type, content_encoding = mimetypes.guess_type(self.filename)
        if not content_type:
            content_type = 'application/octet-stream'
        response = self.request.response
        response.setHeader('Content-Type', content_type)
        if content_encoding:
            response.setHeader('Content-Encoding', content_encoding)
        response.setHeader(
            'Content-Disposition', 'attachment;filename=%s' % self.filename)
        return self.output


