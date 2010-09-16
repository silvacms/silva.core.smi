# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from urllib import urlencode

from AccessControl import getSecurityManager
from five import grok
from zope.component import getUtility
from zope.traversing.browser import absoluteURL

from infrae.layout import layout
from silva.core.interfaces import ISilvaObject
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import BrokenReferenceError
from silva.core.smi.simple import ISimpleSMILayout
from silva.core.smi.interfaces import ISMILayer
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.base import Fields, Field


class BreakReferencePermission(grok.Permission):
    grok.name('perm.breakreference')
    grok.title('Break silva references')


grok.layer(ISMILayer)


class BrokenReferenceErrorPage(silvaviews.Page):
    """ Page to render broken references errors.

    It redirects to break references form if the user as the necessary rights to
    break references.
    """
    grok.context(BrokenReferenceError)
    grok.name('error.html')
    grok.template('error')

    tab_name = 'tab_edit'

    def update(self):
        allowed_to_break = getSecurityManager().checkPermission(
            'Break silva references', self.context)

        if allowed_to_break:
            url = absoluteURL(self.context.error.reference.target, self.request)
            url += '/edit/tab_reference_error?'
            url += urlencode(
                {'form.field.redirect_to': self.url(name="edit")})
            self.redirect(url)
            return

        source = self.context.error.reference.source
        self.source_url = absoluteURL(source, self.request)
        self.source_path = "/".join(source.getPhysicalPath())
        self.source_title = source.get_title_or_id()
        self.next_url = self.url(name="edit")


class RedirectField(Field):
    ignoreRequest = False
    ignoreContent = True
    mode = u'hidden'


class BreakReferencesForm(silvaforms.SMIForm):
    """ Form for breaking references
    """
    grok.require(BreakReferencePermission)
    grok.context(ISilvaObject)
    grok.name('tab_reference_error')
    grok.template('break_references')
    layout(ISimpleSMILayout)

    label = _(u"Break references")
    fields = Fields(RedirectField('redirect_to'))

    def update(self):
        service = getUtility(IReferenceService)
        self.references = service.get_references_to(self.context)

    @silvaforms.action(u'break references')
    def break_references(self):
        for reference in self.references:
            reference.set_target_id(0)
        self.send_message(_("References to %s have been broken.") %
                          "/".join(self.context.getPhysicalPath()))
        self.next_url()

    @silvaforms.action(u'cancel')
    def cancel(self):
        self.next_url()

    def next_url(self):
        data, errors = self.extractData()
        self.redirect(data['redirect_to'] or self.url(name="edit"))
