# -*- coding: utf-8 -*-
# Copyright (c) 2008-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.ftesting import smi_settings
from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from silva.core.interfaces import IPublicationWorkflow


class PublicationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_author_request_approval_and_approve(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # An author should not see Publish new version form, but he
        # should see Request approval new version.
        self.assertEqual(
            browser.inspect.form,
            [u'Request approval for new version',
             u'Manage versions'])

        form = browser.inspect.form[u'Request approval for new version']
        self.assertEqual(form.actions, ['Request approval'])
        self.assertEqual(form.actions['Request approval'].click(), 200)
        browser.macros.assertFeedback(u"Approval requested.")

        browser.logout()
        browser.login('editor')
        # Select document (author change to author)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'author'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Access publish tab
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # An editor should see Publish new version, Reject approval
        # request, and Manage versions
        self.assertEqual(
            browser.inspect.form,
            [u'Publish new version',
             u'Reject approval request',
             u'Manage versions'])
        form = browser.inspect.form[u'Publish new version']
        self.assertEqual(form.actions, ['Approve for future', 'Publish now'])
        self.assertEqual(form.actions['Publish now'].click(), 200)
        browser.macros.assertFeedback(u"Version published.")

        # Now only those forms are available
        self.assertEqual(
            browser.inspect.form,
            [u'Manual close',
             u'Manage versions'])

        browser.logout()
        browser.login('author')
        # Select document (author change to author)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Access publish tab
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # Author should only see those forms
        self.assertEqual(
            browser.inspect.form,
            [u'Manage versions'])

    def test_author_request_approval_and_reject(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # An author should not see Publish new version form, but he
        # should see Request approval new version.
        self.assertEqual(
            browser.inspect.form,
            [u'Request approval for new version', u'Manage versions'])

        form = browser.inspect.form[u'Request approval for new version']
        self.assertEqual(form.actions, ['Request approval'])
        self.assertEqual(form.actions['Request approval'].click(), 200)
        browser.macros.assertFeedback(u"Approval requested.")

        browser.logout()
        browser.login('editor')
        # Select document (author change to author)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'author'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Access publish tab
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # An editor should see Publish new version, Reject approval
        # request, and Manage versions
        self.assertEqual(
            browser.inspect.form,
            [u'Publish new version',
             u'Reject approval request',
             u'Manage versions'])
        form = browser.inspect.form[u'Reject approval request']
        self.assertEqual(form.actions, ['Reject approval request'])
        self.assertEqual(form.actions['Reject approval request'].click(), 200)
        browser.macros.assertFeedback(u"Rejected request for approval.")

        # Now reject version form is no longer available
        self.assertEqual(
            browser.inspect.form,
            [u'Publish new version',
             u'Manage versions'])

    def test_author_request_approval_and_withdraw(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # An author should not see Publish new version form, but he
        # should see Request approval new version.
        self.assertEqual(
            browser.inspect.form,
            [u'Request approval for new version',
             u'Manage versions'])

        form = browser.inspect.form[u'Request approval for new version']
        self.assertEqual(form.actions, ['Request approval'])
        self.assertEqual(form.actions['Request approval'].click(), 200)
        browser.macros.assertFeedback(u"Approval requested.")

        # Request approval form should no longer be here.
        self.assertEqual(
            browser.inspect.form,
            [u'Withdraw approval request',
             u'Manage versions'])
        form = browser.inspect.form[u'Withdraw approval request']
        self.assertEqual(
            form.fields,
            ['Add message on withdrawal'])
        self.assertEqual(form.actions, ['Withdraw approval request'])
        self.assertEqual(form.actions['Withdraw approval request'].click(), 200)
        browser.macros.assertFeedback(u"Withdrew request for approval.")

    def test_editor_publish_and_manual_close(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # You can publish or manage versions
        self.assertEqual(
            browser.inspect.form,
            [u'Publish new version',
             u'Manage versions'])
        form = browser.inspect.form[u'Publish new version']
        self.assertEqual(form.actions, ['Approve for future', 'Publish now'])
        self.assertEqual(form.actions['Publish now'].click(), 200)
        browser.macros.assertFeedback(u"Version published.")

        # You can now manually close the version
        self.assertEqual(
            browser.inspect.form,
            [u'Manual close',
             u'Manage versions'])
        form = browser.inspect.form[u'Manual close']
        self.assertEqual(form.actions, ['Close published version'])
        self.assertEqual(form.actions['Close published version'].click(), 200)
        browser.macros.assertFeedback(u"Version closed.")

        # You can now republish the closed version, if you want.
        self.assertEqual(
            browser.inspect.form,
            [u'Publish closed version',
             u'Manage versions'])
        form = browser.inspect.form[u'Publish closed version']
        self.assertEqual(form.actions, ['Publish now'])
        self.assertEqual(form.actions['Publish now'].click(), 200)
        browser.macros.assertFeedback(u"Version published.")

        # And you end up in the same state than before
        self.assertEqual(
            browser.inspect.form,
            [u'Manual close',
             u'Manage versions'])


class ManageVersionTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

            # Create a couple of test versions
            IPublicationWorkflow(self.root.document).publish()
            IPublicationWorkflow(self.root.document).new_version()
            IPublicationWorkflow(self.root.document).publish()
            IPublicationWorkflow(self.root.document).new_version()
            IPublicationWorkflow(self.root.document).publish()

    def test_editor_copy_for_editing(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # You can publish or manage versions
        self.assertEqual(
            browser.inspect.form,
            [u'Manual close',
             u'Manage versions'])

        form = browser.inspect.form[u'Manage versions']
        self.assertEqual(
            form.actions,
            [u'Delete', u'Copy for editing', u'View', u'Compare'])
        self.assertEqual(len(form.fields), 4)
        self.assertEqual(form.actions['Copy for editing'].click(), 200)
        browser.macros.assertError(u"Please select one version to copy.")

        form = browser.inspect.form[u'Manage versions']
        form.fields['1'].checked = True
        self.assertEqual(form.actions['Copy for editing'].click(), 200)
        browser.macros.assertFeedback(u"Reverted to previous version.")

    def test_editor_view_previous_version(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # You can publish or manage versions
        self.assertEqual(
            browser.inspect.form,
            [u'Manual close',
             u'Manage versions'])

        form = browser.inspect.form[u'Manage versions']
        self.assertEqual(
            form.actions,
            [u'Delete', u'Copy for editing', u'View', u'Compare'])
        self.assertEqual(len(form.fields), 4)
        self.assertEqual(form.actions['View'].click(), 200)
        browser.macros.assertError(u"Please select one version to view it.")

        form = browser.inspect.form[u'Manage versions']
        form.fields['1'].checked = True
        self.assertEqual(form.actions['View'].click(), 200)

    def test_editor_delete_version(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # You can publish or manage versions
        self.assertEqual(
            browser.inspect.form,
            [u'Manual close',
             u'Manage versions'])

        form = browser.inspect.form[u'Manage versions']
        self.assertEqual(
            form.actions,
            [u'Delete', u'Copy for editing', u'View', u'Compare'])
        self.assertEqual(len(form.fields), 4)
        self.assertEqual(form.actions['Delete'].click(), 200)
        browser.macros.assertError(u"No version selected, nothing deleted.")

        form = browser.inspect.form[u'Manage versions']
        form.fields['1'].checked = True
        self.assertEqual(form.actions['Delete'].click(), 200)
        browser.macros.assertFeedback(u"Version(s) deleted.")

        form = browser.inspect.form[u'Manage versions']
        self.assertEqual(
            form.actions,
            [u'Delete', u'Copy for editing', u'View', u'Compare'])
        self.assertEqual(len(form.fields), 3)
        self.assertNotIn('1', form.fields)
        form.fields['0'].checked = True
        form.fields['2'].checked = True
        self.assertEqual(form.actions['Delete'].click(), 200)
        browser.macros.assertError(u"Cannot delete all versions.")

    def test_author_do_not_delete_version(self):
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
        self.assertTrue('Publish' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Publish'].name.click(), 200)

        # You can publish or manage versions
        self.assertEqual(
            browser.inspect.form,
            [u'Manage versions'])

        form = browser.inspect.form[u'Manage versions']
        self.assertEqual(
            form.actions,
            [u'Copy for editing', u'View', u'Compare'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PublicationTestCase))
    suite.addTest(unittest.makeSuite(ManageVersionTestCase))
    return suite


