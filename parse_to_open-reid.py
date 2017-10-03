import argparse
import re

special_chars = {
    'image_id': 'i',
    'camera_id' : 'c',
    'person_id' : 'p',
    'deeper_level' : '/',
    'escape' : '\\',
    'dont_care' : '_'
}

# Get the positions of all the special characters
def get_special_chars_positions(string):
    return {name: [m.start() for m in re.finditer(re.escape(char), string)]
           for name, char in special_chars.items()}

# Check if the string has the correct format and that all paths are reachable
def generic_path(string):
    # The generic path must contain a reference to the image-id ("i")
    if not "i" in string:
        argparse.ArgumentTypeError('{} does not contain "i".'.format(string))
    return "{}".format(string)


parser = argparse.ArgumentParser(description="Transform a dataset into the open-reid format")
parser.add_argument('--input_format', help='The input format.\
                    Use "{camera_id}" for camera-id, "{person_id}" for person-id, "{image_id}" for image-id, "{deeper_level}" for a deeper folder level and "{dont_care}" for a don\'t care.  Use "{escape}" to escape any of the special characters.\
                    The final part of the path is assumed to be the image.\
                    An id character ("{camera_id}", "{person_id}", "{image_id}") can only occur once.\
                    Camera-id ("{camera_id}") and person-id ("{person_id}") are optional, while th image-id("{image_id}") must be in the given string.\
                    If no camera-id (or person-id) is specified, the images will be assumed to all have the same camera-id(resp. person-id).'.format(**special_chars),
                    required=True, type=generic_path)

parser.add_argument('--top_level', help='Path to the top level of the dataset.\
                    Default: current path.', type=str)
args = parser.parse_args()
print(get_special_chars_positions(args.input_format))

# Iterate through all camera-id's

# Iterate through all person-id's

# Iterate through all image-id's

# How many levels deeper than the current level do we need to go to find the id
# specified by the character?


# def find_id_level(id_char, input_format):
