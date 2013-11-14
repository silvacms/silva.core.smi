# -*- coding: utf-8 -*-
# Copyright (c) 2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer, Transaction
from Products.Silva.ftesting import smi_settings
from silva.core.references.reference import get_content_id


class AuthorGhostAssetTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            with self.layer.open_fixture('silva.png') as stream:
                factory.manage_addFile('logo', 'Silva Logo', stream)

    def test_ghost_add_and_listing(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Preview', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn('Silva Ghost', browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva Ghost Asset'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Ghost Asset"])
        self.assertEqual(browser.inspect.toolbar, [])

        form = browser.inspect.form['Add a Silva Ghost Asset']
        self.assertIn('Id', form.fields)
        form.fields['Id'].value = 'ghost_asset'
        # Lookup an element to ghost
        self.assertEqual(browser.inspect.reference[0].click(), 200)
        self.assertEqual(browser.inspect.dialog, ['Lookup an item'])
        dialog = browser.inspect.dialog['Lookup an item']
        self.assertEqual(dialog.buttons, ['Cancel'])
        self.assertEqual(dialog.listing, ['current container', 'logo'])
        self.assertEqual(dialog.listing['logo'].title, 'Silva Logo')
        self.assertEqual(dialog.listing['logo'].select.click(), 200)
        # This should have closed the dialog and selected the document
        # in the hidden field
        self.assertEqual(browser.inspect.dialog, [])
        self.assertIn('Haunted', form.fields)
        self.assertEqual(
            form.fields['Haunted'].value,
            str(get_content_id(self.root.logo)))
        self.assertEqual(form.actions, ['Cancel', 'Save'])
        self.assertEqual(form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Ghost Asset.")

        # Inspect newly created content
        self.assertEqual(browser.inspect.title, u'Silva Logo')
        self.assertEqual(
            browser.inspect.tabs,
            ['Edit', 'Preview', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['View...'])
        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        self.assertEqual(browser.inspect.form, ['Edit ghost'])
        form = browser.inspect.form['Edit ghost']
        self.assertNotEqual(form.fields, [])
        self.assertIn('Haunted', form.fields)
        self.assertEqual(
            form.fields['Haunted'].value,
            str(get_content_id(self.root.logo)))
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

        self.assertEqual(
            browser.inspect.listing_groups,
            [u'Structural items', u'Assets'])
        self.assertEqual(browser.inspect.listing_groups['Assets'].click(), 200)

        # We should see our ghost and the original document.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Silva Logo',
              'identifier': 'ghost_asset',
              'author': self.user},
             {'title': u'Silva Logo',
              'identifier': 'logo',
              'author': u'editor'}])

        # Select it
        self.assertEqual(browser.inspect.listing[1].identifier.click(), 200)

        self.assertEqual(
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename'])
        self.assertEqual(
            browser.inspect.listing[1].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[1].goto_actions,
            ['Preview', 'Properties'])

        self.assertEqual(browser.inspect.toolbar['Delete'].click(), 200)
        # Content is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Silva Logo',
              'identifier': 'ghost_asset',
              'author': self.user},
             {'title': u'Silva Logo',
              'identifier': 'logo',
              'author': u'editor'}])
        self.assertEqual(browser.inspect.dialog, ['Confirm deletion'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons,
            ['Cancel', 'Continue'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons['Continue'].click(),
            200)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Silva Logo',
              'identifier': 'ghost_asset',
              'author': self.user}])
        browser.macros.assertFeedback(u'Deleted "Silva Logo".')


class EditorGhostAssetTestCase(AuthorGhostAssetTestCase):
    user = 'editor'


class ChiefEditorGhostAssetTestCase(EditorGhostAssetTestCase):
    user = 'chiefeditor'


class ManagerGhostAssetTestCase(ChiefEditorGhostAssetTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorGhostAssetTestCase))
    suite.addTest(unittest.makeSuite(EditorGhostAssetTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorGhostAssetTestCase))
    suite.addTest(unittest.makeSuite(ManagerGhostAssetTestCase))
    return suite

