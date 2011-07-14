# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from Products.Silva.testing import FunctionalLayer, smi_settings

class ChiefEditorAddablesTestCase(unittest.TestCase):
    """ChiefEditor (and Manager) have a setting tab and a addable one.
    """
    layer = FunctionalLayer
    username = 'chiefeditor'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')

    def test_addables(self):
        browser = self.layer.get_selenium_browser(smi_settings)
        browser.login(self.username)

        browser.open('/root/edit')
        self.assertTrue('settings' in browser.inspect.content_tabs)

        self.assertEqual(browser.inspect.content_tabs['settings'].click(), 200)

        self.assertTrue('addables' in browser.inspect.content_subtabs)
        self.assertEqual(browser.inspect.content_subtabs['addables'].click(), 200)

        # Addables form
        form = browser.get_form('form')
        addables = form.get_control('form.field.addables')
        self.assertTrue('Silva File' in addables.options)
        self.assertTrue('Silva Image' in addables.options)
        self.assertTrue('Silva Folder' in addables.options)
        self.assertTrue('Silva Link' in addables.options)
        self.assertTrue('Silva AutoTOC' in addables.options)
        self.assertTrue('Silva Publication' in addables.options)

        # Uninstalled products are not addables
        self.assertFalse('Silva Find' in addables.options)

        # Change the addables
        addables.value = ['Silva Folder', 'Silva File', 'Silva Image']
        self.assertEqual(browser.inspect.form_controls['save'].click(), 200)

        self.assertItemsEqual(
            browser.inspect.feedback,
            ['Changes to addables content types saved.'])

        form = browser.get_form('form')
        self.assertItemsEqual(
            form.get_control('form.field.addables').value,
            ['Silva Folder', 'Silva File', 'Silva Image'])

        # There is no acquire option on the root.
        self.assertTrue('form.field.acquire' not in form.controls)

        # Now check the add menu: only the three selected are there
        self.assertTrue('add' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['add'].click()
        self.assertItemsEqual(
            browser.inspect.content_subtabs.keys(),
            ['Silva Folder', 'Silva File', 'Silva Image'])

        # Visit addable tab on this folder.
        self.assertTrue('content' in browser.inspect.content_tabs)
        self.assertEqual(browser.inspect.content_tabs['content'].click(), 200)

        # We have one folder, with an addable tab as well
        self.assertEqual(browser.inspect.folder_identifier, ['folder'])
        browser.inspect.folder_goto[0].click()

        # And we can only add acquired values
        self.assertTrue('add' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['add'].click()
        self.assertItemsEqual(
            browser.inspect.content_subtabs.keys(),
            ['Silva Folder', 'Silva File', 'Silva Image'])

        self.assertTrue('settings' in browser.inspect.content_tabs)
        self.assertEqual(browser.inspect.content_tabs['settings'].click(), 200)
        self.assertTrue('addables' in browser.inspect.content_subtabs)
        self.assertEqual(browser.inspect.content_subtabs['addables'].click(), 200)

        # There is a form, where settings are acquired.
        form = browser.get_form('form')
        addables = form.get_control('form.field.addables')
        self.assertEqual(
            form.get_control('form.field.acquire').checked,
            True)
        self.assertItemsEqual(
            form.get_control('form.field.addables').value,
            ['Silva Folder', 'Silva File', 'Silva Image'])

        # Now change the values
        form.get_control('form.field.acquire').checked = False
        form.get_control('form.field.addables').value = [
            'Silva Folder', 'Silva Link', 'Silva AutoTOC']
        self.assertEqual(browser.inspect.form_controls['save'].click(), 200)

        self.assertItemsEqual(
            browser.inspect.feedback,
            ['Changes to addables content types saved.'])

        form = browser.get_form('form')
        self.assertItemsEqual(
            form.get_control('form.field.addables').value,
            ['Silva Folder', 'Silva Link', 'Silva AutoTOC'])
        self.assertEqual(
            form.get_control('form.field.acquire').checked,
            False)

        # Entries in the add menu changed
        self.assertTrue('add' in browser.inspect.content_tabs)

        browser.inspect.content_tabs['add'].click()
        self.assertItemsEqual(
            browser.inspect.content_subtabs.keys(),
            ['Silva Folder', 'Silva Link', 'Silva AutoTOC'])


class ManagerAddablesTestCase(ChiefEditorAddablesTestCase):
    username = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ChiefEditorAddablesTestCase))
    suite.addTest(unittest.makeSuite(ManagerAddablesTestCase))
    return suite