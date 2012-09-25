# -*- coding: utf-8 -*-
# Copyright (c) 2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings


class ReaderAutoTOCTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addAutoTOC('contents', 'Table of Content')

    def test_autotoc_access(self):
        """A reader cannot create an autotoc, however he look at it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('reader')
        self.assertEqual(browser.inspect.title, u'root')

        # We should see our auto toc.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Table of Content',
              'identifier': 'contents',
              'author': 'editor'}])
        # Select it.
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(browser.inspect.actions, ['Copy'])
        self.assertEqual(browser.inspect.listing[0].goto_dropdown.click(), 200)
        self.assertEqual(browser.inspect.listing[0].goto_actions, ['Preview'])

        # Go on it. We arrive on the edit tab, where we cannot do a thing.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Table of Content')
        self.assertEqual(browser.inspect.actions, [])
        self.assertEqual(browser.inspect.tabs, ['Edit'])
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        self.assertEqual(browser.inspect.form, ['Edit a Silva AutoTOC'])
        edit_form = browser.inspect.form['Edit a Silva AutoTOC']
        self.assertEqual(edit_form.form.inspect.fields, [])
        self.assertEqual(edit_form.actions, ['Back'])

        # We go through the tabs.
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Edit'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])


class AuthorAutoTOCTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    access = False

    def test_autotoc_roundtrip(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].click(), 200)
        self.assertIn('Silva AutoTOC', browser.inspect.subtabs)
        self.assertEqual(browser.inspect.subtabs['Silva AutoTOC'].click(), 200)
        self.assertEqual(browser.inspect.form, ["Add a Silva AutoTOC"])

        add_form = browser.inspect.form['Add a Silva AutoTOC']
        add_form.form.inspect.fields['id'].value = 'contents'
        add_form.form.inspect.fields['title'].value = u'Table des matières'
        self.assertEqual(add_form.actions, ['Cancel', 'Save'])
        self.assertEqual(add_form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva AutoTOC.")

        # Inspect new created content.
        self.assertEqual(browser.inspect.title, u'Table des matières')
        self.assertEqual(
            browser.inspect.tabs,
            ['Edit', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.views,
            ['Preview', 'View'])
        # We are on contents
        self.assertEqual(
            browser.inspect.activetabs,
            ['Edit'])

        self.assertEqual(browser.inspect.form, ['Edit a Silva AutoTOC'])
        edit_form = browser.inspect.form['Edit a Silva AutoTOC']
        self.assertNotEqual(edit_form.form.inspect.fields, [])
        self.assertEqual(edit_form.actions, ['Back', 'Save changes'])
        self.assertIn('Depth', edit_form.form.inspect.fields)
        edit_form.form.inspect.fields['Depth'].value = '10'
        self.assertEqual(edit_form.actions['Save changes'].click(), 200)
        browser.macros.assertFeedback('Changes saved.')

        # We go through the tabs.
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Edit'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        # Go up a level.
        self.assertEqual(browser.inspect.parent.click(), 200)
        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # We should see our auto toc
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Table des matières',
              'identifier': 'contents',
              'author': self.user}])
        # Select it
        self.assertEqual(
            browser.inspect.listing[0].identifier.click(),
            200)
        self.assertEqual(
            browser.inspect.actions,
            ['Cut', 'Copy', 'Delete', 'Rename'])
        self.assertEqual(
            browser.inspect.listing[0].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[0].goto_actions,
            ['Preview', 'Properties'])

        # Delete the autotoc
        self.assertEqual(
            browser.inspect.actions['Delete'].click(),
            200)
        # Content is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Table des matières', 'identifier': 'contents'}])
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
        browser.macros.assertFeedback(u'Deleted "Table des matières".')


class EditorAutoTOCTestCase(AuthorAutoTOCTestCase):
    user = 'editor'


class ChiefEditorAutoTOCTestCase(EditorAutoTOCTestCase):
    user = 'chiefeditor'


class ManagerAutoTOCTestCase(ChiefEditorAutoTOCTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderAutoTOCTestCase))
    suite.addTest(unittest.makeSuite(AuthorAutoTOCTestCase))
    suite.addTest(unittest.makeSuite(EditorAutoTOCTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorAutoTOCTestCase))
    suite.addTest(unittest.makeSuite(ManagerAutoTOCTestCase))
    return suite
