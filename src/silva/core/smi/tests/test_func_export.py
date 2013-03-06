# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
import unittest
import zipfile, os
from datetime import datetime
from lxml import etree
from StringIO import StringIO

from Products.Silva.testing import FunctionalLayer

NS = {
    'silva' : 'http://infrae.com/namespace/silva'
}


class TestExport(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.browser = self.layer.get_browser()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('publication', 'Publication')

    def test_export_form(self):
        self.browser.login('editor')
        status = self.browser.open(
            'http://localhost/root/edit/tab_status_export')
        self.assertEquals(200, status)

    def test_simple_export(self):
        self.browser.login('editor')
        status = self.browser.open(
            'http://localhost/root/edit/tab_status_export')
        self.assertEquals(200, status)
        form = self.browser.get_form('form')
        status = form.get_control('form.action.export').click()
        self.assertEquals(200, status)
        self.assertEquals(
            'application/octet-stream', self.browser.content_type)
        filename = 'root_export_%s.zip' % datetime.now().strftime('%Y-%m-%d')
        self.assertEquals('attachment;filename=%s' % filename,
                          self.browser.headers['content-disposition'])
        fd = StringIO(self.browser.contents)
        zdata = zipfile.ZipFile(fd, 'r')
        self.assertEquals(['silva.xml'], zdata.namelist())
        zdata.testzip()
        silvaxml = zdata.extract('silva.xml')
        try:
            tree = etree.parse(silvaxml)
            self.assertTrue(tree.xpath(
                '//silva:publication[@id="root"]', namespaces=NS))
            self.assertFalse(tree.xpath(
                '//silva:publication[@id="publication"]', namespaces=NS))
        finally:
            os.unlink(silvaxml)

    def test_export_form_with_sub_publication(self):
        self.browser.login('editor')
        status = self.browser.open(
            'http://localhost/root/edit/tab_status_export')
        self.assertEquals(200, status)
        form = self.browser.get_form('form')
        include_cbx = form.get_control('form.field.include_sub_publications')
        include_cbx.checked = True
        status = form.get_control('form.action.export').click()
        self.assertEquals(200, status)
        self.assertEquals(
            'application/octet-stream', self.browser.content_type)
        filename = 'root_export_%s.zip' % datetime.now().strftime('%Y-%m-%d')
        self.assertEquals('attachment;filename=%s' % filename,
                          self.browser.headers['content-disposition'])
        fd = StringIO(self.browser.contents)
        zdata = zipfile.ZipFile(fd, 'r')
        self.assertEquals(['silva.xml'], zdata.namelist())
        zdata.testzip()
        silvaxml = zdata.extract('silva.xml')
        try:
            tree = etree.parse(silvaxml)
            self.assertTrue(
                tree.xpath('//silva:publication[@id="root"]',
                           namespaces=NS))
            self.assertTrue(
                tree.xpath('//silva:publication[@id="publication"]',
                           namespaces=NS))
        finally:
            os.unlink(silvaxml)


def test_suite():
    suite = unittest.TestSuite()
    return suite
    suite.addTest(unittest.makeSuite(TestExport))
