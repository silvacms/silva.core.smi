from AccessControl import getSecurityManager
from five import grok
from silva.core.interfaces import ISilvaObject, IContainer
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import BrokenReferenceError
from silva.core.smi.interfaces import ISMILayer
from silva.core.views import views as silvaviews
from zeam.form import silva as silvaforms
from zope.traversing.browser import absoluteURL
from zope.component import getUtility
from infrae.layout import layout
from silva.core.smi.errors import ISimpleSMILayout


class BreakPerm(grok.Permission):
    grok.name('perm.breakreference')
    grok.title('Break silva references')


grok.layer(ISMILayer)
grok.templatedir('references_templates')


class BrokenReferenceErrorPage(silvaviews.Page):
    """ Page to render broken references errors.

    It redirects to break references form if the user as the necessary rights to
    break references.
    """
    grok.context(BrokenReferenceError)
    grok.name('error.html')
    grok.template('error')

    def update(self):
        allowed_to_break_refs = getSecurityManager().checkPermission(
            'Break silva references', self.context)

        if allowed_to_break_refs:
            self.response.redirect(
                absoluteURL(self.context, self.request) +
                '/edit/break_references')
            return


class BreakReferencesForm(silvaforms.SMIForm):
    """ Form for breaking references
    """
    grok.require(BreakPerm)
    grok.context(ISilvaObject)
    grok.name('break_references')
    grok.template('break_references')
    layout(ISimpleSMILayout)

    tab = None
    tab_name = u'tab_reference_error'

    def update(self):
        ref_service = getUtility(IReferenceService)
        self.references = ref_service.get_references_to(self.context)

    @silvaforms.action(u'break references')
    def break_references(self):
        for ref in self.references:
            ref.set_target(0)
        self._next_url()

    @silvaforms.action(u'cancel')
    def cancel(self):
        rcontext = self.context
        if IContainer.providedBy(self.context):
            rcontext = self.context.get_container()
        self.request.response.redirect(
            absoluteURL(rcontext, self.request) + '/edit'))

    def _next_url():
        pass

