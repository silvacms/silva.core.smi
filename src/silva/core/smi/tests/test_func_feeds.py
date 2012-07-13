# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Products.Silva.testing import FunctionalLayer, smi_settings


class FeedsTestCase(unittest.TestCase):
    """Test properties tab of a Folder.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Test Folder')

    def test_feeds(self):
        xml_browser = self.layer.get_browser()
        # By default feeds are off
        self.assertEqual(xml_browser.open('/root/folder/atom.xml'), 404)
        self.assertEqual(xml_browser.open('/root/folder/rss.xml'), 404)

        # We can enable it in settings
        browser = self.layer.get_web_browser(smi_settings)
        browser.login('manager')
        browser.open('/root/folder/edit')

        self.assertTrue('settings' in browser.inspect.content_tabs)
        self.assertEqual(browser.inspect.content_tabs['settings'].click(), 200)
        self.assertTrue('settings' in browser.inspect.content_subtabs)
        self.assertEqual(browser.inspect.content_subtabs['settings'].click(), 200)

        form = browser.get_form('form.feedsform')
        allow = form.get_control('form.feedsform.field.allow')
        self.assertEqual(allow.checked, False)
        allow.checked = True
        self.assertTrue('Change feed settings' in browser.inspect.form_controls)
        self.assertEqual(browser.inspect.form_controls['change feed settings'].click(), 200)
        self.assertEqual(browser.inspect.feedback, ['Feed settings saved.'])

        # Now feeds works
        self.assertEqual(xml_browser.open('/root/folder/atom.xml'), 200)
        self.assertEqual(xml_browser.content_type, 'text/xml;charset=UTF-8')
        self.assertEqual(xml_browser.open('/root/folder/rss.xml'), 200)
        self.assertEqual(xml_browser.content_type, 'text/xml;charset=UTF-8')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FeedsTestCase))
    return suite
