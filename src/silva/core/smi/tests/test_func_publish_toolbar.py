# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.ftesting import smi_settings
from Products.Silva.testing import FunctionalLayer, Transaction


class ToolbarPublicationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_editor_publish_and_new_version(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('editor')

        # Select document
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        # Editor only see a publish button (no version is waiting
        # approval by default)
        self.assertEqual(browser.inspect.toolbar, ['Publish'])
        self.assertEqual(browser.inspect.toolbar['Publish'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback('Version published.')

        # Now all the editor can do is create a new version
        self.assertEqual(browser.inspect.toolbar, ['New version'])
        self.assertEqual(browser.inspect.toolbar['New version'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback('New version created.')

        # After this you can publish this new version
        self.assertEqual(browser.inspect.toolbar, ['Publish'])

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
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        # Should have a button to request approval in the toolbar
        self.assertEqual(browser.inspect.toolbar, ['Request approval'])
        self.assertEqual(browser.inspect.toolbar['Request approval'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback(
            'Approval requested for immediate publication.')

        # Now all the author see in the toolbar is withdraw
        self.assertEqual(browser.inspect.toolbar, ['Withdraw request'])

        # Editor comes to publish the document
        browser.logout()
        browser.login('editor')

        # Select document
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'author'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Should have a button to publish or reject
        self.assertEqual(browser.inspect.toolbar, ['Publish', 'Reject request'])
        self.assertEqual(browser.inspect.toolbar['Publish'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback('Version published.')

        # Document is publish, the only next possible step is to
        # create a new version
        self.assertEqual(browser.inspect.toolbar, ['New version'])

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
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        # Should have a button to request approval in the toolbar
        self.assertEqual(browser.inspect.toolbar, ['Request approval'])
        self.assertEqual(browser.inspect.toolbar['Request approval'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback(
            'Approval requested for immediate publication.')

        # Now all the author see in the toolbar is withdraw
        self.assertEqual(browser.inspect.toolbar, ['Withdraw request'])
        self.assertEqual(browser.inspect.toolbar['Withdraw request'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback('Withdrew request for approval.')

        # All the author can do now is to ask again
        self.assertEqual(browser.inspect.toolbar, ['Request approval'])

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
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        # Should have a button to request approval in the toolbar
        self.assertEqual(browser.inspect.toolbar, ['Request approval'])
        self.assertEqual(browser.inspect.toolbar['Request approval'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback(
            'Approval requested for immediate publication.')

        # Editor comes to reject the document
        browser.logout()
        browser.login('editor')

        # Select document
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'author'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Should have a button to publish or reject
        self.assertEqual(browser.inspect.toolbar, ['Publish', 'Reject request'])
        self.assertEqual(browser.inspect.toolbar['Reject request'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        browser.macros.assertFeedback('Rejected request for approval.')

        # The editor can still choose to publish the document after
        self.assertEqual(browser.inspect.toolbar, ['Publish'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ToolbarPublicationTestCase))
    return suite
