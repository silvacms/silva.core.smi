# coding=utf-8

from five import grok
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import Interface
from zope import schema

from zeam.form import silva as silvaforms

from silva.core import interfaces as silvainterfaces
from silva.core.smi import interfaces
from silva.core.conf import schema as silvaschema
from silva.translations import translate as _

from Products.Silva.Image import IImageAddFields


class ImageEditTab(silvaforms.SMIComposedForm):
    """ Edit tab
    """
    grok.context(silvainterfaces.IImage)
    grok.name('silva.ui.content')
    grok.require('silva.ChangeSilvaContent')

    label = _('edit')


class ImageEditForm(silvaforms.SMISubForm):
    """ Edit image attributes
    """
    grok.context(silvainterfaces.IImage)
    grok.view(ImageEditTab)
    grok.order(10)

    dataManager = silvaforms.SilvaDataManager
    ignoreContent = False

    label = _('characterization')

    fields = silvaforms.Fields(IImageAddFields).omit('id')
    # XXX: image field is no longer required so it does nothing
    # when image is not specified.

    #fields['image'].required = False
    #fields['image'].ignoreContent = True

    actions  = silvaforms.Actions(silvaforms.EditAction(), silvaforms.CancelEditAction())

image_formats = SimpleVocabulary([SimpleTerm(title=u'jpg', value='JPEG'),
                                  SimpleTerm(title=u'png', value='PNG'),
                                  SimpleTerm(title=u'gif', value='GIF')])


class IFormatAndScalingFields(Interface):
    web_format = schema.Choice(
        source=image_formats,
        title=_(u"web format"),
        description=_(u"Image format for web."))
    web_scale = schema.TextLine(
        title=_(u"scaling"),
        description=_(u'Image scaling for web: use width x  '
                      u'height in pixels, or one axis length, ',
                      u'or a percentage (100x200, 100x*, *x200, 40%).'),
        required=False)
    web_crop = silvaschema.CropCoordinates(
        title=_(u"cropping"),
        description=_(u"Image cropping for web: use the"
                      u" ‘set crop coordinates’ "
                      u"button, or enter X1xY1-X2xY2"
                      u" to define the cropping box."),
        required=False)


class FormatAndScalingForm(silvaforms.SMISubForm):
    """ form to resize / change format of image.
    """
    grok.context(silvainterfaces.IImage)
    grok.implements(interfaces.IImageForm)
    grok.view(ImageEditTab)
    grok.order(20)

    ignoreContent = False
    dataManager = silvaforms.SilvaDataManager

    label = _('format and scaling')
    fields = silvaforms.Fields(IFormatAndScalingFields)
    fields['web_format'].mode = 'radio'
    fields['web_scale'].defaultValue = '100%'

    @silvaforms.action(title=_('change'),
        identifier=_('set_properties'))
    def set_properties(self):
        data, errors = self.extractData()
        if errors:
            return silvaforms.FAILURE
        try:
            self.context.set_web_presentation_properties(
                data.getWithDefault('web_format'),
                data.getWithDefault('web_scale'),
                data.getWithDefault('web_crop'))
        except ValueError as e:
            self.send_message(unicode(e), type='error')
        else:
            self.send_message(_('Scaling and/or format changed.'),
                type='feedback')
        return silvaforms.SUCCESS
