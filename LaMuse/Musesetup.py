#  Copyright (c) 2022. Bart Lamiroy (Bart.Lamiroy@univ-reims.fr) and subsequent contributors
#  as per git commit history. All rights reserved.
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#

import os

version_number = '0.2.3-beta'

image_extensions = ["jpg", "gif", "png", "tga", "jpeg", "pgm", "pnm"]


def either(c):
    return f'[{c.lower()}{c.upper()}]' if c.isalpha() else c


image_extensions = [''.join(either(char) for char in ext) for ext in image_extensions]

segmentation_suffix = "_objets"
default_base_folder = os.path.dirname(__file__)

with open(f'{default_base_folder}/version_number') as vn:
    version_number = vn.readline()

# version_number = '0.2.3'

print(f"Default execution directory = {default_base_folder}")

# @Todo: Currently configuration data is packed with the software and stored in the /bin or /lib
#   directory after installation/deployment. This should be changed to a more convenient location
default_image_folder = f'{default_base_folder}/BaseImages'
default_background_folder = f'{default_base_folder}/Backgrounds'
default_substitute_folder = default_image_folder + segmentation_suffix
default_painting_folder = f'{default_base_folder}/Paintings'
default_interpretation_folder = './Interpretations'
default_watermark_file = f'{default_base_folder}/Watermark.png'
default_trace_file = f'lamuse_tuples.json'

mask_rcnn_config_file = f'{default_base_folder}/mask_rcnn_coco.h5'
