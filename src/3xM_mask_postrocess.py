import os
import shutil
from enum import Enum

import numpy as np
import cv2

from joblib import Parallel, delayed

from pycocotools import mask
import json



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

def mask_postprocess_single_scene_dir(source_path, format=FORMATS.SINGLE_SCENE_DIR):
    for cur_scene_dir in os.listdir(source_path):
        for cur_file in os.listdir(os.path.join(source_path, cur_scene_dir)):
            if cur_file.startswith("mask"):
                mask_rgb_img = cv2.imread(os.path.join(source_path, cur_scene_dir, cur_file))
                if mask_rgb_img is not None:
                    grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
                    cv2.imwrite(os.path.join(source_path, cur_scene_dir, f"grey_{cur_file}"), grey_mask)


def to_dual_dir_and_mask_postprocess(source_path, output_path, with_subfolders=True):
    """
    Change SINGLE_DCENE_DIR Format to DUAL_DIR format and make mask postprocess.

    From:
    cam_1
    ........raw_1.png
    ........mask_1.png
    cam_2
    ...

    to

    color_images
    ........raw_1.png
    ........raw_2.png
    ...
    masks
    ........mask_1.png
    ...
    """
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    
    os.makedirs(output_path, exist_ok=True)

    mask_path = os.path.join(output_path, "masks")
    color_path = os.path.join(output_path, "color_images")
    
    os.makedirs(mask_path, exist_ok=True)
    os.makedirs(color_path, exist_ok=True)
    
    # task_list = []

    # idx = 0
    # for cur_scene_dir in os.listdir(source_path):
    #     task_list += [lambda: move_scene_files(source_path, cur_scene_dir, mask_path, color_path, idx)]
    #     idx += 1
    
    if with_subfolders:
        all_scenes = []
        for cur_dir in os.listdir(source_path):
            for cur_scene in os.listdir(os.path.join(source_path, cur_dir)):
                all_scenes += [os.path.join(source_path, cur_dir, cur_scene)]
    else:
        all_scenes = []
        for cur_scene in os.listdir(source_path):
                all_scenes += [os.path.join(source_path, cur_scene)]
        
    # run all tasks as fast as possible
    Parallel(n_jobs=-1)(
        delayed(move_scene_files)(cur_scene_dir, mask_path, color_path, idx)
        for idx, cur_scene_dir in enumerate(all_scenes)
    )


def move_scene_files(cur_scene_dir, mask_path, color_path, idx):
    grey_mask = None
    rgb_img = None
    for cur_file in os.listdir(cur_scene_dir):
        if cur_file.startswith("mask"):
            mask_rgb_img = cv2.imread(os.path.join(cur_scene_dir, cur_file))
            if mask_rgb_img is not None:
                grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
                
        elif cur_file.startswith("raw"):
            # rgb_img = cv2.imread(os.path.join(cur_scene_dir, cur_file))
            rgb_img = os.path.join(cur_scene_dir, cur_file)

    if rgb_img is not None and grey_mask is not None:
        cv2.imwrite(os.path.join(mask_path, f"image_{idx:08}.png"), grey_mask)
        # cv2.imwrite(os.path.join(color_path, f"image_{idx:08}.png"), rgb_img)
        shutil.copy(rgb_img, os.path.join(color_path, f"image_{idx:08}.png"))

def mask_postprocess(mask_source_path, mask_output_path):
    """
    Make mask postprocess.
    """
    if os.path.exists(mask_output_path):
        shutil.rmtree(mask_output_path)
    
    os.makedirs(mask_output_path, exist_ok=True)

    all_masks = []
    for cur_mask in os.listdir(mask_source_path):
        if any([cur_mask.endswith(i) for i in [".png", ".jpg"]]):
            all_masks += [cur_mask]
        
    # run all tasks as fast as possible
    Parallel(n_jobs=-1)(
        delayed(move_mask)(cur_mask_name, mask_source_path, mask_output_path)
        for cur_mask_name in all_masks
    )

def move_mask(mask_name, source, output):
    mask_rgb_img = cv2.imread(os.path.join(source, mask_name))
    if mask_rgb_img is not None:
        grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
        cv2.imwrite(os.path.join(output, mask_name), grey_mask)


def create_coco_annotation(image_id, category_id, binary_mask, annotation_id):
    # Get the contours for the mask
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    segmentation = []

    for contour in contours:
        contour = contour.flatten().tolist()
        if len(contour) > 4:  # At least 2 points for a polygon
            segmentation.append(contour)
    
    rle = mask.encode(np.asfortranarray(binary_mask))  # RLE encoding
    bbox = cv2.boundingRect(binary_mask)  # Bounding box
    area = mask.area(rle)

    annotation = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "segmentation": segmentation,
        "area": float(area),
        "bbox": [bbox[0], bbox[1], bbox[2], bbox[3]],
        "iscrowd": 0
    }
    
    return annotation

def coco_postprocess(rgb_folder, mask_folder, output_json):
    images = []
    annotations = []
    categories = [{"id": 1, "name": "object"}]
    annotation_id = 1
    
    for idx, file_name in enumerate(os.listdir(rgb_folder)):
        if file_name.endswith('.png') or file_name.endswith('.jpg'):
            # Add image entry
            image_path = os.path.join(rgb_folder, file_name)
            mask_path = os.path.join(mask_folder, file_name)
            image = cv2.imread(image_path)
            height, width, _ = image.shape

            image_info = {
                "id": idx + 1,
                "file_name": file_name,
                "height": height,
                "width": width
            }
            images.append(image_info)
            
            # Load mask and generate annotations
            mask_img = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            unique_values = np.unique(mask_img)

            for val in unique_values:
                if val == 0:
                    continue  # Skip background
                
                binary_mask = np.where(mask_img == val, 1, 0).astype(np.uint8)
                annotation = create_coco_annotation(idx + 1, 1, binary_mask, annotation_id)
                annotations.append(annotation)
                annotation_id += 1
    
    coco_output = {
        "images": images,
        "annotations": annotations,
        "categories": categories
    }

    with open(output_json, 'w') as f:
        json.dump(coco_output, f, indent=4)


if __name__ == "__main__":
    # source_path = "D:/Informatik/Projekte/3xM/3xM"
    # mask_postprocess(source_path=source_path)

    cur_system = "/home/tobia"
    cur_dataset = "3xM_Dataset_1_1_TEST"
    source_path = f"~/Downloads/{cur_dataset}"   # /{cur_dataset}
    output_path = f"~/data/3xM/{cur_dataset}"

    rgb_source_path = f"{cur_system}/Downloads/{cur_dataset}/rgb"
    mask_source_path = f"{cur_system}/Downloads/{cur_dataset}/mask"
    mask_prep_path = f"{cur_system}/Downloads/{cur_dataset}/mask-prep"
    coco_json_path = f"{cur_system}/Downloads/{cur_dataset}/coco_annotations.json" 


    # to_dual_dir_and_mask_postprocess(source_path=source_path, output_path=output_path)

    # creating the grey mask from the rgb mask
    # mask_postprocess(mask_source_path=mask_source_path, mask_output_path=mask_prep_path)

    # coco_postprocess
    coco_postprocess(rgb_folder=rgb_source_path, mask_folder=mask_prep_path, output_json=coco_json_path)


