#!/usr/bin/env python
import argparse
from placeholder import *

# Check if the string has the correct format
def generic_path(string):
    all_positions = get_gpath_placeholders_positions(string)
    # The generic path must contain an image-id placeholder
    if len(all_positions[IMAGE_ID]) == 0:
        raise argparse.ArgumentTypeError(
            'There is no reference to the image-id ("{}")'.format(IMAGE_ID))

    # The path cannot contain more than one image-id, person-id
    # or camera-id placeholder
    for placeholder in id_placeholders:
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
    if len(all_positions[SLASH]) > 0 and min(all_positions[SLASH]) == 0:
        raise argparse.ArgumentTypeError(
            'It is not allowed to start the input format with a slash.')
    return string

# Check if the string is a correct "reassign" argument
def reassign(string):
    if not re.match(reassign_regex, string):
        raise argparse.ArgumentTypeError(
            '"{}" is not a correct reassign argument'
            .format(string))
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
                    If no camera-id (or person-id) is specified, the images will be assumed to all have the same camera-id(resp. person-id).'.format(**gpath_placeholders),
                    required=True, type=generic_path)

parser.add_argument('--itop', help='Path to the top level of the input dataset.\
                    Default: current path.', type=path, default='.')

parser.add_argument('--ofor', help='The output format.', required=True, type=generic_path)

parser.add_argument('--otop', help='Path to the top level of the output', default='.')

parser.add_argument('-r', '--reassign', help='Reassign how one or more id types will be represented in the output format. Should match regex: "{}". E.g. "2dc1wi3dp" could give a file with a name like "012-04-f.jpg" where the person id is "012", the camera id is "04" and the image id is "f".)'.format(reassign_regex), type=reassign)

args = parser.parse_args()
for cmd in generate_cp_commands(args.ifor, args.itop, args.ofor, args.otop, args.reassign):
    print(cmd)
