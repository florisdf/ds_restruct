#!/usr/bin/env python
import argparse
import re
import bisect
import os
import itertools

# For debugging vvv
import inspect
def lineno():
    return inspect.currentframe().f_back.f_lineno
# For debugging ^^^

IMAGE_ID = 'i'
CAMERA_ID = 'c'
PERSON_ID = 'p'
SLASH = '/'
ESCAPE = '\\'
DONT_CARE = '*'

iform_placeholders = {
    'image_id': IMAGE_ID,
    'camera_id': CAMERA_ID,
    'person_id': PERSON_ID,
    'slash': SLASH,
    'escape': ESCAPE,
    'dont_care': DONT_CARE
}

# Get the positions of all the placeholders
def get_iform_placeholders_positions(string):
    return {placeholder: [m.start() for m in re.finditer(re.escape(placeholder), string)]
            for _, placeholder in iform_placeholders.items()}

# Check if two placeholders occur successively in generic_path
def are_placeholders_successive(placeholder1, placeholder2, generic_path):
    all_positions = get_iform_placeholders_positions(generic_path)
    placeholder1_positions = sorted(all_positions[placeholder1])
    placeholder2_positions = sorted(all_positions[placeholder2])
    if (len(placeholder1_positions) == 0 or len(placeholder2_positions) == 0):
        return False

    if min([abs(pos1 - pos2)
            for pos1 in placeholder1_positions
            for pos2 in placeholder2_positions]) == 1:
        return True
    return False

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
            '"{}" must be unique in the input format.')

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
                    Default: current path.', type=path)
args = parser.parse_args()

# Get all files in a directory that match a single generic_path_component
def get_files_matching_comp(generic_path_component, directory):
    assert os.path.isdir(directory)

    # Extract regex from generic_path_component 
    all_positions = get_iform_placeholders_positions(generic_path_component)
    assert(len(all_positions(SLASH)) == 0) # Cannot contain extra subdirs

    # Iterate through chars and build regex
    reg = ""
    escaped = False
    for c in generic_path_component:
        if escaped:
            reg += re.escape(c)
            escaped = False
        elif c == ESCAPE:
            escaped = True
        elif c in iform_placeholders.items():
            reg += ".*"
        else:
            reg += re.escape(c)

    return [d for d in os.listdir(directory) if re.search(reg, d)]

# Get all the placeholder values corresponding to the given placeholder
def get_id_placeholder_values(id_placeholder, top_dir, generic_path):
    all_positions = get_iform_placeholders_positions(generic_path)
    id_positions = all_positions[id_placeholder]
    assert len(id_positions) != 0
    slash_positions = sorted(all_positions[SLASH])

    if len(slash_positions) == 0 or bisect.bisect_left(slash_positions, id_positions[0]) == 0:
        # The id will be found in this directory. Use all files
        # that match the part before the first slash (if there are
        # any slashes) in generic_path.
        if len(slash_positions) == 0:
            # There are no slashes in generic_path
            # Scan through top_dir for matching filenames
            # and extract the id from it
            return None
    else:
        # Call to get_id_placeholder_values using as a new top_dir each directory
        # in top_dir that matches the part before the first slash in 
        # generic_path. Remove the part until the first slash from
        # generic_path and use it as new generic_path.
        return None


def get_identities(top_dir, generic_path):
    # Step through all the levels in the given path
    # Within each level, store all the necessary info about camera-id, image-id, person-id
    identities = {} # dict with person_id as key, 


# Iterate through all camera-id's

# Iterate through all person-id's

# Iterate through all image-id's

