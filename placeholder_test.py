#!/usr/bin/env python
import unittest
from unittest import mock
from placeholder import *
import pyfakefs.fake_filesystem as fake_fs

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
        files = get_id_dicts_for_gpath_part(gpath, '.')
        self.assertEqual(3, len(files))

    # TODO implement a working test (this one is not working)
    @mock.patch('placeholder.os.path.isdir')
    def test_get_id_dicts(self, mock_isdir):
        mock_isdir.return_value = True
        fs = fake_fs.FakeFilesystem()
        correct_ids = []
        # Generate a mock dataset
        for p in range(5):
            for c in range(3):
                for i in range(2):
                    # Correct file
                    path = '/home/patte/data/A{}/{}/{}.jpg'.format(p, c, i)
                    fs.CreateFile(path)
                    correct_ids.append({'p': p, 'c': c, 'i': i, 'path': path})
                    # Wrong file
                    fs.CreateFile('/home/patte/data/A{}/{}/{}'
                                  .format(p,c, i))
        top = '/home/patte'
        gpath = 'data/Ap/c/i.j\pg'
        self.assertEqual(correct_ids, get_id_dicts_for_gpath({}, top, gpath))

if __name__ == '__main__':
    unittest.main()
