import unittest
from Products.Silva.testing import FunctionalLayer, smi_settings


class TestAddablesForm(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        root = self.layer.get_application()
        factory = root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.target = root.folder
        self.browser = self.layer.get_browser(smi_settings)

    def test_addables_editor(self):
        self.browser.login('editor')
        status = self.browser.open('http://localhost/root/edit/tab_addables')
        self.assertEquals(401, status)

    def test_addables_tab(self):
        self.browser.login('chiefeditor')
        status = self.browser.open('http://localhost/root/edit/tab_addables')
        self.assertEquals(200, status)
        self.assertEquals([], self.browser.inspect.feedback)

    def test_addables_still_acquired(self):
        self.browser.login('chiefeditor')
        self.assertTrue(self.target.is_silva_addables_acquired())
        status = self.browser.open(
            'http://localhost/root/folder/edit/tab_addables')
        self.assertEquals(200, status)
        form = self.browser.get_form('form')
        acquire_field = form.get_control('form.field.acquire')
        save_button = form.get_control(
            'form.action.save-addables-settings')
        self.assertTrue(acquire_field)
        self.assertTrue(acquire_field.checkable)
        self.assertTrue(acquire_field.checked)
        self.assertTrue(save_button)
        status = save_button.click()
        self.assertEquals(200, status)
        self.assertTrue(self.target.is_silva_addables_acquired())
        self.assertEquals(
            ['Addable settings have not changed and remain acquired.'],
            self.browser.inspect.feedback)

    def test_addables_set_not_aquired(self):
        self.browser.login('chiefeditor')
        self.assertTrue(self.target.is_silva_addables_acquired())
        status = self.browser.open(
            'http://localhost/root/folder/edit/tab_addables')
        self.assertEquals(200, status)
        form = self.browser.get_form('form')
        acquire_field = form.get_control('form.field.acquire')
        save_button = form.get_control(
            'form.action.save-addables-settings')
        acquire_field.checked = False
        self.assertEquals(200, save_button.click())
        self.assertFalse(self.target.is_silva_addables_acquired())
        self.assertEquals(['Changes to addables content types saved.'],
            self.browser.inspect.feedback)

    def test_now_acquired(self):
        self.browser.login('chiefeditor')
        self.target.set_silva_addables_allowed_in_container('Silva Document')
        self.assertFalse(self.target.is_silva_addables_acquired())
        status = self.browser.open(
            'http://localhost/root/folder/edit/tab_addables')
        self.assertEquals(200, status)
        form = self.browser.get_form('form')
        acquire_field = form.get_control('form.field.acquire')
        save_button = form.get_control(
            'form.action.save-addables-settings')
        self.assertFalse(acquire_field.checked)
        acquire_field.checked = True
        self.assertEquals(200, save_button.click())
        self.assertTrue(self.target.is_silva_addables_acquired())
        self.assertEquals(['Addable settings are now aquired.'],
            self.browser.inspect.feedback)

    def test_change_addables(self):
        self.browser.login('chiefeditor')
        status = self.browser.open(
            'http://localhost/root/folder/edit/tab_addables')
        self.assertEquals(200, status)
        form = self.browser.get_form('form')
        acquire_field = form.get_control('form.field.acquire')
        save_button = form.get_control(
            'form.action.save-addables-settings')
        acquire_field.checked = False
        addables_field = form.get_control('form.field.addables')
        self.assertTrue('Silva Link' in addables_field.value)
        new_value = list(addables_field.value)
        new_value.remove('Silva Link')
        addables_field.value = new_value
        self.assertEquals(200, save_button.click())
        self.assertTrue('Silva Link' not in
            self.target.get_silva_addables_allowed_in_container())
        self.assertEquals(['Changes to addables content types saved.'],
            self.browser.inspect.feedback)


