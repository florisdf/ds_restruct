#!/usr/bin/env python
import argparse
from placeholder import *

# Check if the string has the correct format
def generic_path(string):
    all_positions = get_iform_placeholders_positions(string)
    # The generic path must contain an image-id placeholder
    if len(all_positions[IMAGE_ID]) == 0:
        raise argparse.ArgumentTypeError(
            'There is no reference to the image-id ("{}")'
            .format(IMAGE_ID))

    # The path cannot contain more than one image-id, person-id
    # or camera-id placeholder
    unique_ids = [IMAGE_ID, CAMERA_ID, PERSON_ID]
    for placeholder in unique_ids:
        if len(all_positions[placeholder]) > 1:
            raise argparse.ArgumentTypeError(
            '"{}" must be unique in the input format.'.format(placeholder))

    # Two placeholders or an placeholder and a don't care
    # after each other are not allowed ("forbidden twins")
    forbidden_twins = [IMAGE_ID, CAMERA_ID, PERSON_ID, DONT_CARE]
    for ft1, ft2 in itertools.combinations(forbidden_twins, 2):
        if are_placeholders_successive(ft1, ft2, string):
            err = 'Characters "{}" and "{}" cannot be successive.'.format(ft1, ft2)
            raise argparse.ArgumentTypeError(err)

    # Two successive slashes are not allowed
    if are_placeholders_successive(SLASH, SLASH, string):
        raise argparse.ArgumentTypeError(
            'Two successive slashes are not allowed')

    # The generic path cannot start with a slash placeholder
    if min(all_positions[SLASH]) == 0:
        raise argparse.ArgumentTypeError(
            'It is not allowed to start the input format with a slash.')
    return string

# Check if the string is a directory
def path(string):
    if not os.path.isdir(string):
        raise argparse.ArgumentTypeError(
            '"{}" is not a directory'
            .format(string))
    return string

parser = argparse.ArgumentParser(
    description="Transform a dataset into the open-reid format")
parser.add_argument('--ifor', help='The input format.\
                    Use these placeholders: "{camera_id}" for camera-id, "{person_id}" for person-id, "{image_id}" for image-id, "{slash}" for a deeper folder level and "{dont_care}" for a don\'t care.  Use "{escape}" to escape any of the placeholders.\
                    The final part of the path is assumed to be the image.\
                    An id placeholder ("{camera_id}", "{person_id}", "{image_id}") can only occur once.\
                    Camera-id ("{camera_id}") and person-id ("{person_id}") are optional, while th image-id("{image_id}") must be in the given string.\
                    If no camera-id (or person-id) is specified, the images will be assumed to all have the same camera-id(resp. person-id).'.format(**iform_placeholders),
                    required=True, type=generic_path)

parser.add_argument('--top', help='Path to the top level of the dataset.\
                    Default: current path.', type=path, default='.')
args = parser.parse_args()


print(get_id_dicts_for_gpath({}, args.top, args.ifor))