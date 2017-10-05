#!/usr/bin/env python
import unittest
from unittest import mock
from placeholder import *

class TestPlaceholder(unittest.TestCase):

    def test_placeholder_positions(self):
        gpath = "c/*-p/i.j\pg"
        positions = {
            'i': [6],
             'c': [0],
             'p': [4],
             '/': [1, 5],
             '\\': [9],
             '*': [2]
        }
        self.assertEqual(get_iform_placeholders_positions(gpath), positions)

    def test_successive(self):
        gpath = "p/*-i/*c"
        self.assertTrue(are_placeholders_successive("*", "c", gpath))
        self.assertFalse(are_placeholders_successive("p", "*", gpath))

    @mock.patch('placeholder.os.listdir')
    def test_matching_files(self, mock_listdir):
        mock_listdir.return_value = ['a.jpg', 'b.jpg', 'c.jpg', 'd']
        gpath = 'p.j\pg'
        files = get_files_matching_comp(gpath, '.')
        self.assertEqual(3, len(files))

if __name__ == '__main__':
    unittest.main()
