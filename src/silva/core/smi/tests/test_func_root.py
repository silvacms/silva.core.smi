# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


class ReaderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_root(self):
        """A reader can't add anything.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('reader')

        browser.open('/root/edit')
        self.assertEqual(browser.inspect.content_tabs, ['Content'])
        self.assertEqual(browser.inspect.content_views, ['Preview', 'View'])

        # We are on contents
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.content_views['preview'].click(), 200)
        self.assertEqual(browser.inspect.content_activeviews, ['Preview'])
        self.assertEqual(browser.inspect.content_tabs['content'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])


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

        # We are on contents
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.content_views['preview'].click(), 200)
        self.assertEqual(browser.inspect.content_activeviews, ['Preview'])
        self.assertEqual(browser.inspect.content_tabs['content'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])
        self.assertEqual(browser.inspect.content_tabs['properties'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Properties'])


class EditorTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_root(self):
        """An editor can edit stuff.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('editor')

        browser.open('/root/edit')
        self.assertEqual(browser.inspect.content_tabs, ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.content_views, ['Preview', 'View'])

        # We are on contents
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.content_views['preview'].click(), 200)
        self.assertEqual(browser.inspect.content_activeviews, ['Preview'])
        self.assertEqual(browser.inspect.content_tabs['content'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])
        self.assertEqual(browser.inspect.content_tabs['properties'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Properties'])

        # XXX Settings.
        # An editor can change the skin.

class ChiefEditorTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_root(self):
        """A Chief editor can edit and do some configuration.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('chiefeditor')

        browser.open('/root/edit')
        self.assertEqual(browser.inspect.content_tabs, ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.content_views, ['Preview', 'View'])

        # We are on contents
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.content_views['preview'].click(), 200)
        self.assertEqual(browser.inspect.content_activeviews, ['Preview'])
        self.assertEqual(browser.inspect.content_tabs['content'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])
        self.assertEqual(browser.inspect.content_tabs['properties'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Properties'])

        # XXX Settings.

class ManagerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def test_root(self):
        """A Manager have full access.
        """
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login('chiefeditor')

        browser.open('/root/edit')
        self.assertEqual(browser.inspect.content_tabs, ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.content_views, ['Preview', 'View'])

        # We are on contents
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])

        # We go through the tabs
        self.assertEqual(browser.inspect.content_views['preview'].click(), 200)
        self.assertEqual(browser.inspect.content_activeviews, ['Preview'])
        self.assertEqual(browser.inspect.content_tabs['content'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Content'])
        self.assertEqual(browser.inspect.content_tabs['properties'].click(), 200)
        self.assertEqual(browser.inspect.content_activetabs, ['Properties'])

        # XXX Settings.

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderTestCase))
    suite.addTest(unittest.makeSuite(AuthorTestCase))
    suite.addTest(unittest.makeSuite(EditorTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorTestCase))
    return suite
