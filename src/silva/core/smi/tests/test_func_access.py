# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


class ReaderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')
        factory.manage_addLink('link', 'Link')

    def test_root(self):
        """A reader can't add anything.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('reader')

        browser.open('/root/edit')
        self.assertEqual(browser.inspect.content_tabs, ['Content'])
        self.assertEqual(browser.inspect.content_views, ['Preview', 'View'])

        browser.inspect.content_views['preview'].click()


class AuthorTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_root(self):
        """A reader can't add anything.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('author')

        browser.open('/root/edit')
        self.assertEqual(browser.inspect.content_tabs, ['Content', 'Add', 'Properties'])
        self.assertEqual(browser.inspect.content_views, ['Preview', 'View'])

        browser.inspect.content_views['preview'].click()


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderTestCase))
    suite.addTest(unittest.makeSuite(AuthorTestCase))
    return suite
