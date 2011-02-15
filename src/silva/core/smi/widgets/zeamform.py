from five import grok

from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.schema import TextLine
from zope.schema.interfaces import ITextLine

from zeam.form.base.markers import DISPLAY
from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField
from silva.core.views.interfaces import ISilvaURL


class IPublicationStatus(ITextLine):
    """ interface for publication status field
    """


class PublicationStatus(TextLine):
    grok.implements(IPublicationStatus)
    """ A simple text line representing publication status
    """


class PublicationStatusSchemaField(SchemaField):
    """Publication status field.
    """


class PublicationStatusDisplayWidget(SchemaFieldWidget):
    grok.adapts(PublicationStatusSchemaField, Interface, Interface)
    grok.name(str(DISPLAY))

    def targetURL(self):
        version = self.form.getContent().context
        return getMultiAdapter(
            (version, self.request), ISilvaURL).preview()

    def htmlClass(self):
        return super(PublicationStatusDisplayWidget, self).htmlClass() + ' ' +\
            self.statusHtmlClass()

    def statusHtmlClass(self):
        version_status = self.inputValue()
        return ((version_status == 'unapproved' and 'draft') or
                (version_status == 'last_closed' and 'closed') or
                version_status)

    def valueToUnicode(self, value):
        return unicode(value)


def register():
    registerSchemaField(PublicationStatusSchemaField, IPublicationStatus)


