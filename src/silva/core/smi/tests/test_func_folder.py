# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings


class ReaderFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')

    def test_folder_access(self):
        """A reader cannot create a folder, however he can look into it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('reader')
        self.assertEqual(browser.inspect.title, u'root')
        self.assertEqual(browser.inspect.tabs, ['Content'])
        self.assertEqual(browser.inspect.activetabs, ['Content'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        self.assertEqual(browser.inspect.actions, [])

        # We should see our folder.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Folder', 'identifier': 'folder', 'author': 'editor'}])
        # Select the folder.
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(browser.inspect.actions, ['Copy'])
        self.assertEqual(browser.inspect.listing[0].goto_dropdown.click(), 200)
        self.assertEqual(browser.inspect.listing[0].goto_actions, ['Preview'])

        # Go inside the folder.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Folder')
        self.assertEqual(browser.inspect.tabs, ['Content'])
        self.assertEqual(browser.inspect.activetabs, ['Content'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        self.assertEqual(browser.inspect.listing, [])
        self.assertEqual(browser.inspect.actions, [])

        # We go through the tabs.
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Content'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])


class AuthorFolderTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    publish = False
    access = False

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_folder_roundtrip(self):
        """Create a folder check its tabs and actions and delete it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].click(), 200)
        self.assertIn('Silva Folder', browser.inspect.subtabs)
        self.assertEqual(browser.inspect.subtabs['silva Folder'].click(), 200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Folder"])

        add_form = browser.inspect.form['Add a Silva Folder']
        add_form.form.inspect.fields['id'].value = 'folder'
        add_form.form.inspect.fields['title'].value = 'Test'
        self.assertEqual(add_form.actions, ['Cancel', 'Save'])
        self.assertEqual(add_form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Folder.")

        # Inspect new created content.
        self.assertEqual(browser.inspect.title, u"Test")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.views,
            ['Preview', 'View'])
        self.assertEqual(
            browser.inspect.activetabs,
            ['Content'])
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Test', 'identifier': 'index', 'author': self.user}])

        # We go through the tabs
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Content'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # Go up a level.
        self.assertEqual(browser.inspect.parent.click(), 200)
        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(browser.inspect.activetabs, ['Content'])

        # We should see our folder.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Test', 'identifier': 'folder', 'author': self.user}])
        # Select the folder
        self.assertEqual(
            browser.inspect.listing[0].identifier.click(),
            200)
        self.assertEqual(
            browser.inspect.actions,
            ['Cut', 'Copy', 'Delete', 'Rename'] + (['Publish'] if self.publish else []))
        self.assertEqual(
            browser.inspect.listing[0].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[0].goto_actions,
            ['Preview', 'Properties'] + (['Access'] if self.access else []))

        # Delete the folder
        self.assertEqual(
            browser.inspect.actions['Delete'].click(),
            200)
        # Folder is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Test', 'identifier': 'folder', 'author': self.user}])
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
        browser.macros.assertFeedback(u'Deleted "Test".')

    def test_folder_feeds(self):
        """Test feeds settings. An author doesn't have the right to change them.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Feeds')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Feeds', 'identifier': 'folder', 'author': 'editor'}])
        self.assertEqual(
            browser.inspect.listing[0].goto.click(),
            200)
        self.assertEqual(browser.inspect.title, u'Feeds')
        self.assertIn('Settings', browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertNotIn({'title': u'Atom/rss feeds'}, browser.inspect.form)

        # By default feeds are off
        xml_browser = self.layer.get_browser()
        self.assertEqual(xml_browser.open('/root/folder/atom.xml'), 404)
        self.assertEqual(xml_browser.open('/root/folder/rss.xml'), 404)

    def test_folder_convert(self):
        """Test folder to publication conversion.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Data')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Data', 'identifier': 'folder', 'author': 'editor'}])
        self.assertEqual(
            browser.inspect.listing[0].goto.click(),
            200)
        self.assertEqual(browser.inspect.title, u'Data')
        self.assertIn('Settings', browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertNotIn({'title': u'Container type'}, browser.inspect.form)


class EditorFolderTestCase(AuthorFolderTestCase):
    user = 'editor'
    publish = True

    def test_folder_feeds(self):
        """Test feeds settings. An editor and above can change them
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Feeds')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Feeds', 'identifier': 'folder', 'author': 'editor'}])
        self.assertEqual(
            browser.inspect.listing[0].goto.click(),
            200)
        self.assertEqual(browser.inspect.title, u'Feeds')
        self.assertIn('Settings', browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)

        self.assertIn({'title': u'Atom/rss feeds'}, browser.inspect.form)
        settings = browser.inspect.form['feeds']
        self.assertEqual(settings.title, 'Atom/rss feeds')
        self.assertEqual(settings.form.inspect.fields, [u'Allow feeds'])
        self.assertEqual(settings.actions, [u'Change feed settings'])
        self.assertEqual(
            settings.form.inspect.fields['Allow feeds'].checked,
            False)

        settings.form.inspect.fields['Allow feeds'].checked = True
        self.assertEqual(settings.actions['Change feed settings'].click(), 200)
        browser.macros.assertFeedback('Feed settings saved.')

        self.assertIn({'title': u'Atom/rss feeds'}, browser.inspect.form)
        settings = browser.inspect.form['feeds']
        self.assertEqual(settings.form.inspect.fields, [u'Allow feeds'])
        self.assertEqual(settings.actions, [u'Change feed settings'])
        self.assertEqual(
            settings.form.inspect.fields['Allow feeds'].checked,
            True)

        # Feeds are now available.
        xml_browser = self.layer.get_browser()
        self.assertEqual(xml_browser.open('/root/folder/atom.xml'), 200)
        self.assertEqual(xml_browser.content_type, 'text/xml;charset=UTF-8')
        self.assertEqual(xml_browser.open('/root/folder/rss.xml'), 200)
        self.assertEqual(xml_browser.content_type, 'text/xml;charset=UTF-8')

    def test_folder_convert(self):
        """Test folder to publication conversion.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Data')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Data', 'identifier': 'folder', 'author': 'editor'}])
        self.assertEqual(
            browser.inspect.listing[0].goto.click(),
            200)
        self.assertEqual(browser.inspect.title, u'Data')
        self.assertIn('Settings', browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertIn({'title': u'Container type'}, browser.inspect.form)

        convert = browser.inspect.form['Container type']
        self.assertEqual(convert.title, 'Container type')
        self.assertEqual(convert.form.inspect.fields, [])
        self.assertEqual(convert.actions, ['Convert to publication'])
        self.assertEqual(convert.actions['Convert to publication'].click(), 200)
        browser.macros.assertFeedback("Changed into publication.")

        self.assertEqual(browser.inspect.title, u'Data')
        convert = browser.inspect.form['Container type']
        self.assertEqual(convert.title, 'Container type')
        self.assertEqual(convert.form.inspect.fields, [])
        self.assertNotIn('Convert to publication', convert.actions)


class ChiefEditorFolderTestCase(EditorFolderTestCase):
    user = 'chiefeditor'
    access = True


class ManagerFolderTestCase(ChiefEditorFolderTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderFolderTestCase))
    suite.addTest(unittest.makeSuite(AuthorFolderTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderTestCase))
    suite.addTest(unittest.makeSuite(ManagerFolderTestCase))
    return suite
