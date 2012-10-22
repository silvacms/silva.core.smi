

import unittest


from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings


class AuthorLinkTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    toolbar = ['Request approval']

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_link_add_internal_and_listing(self):
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn('Silva Link', browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva Link'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Link"])
        self.assertEqual(browser.inspect.toolbar, [])

        # Add a new internal link
        form = browser.inspect.form['Add a Silva Link']
        self.assertIn('Id', form.fields)
        form.fields['Id'].value = 'silvacms'
        self.assertIn('Title', form.fields)
        form.fields['Title'].value = 'silvacms.org site'
        self.assertIn('Relative link', form.fields)
        form.fields['Relative link'].checked = True
        # Select an item to refer to.
        self.assertEqual(len(browser.inspect.reference), 1)
        self.assertEqual(browser.inspect.reference[0].click(), 200)
        self.assertEqual(browser.inspect.dialog, ['Lookup an item'])
        dialog = browser.inspect.dialog['Lookup an item']
        self.assertEqual(dialog.title, 'Lookup an item')
        self.assertEqual(dialog.buttons, ['Cancel', 'Clear'])
        self.assertEqual(dialog.listing, ['current container', 'document'])
        self.assertEqual(dialog.listing['document'].title, 'Document')
        self.assertEqual(dialog.listing['document'].select.click(), 200)
        # This select the item
        self.assertEqual(browser.inspect.dialog, [])
        self.assertEqual(form.actions, ['Cancel', 'Save'])
        self.assertEqual(form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Link.")

        # Inspect newly created content
        self.assertEqual(browser.inspect.title, u'silvacms.org site')
        # An action let you directly request approval
        self.assertEqual(browser.inspect.toolbar, self.toolbar)

    def test_link_add_external_and_listing(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].open.click(), 200)
        self.assertIn('Silva Link', browser.inspect.tabs['Add'].entries)
        self.assertEqual(
            browser.inspect.tabs['Add'].entries['Silva Link'].click(),
            200)
        self.assertEqual(browser.inspect.form, ["Add a Silva Link"])
        self.assertEqual(browser.inspect.toolbar, [])

        form = browser.inspect.form['Add a Silva Link']
        self.assertIn('Id', form.fields)
        form.fields['Id'].value = 'silvacms'
        self.assertIn('Title', form.fields)
        form.fields['Title'].value = 'silvacms.org site'
        self.assertIn('URL', form.fields)
        form.fields['URL'].value = 'http://silvacms.org'
        self.assertIn('Relative link', form.fields)
        self.assertEqual(form.fields['Relative link'].checked, False)
        self.assertEqual(form.actions, ['Cancel', 'Save'])
        self.assertEqual(form.actions['Save'].click(), 200)
        browser.macros.assertFeedback(u"Added Silva Link.")

        # Inspect newly created content
        self.assertEqual(browser.inspect.title, u'silvacms.org site')
        self.assertEqual(
            browser.inspect.tabs,
            ['Edit', 'Properties', 'Publish', 'Settings'])
        self.assertEqual(browser.inspect.views, ['Preview', 'View'])
        # We are on contents
        self.assertEqual(browser.inspect.activetabs, ['Edit'])

        self.assertEqual(browser.inspect.form, ['Edit a Silva Link'])
        form = browser.inspect.form['Edit a Silva Link']
        self.assertNotEqual(form.fields, [])
        self.assertEqual(form.fields['Title'].value, 'silvacms.org site')
        self.assertEqual(form.fields['URL'].value, 'http://silvacms.org')
        self.assertEqual(form.fields['Relative link'].checked, False)
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
            [{'title': u'silvacms.org site',
              'identifier': 'silvacms',
              'author': self.user}])
        # Select it
        self.assertEqual(browser.inspect.listing[0].identifier.click(), 200)

        self.assertEqual(
            browser.inspect.toolbar,
            ['Cut', 'Copy', 'Delete', 'Rename'] + self.toolbar)
        self.assertEqual(
            browser.inspect.listing[0].goto_dropdown.click(),
            200)
        self.assertEqual(
            browser.inspect.listing[0].goto_actions,
            ['Preview', 'Properties', 'Publish'])

        self.assertEqual(browser.inspect.toolbar['Delete'].click(), 200)
        # Content is not deleted, you have to confirm the deletion first.
        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'silvacms.org site',
              'identifier': 'silvacms',
              'author': self.user}])
        self.assertEqual(browser.inspect.dialog, ['Confirm deletion'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons,
            ['Cancel', 'Continue'])
        self.assertEqual(
            browser.inspect.dialog[0].buttons['Continue'].click(),
            200)
        self.assertEqual(browser.inspect.listing, [])
        browser.macros.assertFeedback(u'Deleted "silvacms.org site".')


class EditorLinkTestCase(AuthorLinkTestCase):
    user = 'editor'
    toolbar = ['Publish']


class ChiefEditorLinkTestCase(EditorLinkTestCase):
    user = 'chiefeditor'


class ManagerLinkTestCase(ChiefEditorLinkTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorLinkTestCase))
    suite.addTest(unittest.makeSuite(EditorLinkTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorLinkTestCase))
    suite.addTest(unittest.makeSuite(ManagerLinkTestCase))
    return suite

