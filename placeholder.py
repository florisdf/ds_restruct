import re
import bisect
import os
import itertools
import copy

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

id_placeholders = [IMAGE_ID, CAMERA_ID, PERSON_ID]
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
    positions = {c: [] for c in iform_placeholders.values()}
    escaped = False
    counter = 0

    for c in string:
        if escaped:
            escaped = False
        elif c is ESCAPE:
            escaped = True
            positions[ESCAPE].append(counter)
        elif c in iform_placeholders.values():
            positions[c].append(counter)
        counter += 1

    return positions

# Check if two placeholders occur successively in generic_path
def are_placeholders_successive(placeholder1, placeholder2, generic_path):
    assert(placeholder1 in iform_placeholders.values())
    assert(placeholder2 in iform_placeholders.values())
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

# Get all files in a single directory that match a generic_path_part
def get_id_dicts_for_gpath_part(generic_path_part, directory):
    assert os.path.isdir(directory)

    # Extract regex from generic_path_part 
    all_positions = get_iform_placeholders_positions(generic_path_part)
    assert(len(all_positions[SLASH]) == 0) # Cannot contain extra subdirs

    # Iterate through chars and build regex
    reg = ""
    escaped = False
    for (index, c) in enumerate(list(generic_path_part)):
        if escaped:
            reg += re.escape(c)
            escaped = False
        elif c == ESCAPE:
            escaped = True
        elif c in id_placeholders:
            # Create a named group for id-placeholders, so we can refer to them
            # ! Group names must be valid Python identifiers
            reg += "(?P<{}>.*)".format(c)
        elif c == DONT_CARE:
            reg += ".*"
        else:
            reg += re.escape(c)

    # Match the files in this dir and parse id's
    id_dicts = []
    for d in os.listdir(directory):
        m = re.match(reg, d)
        if not m: continue
        id_dict = {id_ph: m.group(id_ph) for id_ph in id_placeholders
                    if id_ph in m.groupdict().keys()}
        id_dict["path"] = os.path.join(directory, d)
        id_dicts.append(id_dict)
    return id_dicts

# Get a list of id-dicts
def get_id_dicts_for_gpath(id_dict, current_dir, generic_path):
    all_positions = get_iform_placeholders_positions(generic_path)
    slash_positions = sorted(all_positions[SLASH])

    if len(slash_positions) == 0:
        # There are no deeper folders, we reached the bottom.
        # List all files matching gpath and parse them into id-dicts.
        id_dicts = []
        for i in get_id_dicts_for_gpath_part(generic_path, current_dir):
            new_id_dict = copy.deepcopy(id_dict)
            new_id_dict.update(i)
            id_dicts.append(new_id_dict)
        return id_dicts
    else:
        # There are still deeper folders to explore!
        # List all files matching the first part of gpath.
        # Use these files for a recursive call.
        first_path_part = generic_path[:slash_positions[0]]
        assert(slash_positions[0] + 1 < len(generic_path))
        last_path_part = generic_path[slash_positions[0] + 1:]

        id_dicts = []
        for i in get_id_dicts_for_gpath_part(first_path_part, current_dir):
            new_id_dict = copy.deepcopy(id_dict)
            new_id_dict.update(i)
            id_dicts.extend(get_id_dicts_for_gpath(
                new_id_dict, new_id_dict['path'], last_path_part))
        return id_dicts
