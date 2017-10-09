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
        self.assertEqual(get_gpath_placeholders_positions(gpath), positions)

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

    def test_hierarchy(self):
        id_dicts = [{'p': i, 'c': j+1, 'i': k}
                    for i in range(2)
                    for j in range(2)
                    for k in range(2)]
        hierarchy = "pci"
        correct_out_dict = {0: {1: [0, 1], 2: [0, 1]}, 1: {1: [0, 1], 2: [0, 1]}}
        self.assertEqual(correct_out_dict,
                         get_hierarchy_dict(hierarchy, id_dicts))

    # TODO this test is not working due to the randomness of dict ordering
    def test_index_id_dicts(self):
        id_dicts = [
            {'p': 'A', 'c': 0, 'i': 'a'},
            {'p': 'A', 'c': 0, 'i': 'b'},
            {'p': 'B', 'c': 0, 'i': 'e'},
            {'p': 'B', 'c': 1, 'i': 'e'},
            {'p': 'C', 'c': 0, 'i': 'g'},
            {'p': 'C', 'c': 1, 'i': 'i'}
        ]

        #correct_output = [
        #    {'p': 2, 'c': 0, 'i': 0},
        #    {'p': 2, 'c': 0, 'i': 1},
        #    {'p': 0, 'c': 0, 'i': 0},
        #    {'p': 0, 'c': 1, 'i': 0},
        #    {'p': 1, 'c': 0, 'i': 0},
        #    {'p': 1, 'c': 1, 'i': 0}
        #]
        #import pdb; pdb.set_trace()
        index_id_dicts('pci', id_dicts)
        print(id_dicts)

    def test_reassign(self):
        id_dicts = [{'p': i, 'c': 0, 'i': i} for i in range(5)]
        reass_str = "4p2c3i"
        correct_out_dict = [{'p': '000' + str(i), 'c': '00', 'i': '00' + str(i)}
                            for i in range(5)]
        self.assertEqual(correct_out_dict,
                         reassign_ids(id_dicts, reass_str))


    # TODO implement a working test (this one is not working)
    #@mock.patch('placeholder.os.path.isdir')
    #def test_get_id_dicts(self, mock_isdir):
    #    mock_isdir.return_value = True
    #    fs = fake_fs.FakeFilesystem()
    #    correct_ids = []
    #    # Generate a mock dataset
    #    for p in range(5):
    #        for c in range(3):
    #            for i in range(2):
    #                # Correct file
    #                path = '/home/patte/data/A{}/{}/{}.jpg'.format(p, c, i)
    #                fs.CreateFile(path)
    #                correct_ids.append({'p': p, 'c': c, 'i': i, 'path': path})
    #                # Wrong file
    #                fs.CreateFile('/home/patte/data/A{}/{}/{}'
    #                              .format(p,c, i))
    #    top = '/home/patte'
    #    gpath = 'data/Ap/c/i.j\pg'
    #    self.assertEqual(correct_ids, get_id_dicts_for_gpath({}, top, gpath))

if __name__ == '__main__':
    unittest.main()
