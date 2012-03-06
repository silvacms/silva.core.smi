# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime
import mimetypes

from five import grok
from zope import schema
from zope.component import getAdapter, getAdapters
from zope.interface import Interface
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from silva.core.interfaces import IContainer
from silva.core.interfaces import IContentExporter, IDefaultContentExporter
from silva.core.smi.content.container import ContainerMenu, Container
from silva.translations import translate as _
from silva.ui.menu import MenuItem
from silva.ui.rest import RESTResult
from zeam.form import silva as silvaforms
from zeam.form.ztk.interfaces import ISourceFactory

from zExceptions import BadRequest


@grok.provider(ISourceFactory)
def exporters_vocabulary(form):
    """List available exporter (this works only with Zeam form).
    """
    terms = []
    for token, adapter in form.exporters:
        terms.append(SimpleTerm(value=token, title=adapter.name))
    return SimpleVocabulary(terms)

def default_format(form):
    if len(form.exporters):
        return form.exporters[0][0]
    return None


class IExportFields(Interface):
    export_format = schema.Choice(
        source=exporters_vocabulary,
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

        options = {}
        for key in data:
            options[key] = data.getWithDefault(key)

        exporter = getAdapter(
            form.context, IContentExporter, name=options['export_format'])
        filename = '%s_export_%s.%s' % (
            form.context.id,
            datetime.now().strftime("%Y-%m-%d"),
            exporter.extension)
        output = exporter.export(**options)

        def payload(rest):
            content_type, content_encoding = mimetypes.guess_type(filename)
            if not content_type:
                content_type = 'application/octet-stream'
            response = rest.response
            response.setHeader('Content-Type', content_type)
            if content_encoding:
                response.setHeader('Content-Encoding', content_encoding)
            response.setHeader(
                'Content-Disposition', 'attachment;filename=%s' % filename)
            return output

        raise RESTResult(payload)


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

    def update(self):
        exporters = []
        default = None
        options = silvaforms.Fields()
        for adapter in getAdapters((self.context,), IContentExporter):
            if IDefaultContentExporter.providedBy(adapter[1]):
                assert default is None, \
                    "There are two defaults content exporter"
                default = adapter
            else:
                exporters.append(adapter)
            options.extend(adapter[1].options)
        self.exporters = [default,] + exporters
        self.fields += options


class ExportMenu(MenuItem):
    grok.adapts(ContainerMenu, IContainer)
    grok.order(81)
    grok.require('silva.ManageSilvaContentSettings')

    name = _(u'Export')
    screen = ExportForm


