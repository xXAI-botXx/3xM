"""
Formatting the OCID (Object Clutter Indoor Dataset) Dataset in a dual dir format, where only 2 folders with color images and masks exist.

Download the dataset here: https://www.acin.tuwien.ac.at/en/vision-for-robotics/software-tools/object-clutter-indoor-dataset/
Or here: https://researchdata.tuwien.at/records/pcbjd-4wa12
"""

import os
import shutil

import numpy as np
import cv2

def has_an_object(mask_img_path):
    mask_img = cv2.imread(mask_img_path, cv2.IMREAD_UNCHANGED)
    uniques = np.unique(mask_img)

    if len(uniques) > 1:
        return True
    else:
        return False

source_path = "/home/tobia/data/3xM/3xM-Test/OCID-dataset"
output_path = "/home/tobia/data/3xM/3xM-Test/OCID-dataset-prep"

# clear and create output path
if os.path.exists(output_path):
    shutil.rmtree(output_path)

os.makedirs(output_path, exist_ok=True)

mask_path = os.path.join(output_path, "masks")
color_path = os.path.join(output_path, "rgb")
depth_path = os.path.join(output_path, "depth")

os.makedirs(mask_path, exist_ok=True)
os.makedirs(color_path, exist_ok=True)
os.makedirs(depth_path, exist_ok=True)


cur_idx = 0
for cur_root, cur_dirs, cur_files in os.walk(source_path):
    if "rgb" in cur_dirs and "label" in cur_dirs:
        for cur_image_name in os.listdir(os.path.join(cur_root, "rgb")):
            image = os.path.join(cur_root, "rgb", cur_image_name)
            depth = os.path.join(cur_root, "depth", cur_image_name)
            mask = os.path.join(cur_root, "label", cur_image_name)

            if os.path.exists(image) and os.path.exists(mask):
                if has_an_object(mask_img_path=mask):
                    shutil.copy(image, os.path.join(color_path, f"image_{cur_idx:08}.png"))

                    # shutil.copy(image, os.path.join(depth_path, f"image_{cur_idx:08}.png"))
                    depth_img = cv2.imread(depth, cv2.IMREAD_UNCHANGED)
                    depth_img = depth_img.astype(np.uint8)
                    cv2.imwrite(os.path.join(depth_path, f"image_{cur_idx:08}.png"), depth_img)

                    # shutil.copy(mask, os.path.join(mask_path, f"image_{cur_idx:08}.png"))
                    mask_img = cv2.imread(mask, cv2.IMREAD_UNCHANGED)
                    mask_img = mask_img.astype(np.uint8)
                    cv2.imwrite(os.path.join(mask_path, f"image_{cur_idx:08}.png"), mask_img)

                    cur_idx += 1
                    print("Successfull transfered images!")
                else:
                    print(f"Mask has no objects: {mask}")

