# -*- coding: utf-8 -*-
# Copyright (c) 2008-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime
import unittest

from Products.Silva.ftesting import smi_settings
from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from silva.core.interfaces import IPublicationWorkflow


class TestDocumentRequestApproval(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_editor_available_default_forms(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('editor')

        # Select document
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Access publish tab
        self.assertTrue('publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['publish'].click(), 200)

        # An editor should not sheee the request approval form
        self.assertEqual(
            browser.inspect.form,
            [u'Publish new version', u'Manage versions'])

    def test_author_request_approval_form(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('author')

        # Select document
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Access publish tab
        self.assertTrue('publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['publish'].click(), 200)

        # An author should not see Publish new version form, but he
        # should see Request approval new version.
        self.assertEqual(
            browser.inspect.form,
            [u'Request approval for new version', u'Manage versions'])

        form = browser.inspect.form[u'Request approval for new version']
        self.assertEqual(
            form.form.inspect.fields,
            [])

        self.assertFalse(browser.inspect.request_approval_form)
        form = browser.get_form('form.requestapprovalform')
        browser.macros.set_datetime(
            form,
            'form.requestapprovalform.field.publication_datetime',
            datetime.now())

        button = form.get_control('form.requestapprovalform.action.request-approval')
        self.assertEquals(200, button.click())
        self.assertEquals(['Approval requested.'],
            browser.inspect.feedback)


class TestDocumentPendingApproval(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('document', 'Document')

    def test_pending(self):
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
        browser.login('editor')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertFalse(browser.inspect.withdrawal_form)

    def test_author_should_see_withdraw_form(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertTrue(browser.inspect.withdrawal_form)

    def test_withdrawal_form_submit(self):
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
        browser.login('author')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertFalse(browser.inspect.rejection_form)

    def test_editor_should_see_rejection_form(self):
        browser = self.layer.get_browser(smi_settings)
        browser.login('editor')
        self.assertEquals(200,
            browser.open('http://localhost/root/document/edit/tab_status'))
        self.assertTrue(browser.inspect.rejection_form)

    def test_reject_form_submit(self):
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
        browser.login('editor')
        status = browser.open('http://localhost/root/document/edit/tab_status')
        self.assertEquals(200, status)
        self.assertFalse(browser.inspect.manual_close_form)

    def test_close_public_version(self):
        IPublicationWorkflow(self.root.document).approve()
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
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
        browser = self.layer.get_browser(smi_settings)
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
    return suite
    suite.addTest(unittest.makeSuite(TestDocumentWithdraw))
    suite.addTest(unittest.makeSuite(TestRejectRequest))
    suite.addTest(unittest.makeSuite(TestManualClose))
    suite.addTest(unittest.makeSuite(TestVersionListing))


