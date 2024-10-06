import os
import shutil
from enum import Enum

import numpy as np
import cv2

from concurrent.futures import ThreadPoolExecutor

class FORMATS(Enum):
    SINGLE_SCENE_DIR = 0
    DUAL_DIR = 1

def verify_mask_post_processing(original_mask, new_mask):
    # check object amounts
    rgb_mask_unqiue = np.unique(original_mask.reshape(-1, 3), axis=0)
    len_1 = len(rgb_mask_unqiue)

    grey_mask_unqiue = np.unique(new_mask.reshape(-1, 1), axis=0)
    len_2 = len(grey_mask_unqiue)

    if len_1 != len_2:
        raise ValueError(f"Validation failed: The amount of objects are wrong:\n    From {len_1-1} objects to {len_2-1} objects")
    
    # check object pixels
    unique_values_org, counts_org = np.unique(original_mask.reshape(-1, 3), axis=0, return_counts=True)
    unique_values_new, counts_new = np.unique(new_mask.reshape(-1, 1), axis=0, return_counts=True)

    for cur_count_amount in counts_new:
        if not cur_count_amount in counts_org:
            raise ValueError(f"Validation failed: One or more amount of mask-pixel are wrong (the sequence order is not important):\n    -> Original Pixel-amount = {counts_org}\n    -> New Pixel-amount = {counts_new}")
        
    return True

def rgb_mask_to_grey_mask(rgb_img):
    """
    Tries to transform a RGB Mask to a Grey Mask. Every unique RGB Value should be a new increasing number = 1, 2, 3, 4, 5, 6

    And 0, 0, 0 should be 0
    """
    height, width, channels = rgb_img.shape

    # init new mask with only 0 -> everything is background
    grey_mask = np.zeros((height, width), dtype=np.uint8)

   # Get unique RGB values for every row (axis = 0) and before tranform in a simple 2D rgb array
    unique_rgb_values = np.unique(rgb_img.reshape(-1, rgb_img.shape[2]), axis=0)
    
    # Create a mapping from RGB values to increasing integers
    rgb_to_grey = {}
    counter = 1  # Start with 1 since 0 will be reserved for black
    for cur_rgb_value in unique_rgb_values:
        if not np.array_equal(cur_rgb_value, [0, 0, 0]):  # Exclude black
            rgb_to_grey[tuple(cur_rgb_value)] = counter
            counter += 1
        else:
            rgb_to_grey[tuple([0, 0, 0])] = 0

    # Fill the grey mask using the mapping
    for y in range(height):
        for x in range(width):
            rgb_tuple = tuple(rgb_img[y, x])
            grey_mask[y, x] = rgb_to_grey[rgb_tuple] # rgb_to_grey.get(rgb_tuple, 0)  # Default to 0 for black

    # Verify Transaction
    print("Verify transaction...")
    verify_mask_post_processing(original_mask=rgb_img, new_mask=grey_mask)

    print("Successfull Created a grey mask!")

    return grey_mask

def mask_postprocess(source_path, format=FORMATS.SINGLE_SCENE_DIR):
    if format == FORMATS.SINGLE_SCENE_DIR:
        for cur_dataset_dir in os.listdir(source_path):
            for cur_scene_dir in os.listdir(os.path.join(source_path, cur_dataset_dir)):
                for cur_file in os.listdir(os.path.join(source_path, cur_dataset_dir, cur_scene_dir)):
                    if cur_file.startswith("mask"):
                        mask_rgb_img = cv2.imread(os.path.join(source_path, cur_dataset_dir, cur_scene_dir, cur_file))
                        if mask_rgb_img is not None:
                            grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
                            cv2.imwrite(os.path.join(source_path, cur_dataset_dir, cur_scene_dir, f"grey_{cur_file}"), grey_mask)

    elif format == FORMATS.DUAL_DIR:
        pass


# def to_dual_dir_and_mask_postprocess(source_path, output_path):
#     """
#     Change SINGLE_DCENE_DIR Format to DUAL_DIR format and make mask postprocess.

#     From:
#     cam_1
#     ........raw_1.png
#     ........mask_1.png
#     cam_2
#     ...

#     to

#     color_images
#     ........raw_1.png
#     ........raw_2.png
#     ...
#     masks
#     ........mask_1.png
#     ...
#     """
#     if os.path.exists(output_path):
#         shutil.rmtree(output_path)
    
#     os.makedirs(output_path, exist_ok=True)

#     mask_path = os.path.join(output_path, "masks")
#     color_path = os.path.join(output_path, "color_images")
    
#     os.makedirs(mask_path, exist_ok=True)
#     os.makedirs(color_path, exist_ok=True)

#     idx = 0
#     for cur_scene_dir in os.listdir(source_path):
#         grey_mask = None
#         rgb_img = None
#         for cur_file in os.listdir(os.path.join(source_path, cur_scene_dir)):
#             if cur_file.startswith("mask"):
#                 mask_rgb_img = cv2.imread(os.path.join(source_path, cur_scene_dir, cur_file))
#                 if mask_rgb_img is not None:
#                     grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
                    
#             elif cur_file.startswith("raw"):
#                 rgb_img = cv2.imread(os.path.join(source_path, cur_scene_dir, cur_file))
                
#         if rgb_img is not None and grey_mask is not None:
#             cv2.imwrite(os.path.join(mask_path, f"image_{idx:08}.png"), grey_mask)
#             cv2.imwrite(os.path.join(color_path, f"image_{idx:08}.png"), rgb_img)
#             idx += 1


def move_scene_files(cur_scene_dir, source_path, mask_path, color_path, idx):
    grey_mask = None
    rgb_img = None
    for cur_file in os.listdir(os.path.join(source_path, cur_scene_dir)):
        if cur_file.startswith("mask"):
            mask_rgb_img = cv2.imread(os.path.join(source_path, cur_scene_dir, cur_file))
            if mask_rgb_img is not None:
                grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
                
        elif cur_file.startswith("raw"):
            rgb_img = cv2.imread(os.path.join(source_path, cur_scene_dir, cur_file))

    if rgb_img is not None and grey_mask is not None:
        cv2.imwrite(os.path.join(mask_path, f"image_{idx:08}.png"), grey_mask)
        cv2.imwrite(os.path.join(color_path, f"image_{idx:08}.png"), rgb_img)

def to_dual_dir_and_mask_postprocess(source_path, output_path, max_workers=4):
    """
    Change SINGLE_DCENE_DIR Format to DUAL_DIR format and make mask postprocess.
    """
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    
    os.makedirs(output_path, exist_ok=True)

    mask_path = os.path.join(output_path, "masks")
    color_path = os.path.join(output_path, "color_images")
    
    os.makedirs(mask_path, exist_ok=True)
    os.makedirs(color_path, exist_ok=True)

    scene_dirs = os.listdir(source_path)
    
    # Parallel processing using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for idx, cur_scene_dir in enumerate(scene_dirs):
            futures.append(executor.submit(
                move_scene_files, cur_scene_dir, source_path, mask_path, color_path, idx
            ))
        
        # Optionally wait for all futures to complete
        for future in futures:
            future.result()


if __name__ == "__main__":
    # source_path = "D:/Informatik/Projekte/3xM/3xM"
    # mask_postprocess(source_path=source_path)

    cur_dataset = "3xM_Dataset_0_1_1"
    source_path = f"/home/local-admin/Downloads/{cur_dataset}"   # /{cur_dataset}
    output_path = f"/home/local-admin/data/3xM/{cur_dataset}"
    to_dual_dir_and_mask_postprocess(source_path=source_path, output_path=output_path)


