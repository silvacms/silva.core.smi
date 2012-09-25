# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from zope.component import getUtility
from Products.Silva.ftesting import rest_settings
from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import BrokenReferenceError
from silva.core.references.reference import get_content_id


class BreakReferenceTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'editor'

    def setUp(self):
        self.root = self.layer.get_application()
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFile('file', 'File')
            factory.manage_addLink('data', 'Link to File', target=self.root.file)

    def test_delete_referenced_content(self):
        with self.layer.get_browser(rest_settings) as browser:
            browser.options.handle_errors = False
            browser.login(self.user)
            with self.assertRaises(BrokenReferenceError):
                browser.open(
                    '/root/++rest++silva.ui.listing.delete',
                    method="POST",
                    form={'content': get_content_id(self.root.file)})

    def test_break_references(self):
        get_references_to = getUtility(IReferenceService).get_references_to

        self.assertNotEqual(list(get_references_to(self.root.file)), [])
        self.assertIsNot(self.root._getOb('file'), None)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.delete',
                    method="POST",
                    form={'content': get_content_id(self.root.file)}),
                400)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertEqual(
                browser.open(
                    '/root/file/++rest++silva.core.smi.breakreferences',
                    method="POST",
                    form={'form.action.break-references': 'Break'}),
                401)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertNotEqual(list(get_references_to(self.root.file)), [])
            self.assertIsNot(self.root._getOb('file'), None)


class ManagerBreakReferenceTestCase(BreakReferenceTestCase):
    user = 'manager'

    def test_break_references(self):
        get_references_to = getUtility(IReferenceService).get_references_to

        self.assertNotEqual(list(get_references_to(self.root.file)), [])
        self.assertIsNot(self.root._getOb('file'), None)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.delete',
                    method="POST",
                    form={'content': get_content_id(self.root.file)}),
                400)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertEqual(
                browser.open(
                    '/root/file/++rest++silva.core.smi.breakreferences',
                    method="POST",
                    form={'form.action.break-references': 'Break'}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertItemsEqual(list(get_references_to(self.root.file)), [])
            self.assertIsNot(self.root._getOb('file'), None)
            # To debug this issue
            browser.options.handle_errors = False
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.delete',
                    method="POST",
                    form={'content': get_content_id(self.root.file)}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertIs(self.root._getOb('file', None), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BreakReferenceTestCase))
    suite.addTest(unittest.makeSuite(ManagerBreakReferenceTestCase))
    return suite
