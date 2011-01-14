import urllib
from datetime import datetime

from five import grok

from zope.interface import Interface
from zope import schema, component
from zope.schema.interfaces import IContextSourceBinder

from zeam.form import silva as silvaforms
from silva.core.interfaces import ISilvaObject
from silva.translations import translate as _
from silva.core.views import views as silvaviews

from silva.core.smi import interfaces
from Products.Silva.utility.interfaces import IExportUtility
from Products.Silva.silvaxml import xmlexport
from zExceptions import BadRequest

@grok.provider(IContextSourceBinder)
def export_formats(context):
    utility = component.getUtility(IExportUtility)
    return utility.listContentExporter(context)


def default_format(form):
    exporters = component.getUtility(IExportUtility).\
        listContentExporter(form.context)
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


class ExportTab(silvaforms.SMIForm):
    """Export form for containers.
    """
    grok.name('tab_status_export')
    grok.implements(interfaces.IPublishTab)
    grok.context(ISilvaObject)
    grok.require('silva.ReadSilvaContent')

    tab = 'publish'
    label = _(u"export")

    fields = silvaforms.Fields(IExportFields)
    fields['export_format'].mode = 'radio'
    fields['export_format'].defaultValue = default_format

    postOnly = False
    ignoreContent=True
    ignoreRequest=False

    @silvaforms.action(title=_(u"export"),
        description=_(u"access key: alt-z"),
        accesskey=u"z")
    def export(self):
        data, errors = self.extractData()
        if len(errors) == 0:
            url = self.url() + '/edit/tab_status_export/download'
            query_string = "?" + urllib.urlencode(self.request.form)
            self.redirect(url + query_string)
            return silvaforms.SUCCESS
        return silvaforms.FAILURE

    def publishTraverse(self, request, name):
        if name == 'download':
            return ExportDownload(self, request)


class ExportDownload(silvaviews.View):
    grok.context(ExportTab)
    grok.require('silva.ReadSilvaContent')
    grok.name('download')

    def update(self):
        form = self.context
        data, errors = form.extractData()
        if len(errors) > 0:
            raise BadRequest('invalid export parameters')
        settings = xmlexport.ExportSettings()
        settings.setWithSubPublications(
            data.getWithDefault('include_sub_publications'))
        settings.setLastVersion(
            data.getWithDefault('export_newest_version_only'))

        utility = component.getUtility(IExportUtility)
        exporter = utility.createContentExporter(
            form.context, data.getWithDefault('export_format'))
        self.filename = '%s_export_%s.%s' % (
            form.context.id,
            datetime.now().strftime("%Y-%m-%d"),
            exporter.extension)
        self.output = exporter.export(settings)

    def render(self):
        response = self.request.response
        response.setHeader('Content-Type', 'application/octet-stream')
        response.setHeader(
            'Content-Disposition', 'attachment;filename=%s' % self.filename)
        return self.output


