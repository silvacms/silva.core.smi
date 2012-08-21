# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.testing import CatalogTransaction
from Products.Silva.testing import FunctionalLayer, smi_settings


class ReaderFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')

    def test_folder_access(self):
        """A reader cannot create a folder, however he can look into it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('reader')
        self.assertEqual(browser.inspect.title, u'root')
        self.assertEqual(browser.inspect.tabs, ['Content'])
        self.assertEqual(browser.inspect.activetabs, ['Content'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        self.assertEqual(browser.inspect.actions, [])

        # We should see our folder.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Folder', 'identifier': 'folder', 'author': 'editor'}])
        # Select the folder.
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(browser.inspect.actions, ['Copy'])

        # Go inside the folder.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Folder')
        self.assertEqual(browser.inspect.listing, [])


class AuthorFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    publisher = False

    def test_folder_roundtrip(self):
        """Create a folder check its tabs and actions and delete it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        browser.inspect.tabs['Add'].click()
        self.assertTrue('silva folder' in browser.inspect.subtabs)
        self.assertEqual(browser.inspect.subtabs['silva folder'].click(), 200)

        form = browser.get_form('addform')
        form.get_control('addform.field.id').value = 'folder'
        form.get_control('addform.field.title').value = 'Test'

        self.assertEqual(browser.inspect.form_controls, ['Cancel', 'Save'])
        self.assertEqual(browser.inspect.form_controls['Save'].click(), 200)
        self.assertEqual(browser.inspect.feedback, [u"Added Silva Folder."])

        self.assertEqual(browser.inspect.title, u"Test")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.views,
            ['Preview', 'View'])
        # We are on contents
        self.assertEqual(
            browser.inspect.activetabs,
            ['Content'])
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Test', 'identifier': 'index', 'author': self.user}])

        # We go through the tabs
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Content'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # Go up a level.
        self.assertEqual(browser.inspect.parent.click(), 200)
        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # We should see our folder.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Test', 'identifier': 'folder', 'author': self.user}])
        # Select the folder
        self.assertEqual(
            browser.inspect.listing[0].identifier.click(),
            200)
        self.assertEqual(
            browser.inspect.actions,
            ['Cut', 'Copy', 'Delete', 'Rename'] + (['Publish'] if self.publisher else []))

        # Delete the folder
        self.assertEqual(
            browser.inspect.actions['Delete'].click(),
            200)
        # Folder is yet deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Test', 'identifier': 'folder', 'author': self.user}])
        self.assertEqual(
            browser.inspect.dialog,
            [{'title': 'Confirm deletion'}])
        self.assertEqual(
            browser.inspect.dialog[0].buttons,
            ['Cancel', 'Continue'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons['Continue'].click(),
            200)
        self.assertEqual(
            browser.inspect.listing,
            [])
        self.assertIn(
            u'Deleted "Test".',
            browser.inspect.feedback)


class EditorFolderTestCase(AuthorFolderTestCase):
    user = 'editor'
    publisher = True

class ChiefEditorFolderTestCase(EditorFolderTestCase):
    user = 'chiefeditor'


class ManagerFolderTestCase(ChiefEditorFolderTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderFolderTestCase))
    suite.addTest(unittest.makeSuite(AuthorFolderTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderTestCase))
    suite.addTest(unittest.makeSuite(ManagerFolderTestCase))
    return suite
