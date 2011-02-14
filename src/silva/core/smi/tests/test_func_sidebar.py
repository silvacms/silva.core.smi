
import unittest
from Products.Silva.testing import FunctionalLayer, smi_settings
from silva.core.smi.navigation import get_sidebar_cache, sidebar_cache_key


class TestSidebar(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.browser = self.layer.get_browser(smi_settings)
        self.browser.options.handle_errors = False
        self.browser.login('manager', 'manager')

        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory.manage_addPublication('publication', 'Publication')
        factory = self.root.publication.manage_addProduct['Silva']
        factory.manage_addFolder('first_folder', 'Folder 1')
        factory.manage_addFolder('second_folder', 'Folder 2')
        factory.manage_addFolder('third_folder', 'Folder 3')
        self.layer.logout()


    def test_sidebar_display(self):
        status = self.browser.open('/root/edit/tab_access')
        self.assertEquals(200, status)

        self.assertEquals([u'root'], self.browser.inspect.navigation_root)
        self.assertEquals([u'root', u'Folder', u'Publication'],
                          self.browser.inspect.navigation)

    def test_simple_sidebar_cache(self):
        cache = get_sidebar_cache()
        key = sidebar_cache_key(self.root)

        def get_cache():
            return cache.get(key)

        self.assertRaises(KeyError, get_cache)

        status = self.browser.open('root/edit/tab_access')
        self.assertEquals(200, status)
        self.assertTrue(get_cache())

    def test_simple_cache_invalidation(self):
        cache = get_sidebar_cache()
        key = sidebar_cache_key(self.root)

        def get_cache():
            return cache.get(key)

        status = self.browser.open('root/edit/tab_access')
        self.assertEquals(200, status)
        self.assertTrue(get_cache())

        status = self.browser.open('root/folder/edit/tab_metadata')
        self.browser.html.resolve_base_href()
        form = self.browser.get_form('form')
        title_field = form.get_control('silva-content.maintitle:record')
        title_field.value = u'New Folder Title'
        self.assertEquals(form.submit('save_metadata:method'), 200)
        self.assertEquals([u'Metadata saved.'],
                          self.browser.inspect.feedback)
        self.assertEquals(u'New Folder Title',
                          self.root.folder.get_title())

        status = self.browser.open('root/edit/tab_access')
        self.assertEquals(200, status)
        self.assertEquals([u'root', u'New Folder Title', u'Publication'],
                          self.browser.inspect.navigation)

    def test_invalidation_on_publication(self):
        status = self.browser.open(
            '/root/publication/first_folder/edit/tab_access')
        self.assertEquals(200, status)

        status = self.browser.open('/root/publication/edit/tab_metadata')
        form = self.browser.get_form('form')
        title_field = form.get_control('silva-content.maintitle:record')
        title_field.value = u'New Publication Title'
        self.assertEquals(form.submit('save_metadata:method'), 200)
        self.assertEquals([u'Metadata saved.'],
                          self.browser.inspect.feedback)

        status = self.browser.open(
            '/root/publication/first_folder/edit/tab_access')
        self.assertEquals(200, status)
        self.assertEquals([u'New Publication Title'],
                          self.browser.inspect.navigation_root)

        # check publication upper level
        status = self.browser.open('/root/edit/tab_access')
        self.assertEquals(200, status)
        self.assertEquals([u'root', u'Folder', u'New Publication Title'],
                          self.browser.inspect.navigation)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSidebar))
    return suite
