# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager
from five import grok
from zope.component import getUtility
from zope.traversing.browser import absoluteURL

from silva.core.interfaces import ISilvaObject
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import BrokenReferenceError
from silva.ui.rest.errors import ErrorREST
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import ICancelerAction


class BreakReferencePermission(grok.Permission):
    grok.name('silva.breakreference')
    grok.title('Break silva references')


class BrokenReferenceErrorPage(ErrorREST):
    """ Page to render broken references errors.

    Redirects to the break references form if the user has the necessary rights
    to break references.
    """
    grok.context(BrokenReferenceError)

    title = _('Broken references')

    def update(self):
        allowed_to_break = getSecurityManager().checkPermission(
            'Break silva references', self.context)

        #if allowed_to_break:
        #    url = absoluteURL(self.context.error.reference.target, self.request)
        #    url += '/edit/tab_reference_error?'
        #    self.redirect(url)
        #    return

        source = self.context.error.reference.source
        self.source_url = absoluteURL(source, self.request)
        self.source_path = "/".join(source.getPhysicalPath())
        self.source_title = source.get_title_or_id()


class BreakReferencesForm(silvaforms.SMIForm):
    """ Form for breaking references
    """
    grok.require(BreakReferencePermission)
    grok.context(ISilvaObject)
    grok.name('tab_reference_error')
    grok.template('break_references')

    label = _(u"Break references?")

    def update(self):
        service = getUtility(IReferenceService)
        self.references = service.get_references_to(self.context)

    def next_url(self):
        data, errors = self.extractData()
        self.redirect(data['redirect_to'] or self.url(name="edit"))

    @silvaforms.action(
        _(u'cancel'),
        implements=ICancelerAction)
    def cancel(self):
        self.next_url()

    @silvaforms.action(
        _(u'break references'))
    def break_references(self):
        for reference in list(self.references):
            reference.set_target_id(0)
        self.send_message(_("References to %s have been broken.") %
                          "/".join(self.context.getPhysicalPath()))
        self.next_url()
