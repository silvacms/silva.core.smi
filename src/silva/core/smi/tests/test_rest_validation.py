# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
import json
from Products.Silva.testing import FunctionalLayer


class TestRESTIDValidation(unittest.TestCase):

    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        self.folder = self.root._getOb('folder')
        self.assertIsNot(None, self.folder)

        factory = self.folder.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('existing', 'Existing')
        self.content = self.folder._getOb('existing')
        self.assertIsNot(None, self.content)

    def test_id_valid(self):
        with self.layer.get_browser() as browser:
            browser.options.handle_errors = False
            browser.login('author')
            status = browser.open(
                'http://localhost/root/folder/++rest++silva.ui/adding/'
                'Silva Publication/++rest++zeam.form.silva.validate',
                form={'addform.field.id': 'notexisting',
                      'prefix.field': 'addform.field.id',
                      'prefix.form': 'addform'},
                method='POST')
            self.assertEqual(200, status)
            self.assertEqual('application/json', browser.content_type)
            data = json.loads(browser.contents)
            self.assertEqual(data['success'], True)

    def test_id_exists(self):
        with self.layer.get_browser() as browser:
            browser.options.handle_errors = False
            browser.login('author')
            status = browser.open(
                'http://localhost/root/folder/++rest++silva.ui/adding/'
                'Silva Publication/++rest++zeam.form.silva.validate',
                form={'addform.field.id': 'existing',
                      'prefix.field': 'addform.field.id',
                      'prefix.form': 'addform'},
                method='POST')
            self.assertEqual(200, status)
            self.assertEqual('application/json', browser.content_type)
            data = json.loads(browser.contents)
            self.assertEqual(data['success'], False)
            self.assertEqual(
                'There is already an object with the'
                ' id existing in this container.',
                data['errors']['addform.field.id'])

    def test_id_invalid(self):
        with self.layer.get_browser() as browser:
            browser.options.handle_errors = False
            browser.login('author')
            status = browser.open(
                'http://localhost/root/folder/++rest++silva.ui/adding/'
                'Silva Publication/++rest++zeam.form.silva.validate',
                form={'addform.field.id': 'in  v alid',
                      'prefix.field': 'addform.field.id',
                      'prefix.form': 'addform'},
                method='POST')
            self.assertEqual(200, status)
            self.assertEqual('application/json', browser.content_type)
            data = json.loads(browser.contents)
            self.assertEqual(data['success'], False)
            self.assertTrue(data['errors']['addform.field.id'].startswith(
                'The id contains strange characters.'))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRESTIDValidation))
    return suite

