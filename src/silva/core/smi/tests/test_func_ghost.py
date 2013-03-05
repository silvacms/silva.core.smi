# -*- coding: utf-8 -*-
# Copyright (c) 2008-2012 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings
from silva.core.references.reference import get_content_id


class AuthorGhostTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    toolbar = ['Request approval']

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_ghost_add_and_listing(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn('Silva Ghost', browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva Ghost'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Ghost"])
        self.assertEqual(browser.inspect.toolbar, [])

        form = browser.inspect.form['Add a Silva Ghost']
        self.assertIn('Id', form.fields)
        form.fields['Id'].value = 'ghost_document'
        # Lookup an element to ghost
        self.assertEqual(browser.inspect.reference[0].click(), 200)
        self.assertEqual(browser.inspect.dialog, ['Lookup an item'])
        dialog = browser.inspect.dialog['Lookup an item']
        self.assertEqual(dialog.buttons, ['Cancel'])
        self.assertEqual(dialog.listing, ['current container', 'document'])
        self.assertEqual(dialog.listing['document'].title, 'Document')
        self.assertEqual(dialog.listing['document'].select.click(), 200)
        # This should have closed the dialog and selected the document
        # in the hidden field
        self.assertEqual(browser.inspect.dialog, [])
        self.assertIn('Haunted', form.fields)
        self.assertEqual(
            form.fields['Haunted'].value,
            str(get_content_id(self.root.document)))
        self.assertEqual(form.actions, ['Cancel', 'Save'])
        self.assertEqual(form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Ghost.")

        # Inspect newly created content
        self.assertEqual(browser.inspect.title, u'Document')
        self.assertEqual(
            browser.inspect.tabs,
            ['Edit', 'Properties', 'Publish', 'Settings'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View...'])
        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        self.assertEqual(browser.inspect.form, ['Edit a Silva Ghost'])
        form = browser.inspect.form['Edit a Silva Ghost']
        self.assertNotEqual(form.fields, [])
        self.assertIn('Haunted', form.fields)
        self.assertEqual(
            form.fields['Haunted'].value,
            str(get_content_id(self.root.document)))
        self.assertEqual(form.actions, ['Back', 'Save changes'])

        # An action let you directly request approval
        self.assertEqual(browser.inspect.toolbar, self.toolbar)

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

        # We should see our ghost and the original document.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': u'editor'},
             {'title': u'Document',
              'identifier': 'ghost_document',
              'author': self.user}])
        # Select it
        self.assertEqual(browser.inspect.listing[1].identifier.click(), 200)

        self.assertEqual(
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename'] + self.toolbar)
        self.assertEqual(
            browser.inspect.listing[1].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[1].goto_actions,
            ['Preview', 'Properties', 'Publish'])

        self.assertEqual(browser.inspect.toolbar['Delete'].click(), 200)
        # Content is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': u'editor'},
             {'title': u'Document',
              'identifier': 'ghost_document',
              'author': self.user}])
        self.assertEqual(browser.inspect.dialog, ['Confirm deletion'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons,
            ['Cancel', 'Continue'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons['Continue'].click(),
            200)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': u'editor'}])
        browser.macros.assertFeedback(u'Deleted "Document".')


class EditorGhostTestCase(AuthorGhostTestCase):
    user = 'editor'
    toolbar = ['Publish']


class ChiefEditorGhostTestCase(EditorGhostTestCase):
    user = 'chiefeditor'


class ManagerGhostTestCase(ChiefEditorGhostTestCase):
    user = 'manager'




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorGhostTestCase))
    suite.addTest(unittest.makeSuite(EditorGhostTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorGhostTestCase))
    suite.addTest(unittest.makeSuite(ManagerGhostTestCase))
    return suite

