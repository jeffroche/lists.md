# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import unittest
import web


class FlaskAppTestClient(unittest.TestCase):

    def setUp(self):
        self.app = web.app.test_client()

    def test_get_index_no_lists(self):
        rv = self.app.get('/')
        assert rv.status_code == 200
        if '<li>' not in rv.data:
            assert 'No lists found' in rv.data


if __name__ == '__main__':
    unittest.main()
