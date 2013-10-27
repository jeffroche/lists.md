# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import listsdotmd
import unittest
from dropbox.rest import ErrorResponse
from datetime import datetime as dt


class DropboxTestSuite(unittest.TestCase):
    """Test connection to Dropbox API"""

    def test_get_dropbox_token(self):
        self.assertNotEqual(listsdotmd.DROPBOX_TOKEN, None)

    def test_connect_dropbox_success(self):
        try:
            db_client = listsdotmd.connect_to_dropbox()
        except ValueError:
            self.fail(msg="Bad token")
        try:
            account = db_client.account_info()
        except ErrorResponse as e:
            print e
            self.fail()
        self.assertIn('uid', account)

    def test_connect_dropbox_fail(self):
        bad_token = 'rawr'
        db_client = listsdotmd.connect_to_dropbox(token=bad_token)
        with self.assertRaises(ErrorResponse):
            db_client.account_info()


class ListsdotmdTestSuite(unittest.TestCase):
    """Test each listsdotmd function"""

    def test_index_lists(self):
        """Should return a list of the .md files in the folder"""
        db_client = MockDropboxClient()
        file_list = listsdotmd.index_lists(db_client, '/')
        _expected_list = [
            {'path': '/list1.md',
             'name': 'list1',
             'updated': 'Thu, 25 Aug 2011 00:03:15 +0000'},
            {'path': '/list2.md',
             'name': 'list2',
             'updated': 'Thu, 25 Aug 2011 00:03:15 +0000'}]
        self.assertEqual(file_list, _expected_list)

    def test_load_list_as_string(self):
        """Should load the text of a test markdown file"""
        db_client = MockDropboxClient()
        list_str = listsdotmd.load_list_as_string(db_client, 'list1.md')
        _expected_str = """# List 1\n\n- list item 1\n- list item 2"""
        self.assertEqual(list_str, _expected_str)

    def test_markdown_conversion(self):
        """Should correctly generate HTML from the test markdown file"""
        db_client = MockDropboxClient()
        list_str = listsdotmd.load_list_as_string(db_client, 'list1.md')
        markup = listsdotmd.convert_list_to_html(list_str)
        _expected_html = u'<h1>List 1</h1>\n\n<ul>\n<li>list item 1</li>\n<li>list item 2</li>\n</ul>\n'
        self.assertEqual(markup, _expected_html)

    def test_folder_last_update_time(self):
        db_client = MockDropboxClient()
        last_updated = listsdotmd.last_update_time(db_client, '/')
        last_updated_dt = dt.strptime(last_updated, '%a, %d %b %Y %H:%M:%S +0000')
        self.assertEqual(last_updated_dt,
            dt(2011, 4, 27, 22, 18, 51))


class MockDropboxClient(object):
    """A test class to mock the outputs of Dropbox"""

    def metadata(self, folder):
        if folder == '/':
            result = \
            {
                'bytes': 0,
                'contents': [
                    {
                       'bytes': 0,
                       'icon': 'folder',
                       'is_dir': True,
                       'modified': 'Thu, 25 Aug 2011 00:03:15 +0000',
                       'path': '/Sample Folder',
                       'rev': '803beb471',
                       'revision': 8,
                       'root': 'dropbox',
                       'size': '0 bytes',
                       'thumb_exists': False
                    }, 
                    {
                       'bytes': 77,
                       'icon': 'page_white_text',
                       'is_dir': False,
                       'mime_type': 'text/plain',
                       'modified': 'Wed, 20 Jul 2011 22:04:50 +0000',
                       'path': '/magnum-opus.txt',
                       'rev': '362e2029684fe',
                       'revision': 221922,
                       'root': 'dropbox',
                       'size': '77 bytes',
                       'thumb_exists': False
                    }, 
                    {
                       'bytes': 77,
                       'icon': 'page_white_text',
                       'is_dir': False,
                       'mime_type': 'text/plain',
                       'modified': 'Thu, 25 Aug 2011 00:03:15 +0000',
                       'path': '/list1.md',
                       'rev': '362e2029684fe',
                       'revision': 221922,
                       'root': 'dropbox',
                       'size': '77 bytes',
                       'thumb_exists': False
                    }, 
                    {
                       'bytes': 77,
                       'icon': 'page_white_text',
                       'is_dir': False,
                       'mime_type': 'text/plain',
                       'modified': 'Thu, 25 Aug 2011 00:03:15 +0000',
                       'path': '/list2.md',
                       'rev': '362e2029684fe',
                       'revision': 221922,
                       'root': 'dropbox',
                       'size': '77 bytes',
                       'thumb_exists': False
                    }
                ],
                'hash': 'efdac89c4da886a9cece1927e6c22977',
                'icon': 'folder',
                'is_dir': True,
                'path': '/',
                'root': 'app_folder',
                'size': '0 bytes',
                "modified": "Wed, 27 Apr 2011 22:18:51 +0000",
                'thumb_exists': False
            }
        else:
            raise ErrorResponseMock
        return result

    def get_file_and_metadata(self, list_path):
        f = open(list_path)
        metadata = \
            {
               'bytes': 77,
               'icon': 'page_white_text',
               'is_dir': False,
               'mime_type': 'text/plain',
               'modified': 'Thu, 25 Aug 2011 00:03:15 +0000',
               'path': list_path,
               'rev': '362e2029684fe',
               'revision': 221922,
               'root': 'dropbox',
               'size': '77 bytes',
               'thumb_exists': False
            }
        return f, metadata

class ErrorResponseMock(Exception):
    """Dropbox client would throw an ErrorResponse"""
    pass


if __name__ == '__main__':
    unittest.main()