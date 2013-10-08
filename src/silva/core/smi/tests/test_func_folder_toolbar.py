# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.ftesting import smi_settings
from Products.Silva.testing import FunctionalLayer, Transaction


class AuthorFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    toolbar = ['Request approval']

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_content_cut(self):
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')
            factory.manage_addMockupVersionedContent('document', 'Document')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(browser.inspect.title, 'root')

        # Select document
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Folder',
              'identifier': 'folder',
              'author': u'editor'},
             {'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])
        self.assertEqual(browser.inspect.toolbar, [])
        self.assertEqual(browser.inspect.listing[1].identifier.click(), 200)

        self.assertEqual(
            browser.inspect.toolbar,
            [u'Cut', u'Copy', u'Delete', u'Rename'] + self.toolbar)
        self.assertEqual(browser.inspect.toolbar['Cut'].click(), 200)
        browser.macros.assertFeedback('Cut 1 item(s) in the clipboard.')

        # Go in the folder and past the document.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, 'Folder')

        self.assertEqual(browser.inspect.toolbar, ['Paste'])
        self.assertEqual(browser.inspect.toolbar['Paste'].click(), 200)
        browser.macros.assertFeedback('Moved "Document".')

        # The document is now in the folder.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])

        # The document is gone from the root
        self.assertEqual(browser.inspect.parent.click(), 200)
        self.assertEqual(browser.inspect.title, 'root')
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Folder',
              'identifier': 'folder',
              'author': self.user}])

    def test_content_copy(self):
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(browser.inspect.title, 'root')

        # Select document
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])
        self.assertEqual(browser.inspect.toolbar, [])
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)

        self.assertEqual(
            browser.inspect.toolbar,
            [u'Cut', u'Copy', u'Delete', u'Rename'] + self.toolbar)
        self.assertEqual(browser.inspect.toolbar['Copy'].click(), 200)
        browser.macros.assertFeedback('Copied 1 item(s) in the clipboard.')

        self.assertEqual(
            browser.inspect.toolbar,
            [u'Cut', u'Copy', u'Paste', u'Delete', u'Rename'] + self.toolbar)
        self.assertEqual(browser.inspect.toolbar['Paste'].click(), 200)
        browser.macros.assertFeedback('Pasted as a copy "Document".')

        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'},
              {'title': u'Document',
               'identifier': 'copy_of_document',
               'author': self.user}])


class EditorFolderTestCase(AuthorFolderTestCase):
    user = 'editor'
    toolbar = ['Publish']


class ChiefEditorFolderTestCase(EditorFolderTestCase):
    user = 'chiefeditor'


class ManagerFolderTestCase(ChiefEditorFolderTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorFolderTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderTestCase))
    suite.addTest(unittest.makeSuite(ManagerFolderTestCase))
    return suite
