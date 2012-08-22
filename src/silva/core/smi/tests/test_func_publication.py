# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings


class ReaderPublicationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('site', 'Site')

    def test_publication_access(self):
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
            [{'title': u'Site', 'identifier': 'site', 'author': 'editor'}])
        # Select the folder.
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(browser.inspect.actions, ['Copy'])
        self.assertEqual(browser.inspect.listing[0].goto_dropdown.click(), 200)
        self.assertEqual(browser.inspect.listing[0].goto_actions, ['Preview'])

        # Go inside the publication.
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Site')
        self.assertEqual(browser.inspect.listing, [])


class AuthorPublicationTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    publish = False
    access = False

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_publication_roundtrip(self):
        """Create a Publication check its tabs and actions and delete it.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('site', 'Site')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        browser.inspect.tabs['Add'].click()
        self.assertNotIn('Silva Publication', browser.inspect.subtabs)

        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Site', 'identifier': 'site', 'author': 'editor'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Site')
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.views,
            ['Preview', 'View'])
        # We are on contents
        self.assertEqual(
            browser.inspect.activetabs,
            ['Content'])
        self.assertEqual(
            browser.inspect.listing,
            [])

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

        # We should see our publication.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Site', 'identifier': 'site', 'author': 'editor'}])
        # Select the folder
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

        # Delete the publication
        self.assertEqual(
            browser.inspect.actions['Delete'].click(),
            200)
        # Publication is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Site', 'identifier': 'site', 'author': 'editor'}])
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
        browser.macros.assertFeedback(u'Deleted "Site".')

    def test_publication_convert(self):
        """Test folder to publication conversion.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Data')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Data', 'identifier': 'publication'}])
        self.assertEqual(
            browser.inspect.listing[0].goto.click(),
            200)
        self.assertEqual(browser.inspect.title, u'Data')
        self.assertIn('Settings', browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['Settings'].click(), 200)
        self.assertNotIn({'title': u'Container type'}, browser.inspect.form)


class EditorPublicationTestCase(AuthorPublicationTestCase):
    user = 'editor'

    def test_publication_roundtrip(self):
        """Create a folder check its tabs and actions and delete it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        browser.inspect.tabs['Add'].click()
        self.assertIn('Silva Publication', browser.inspect.subtabs)
        self.assertEqual(browser.inspect.subtabs['Silva Publication'].click(), 200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Publication"])

        add_form = browser.inspect.form['Add a Silva Publication']
        add_form.form.inspect.fields['id'].value = 'site'
        add_form.form.inspect.fields['title'].value = 'Site'
        self.assertEqual(add_form.actions, ['Cancel', 'Save'])
        self.assertEqual(add_form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Publication.")

        self.assertEqual(browser.inspect.title, u"Site")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(
            browser.inspect.views,
            ['Preview', 'View'])
        # We are on contents
        self.assertEqual(
            browser.inspect.activetabs,
            ['Content'])
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Site', 'identifier': 'index', 'author': self.user}])

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
            [{'title': 'Site', 'identifier': 'site', 'author': self.user}])
        # Select the folder
        self.assertEqual(
            browser.inspect.listing[0].identifier.click(),
            200)
        self.assertEqual(
            browser.inspect.actions,
            ['Cut', 'Copy', 'Delete', 'Rename', 'Publish'])
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
        # Folder is yet deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Site', 'identifier': 'site', 'author': self.user}])
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
        browser.macros.assertFeedback(u'Deleted "Site".')

    def test_publication_convert(self):
        """Test folder to publication conversion.
        """
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Data')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Data', 'identifier': 'publication'}])
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
        self.assertEqual(convert.actions, ['Convert to folder', 'Make local site'])
        self.assertEqual(convert.actions['Convert to folder'].click(), 200)
        browser.macros.assertFeedback("Changed into folder.")

        self.assertEqual(browser.inspect.title, u'Data')
        convert = browser.inspect.form['Container type']
        self.assertEqual(convert.title, 'Container type')
        self.assertEqual(convert.form.inspect.fields, [])
        self.assertNotIn('Convert to folder', convert.actions)


class ChiefEditorPublicationTestCase(EditorPublicationTestCase):
    user = 'chiefeditor'
    access = True


class ManagerPublicationTestCase(ChiefEditorPublicationTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderPublicationTestCase))
    suite.addTest(unittest.makeSuite(AuthorPublicationTestCase))
    suite.addTest(unittest.makeSuite(EditorPublicationTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorPublicationTestCase))
    suite.addTest(unittest.makeSuite(ManagerPublicationTestCase))
    return suite
