# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.testing import FunctionalLayer, smi_settings


class ReaderFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_folder_access(self):
        """A reader cannot create a folder, however he can look into it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('reader')


class AuthorFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_folder(self):
        """Create a folder and check its tabs.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('author')

        self.assertTrue('add' in browser.inspect.content_tabs)
        browser.inspect.content_tabs['add'].click()
        self.assertTrue('silva folder' in browser.inspect.content_subtabs)
        self.assertEqual(browser.inspect.content_subtabs['silva folder'].click(), 200)

        form = browser.get_form('addform')
        form.get_control('addform.field.id').value = 'folder'
        form.get_control('addform.field.title').value = 'Test Folder'

        self.assertEqual(browser.inspect.form_controls, ['Cancel', 'Save'])
        self.assertEqual(browser.inspect.form_controls['Save'].click(), 200)
        self.assertEqual(browser.inspect.feedback, [u"Added Silva Folder."])

        self.assertEqual(browser.inspect.content_title, [u"Test Folder"])
        self.assertEqual(browser.inspect.content_tabs, ['Content', 'Add', 'Properties'])
        self.assertEqual(browser.inspect.content_views, ['Preview', 'View'])

        # We are on contents
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.content_views['preview'].click(), 200)
        self.assertEqual(browser.inspect.content_activeviews, ['Preview'])
        self.assertEqual(browser.inspect.content_tabs['properties'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Properties'])
        self.assertEqual(browser.inspect.content_tabs['content'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])

        browser.inspect.content_parent[0].click()
        self.assertEqual(browser.inspect.content_title, [u"root"])
        # XXX Delete


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderFolderTestCase))
    suite.addTest(unittest.makeSuite(AuthorFolderTestCase))
    return suite
