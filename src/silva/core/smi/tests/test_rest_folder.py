# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.ftesting import rest_settings
from Products.Silva.testing import FunctionalLayer, Transaction
from silva.core.cache.memcacheutils import Reset
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


MOCKUP_ICON = u'http://localhost/root/++resource++icon-Mockup-VersionedContent.png'


class AuthorFolderActionsTestCase(unittest.TestCase):
    layer = FunctionalLayer
    user = 'author'
    access = 'write'
    maxDiff = None

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login(self.user)
        self.get_id = getUtility(IIntIds).getId
        with Reset():
            with Transaction():
                factory = self.root.manage_addProduct['Silva']
                factory.manage_addFolder('folder', 'Folder')
                factory = self.root.folder.manage_addProduct['Silva']
                factory.manage_addMockupVersionedContent('document', 'Document')
                factory.manage_addFolder('information', 'Information')

    def test_delete_unexisting_content(self):
        """Test delete an unexisting content.
        """
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.delete',
                    method='POST',
                    form={'content': '42'}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertIsInstance(browser.json, dict)
            self.assertEquals(
                browser.json,
                {u'content': {
                        u'actions': {},
                        u'ifaces': [u'listing-changes']},
                 u'notifications': [{
                            u'category': u'error',
                            u'message': u'1 contents could not be found (they probably have been deleted).'}]})

    def test_delete_unpublished_folder(self):
        """Test deleting an unpublished folder.
        """
        information_id = self.get_id(self.root.folder.information)
        folder_id = self.get_id(self.root.folder)
        root_id = self.get_id(self.root)
        zope_id = self.get_id(self.root.__parent__)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.delete',
                    method='POST',
                    form={'content': folder_id}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertIsInstance(browser.json, dict)
            self.assertEquals(
                browser.json,
                {u'content': {
                        u'actions': {u'remove': [folder_id]},
                        u'ifaces': [u'listing-changes']},
                 u'navigation': {
                        u'invalidation': [{
                                u'action': u'remove',
                                u'info': {
                                    u'target': u'nav%s' % information_id}}, {
                                u'action': u'remove',
                                u'info': {
                                    u'target': u'nav%s' % folder_id}}, {
                                u'action': u'update',
                                u'info': {
                                    u'parent': u'nav%s' % zope_id,
                                    u'position': -1,
                                    u'target': u'nav%s' % root_id}}]},
                 u'notifications': [{
                            u'category': u'feedback',
                            u'message': u'Deleted "Folder".'}]})

    def test_copy_unpublished_folder(self):
        """Test copying an unpublished folder.
        """
        folder_id = self.get_id(self.root.folder.information)
        root_id = self.get_id(self.root)
        zope_id = self.get_id(self.root.__parent__)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.paste',
                    method='POST',
                    form={'copied': folder_id}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertIsInstance(browser.json, dict)
            copy = self.root._getOb('information', None)
            self.assertIsNot(copy, None)
            self.assertIsNot(self.root.folder._getOb('information', None), None)
            copy_id = self.get_id(copy)
            copy_date = copy.get_modification_datetime()
            self.assertIsNot(copy_date, None)
            self.assertEquals(
                browser.json,
                {u'content': {
                        u'actions': {
                            u'add': {
                                u'publishables': [{
                                        u'access': self.access,
                                        u'author': self.user,
                                        u'icon': u'silva_folder',
                                        u'id': copy_id,
                                        u'identifier': u'information',
                                        u'ifaces': [u'container'],
                                        u'modified': copy_date.strftime('%y/%m/%d %H:%M'),
                                        u'moveable': True,
                                        u'path': u'information',
                                        u'position': -1,
                                        u'status_next': None,
                                        u'status_public': None,
                                        u'title': u'Information'}]}},
                              u'ifaces': [u'listing-changes']},
                 u'navigation': {
                        u'invalidation': [{
                                u'action': u'add',
                                u'info': {
                                    u'parent': u'nav%s' % root_id,
                                    u'position': -1,
                                    u'target': u'nav%s' % copy_id}}, {
                                u'action': u'update',
                                u'info': {
                                    u'parent': u'nav%s' % zope_id,
                                    u'position': -1,
                                    u'target': u'nav%s' % root_id}}]},
                 u'notifications': [{
                            u'category': u'feedback',
                            u'message': u'Pasted as a copy "Information".'}]})

    def test_copy_unpublished_document(self):
        """Test copying an unpublished document.
        """
        document_id = self.get_id(self.root.folder.document)
        root_id = self.get_id(self.root)
        zope_id = self.get_id(self.root.__parent__)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.paste',
                    method='POST',
                    form={'copied': document_id}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertIsInstance(browser.json, dict)
            copy = self.root._getOb('document', None)
            self.assertIsNot(copy, None)
            self.assertIsNot(self.root.folder._getOb('document', None), None)
            copy_id = self.get_id(copy)
            copy_date = copy.get_modification_datetime()
            self.assertIsNot(copy_date, None)
            self.assertEquals(
                browser.json,
                {u'content': {
                        u'actions': {
                            u'add': {
                                u'publishables': [{
                                        u'access': self.access,
                                        u'author': self.user,
                                        u'icon': MOCKUP_ICON,
                                        u'id': copy_id,
                                        u'identifier': u'document',
                                        u'ifaces': [u'versioned'],
                                        u'modified': copy_date.strftime('%y/%m/%d %H:%M'),
                                        u'moveable': True,
                                        u'path': u'document',
                                        u'position': -1,
                                        u'status_next': u'draft',
                                        u'status_public': None,
                                        u'title': u'Document'}]}},
                              u'ifaces': [u'listing-changes']},
                 u'navigation': {
                        u'invalidation': [{
                                u'action': u'update',
                                u'info': {
                                    u'parent': u'nav%s' % zope_id,
                                    u'position': -1,
                                    u'target': u'nav%s' % root_id}}]},
                 u'notifications': [{
                            u'category': u'feedback',
                            u'message': u'Pasted as a copy "Document".'}]})

    def test_moving_unpublished_document(self):
        """Test moving an unpublished document using the REST interface.
        """
        document_id = self.get_id(self.root.folder.document)
        root_id = self.get_id(self.root)
        folder_id = self.get_id(self.root.folder)
        zope_id = self.get_id(self.root.__parent__)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/++rest++silva.ui.listing.paste',
                    method='POST',
                    form={'cutted': document_id}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertIsInstance(browser.json, dict)
            self.assertIsNot(self.root._getOb('document', None), None)
            self.assertIs(self.root.folder._getOb('document', None), None)
            document_date = self.root.document.get_modification_datetime()
            folder_date = self.root.folder.get_modification_datetime()
            self.assertEquals(
                browser.json,
                {u'content': {
                        u'actions': {
                            u'add': {
                                u'publishables': [{
                                        u'access': self.access,
                                        u'author': self.user,
                                        u'icon': MOCKUP_ICON,
                                        u'id': document_id,
                                        u'identifier': u'document',
                                        u'ifaces': [u'versioned'],
                                        u'modified': document_date.strftime('%y/%m/%d %H:%M'),
                                        u'moveable': True,
                                        u'path': u'document',
                                        u'position': -1,
                                        u'status_next': u'draft',
                                        u'status_public': None,
                                        u'title': u'Document'}]},
                            u'update': [{
                                    u'access': self.access,
                                    u'author': self.user,
                                    u'icon': u'silva_folder',
                                    u'id': folder_id,
                                    u'identifier': u'folder',
                                    u'ifaces': [u'container'],
                                    u'modified': folder_date.strftime('%y/%m/%d %H:%M'),
                                    u'moveable': True,
                                    u'path': u'folder',
                                    u'position': 1,
                                    u'status_next': None,
                                    u'status_public': None,
                                    u'title': u'Folder'}]},
                        u'ifaces': [u'listing-changes']},
                 u'navigation': {
                        u'invalidation': [{
                                u'action': u'update',
                                u'info': {u'parent': u'nav%s' % root_id,
                                          u'position': 1,
                                          u'target': u'nav%s' % folder_id}}, {
                                u'action': u'update',
                                u'info': {
                                    u'parent': u'nav%s' % zope_id,
                                    u'position': -1,
                                    u'target': u'nav%s' % root_id}}]},
                 u'notifications': [{
                            u'category': u'feedback',
                            u'message': u'Moved "Document".'}]})

    def test_publish_document(self):
        """Test publishing a document from the REST interface.
        """
        document_id = self.get_id(self.root.folder.document)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/folder/++rest++silva.ui.listing.publish',
                    method='POST',
                    form={'content': document_id}),
                401)


class EditorFolderActionsTestCase(AuthorFolderActionsTestCase):
    user = 'editor'
    access = 'publish'

    def test_publish_document(self):
        """Test publishing a document from the REST interface.
        """
        document_id = self.get_id(self.root.folder.document)
        with self.layer.get_browser(rest_settings) as browser:
            browser.login(self.user)
            self.assertEqual(
                browser.open(
                    '/root/folder/++rest++silva.ui.listing.publish',
                    method='POST',
                    form={'content': document_id}),
                200)
            self.assertEqual(
                browser.content_type,
                'application/json')
            self.assertIsInstance(browser.json, dict)
            document_date = self.root.folder.document.get_modification_datetime()
            self.assertEqual(
                browser.json,
                {u'content': {
                        u'actions': {
                            u'update': [{
                                    u'access': self.access,
                                    u'author': self.user,
                                    u'icon': MOCKUP_ICON,
                                    u'id': document_id,
                                    u'identifier': u'document',
                                    u'ifaces': [u'versioned'],
                                    u'modified': document_date.strftime('%y/%m/%d %H:%M'),
                                    u'moveable': True,
                                    u'path': u'folder/document',
                                    u'position': 1,
                                    u'status_next': None,
                                    u'status_public': u'published',
                                    u'title': u'Document'}]},
                        u'ifaces': [u'listing-changes']},
                 u'notifications': [{
                            u'category': u'feedback',
                            u'message': u'Published "Document".'}]})


class ChiefEditorFolderActionsTestCase(EditorFolderActionsTestCase):
    user = 'chiefeditor'
    access = 'manage'


class ManagerFolderActionsTestCase(ChiefEditorFolderActionsTestCase):
    user = 'manager'


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorFolderActionsTestCase))
    suite.addTest(unittest.makeSuite(EditorFolderActionsTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorFolderActionsTestCase))
    suite.addTest(unittest.makeSuite(ManagerFolderActionsTestCase))
    return suite
