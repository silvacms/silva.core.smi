
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
        self.assertEqual(edit_form.form.inspect.fields, [])
        self.assertEqual(edit_form.actions, ['Back'])

        # We go through the tabs.
        self.assertEqual(browser.inspect.views['Preview'].click(), 200)
        self.assertEqual(browser.inspect.activeviews, ['Preview'])
        self.assertEqual(browser.inspect.tabs['Edit'].click(), 200)
        self.assertEqual(browser.inspect.activetabs, ['Edit'])


class AuthorIndexerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addIndexer('indexer', 'Indexer')

    def test_indexer_roundtrip(self):
        """An author cannot an an indexer, but can update it.
        """
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('author')

        self.assertEqual(browser.inspect.title, u"root")
        self.assertEqual(
            browser.inspect.tabs,
            ['Content', 'Add', 'Properties', 'Settings'])
        self.assertEqual(browser.inspect.tabs['Add'].click(), 200)
        self.assertNotIn('Silva Indexer', browser.inspect.subtabs)

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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReaderIndexerTestCase))
    suite.addTest(unittest.makeSuite(AuthorIndexerTestCase))
    return suite
