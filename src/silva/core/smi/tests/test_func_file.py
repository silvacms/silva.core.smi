# -*- coding: utf-8 -*-
# Copyright (c) 2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer, Transaction
from Products.Silva.ftesting import smi_settings
from silva.core.references.reference import get_content_id


class AuthorFileTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            with self.layer.open_fixture('silva.png') as stream:
                factory.manage_addFile('logo', 'Silva Logo', stream)

    def test_file_listing(self):
        """You can add a file with Selenium (since the upload button
        doesn't work), however we can check the listing and edit view.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Preview', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn('Silva Ghost', browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva File'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva File"])
        self.assertEqual(browser.inspect.toolbar, [])

        form = browser.inspect.form['Add a Silva File']
        self.assertIn('Id', form.fields)
        self.assertIn('Title', form.fields)
        self.assertEqual(form.actions, ['Cancel', 'Save'])
        self.assertEqual(form.actions['Cancel'].click(), 200)

        self.assertEqual(
            browser.inspect.listing_groups,
            [u'Structural items', u'Assets'])
        self.assertEqual(browser.inspect.listing_groups['Assets'].click(), 200)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Silva Logo',
              'identifier': 'logo',
              'author': u'editor'}])
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(browser.inspect.listing[0].goto_dropdown.click(), 200)
        self.assertEqual(
            browser.inspect.listing[0].goto_actions,
            ['Preview', 'Properties'])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Inspect newly created content
        self.assertEqual(browser.inspect.title, u'Silva Logo')
        self.assertEqual(
            browser.inspect.tabs,
            ['Edit', 'Preview', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['View...'])
        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        self.assertEqual(browser.inspect.form, ['Edit file content'])
        form = browser.inspect.form['Edit file content']
        self.assertIn('Title', form.fields)
        self.assertIn('File', form.fields)
        self.assertEqual(form.actions, ['Back', 'Save changes'])

        # An action let you directly request approval
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

        # We should see our ghost and the original document.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Silva Logo',
              'identifier': 'logo',
              'author': u'editor'}])

        # Select it
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename'])

        self.assertEqual(browser.inspect.toolbar['Delete'].click(), 200)
        # Content is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Silva Logo',
              'identifier': 'logo',
              'author': u'editor'}])
        self.assertEqual(browser.inspect.dialog, ['Confirm deletion'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons,
            ['Cancel', 'Continue'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons['Continue'].click(),
            200)
        self.assertEqual(browser.inspect.listing, [])
        browser.macros.assertFeedback(u'Deleted "Silva Logo".')


class EditorFileTestCase(AuthorFileTestCase):
    user = 'editor'


class ChiefEditorFileTestCase(EditorFileTestCase):
    user = 'chiefeditor'


class ManagerFileTestCase(ChiefEditorFileTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorFileTestCase))
    suite.addTest(unittest.makeSuite(EditorFileTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFileTestCase))
    suite.addTest(unittest.makeSuite(ManagerFileTestCase))
    return suite

