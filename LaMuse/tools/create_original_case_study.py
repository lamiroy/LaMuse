#  Copyright (c) 2022-2023. Bart Lamiroy (Bart.Lamiroy@univ-reims.fr) and subsequent contributors
#  as per git commit history. All rights reserved.
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#
#  La Muse, Leveraging Artificial Intelligence for Sparking Inspiration
#  https://hal.archives-ouvertes.fr/hal-03470467/
#
#  This code is licenced under the GNU LESSER GENERAL PUBLIC LICENSE
#  Version 3, 29 June 2007
#
import shutil
from glob import glob
from math import fabs, log
import numpy as np
from numpy import Inf
import cv2
import random

from .MaskRCNNModel import MaskRCNNModel
from .fast_style_transfer import apply_style_transfer
from .compare_images import best_image
from .generate_segmented_pictures import get_segmented_mask
from ..Musesetup import *

# @Todo find out why there are global variables and how to (maybe) get rid of them
# object_file_list = {}
object_image_list_nested = {}
object_image_list = []


def create_image_with_shapes(background_image: np.ndarray, painting: np.ndarray, r: dict, cursor) -> tuple:
    """
    Replace the objects on the background using shapes corresponding to the painting

    :param background_image:
    :param painting:
    :param r:
    :param cursor:
    :return:
    """
    # @TODO : find how to make images not looking blue

    nb_element = r['class_ids'].size
    real_value = None

    # dispach the value of the cursor between all elements
    if nb_element != 0:
        cursor = cursor / nb_element

    for i in range(nb_element):
        # print("Replace a ", MaskRCNNModel.class_names[r['class_ids'][i]])
        # @TODO: find out why real_value is reset to 0.0
        real_value = 0.0

        shape_mask = get_segmented_mask(painting, r, i)
        cropped_shape = shape_mask[r['rois'][i][0]: r['rois'][i][2], r['rois'][i][1]: r['rois'][i][3]]  # crop the image
        """fig, axs = plt.subplots(1, 2)
        fig.suptitle(str(i))
        axs[0].imshow(target_image)
        axs[0].set_title("image de base")
        axs[1].imshow(segment)
        axs[1].set_title("image modèle")
        plt.show()"""

        # Pick object that best fit the hole
        if cropped_shape is not None:
            # get the image with the best shape
            # @TODO get rid of this global 'object_image_list' variable
            replacement_shape, result, _ = best_image(cropped_shape, object_image_list, cursor)
            real_value += result
            """fig, axs = plt.subplots(1, 2)
            fig.suptitle(str(i))
            axs[0].imshow(target_image)
            axs[0].set_title("image de base")
            axs[1].imshow(result_image)
            axs[1].set_title("image modèle")
            plt.show()"""

            # replacement_object = Image.fromarray(replacement_shape)  # convert to Image
            replacement_object = replacement_shape  # convert to Image

            # Définition des dimensions et du placement du futur objet à coller
            original_object_bbox = (r['rois'][i][1], r['rois'][i][0], r['rois'][i][3], r['rois'][i][2])
            original_object_width = original_object_bbox[2] - original_object_bbox[0]
            original_object_height = original_object_bbox[3] - original_object_bbox[1]

            # Resizing replacement_object to original_object dimensions.
            replacement_object = cv2.resize(replacement_object, (original_object_width, original_object_height))

            # Paste replacement_object into background_image using alpha channel
            # background_image.paste(replacement_object, (r['rois'][i][1], r['rois'][i][0]), replacement_object)

            y1, y2 = r['rois'][i][0], r['rois'][i][2]
            x1, x2 = r['rois'][i][1], r['rois'][i][3]

            alpha_s = replacement_object[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                background_image[y1:y2, x1:x2, c] = (alpha_s * replacement_object[:, :, c] +
                                                     alpha_l * background_image[y1:y2, x1:x2, c])
        else:
            print("Warning : None image")

    return background_image, real_value


def create_image_with_categories_and_shapes(background_image, painting, r, cursor):
    nb_element = r['class_ids'].size
    real_value = None
    # dispach the value of the cursor between all elements
    if nb_element != 0:
        cursor = cursor / nb_element

    for i in range(nb_element):

        current_class = MaskRCNNModel.class_names[r['class_ids'][i]]
        # print("Replace a ", current_class)
        real_value = 0.0

        source_mask = get_segmented_mask(painting, r, i)
        source_mask = source_mask[r['rois'][i][0]: r['rois'][i][2], r['rois'][i][1]: r['rois'][i][3]]  # crop the image

        # Pick object that best fits the hole
        if source_mask is not None:
            # get the image with the best shape
            result_image, result, _ = best_image(source_mask, object_image_list_nested[current_class], cursor)
            real_value += result

            # replacement_object = Image.fromarray(result_image)  # convert to Image
            replacement_object = result_image  # convert to Image

            # Définition des dimensions et du placement du futur objet à coller
            original_object_bbox = (r['rois'][i][1], r['rois'][i][0], r['rois'][i][3], r['rois'][i][2])
            original_object_width = original_object_bbox[2] - original_object_bbox[0]
            original_object_height = original_object_bbox[3] - original_object_bbox[1]

            # Resizing replacement_object to original_object dimensions.
            replacement_object = cv2.resize(replacement_object, (original_object_width, original_object_height))

            # Paste replacement_object into background_image using alpha channel
            # background_image.paste(replacement_object, (r['rois'][i][1], r['rois'][i][0]), replacement_object)

            y1, y2 = r['rois'][i][0], r['rois'][i][2]
            x1, x2 = r['rois'][i][1], r['rois'][i][3]

            alpha_s = replacement_object[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                background_image[y1:y2, x1:x2, c] = (alpha_s * replacement_object[:, :, c] +
                                                     alpha_l * background_image[y1:y2, x1:x2, c])
        else:
            print("Warning : None image")

    return background_image, real_value


# replace the objects on the background using categories corresponding to the painting
def create_image_with_categories(background_image, painting, r, cursor):
    for i in range(r['class_ids'].size):

        current_class = MaskRCNNModel.class_names[r['class_ids'][i]]
        # print("Replace a ", current_class)

        # Définition des dimensions et du placement du futur objet à coller
        original_object_bbox = (r['rois'][i][1], r['rois'][i][0], r['rois'][i][3], r['rois'][i][2])
        original_object_width = original_object_bbox[2] - original_object_bbox[0]
        original_object_height = original_object_bbox[3] - original_object_bbox[1]
        original_object_size = original_object_width * original_object_height

        # get image in the painting (as done when generating images)
        # Pick a random object
        try:
            # @Todo: transform hard-coded 3.0 value to a parameter
            similar_objects = [i for i in object_image_list_nested[current_class] if
                               fabs(log(i.size / original_object_size)) < 3.0]
            if len(similar_objects) == 0:
                similar_objects = object_image_list_nested[current_class]

            # replacement_object = Image.fromarray(random.choice(similar_objects))
            replacement_object = random.choice(similar_objects)

        except IndexError:
            print("Cannot find", current_class)  # , "in", path_to_substitute_objects, "for", painting_name)
            break

        # Resizing replacement_object to original_object dimensions.
        replacement_object = cv2.resize(replacement_object, (original_object_width, original_object_height))

        # Paste replacement_object into background_image using alpha channel
        # background_image.paste(replacement_object, (r['rois'][i][1], r['rois'][i][0]), replacement_object)

        y1, y2 = r['rois'][i][0], r['rois'][i][2]
        x1, x2 = r['rois'][i][1], r['rois'][i][3]

        alpha_s = replacement_object[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        for c in range(0, 3):
            background_image[y1:y2, x1:x2, c] = (alpha_s * replacement_object[:, :, c] +
                                                 alpha_l * background_image[y1:y2, x1:x2, c])

    return background_image, 0


def create_collage(path_to_paintings: str, path_to_substitute_objects: str,
                   path_to_background_images: str,
                   path_to_results: str,
                   nb_paintings: int = 3,
                   bw_convert=False) -> dict:
    """
    :param bw_convert:
    :param path_to_paintings:
    :param path_to_substitute_objects:
    :param path_to_background_images:
    :param path_to_results:
    :param nb_paintings:
    :return:
    """
    path_to_results += '/'
    trace_log = {}

    cursor_step = 0
    if nb_paintings != 1:
        cursor_step = 20 / (nb_paintings - 1)  # cursor values in [0,20]

    '''
    list_of_methods = [create_image_with_shapes] * nb_paintings + [create_image_with_categories_and_shapes] * nb_paintings + [
        create_image_with_categories] * nb_paintings
    method_names = ["shapes", "shapes and categories", "categories"]
    '''
    list_of_methods = [create_image_with_categories] * nb_paintings
    method_names = ["categories"]

    if not os.path.exists(path_to_results):
        os.mkdir(path_to_results)

    # Run the model on the painting.
    model = MaskRCNNModel().model

    painting_file_list = [y for x in [glob(path_to_paintings + '/*.%s' % ext) for ext in image_extensions] for y in x]

    # print(f"Painting file list: {painting_file_list}")

    # List of available background images
    background_file_list = \
        [y for x in [glob(path_to_background_images + '/*.%s' % ext) for ext in image_extensions] for y in x]

    # print(f"Background file list: {background_file_list}")

    if len(object_image_list) == 0 or len(object_image_list_nested) == 0:
        print("Updating objects...")
        # List of candidate replacement objects
        for obj in MaskRCNNModel.class_names:
            # object_file_list[obj] = [y for x in [glob(path_to_substitute_objects + '/%s/*.%s' % (obj, ext))
            # for ext in image_extensions] for y in x]
            file_list = [y for x in [glob(path_to_substitute_objects + '/%s/*.%s' % (obj, ext))
                                     for ext in image_extensions] for y in x]
            object_image_list_nested[obj] = [cv2.imread(i, cv2.IMREAD_UNCHANGED) for i in file_list]
            [object_image_list.append(img) for img in object_image_list_nested[obj]]
        # for nested_list in object_file_list.values():
        # for i in nested_list:
        # object_image_list.append(cv2.imread(i, cv2.IMREAD_UNCHANGED))

    for painting_filename in painting_file_list:
        print("\nPainting : ", painting_filename)
        painting_name = os.path.basename(painting_filename)

        trace_log[painting_filename] = f'(painting_name,{painting_name})'

        #painting = load_img(painting_filename)
        #painting = img_to_array(painting)
        painting = cv2.imread(painting_filename)
        painting_width, painting_height = painting.shape[1], painting.shape[0]

        # Extract significant items from painting
        results = model.detect([painting], verbose=0, probability_criteria=0.7)
        detected_items = results[0]

        for class_id in detected_items['class_ids']:
            trace_log[painting_filename] += f'(contains,{MaskRCNNModel.class_names[class_id]})'

        cursor = 0
        j = 0

        # Generate a number of altered forms of painting for each technic
        for technic in list_of_methods:
            print("Painting number : ", j)

            # Pick a random background image
            try:
                background_image_name = random.choice(background_file_list)
            except IndexError:
                print(path_to_background_images + " is empty, taking initial image instead")
                background_image_name = painting_filename

            # background_image = Image.open(background_image_name)
            background_image = cv2.imread(background_image_name, cv2.IMREAD_UNCHANGED)

            trace_log[painting_filename] += f'(background_image,{background_image_name})'

            # Resize the background image with the size of painting.
            # background_image = background_image.resize((painting_width, painting_height), Image.ANTIALIAS)
            # background_image = background_image.convert("RGBA")

            background_image = cv2.resize(background_image, (painting_width, painting_height),
                                          interpolation=cv2.INTER_AREA)

            background_image, real_value = technic(background_image, painting, detected_items, cursor)
            if real_value is None:
                real_value = -1.0
            elif real_value > 1000.0:
                real_value = Inf
            # background_image, real_value = create_image_with_shapes(background_image, painting, r, cursor)

            if bw_convert:
                print("Converting to greyscale")
                # background_image = ImageOps.grayscale(background_image)
                # background_image = background_image.convert("BGR")
                # background_image.save(file_saved)
                background_image = cv2.cvtColor(background_image, cv2.COLOR_BGR2GRAY)
            else:
                print("No conversion")
                # background_image = background_image.convert("RGB")
                # background_image.save(file_saved)

            # Save background_image.
            file_saved = f'{path_to_results}{painting_name}-method={method_names[j // nb_paintings]}-value=' + '%.3f' % real_value + '.png'
            cv2.imwrite(file_saved, background_image)

            if False:  # Old experiment checking influence of image filtering kept for reference
                new_file_saved = path_to_results + painting_name + "-method=" + method_names[
                    j // nb_paintings] + "-value=" + '%.3f' % real_value + '-V2.png'
                apply_style_transfer(file_saved, background_image_name, new_file_saved)

                new_file_copy = path_to_results + 'No-' + painting_name + "-method=" + method_names[
                    j // nb_paintings] + "-value=" + '%.3f' % real_value + '-V2.png'
                shutil.copyfile(new_file_saved, new_file_copy)

            cursor += cursor_step  # to have different result for an image
            j += 1

    return trace_log


if __name__ == "__main__":
    painting_dir = default_painting_folder
    background_dir = default_background_folder
    output_dir = './NewRésultats2/'

    create_collage(painting_dir, default_substitute_folder, background_dir, output_dir)
