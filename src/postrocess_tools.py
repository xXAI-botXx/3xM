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

def depth_postprocess(depth_source_path, depth_output_path):
    if os.path.exists(depth_output_path):
        shutil.rmtree(depth_output_path)
    
    os.makedirs(depth_output_path, exist_ok=True)

    all_depth = []
    for cur_depth in os.listdir(depth_source_path):
        if any([cur_depth.endswith(i) for i in [".png", ".jpg"]]):
            all_depth += [cur_depth]

    # run all tasks as fast as possible
    Parallel(n_jobs=-1)(
        delayed(depth_postprocess)(cur_depth_name, depth_source_path, depth_output_path)
        for cur_depth_name in all_depth
    )

    print("Successfull finsihed Depth preparation!")

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




# if __name__ == "__main__":

    # creating grey depth images from RGB depth
    # depth_postprocess(depth_source_path, depth_prep_path)

    # coco_postprocess
    # coco_postprocess(rgb_folder=rgb_source_path, mask_folder=mask_prep_path, output_json=coco_json_path)


