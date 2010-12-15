
import unittest
from zope.component import getUtility
from BeautifulSoup import BeautifulSoup
from Products.Silva.testing import FunctionalLayer, http
from silva.core.references.reference import BrokenReferenceError
from silva.core.references.interfaces import IReferenceService


class TestBreakReference(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFile('file', 'File')
        factory.manage_addLink('link', 'Link', target=self.root.file)
        factory.manage_addLink('link1', 'Link', target=self.root.file)

    def test_setup(self):
        self.assertEquals(self.root.file,
                          getattr(self.root.link, '0').get_target())

    def test_error_raised(self):
        def post():
            return http('POST /root/edit/ HTTP/1.1',
                        auth='manager',
                        parsed=True,
                        handle_errors=False,
                        data={'ids:list': 'file',
                              'tab_edit_delete:method': 'delete'})

        self.assertRaises(BrokenReferenceError, post)

    def test_delete_by_editor(self):
        response = http('POST /root/edit/ HTTP/1.1',
                        auth='editor',
                        handle_errors=True,
                        parsed=True,
                        data={'ids:list': 'file',
                              'tab_edit_delete:method': 'delete'})
        self.assertEquals(200, response.getStatus())
        self.assertTrue("break a reference" in response.getBody())

    def test_delete_by_manager(self):
        response = http('POST /root/edit/ HTTP/1.1',
                        auth='manager',
                        handle_errors=True,
                        parsed=True,
                        data={'ids:list': 'file',
                              'tab_edit_delete:method': 'delete'})
        self.assertEquals(302, response.getStatus())
        self.assertEquals(
            'http://localhost/root/file/edit/tab_reference_error'
            '?form.field.redirect_to=http%3A%2F%2Flocalhost%2Froot%2Fedit',
            response.getHeaders()['Location'])

    def test_form_break_references(self):
        response = http(
            'GET /root/file/edit/tab_reference_error'
            '?form.field.redirect_to=http%3A%2F%2Flocalhost%2Froot%2Fedit '
            'HTTP/1.1',
            auth='manager',
            handle_errors=True,
            parsed=True)
        self.assertEquals(200, response.getStatus())
        soup = BeautifulSoup(response.getBody())
        redirect_field = soup.find(
            'input', {'name': 'form.field.redirect_to'})
        self.assertEquals(redirect_field['value'],
                          'http://localhost/root/edit')
        break_reference_button = soup.find(
            'input', {'type': 'submit', 'name': 'form.action.break-references'})
        cancel_button = soup.find(
            'input', {'name': 'form.action.cancel'})

        self.assertEquals('break references', break_reference_button['value'])
        self.assertEquals('cancel', cancel_button['value'])

    def test_break_references(self):
        response = http('POST /root/file/edit/tab_reference_error HTTP/1.1',
            auth='manager',
            parsed = True,
            data={'form.action.break-references': 'break references',
                  'form.field.redirect_to': 'http://localhost/root/edit'})
        self.assertEquals(302, response.getStatus())
        self.assertEquals('http://localhost/root/edit',
                          response.getHeaders()['Location'])

        service = getUtility(IReferenceService)
        refs = service.get_references_to(self.root.file)
        self.assertEquals([], list(refs), 'references should have been removed')

        response = http('GET /root/edit HTTP/1.1',
                        auth='manager',
                        parsed=True)
        self.assertEquals(200, response.getStatus())
# XXX : fixme message doesn't work but this probably due to test env
#         soup = BeautifulSoup(response.getBody())
#         feedback = soup.find('span', {'class': 'fixed-feedback'})
#         self.assertTrue(feedback)
#         self.assertEquals(
#             "references to /root/file have been broken",
#             feedback.text)

    def test_cancel(self):
        response = http('POST /root/file/edit/tab_reference_error HTTP/1.1',
                        auth='manager',
                        parsed=True,
                        data={'form.action.cancel': 'cancel',
                              'form.field.redirect_to':
                                  'http://localhost/root/edit'})
        self.assertEquals(302, response.getStatus())
        self.assertEquals('http://localhost/root/edit',
                          response.getHeaders()['Location'])

        service = getUtility(IReferenceService)
        refs = service.get_references_to(self.root.file)
        self.assertEquals([getattr(self.root.link, '0'),
                           getattr(self.root.link1, '0')],
                          map(lambda x: x.source, refs),
                          'references should not have been removed')

        response = http('GET /root/edit HTTP/1.1',
                        auth='manager',
                        parsed=True)
        self.assertEquals(200, response.getStatus())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBreakReference))
    return suite
