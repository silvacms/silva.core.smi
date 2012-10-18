# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer
from Products.Silva.ftesting import smi_settings


class ReaderRootTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_root_roundtrip(self):
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
        self.assertEqual(browser.inspect.tabs['Content'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])


class AuthorRootTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'

    def test_root_roundtrip(self):
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
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Content'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])

    def test_root_settings(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('author')

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertNotIn({'title': u'Container type'}, browser.inspect.form)


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
