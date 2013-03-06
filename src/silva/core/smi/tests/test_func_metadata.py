# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility
from silva.core.services.interfaces import IMetadataService

from Products.Silva.testing import FunctionalLayer, CatalogTransaction
from Products.Silva.ftesting import smi_settings


class AuthorMetadataTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        with CatalogTransaction():
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addMockupVersionedContent('document', 'Document')

    def test_content_draft_metadata(self):
        browser = self.layer.get_web_browser(smi_settings)
        browser.login(self.user)

        self.assertEqual(
            browser.inspect.listing,
            [{'title': u'Document',
              'identifier': 'document',
              'author': 'editor'}])
        self.assertEqual(browser.inspect.listing[0].goto.click(), 200)

        # Access publish tab
        self.assertTrue('Properties' in browser.inspect.tabs)
        self.assertTrue(browser.inspect.tabs['Properties'].name.click(), 200)
        self.assertEqual(browser.inspect.form, ['Editable item properties'])

        # You can edit editable metadata
        # There two times the controls to save the metadata
        form = browser.inspect.form['Editable item properties']
        self.assertEqual(
            form.fields,
            [u'keywords', u'short title', u'contact name', u'title',
             u'contact email', u'subject', u'comment', u'language',
             u'description'])
        self.assertEqual(form.fields['title'].value, 'Document')
        self.assertEqual(form.fields['short title'].value, '')
        self.assertEqual(form.fields['comment'].value, '')
        form.fields['title'].value = 'New document'
        form.fields['short title'].value = 'Document'
        form.fields['comment'].value = u'Ce document a été récement créé.'
        self.assertEqual(
            form.actions,
            ['Cancel', 'Save changes', 'Cancel', 'Save changes'])
        self.assertEqual(
            form.actions.get('Save changes', multiple=True)[0].click(),
            200)
        browser.macros.assertFeedback('Metadata saved.')

        # Metadata changes. So the title
        self.assertEqual(browser.inspect.title, 'New document')
        self.assertEqual(browser.inspect.form, ['Editable item properties'])

        form = browser.inspect.form['Editable item properties']
        self.assertEqual(
            form.fields,
            [u'keywords', u'short title', u'contact name', u'title',
             u'contact email', u'subject', u'comment', u'language',
             u'description'])
        self.assertEqual(form.fields['title'].value, 'New document')
        self.assertEqual(form.fields['short title'].value, 'Document')
        self.assertEqual(
            form.fields['comment'].value,
            u'Ce document a été récement créé.')

        metadata = getUtility(IMetadataService).getMetadata(self.root.document)
        self.assertEqual(
            metadata.get('silva-content', 'maintitle'),
            'New document')
        self.assertEqual(
            metadata.get('silva-content', 'shorttitle'),
            'Document')
        self.assertEqual(
            metadata.get('silva-extra', 'comment'),
            u'Ce document a été récement créé.')


class EditorMetadataTestCase(AuthorMetadataTestCase):
    user = 'editor'


class ChiefEditorMetadataTestCase(EditorMetadataTestCase):
    user = 'chiefeditor'


class ManagerMetadataTestCase(ChiefEditorMetadataTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorMetadataTestCase))
    suite.addTest(unittest.makeSuite(EditorMetadataTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorMetadataTestCase))
    suite.addTest(unittest.makeSuite(ManagerMetadataTestCase))
    return suite
