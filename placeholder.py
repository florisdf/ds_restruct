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

reassign_regex = "(([0-9]+)([p|c|i]))*"
id_placeholders = [IMAGE_ID, CAMERA_ID, PERSON_ID]
gpath_placeholders = {
    'image_id': IMAGE_ID,
    'camera_id': CAMERA_ID,
    'person_id': PERSON_ID,
    'slash': SLASH,
    'escape': ESCAPE,
    'dont_care': DONT_CARE
}

# Get the positions of all the placeholders
def get_gpath_placeholders_positions(string):
    positions = {c: [] for c in gpath_placeholders.values()}
    escaped = False
    counter = 0

    for c in string:
        if escaped:
            escaped = False
        elif c is ESCAPE:
            escaped = True
            positions[ESCAPE].append(counter)
        elif c in gpath_placeholders.values():
            positions[c].append(counter)
        counter += 1

    return positions

# Check if two placeholders occur successively in generic_path
def are_placeholders_successive(placeholder1, placeholder2, generic_path):
    assert(placeholder1 in gpath_placeholders.values())
    assert(placeholder2 in gpath_placeholders.values())
    all_positions = get_gpath_placeholders_positions(generic_path)
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
    # Extract regex from generic_path_part 
    all_positions = get_gpath_placeholders_positions(generic_path_part)
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
def get_id_dicts_for_gpath(generic_path, current_dir, id_dict={}):
    all_positions = get_gpath_placeholders_positions(generic_path)
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
                last_path_part, new_id_dict['path'], id_dict=new_id_dict))
        return id_dicts

# Create a dict that contains the width for each id_placeholder
def get_reassign_list(reass_str):
    reass_list = []
    for id_ph in id_placeholders:
        m = re.search('([0-9]+)({})'.format(id_ph), reass_str)
        if m: reass_list.append((id_ph, "{{:0{}d}}".format(m.group(1))))
    return reass_list

def get_hierarchy_dict(hierarchy, flat_dicts):
    assert(len(hierarchy) > 0)
    id_ph = hierarchy[0]
    if len(hierarchy) == 1:
        return [flat_dict[id_ph] for flat_dict in flat_dicts]
    all_id_values = list({flat_dict[id_ph]
                         for flat_dict in flat_dicts
                         if id_ph in flat_dict.keys()})
    all_id_value_dicts = {id_value:
                          [id_value_dict for id_value_dict in flat_dicts
                          if id_value_dict[id_ph] is id_value]
                         for id_value in all_id_values}
    return {id_value:
            get_hierarchy_dict(
                hierarchy[1:],
                all_id_value_dicts[id_value])
            for id_value in all_id_values}

# Turn the id values in id_dicts into indexed values.
def index_id_dicts(hierarchy, id_dicts, hierarchy_dict=None):
    assert(len(hierarchy) > 0)
    if not hierarchy_dict:
        hierarchy_dict = get_hierarchy_dict(hierarchy, id_dicts)
    id_ph = hierarchy[0]
    # Get a list of all the id values of the first id placeholder in hierarchy
    id_values = list(hierarchy_dict)
    for id_val in id_values:
        # Get all the id_dicts that have this id_val
        selected_dicts = [id_dict for id_dict in id_dicts
                          if id_ph in id_dict.keys()
                          and id_dict[id_ph] is id_val]
        for id_dict in selected_dicts:
            id_dict[id_ph] = id_values.index(id_val)
        if len(hierarchy) > 1:
            index_id_dicts(hierarchy[1:],
                           selected_dicts,
                           hierarchy_dict[id_val])
    return id_dicts

def reassign_ids(id_dicts, reass_str):
    reass_list = get_reassign_list(reass_str)
    reass_dict = {id_ph: id_val for (id_ph, id_val) in reass_list}
    #hierarchy = str([c for c, _ in reass_list])
    hierarchy = 'pci' # TODO parse hierarchy from reass_str
    index_id_dicts(hierarchy, id_dicts)
    for id_ph in id_placeholders:
        for id_dict in id_dicts:
            if not id_ph in id_dict.keys(): continue
            id_dict[id_ph] = reass_dict[id_ph].format(int(id_dict[id_ph]))
    return id_dicts


# Using a list of id-dicts, generate code to copy them into a format defined by a generic_path
def generate_cp_commands(i_gpath, i_dir, o_gpath, o_dir, reassign_str):
    id_dicts = get_id_dicts_for_gpath(i_gpath, i_dir)
    id_dicts = reassign_ids(id_dicts, reassign_str)
    output_positions = get_gpath_placeholders_positions(o_gpath)
    commands = []
    newly_created_dirs= []
    for id_dict in id_dicts:
        # Parse ids into o_gpath
        escaped = False
        o_file = ""
        for c in o_gpath:
            if escaped:
                o_file += c
                escaped = False
            elif c == ESCAPE:
                escaped = True
            elif c in id_placeholders:
                if c in id_dict.keys(): o_file += id_dict[c]
            else:
                o_file += c
        # Join o_file and o_dir
        o_full_path = os.path.join(o_dir, o_file)
        # Create cp command that copies original -> destination
        dirname = os.path.dirname(o_full_path)
        cmd = ''
        if not dirname in newly_created_dirs:
            cmd += 'mkdir -p {} && '.format(dirname)
            newly_created_dirs.append(dirname)
        cmd += 'cp {} {}'.format(id_dict['path'], o_full_path)
        commands.append(cmd)
    return commands
