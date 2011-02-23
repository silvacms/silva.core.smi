from five import grok
from zope.interface import Interface

from zeam.form.ztk.fields import SchemaField, SchemaFieldWidget
from zeam.form.ztk.fields import registerSchemaField

from silva.core.smi import interfaces
from silva.core.conf import schema as silvaschema


class CropSchemaField(SchemaField):
    """ Field to set cropping of image
    """


class CropImageInputWidget(SchemaFieldWidget):
    grok.adapts(CropSchemaField, interfaces.IImageForm, Interface)
    grok.name(u'input')

    def originalImageURL(self):
        return self.form.url(self.form.context)

    def valueToUnicode(self, value):
        return unicode(value)


def register():
    registerSchemaField(CropSchemaField, silvaschema.ICropCoordinates)


