# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from silva.core.interfaces import ISiteManager
from Products.Silva.testing import FunctionalLayer, Transaction
from Products.Silva.ftesting import smi_settings


class ReaderPublicationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('site', 'Site')

    def test_publication_access(self):
        """A reader cannot create a folder, however he can look into it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('reader')
        self.assertEqual(browser.inspect.title, u'root')
        self.assertEqual(browser.inspect.tabs, ['Content', 'Preview', ])
        self.assertEqual(browser.inspect.activetabs, ['Content'])
        self.assertEqual(browser.inspect.views, ['View...'])
        self.assertEqual(browser.inspect.toolbar, [])

        # We should see our folder.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Site', 'identifier': 'site', 'author': 'editor'}])
        # Select the folder.
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(browser.inspect.toolbar, ['Copy'])
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

    def test_publication_add_and_listing(self):
        """Create a Publication check its tabs and actions and delete it.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('site', 'Site')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Preview', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertNotIn(
            'Silva Publication',
            browser.inspect.tabs['Add'].entries)

        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Site', 'identifier': 'site', 'author': 'editor'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Site')
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Preview', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['View...'])
        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Content'])
        self.assertEqual(browser.inspect.listing, [])

        # We go through the tabs
        self.assertEqual(browser.inspect.tabs['Preview'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Content'].name.click(), 200)
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
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename'])
        self.assertEqual(
            browser.inspect.listing[0].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[0].goto_actions,
            ['Preview', 'Properties'])

        # Delete the publication
        self.assertEqual(
            browser.inspect.toolbar['Delete'].click(),
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
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Data')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Data', 'identifier': 'publication'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Data')
        self.assertIn('Settings', browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertNotIn({'title': u'Container type'}, browser.inspect.form)


class EditorPublicationTestCase(AuthorPublicationTestCase):
    user = 'editor'

    def test_publication_add_and_listing(self):
        """Create a folder check its tabs and actions and delete it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Preview', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn(
            'Silva Publication',
            browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva Publication'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Publication"])

        add_form = browser.inspect.form['Add a Silva Publication']
        add_form.fields['id'].value = 'site'
        add_form.fields['title'].value = 'Site'
        self.assertEqual(add_form.actions, ['Cancel', 'Save'])
        self.assertEqual(add_form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Publication.")

        self.assertEqual(browser.inspect.title, u"Site")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Preview', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.views, ['View...'])
        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Content'])
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Site', 'identifier': 'index', 'author': self.user}])

        # We go through the tabs
        self.assertEqual(browser.inspect.tabs['Preview'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Settings'])
        self.assertEqual(browser.inspect.tabs['Properties'].name.click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Properties'])
        self.assertEqual(browser.inspect.tabs['Content'].name.click(), 200)
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
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)
        self.assertEqual(
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename', 'Publish'])
        self.assertEqual(
            browser.inspect.listing[0].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[0].goto_actions,
            ['Preview', 'Properties'] + (['Access'] if self.access else []))

        # Delete the folder
        self.assertEqual(
            browser.inspect.toolbar['Delete'].click(),
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
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Data')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)
        self.assertEqual(
            browser.inspect.listing,
            [{'title': 'Data', 'identifier': 'publication'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)
        self.assertEqual(browser.inspect.title, u'Data')
        self.assertIn('Settings', browser.inspect.tabs)
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
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

    def test_publication_localsite(self):
        """Test activating a local site on a publication.
        """
        with Transaction():
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
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertIn({'title': u'Container type'}, browser.inspect.form)
        # The publication is not a local site by default.
        self.assertFalse(ISiteManager(self.root.publication).is_site())

        # You can activate the local site.
        convert = browser.inspect.form['Container type']
        self.assertEqual(convert.title, 'Container type')
        self.assertEqual(convert.form.inspect.fields, [])
        self.assertEqual(convert.actions, ['Convert to folder', 'Make local site'])
        self.assertEqual(convert.actions['Make local site'].click(), 200)
        browser.macros.assertFeedback("Local site activated.")
        # And the publication is now a local site.
        self.assertTrue(ISiteManager(self.root.publication).is_site())

        # After you activated the site, you can only deactivate it.
        self.assertIn({'title': u'Container type'}, browser.inspect.form)
        convert = browser.inspect.form['Container type']
        self.assertEqual(convert.title, 'Container type')
        self.assertEqual(convert.form.inspect.fields, [])
        self.assertEqual(convert.actions, ['Remove local site'])
        self.assertEqual(convert.actions['Remove local site'].click(), 200)
        browser.macros.assertFeedback("Local site deactivated.")
        # And the publication is no longer a local site.
        self.assertFalse(ISiteManager(self.root.publication).is_site())

        # Once deactivated, you can reactivate it.
        self.assertIn({'title': u'Container type'}, browser.inspect.form)
        convert = browser.inspect.form['Container type']
        self.assertEqual(convert.title, 'Container type')
        self.assertEqual(convert.form.inspect.fields, [])
        self.assertEqual(convert.actions, ['Convert to folder', 'Make local site'])

    def test_publication_localsite_active(self):
        """You cannot unactivate a local site if there are services
        registered in it.
        """
        with Transaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addPublication('publication', 'Data')
            ISiteManager(self.root.publication).make_site()
            factory = self.root.publication.manage_addProduct['silva.core.layout']
            factory.manage_addCustomizationService('service_customization')

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
        self.assertEqual(browser.inspect.tabs['Settings'].name.click(), 200)
        self.assertIn({'title': u'Container type'}, browser.inspect.form)

        # You should have the local site form, and the site should be active.
        convert = browser.inspect.form['Container type']
        self.assertEqual(convert.title, 'Container type')
        self.assertEqual(convert.form.inspect.fields, [])
        self.assertEqual(convert.actions, ['Remove local site'])
        self.assertEqual(convert.actions['Remove local site'].click(), 200)
        browser.macros.assertError("Still have registered services.")

        # The site was not removed.
        self.assertTrue(ISiteManager(self.root.publication).is_site())


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
