# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings


class ReaderIndexerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addIndexer('indexer', 'Indexer')

    def test_indexer_access(self):
        """A reader cannot create an indexer, however he look at it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('reader')
        self.assertEqual(browser.inspect.title, u'root')

        # We should see our indexer
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Indexer',
              'identifier': 'indexer',
              'author': 'editor'}])
        # Select it.
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(browser.inspect.actions, ['Copy'])
        self.assertEqual(browser.inspect.listing[0].goto_dropdown.click(), 200)
        self.assertEqual(browser.inspect.listing[0].goto_actions, ['Preview'])

        # Go on it. We arrive on the edit tab, where we cannot do a thing.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Indexer')
        self.assertEqual(browser.inspect.actions, [])
        self.assertEqual(browser.inspect.tabs, ['Edit'])
        self.assertEqual(browser.inspect.activetabs, ['Edit'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        self.assertEqual(browser.inspect.form, ['Update Silva Indexer'])
        edit_form = browser.inspect.form['Update Silva Indexer']
        self.assertEqual(edit_form.fields, [])
        self.assertEqual(edit_form.actions, ['Back'])

        # We go through the tabs.
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Edit'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])


class AuthorIndexerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addIndexer('indexer', 'Indexer')

    def test_indexer_update(self):
        """An author cannot an an indexer, but can update it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('author')

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.tabs['Add'].name.click(),
            200)
        self.assertNotIn(
            'Silva Indexer',
            browser.inspect.tabs['Add'].entries)

        # We should see our indexer
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Indexer',
              'identifier': 'indexer',
              'author': 'editor'}])
        # Visit it.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        self.assertEqual(browser.inspect.title, u'Indexer')
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


class EditorIndexerTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'editor'

    def setUp(self):
        self.root = self.layer.get_application()

    def test_indexer_roundtrip(self):
        """An editor can an an indexer, and update it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn(
            'Silva Indexer',
            browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva Indexer'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Indexer"])

        # Add an indexer
        add_form = browser.inspect.form['Add a Silva Indexer']
        add_form.fields['id'].value = 'indexer'
        add_form.fields['title'].value = u'Indexer'
        self.assertEqual(add_form.actions, ['Cancel', 'Save'])
        self.assertEqual(add_form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Indexer.")

        # Inspect new created content
        self.assertEqual(browser.inspect.title, u'Indexer')
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

        # Check the edit form. There is only an update button.
        self.assertEqual(browser.inspect.form, ['Update Silva Indexer'])
        edit_form = browser.inspect.form['Update Silva Indexer']
        self.assertEqual(edit_form.fields, [])
        self.assertEqual(edit_form.actions, ['Back', 'Update index'])
        self.assertEqual(edit_form.actions['Update index'].click(), 200)
        browser.macros.assertFeedback(
            u'Index content have been successfully updated.')

        # We go through the tabs.
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
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
            [{'title': u'Indexer',
              'identifier': 'indexer',
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

        # Delete the indexer
        self.assertEqual(
            browser.inspect.actions['Delete'].click(),
            200)
        # Content is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Indexer', 'identifier': 'indexer'}])
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
        browser.macros.assertFeedback(u'Deleted "Indexer".')


class ChiefEditorIndexerTestCase(EditorIndexerTestCase):
    user = 'chiefeditor'


class ManagerIndexerTestCase(ChiefEditorIndexerTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderIndexerTestCase))
    suite.addTest(unittest.makeSuite(AuthorIndexerTestCase))
    suite.addTest(unittest.makeSuite(EditorIndexerTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorIndexerTestCase))
    suite.addTest(unittest.makeSuite(ManagerIndexerTestCase))
    return suite
