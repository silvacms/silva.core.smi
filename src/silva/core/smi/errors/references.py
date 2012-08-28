# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager
from five import grok
from zope.component import getUtility

from silva.ui.rest import UIREST
from silva.core.interfaces import ISilvaObject
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import BrokenReferenceError
from silva.translations import translate as _
from zope.traversing.browser import absoluteURL
from zeam.form import silva as silvaforms
from zeam.form.silva.interfaces import IDefaultAction


class BreakReferencePermission(grok.Permission):
    grok.name('silva.breakreference')
    grok.title('Break silva references')


class BreakReferencesForm(silvaforms.PopupForm):
    """ Form for breaking references
    """
    grok.context(BrokenReferenceError)
    grok.template('break_references')
    grok.name('error.html')

    label = _(u"Broken references")
    actions = silvaforms.Actions(
        silvaforms.CancelAction())

    def get_info(self, content):
        return {
            'title': content.get_title(),
            'path': self.get_content_path(content),
            'url': absoluteURL(content, self.request)}

    def update(self):
        self.content = self.context.error.args[0].target
        self.info = self.get_info(self.content)

    def referrers(self):
        service = getUtility(IReferenceService)
        return (self.get_info(reference.source)
                for reference in service.get_references_to(self.content))

    def allowed_to_break(self):
        return getSecurityManager().checkPermission(
            'Break silva references', self.context)

    def updateForm(self):
        # XXX Hack properties to get URL working
        self.__parent__ = self.context
        self.__name__ = 'error.html'
        # Force form url to our content form.
        result = super(BreakReferencesForm, self).updateForm()
        result['content']['submit_url'] = '/'.join(
            (absoluteURL(self.content, self.request),
             '++rest++silva.core.smi.breakreferences'))
        self.response.setStatus(400)
        return result

    @silvaforms.action(
        _(u'Break references'),
        available=allowed_to_break,
        implements=IDefaultAction)
    def break_references(self):
        # This is a fake action to create the action.
        pass


class BreakReferenceContentForm(UIREST):
    grok.context(ISilvaObject)
    grok.name('silva.core.smi.breakreferences')
    grok.require('silva.breakreference')

    def POST(self):
        service = getUtility(IReferenceService)
        for reference in list(service.get_references_to(self.context)):
            reference.set_target_id(0)
        return self.json_response({
                'content': {
                    'ifaces': ['message'],
                    'title': self.translate(_(u"References broken")),
                    'message': self.translate(
                        _(u"References to ${content} (${path}) have been broken.",
                          mapping={'content': self.context.get_title_or_id(),
                                   'path': self.get_content_path(self.context)}))
                    }})
