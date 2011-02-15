from datetime import datetime
import unittest
from Products.Silva.testing import smi_settings, FunctionalLayer
from silva.core.interfaces import IPublicationWorkflow


def publish_settings(browser):
    smi_settings(browser)
    browser.inspect.add('request_approval_form',
        xpath='//form[@name="form.requestapprovalform"]')
    browser.inspect.add('withdrawal_form',
        xpath='//form[@name="form.withdrawapprovalrequestform"]')
    browser.inspect.add('rejection_form',
        xpath='//form[@name="form.rejectapprovalrequestform"]')
    browser.inspect.add('manual_close_form',
        xpath='//form[@name="form.manualcloseform"]')
    browser.inspect.add('version_checkboxes',
        css='input.form-publicationstatustableform-select', type='node')
    return browser


def fill_datetime(form, control_prefix, dt):
    mapping = {
        'day': lambda d: d.day,
        'month': lambda d: d.month,
        'year': lambda d: d.year,
        'hour': lambda d: d.hour,
        'min': lambda d: d.minute
    }

    for name, callback in mapping.items():
        control = form.get_control(".".join([control_prefix, name]))
        control.value = callback(dt)


class TestDocumentRequestApproval(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')

    def test_editor_should_not_see_request_approval_form(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertFalse(browser.inspect.request_approval_form)

    def test_author_should_see_request_approval_form(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertTrue(browser.inspect.request_approval_form)

    def test_request_approval_submit(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        form = browser.get_form('form.requestapprovalform')
        publication_datetime = datetime.now()
        fill_datetime(form,
            'form.requestapprovalform.field.publication_datetime',
            publication_datetime)
        button = \
            form.get_control('form.requestapprovalform.action.request-approval')
        self.assertEquals(200, button.click())
        self.assertEquals(['Approval requested.'],
            browser.inspect.feedback)

    def test_withdrawal_form_should_not_show(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertFalse(browser.inspect.withdrawal_form)


class TestDocumentPendingApproval(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        form = browser.get_form('form.requestapprovalform')
        self.assertTrue(form)
        publication_datetime = datetime.now()
        fill_datetime(form,
            'form.requestapprovalform.field.publication_datetime',
            publication_datetime)
        button = \
            form.get_control('form.requestapprovalform.action.request-approval')
        self.assertEquals(200, button.click())


class TestDocumentWithdraw(TestDocumentPendingApproval):

    def test_editor_should_not_see_withdraw_form(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertFalse(browser.inspect.withdrawal_form)

    def test_author_should_see_withdraw_form(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertTrue(browser.inspect.withdrawal_form)

    def test_withdrawal_form_submit(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        form = browser.get_form('form.withdrawapprovalrequestform')
        button = \
            form.get_control(
                'form.withdrawapprovalrequestform.action.withdraw')
        self.assertEquals(200, button.click())
        self.assertEquals(['Withdrew request for approval'],
            browser.inspect.feedback)
        self.assertFalse(browser.inspect.withdrawal_form)
        self.assertTrue(browser.inspect.request_approval_form)


class TestRejectRequest(TestDocumentPendingApproval):
    layer = FunctionalLayer

    def test_author_should_not_see_rejection_form(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertFalse(browser.inspect.rejection_form)

    def test_editor_should_see_rejection_form(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertTrue(browser.inspect.rejection_form)

    def test_reject_form_submit(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertTrue(browser.inspect.rejection_form)
        form = browser.get_form('form.rejectapprovalrequestform')
        button = form.get_control(
            'form.rejectapprovalrequestform.action.reject')
        self.assertEquals(200, button.click())
        self.assertFalse(browser.inspect.rejection_form)

        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertFalse(browser.inspect.rejection_form)
        self.assertTrue(browser.inspect.request_approval_form)


class TestManualClose(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')

    def test_no_public_version(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        self.assertFalse(browser.inspect.manual_close_form)

    def test_close_public_version(self):
        IPublicationWorkflow(self.root.document).approve()
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        self.assertTrue(browser.inspect.manual_close_form)
        form = browser.get_form('form.manualcloseform')
        button = form.get_control('form.manualcloseform.action.close')
        self.assertEquals(200, button.click())
        self.assertFalse(browser.inspect.manual_close_form)
        self.assertEquals(None, self.root.document.get_public_version())

    def test_author_does_not_see_form(self):
        IPublicationWorkflow(self.root.document).approve()
        browser = self.layer.get_browser(publish_settings)
        browser.login('author')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        self.assertFalse(browser.inspect.manual_close_form)


class TestVersionListing(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')

    def test_simple_copy_for_editing(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        form = browser.get_form('form.publicationstatustableform')
        self.assertEquals(0, int(self.root.document.get_editable().id))
        self.assertEquals(1, len(browser.inspect.version_checkboxes))
        form.get_control(
            'form.publicationstatustableform.line-0.select.0').checked = True
        status = form.get_control(
            'form.publicationstatustableform.action.copy').click()
        self.assertEquals(200, status)
        self.assertEquals(2, len(browser.inspect.version_checkboxes))
        self.assertEquals(1, int(self.root.document.get_editable().id))

    def test_delete_fail_if_alone(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        form = browser.get_form('form.publicationstatustableform')
        form.get_control(
            'form.publicationstatustableform.line-0.select.0').checked = True
        status = form.get_control(
            'form.publicationstatustableform.action.delete').click()
        self.assertEquals(200, status)
        self.assertEquals(1, len(browser.inspect.version_checkboxes))
        self.assertEquals(['Can not delete all versions'],
            browser.inspect.feedback)

    def test_delete_succeed_if_not_alone(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        form = browser.get_form('form.publicationstatustableform')
        form.get_control(
            'form.publicationstatustableform.line-0.select.0').checked = True
        status = form.get_control(
            'form.publicationstatustableform.action.copy').click()
        self.assertEquals(200, status)
        self.assertEquals(2, len(browser.inspect.version_checkboxes))
        form = browser.get_form('form.publicationstatustableform')
        form.get_control(
            'form.publicationstatustableform.line-0.select.0').checked = True
        status = form.get_control(
            'form.publicationstatustableform.action.delete').click()
        self.assertEquals(1, len(browser.inspect.version_checkboxes))
        self.assertEquals(['deleted 1'],
            browser.inspect.feedback)

    def test_cannot_delete_publish_version(self):
        browser = self.layer.get_browser(publish_settings)
        browser.login('editor')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        form = browser.get_form('form.publicationstatustableform')
        form.get_control(
            'form.publicationstatustableform.line-0.select.0').checked = True
        status = form.get_control(
            'form.publicationstatustableform.action.copy').click()
        self.assertEquals(200, status)
        self.assertEquals(2, len(browser.inspect.version_checkboxes))

        IPublicationWorkflow(self.root.document).approve()
        form.get_control(
            'form.publicationstatustableform.line-0.select.0').checked = True
        status = form.get_control(
            'form.publicationstatustableform.action.delete').click()
        self.assertEquals(2, len(browser.inspect.version_checkboxes))
        self.assertEquals(['could not delete 1: version is published'],
            browser.inspect.feedback)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocumentRequestApproval))
    suite.addTest(unittest.makeSuite(TestDocumentWithdraw))
    suite.addTest(unittest.makeSuite(TestRejectRequest))
    suite.addTest(unittest.makeSuite(TestManualClose))
    suite.addTest(unittest.makeSuite(TestVersionListing))
    return suite

