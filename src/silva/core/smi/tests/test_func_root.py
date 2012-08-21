# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


class ReaderRootTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_root(self):
        """A reader can't add anything.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('reader')

        browser.open('/root/edit')
        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(browser.inspect.tabs, ['Content'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])

        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Content'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])


class AuthorRootTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'

    def test_root(self):
        """Test root as an author.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('author')

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.views,
            ['Preview', 'View'])

        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Content'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])


class EditorRootTestCase(AuthorRootTestCase):
    layer = FunctionalLayer
    user = 'editor'


class ChiefEditorRootTestCase(EditorRootTestCase):
    layer = FunctionalLayer
    user = 'chiefeditor'


class ManagerRootTestCase(ChiefEditorRootTestCase):
    layer = FunctionalLayer
    manager = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderRootTestCase))
    suite.addTest(unittest.makeSuite(AuthorRootTestCase))
    suite.addTest(unittest.makeSuite(EditorRootTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorRootTestCase))
    suite.addTest(unittest.makeSuite(ManagerRootTestCase))
    return suite
