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
    return { placeholder:
            [
                m.start() for m in
                re.finditer(r'([^\\]|^)' + re.escape(placeholder), string)
            ]
            for _, placeholder in iform_placeholders.items()
           }

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

# Get all files in a directory that match a single generic_path_component
def get_files_matching_comp(generic_path_component, directory):
    import pdb; pdb.set_trace()
    assert os.path.isdir(directory)

    # Extract regex from generic_path_component 
    all_positions = get_iform_placeholders_positions(generic_path_component)
    assert(len(all_positions[SLASH]) == 0) # Cannot contain extra subdirs

    # Iterate through chars and build regex
    reg = ""
    escaped = False
    for c in generic_path_component:
        if escaped:
            reg += re.escape(c)
            escaped = False
        elif c == ESCAPE:
            escaped = True
        elif c in iform_placeholders.values():
            reg += ".*"
        else:
            reg += re.escape(c)
    print("This is the regex: " + reg)
    return [d for d in os.listdir(directory) if re.search(reg, d)]

# Get all the placeholder values corresponding to the given placeholder
def get_id_placeholder_values(id_placeholder, top_dir, generic_path):
    all_positions = get_iform_placeholders_positions(generic_path)
    id_positions = all_positions[id_placeholder]
    print(lineno())
    print(all_positions)
    assert len(id_positions) == 1
    slash_positions = sorted(all_positions[SLASH])

    if len(slash_positions) == 0:
        # There are no slashes in generic_path.
        # Scan through top_dir for matching filenames
        # and extract the id from it
        print(lineno())
        return get_files_matching_comp(generic_path, top_dir)
    elif bisect.bisect_left(slash_positions, id_positions[0]) == 0:
        # The id will be found in this directory. Use all files
        # that match the part before the first slash in generic_path.
        print("gp: {} top: {} id: {}".format(generic_path, top_dir, id_placeholder))
        new_gp = generic_path[:slash_positions[0]]
        print("newgp: {} top: {}".format(new_gp, top_dir))
        return get_files_matching_comp(new_gp, top_dir)
    else:
        # Recursive call to get_id_placeholder_values using as a new top_dir
        # each directory in top_dir that matches the part before the 
        # first slash in generic_path. Remove the part until the first
        # slash from generic_path and use it as new generic_path.
        print(lineno())
        new_gp = generic_path[slash_positions[0] : slash_positions[1]]
        return [item for sublist in
                get_id_placeholder_values(id_placeholder, new_td, new_gp)
                for new_td in get_files_matching_comp(gen_p, top_d)
                for item in sublist]
