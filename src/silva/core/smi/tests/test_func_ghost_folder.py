# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings
from silva.core.references.reference import get_content_id


class EditorGhostFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'editor'
    goto = []

    def setUp(self):
        """Set up objects for test :

           + root (Silva root)
               |
               + folder (Silva Folder)
                   |
                   +- document (Silva Mockup)
                   |
                   +- publication (Silva Publication)
                       |
                       +- document (Silva Mockup)
        """
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')
            folder = self.root._getOb('folder')

            factory = folder.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')
            factory.manage_addPublication('publication', 'Publication')
            publication = folder._getOb('publication')

            factory = publication.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_ghost_folder_add_and_listing(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn('Silva Ghost Folder', browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva Ghost Folder'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Ghost Folder"])
        self.assertEqual(browser.inspect.toolbar, [])

        form = browser.inspect.form['Add a Silva Ghost Folder']
        self.assertIn('Id', form.fields)
        form.fields['Id'].value = 'ghost_folder'
        # Lookup an element to ghost
        self.assertEqual(browser.inspect.reference[0].click(), 200)
        self.assertEqual(browser.inspect.dialog, ['Lookup an item'])
        dialog = browser.inspect.dialog['Lookup an item']
        self.assertEqual(dialog.buttons, ['Cancel'])
        self.assertEqual(dialog.listing, ['current container', 'folder'])
        self.assertEqual(dialog.listing['folder'].title, 'Folder')
        self.assertEqual(dialog.listing['folder'].select.click(), 200)
        # This should have closed the dialog and selected the document
        # in the hidden field
        self.assertEqual(browser.inspect.dialog, [])

        self.assertEqual(form.actions, ['Cancel', 'Save'])
        self.assertEqual(form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Ghost Folder.")
        # Inspect newly created content

        self.assertEqual(browser.inspect.title, u'Folder')
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Edit', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View...'])
        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Content'])
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': self.user},
             {'title': u'Publication',
              'identifier': 'publication',
              'author': self.user}])

        # Go though the tabs
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Edit'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        # Check edit form
        self.assertEqual(browser.inspect.form, ['Edit a Silva Ghost Folder'])
        form = browser.inspect.form['Edit a Silva Ghost Folder']
        self.assertNotEqual(form.fields, [])
        self.assertIn('Haunted', form.fields)
        self.assertEqual(
            form.fields['Haunted'].value,
            str(get_content_id(self.root.folder)))
        self.assertEqual(form.actions, ['Back', 'Save changes', 'Synchronize'])
        self.assertEqual(form.actions['Synchronize'].click(), 200)
        browser.macros.assertFeedback(u"Ghost Folder synchronized.")

        self.assertEqual(browser.inspect.tabs['Content'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # Go up a level.
        self.assertEqual(browser.inspect.parent.click(), 200)
        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # We should see our ghost and the original document.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Folder',
              'identifier': 'folder',
              'author': u'editor'},
             {'title': u'Folder',
              'identifier': 'ghost_folder',
              'author': self.user}])
        # Select it
        self.assertEqual(browser.inspect.listing[1].identifier.click(), 200)
        self.assertEqual(
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename', 'Publish'])
        self.assertEqual(
            browser.inspect.listing[1].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[1].goto_actions,
            ['Preview', 'Properties'] + self.goto)

        self.assertEqual(browser.inspect.toolbar['Delete'].click(), 200)
        # Content is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Folder',
              'identifier': 'folder',
              'author': u'editor'},
             {'title': u'Folder',
              'identifier': 'ghost_folder',
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
            [{'title': u'Folder',
              'identifier': 'folder',
              'author': u'editor'}])
        browser.macros.assertFeedback(u'Deleted "Folder".')


class ChiefEditorGhostFolderTestCase(EditorGhostFolderTestCase):
    user = 'chiefeditor'
    goto = ['Access']


class ManagerGhostFolderTestCase(ChiefEditorGhostFolderTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EditorGhostFolderTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorGhostFolderTestCase))
    suite.addTest(unittest.makeSuite(ManagerGhostFolderTestCase))
    return suite
