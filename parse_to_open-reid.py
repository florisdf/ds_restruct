import argparse
import re
import bisect
import os

special_chars = {
    'image_id': 'i',
    'camera_id': 'c',
    'person_id': 'p',
    'slash': '/',
    'escape': '\\',
    'dont_care': '*'
}

# Get the positions of all the special characters
def get_special_chars_positions(string):
    return {char: [m.start() for m in re.finditer(re.escape(char), string)]
            for _, char in special_chars.items()}

# Check if the string has the correct format and that all paths are reachable
def generic_path(string):
    char_positions = get_special_chars_positions(string)
    # The generic path must contain a reference to the image-id ("i")
    if len(char_positions[special_chars['image_id']]) is 0:
        raise argparse.ArgumentTypeError(
            'There is no reference to the image-id ("{}")'
            .format(special_chars['image_id']))

    # The path cannot contain more than one image-id, person-id or camera-id
    if len(char_positions[special_chars['image_id']]) > 1:
        raise argparse.ArgumentTypeError(
            'Only one image_id reference can be given.')
    if len(char_positions[special_chars['camera_id']]) > 1:
        raise argparse.ArgumentTypeError(
            'Only one camera_id reference can be given.')
    if len(char_positions[special_chars['person_id']]) > 1:
        raise argparse.ArgumentTypeError(
            'Only one person_id reference can be given.')

    # Two deeper-level characters after each other are not allowed
    chars_positions = char_positions[special_chars['slash']]
    sorted_pos, size = sorted(chars_positions), len(pos)
    if min([sorted_pos[i + 1] - sorted_pos[i]
            for i in range(size) if i + 1 < size]) == 1:
        raise argparse.ArgumentTypeError(
            'Two successive "{}" characters are not allowed.'
        .format(special_chars['slash']))

    # The generic path cannot start with a deeper-level character
    if min(pos) is 0:
        raise argparse.ArgumentTypeError(
            'It is not allowed to start the input format with a "{}".'
            .format(special_chars['slash']))

    return string

# Check if the string is a directory
def path(string):
    if not os.path.isdir(string):
        raise argparse.ArgumentTypeError(
            '"{}" is not a directory'
            .format(string))

parser = argparse.ArgumentParser(
    description="Transform a dataset into the open-reid format")
parser.add_argument('--ifor', help='The input format.\
                    Use "{camera_id}" for camera-id, "{person_id}" for person-id, "{image_id}" for image-id, "{slash}" for a deeper folder level and "{dont_care}" for a don\'t care.  Use "{escape}" to escape any of the special characters.\
                    The final part of the path is assumed to be the image.\
                    An id character ("{camera_id}", "{person_id}", "{image_id}") can only occur once.\
                    Camera-id ("{camera_id}") and person-id ("{person_id}") are optional, while th image-id("{image_id}") must be in the given string.\
                    If no camera-id (or person-id) is specified, the images will be assumed to all have the same camera-id(resp. person-id).'.format(**special_chars),
                    required=True, type=generic_path)

parser.add_argument('--top', help='Path to the top level of the dataset.\
                    Default: current path.', type=path)
args = parser.parse_args()

# Get all the id values corresponding to the given id character
def get_id_values(id_char, top_dir, general_path):
    chars_positions = get_special_chars_positions(general_path)
    id_positions = chars_positions[id_char]
    assert len(id_positions) is not 0
    slash_positions = sorted(chars_positions[special_chars['slash']])

    if len(slash_positions) is 0 or
    bisect.bisect_left(slash_positions, id_positions[0]) == 0:
        # The id will be found in this directory
        return None
    else:
        # Recursive call
        return None


def get_identities(top_dir, general_path):
    # Step through all the levels in the given path
    # Within each level, store all the necessary info about camera-id, image-id, person-id
    identities = {} # dict with person_id as key, 


# Iterate through all camera-id's

# Iterate through all person-id's

# Iterate through all image-id's

