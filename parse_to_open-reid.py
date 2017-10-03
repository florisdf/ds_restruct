import argparse

# Check if the string has the correct format and that all paths are reachable
def generic_path(string):


parser = argparse.ArgumentParser(description="Transform a dataset into the\
                                 open-reid format")
parser.add_argument('--input_format', help='The input format. Use "c" for\
                    camera-id, "p" for person-id, "i" for image-id, "/" for\
                    a deeper folder level and "_" for a don\'t care.\
                    Use "\\" to escape any of the special characters.\
                    The final part of the path is assumed to be the image.\
                    An id character ("c", "p", "i") can only occur once. The\
                    camera-id ("c") and person-id ("p") are optional, while the
                    image-id ("i") must be in the given string. If no camera-id
                    (or person-id) is specified, the images will be assumed to\
                    all have the same camera-id (resp. person-id).',
                    type=str, required=True, type=generic_path)
parser.add_argument('--top_level', help='Path to the top level of the\
                    dataset. Default: current path.', type=str)
args = parser.parse_args()
print(args)

# Iterate through all camera-id's

# Iterate through all person-id's

# Iterate through all image-id's

# How many levels deeper than the current level do we need to go to find the id
# specified by the character?
def find_id_level(id_char, input_format):
