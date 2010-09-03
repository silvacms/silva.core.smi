import unittest
from Products.Silva.testing import FunctionalLayer
from infrae.testbrowser.browser import Browser
from silva.core.smi.navigation import get_sidebar_cache, sidebar_cache_key

class SidebarTest(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.browser = Browser(self.layer._test_wsgi_application)
        self.setup_content()
        self.browser.login('manager', 'manager')
        self.browser.inspect.add('sidebar_root',
            '(//div[@class="navigation"]/table[@class="listing"]'
            '//td)[1]')
        self.browser.inspect.add('sidebar_elements',
            '//div[@class="navigation"]/table[@class="listing"]//td')
        self.browser.inspect.add('feedback',
            '//div[@class="fixed-feedback"]/span')

    def setup_content(self):
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

        self.assertEquals([u'root'], self.browser.inspect.sidebar_root)
        self.assertEquals([u'root', u'Folder', u'Publication'],
                          self.browser.inspect.sidebar_elements)

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
                          self.browser.inspect.sidebar_elements)

    def test_invalidation_on_publication(self):
        status = self.browser.open(
            '/root/publication/first_folder/edit/tab_access')
        self.assertEquals(200, status)

        status = self.browser.open('/root/publication/edit/tab_metadata')
        self.browser.html.resolve_base_href()
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
                          self.browser.inspect.sidebar_root)

        # check publication upper level
        status = self.browser.open('/root/edit/tab_access')
        self.assertEquals(200, status)
        self.assertEquals([u'root', u'Folder', u'New Publication Title'],
                          self.browser.inspect.sidebar_elements)
