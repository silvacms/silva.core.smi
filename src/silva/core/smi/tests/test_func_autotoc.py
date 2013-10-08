# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import IAutoTOC
from zope.interface.verify import verifyObject

from Products.Silva.testing import FunctionalLayer, Transaction
from Products.Silva.ftesting import smi_settings


class ReaderAutoTOCTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with Transaction():
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
        self.assertEqual(browser.inspect.toolbar, ['Copy'])
        self.assertEqual(browser.inspect.listing[0].goto_dropdown.click(), 200)
        self.assertEqual(browser.inspect.listing[0].goto_actions, ['Preview'])

        # Go on it. We arrive on the edit tab, where we cannot do a thing.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Table of Content')
        self.assertEqual(browser.inspect.toolbar, [])
        self.assertEqual(browser.inspect.tabs, ['Edit', 'Preview'])
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        self.assertEqual(browser.inspect.views, ['View...'])
        self.assertEqual(browser.inspect.form, ['Edit a Silva AutoTOC'])
        edit_form = browser.inspect.form['Edit a Silva AutoTOC']
        self.assertEqual(edit_form.fields, [])
        self.assertEqual(edit_form.actions, ['Back'])

        # We go through the tabs.
        self.assertEqual(browser.inspect.tabs['Preview'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Edit'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])


class AuthorAutoTOCTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    access = False

    def setUp(self):
        self.root = self.layer.get_application()

    def test_autotoc_add_and_listing(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Preview', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn('Silva AutoTOC', browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva AutoTOC'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva AutoTOC"])
        self.assertEqual(browser.inspect.toolbar, [])

        add_form = browser.inspect.form['Add a Silva AutoTOC']
        add_form.fields['id'].value = 'contents'
        add_form.fields['title'].value = u'Table des matières'
        self.assertEqual(add_form.actions, ['Cancel', 'Save'])
        self.assertEqual(add_form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva AutoTOC.")
        # We should have now an AutoTOC with the id 'contents'
        self.assertTrue(verifyObject(IAutoTOC, self.root._getOb('contents', None)))

        # Inspect newly created content.
        self.assertEqual(browser.inspect.title, u'Table des matières')
        self.assertEqual(
            browser.inspect.tabs,
            ['Edit', 'Preview', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.views,
            ['View...'])
        # We are on contents
        self.assertEqual(
            browser.inspect.activetabs,
            ['Edit'])

        self.assertEqual(browser.inspect.form, ['Edit a Silva AutoTOC'])
        edit_form = browser.inspect.form['Edit a Silva AutoTOC']
        self.assertNotEqual(edit_form.fields, [])
        self.assertEqual(edit_form.actions, ['Back', 'Save changes'])
        self.assertIn('Depth', edit_form.fields)
        edit_form.fields['Depth'].value = '10'
        self.assertEqual(edit_form.actions['Save changes'].click(), 200)
        browser.macros.assertFeedback('Changes saved.')

        # No special actions in toolbar
        self.assertEqual(browser.inspect.toolbar, [])

        # We go through the tabs.
        self.assertEqual(browser.inspect.tabs['Preview'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Edit'].name.click(), 200)
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
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename'])
        self.assertEqual(
            browser.inspect.listing[0].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[0].goto_actions,
            ['Preview', 'Properties'])

        # Delete the autotoc
        self.assertEqual(browser.inspect.toolbar['Delete'].click(), 200)
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
        self.assertEqual(browser.inspect.listing, [])
        browser.macros.assertFeedback(u'Deleted "Table des matières".')
        self.assertIs(self.root._getOb('contents', None), None)


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
