
##################
# User Variables #
##################
SHOULD_UNZIP = False
ZIP_PATH = "/home/local-admin/Downloads/"

SOURCE_PATH = "/home/local-admin/data/3xM/3xM_Dataset_10_10"

WIDTH = 800
HEIGHT =  450



###########
# Imports #
###########
import os
import shutil
from datetime import datetime
import time

from joblib import Parallel, delayed

import numpy as np
import cv2



#############
# Functions #
#############
def get_time_str():
    now = datetime.now()
    return f"{now.hour:02}:{now.minute:02} {now.day:02}.{now.month:02}.{now.year:04}"

def calc_duration(start_time):
    current_time = time.time()
    duration = int(current_time - start_time)

    days = duration // (24 * 3600)  # Calculate days
    duration %= (24 * 3600)  # remaining seconds
    hours = duration // 3600  # Calculate hours
    duration %= 3600  # remaining seconds
    minutes = duration // 60  # Calculate minutes

    return f"{days} Days {hours} Hours {minutes} Minutes"

def clear_printing():
    # terminal
    os.system('cls' if os.name == 'nt' else 'clear')
    
def print_progress(current, total):
    progress = current / total
    progress_bar_size = 20
    progress_bar = int(progress * progress_bar_size)
    white_spaces = progress_bar_size - progress_bar
    print(f"[{'#' * progress_bar}{' ' * white_spaces}] {current}/{total} images processed.")

def resize(img, width, height, is_mask=False):
    """
    Resize the image to the given width and height.
    """
    if is_mask:
        method = cv2.INTER_NEAREST
    else:
        method = cv2.INTER_LINEAR
    
    cur_height, cur_width = img.shape[:2]
    if cur_height == height and cur_width == width:
        return img
    else:
        return cv2.resize(img, (width, height), interpolation=method)
    
def rgb_postprocess(rgb_name, source, output, width, height):
    source_path = os.path.join(source, rgb_name)
    output_path = os.path.join(output, rgb_name)

    img = cv2.imread(source_path)
    
    if img is not None:
        img = resize(img, width, height, is_mask=False)
        cv2.imwrite(output_path, img)

def depth_postprocess(depth_name, source, output, width, height):
    source_path = os.path.join(source, depth_name)
    output_path = os.path.join(output, depth_name)

    img = cv2.imread(source_path, cv2.IMREAD_UNCHANGED)
    
    if img is not None:

        # Convert the RGB image to grayscale (assuming depth is encoded in the G channel)
        _, grey_img, _, _ = cv2.split(img)
        grey_img = resize(grey_img, width, height, is_mask=False)
        cv2.imwrite(output_path, grey_img)
    
def mask_postprocess(mask_name, source, output, width, height):
    source_path = os.path.join(source, mask_name)
    output_path = os.path.join(output, mask_name)
    
    mask_rgb_img = cv2.imread(source_path, cv2.IMREAD_UNCHANGED)
    if mask_rgb_img is not None:
        grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
        grey_mask = resize(grey_mask, width, height, is_mask=True)
        cv2.imwrite(output_path, grey_mask)
        
def rgb_mask_to_grey_mask(rgb_img, verify=False):
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

    return grey_mask

def rgb_depth_mask_postprocess(name, source, width, height):
    
    rgb_postprocess(name, os.path.join(source, "rgb"), os.path.join(source, "rgb-prep"), width, height)
    depth_postprocess(name, os.path.join(source, "depth"), os.path.join(source, "depth-prep"), width, height)
    mask_postprocess(name, os.path.join(source, "mask"), os.path.join(source, "mask-prep"), width, height)


def postprocess(source_path, width, height, delete_original=False):
    """
    Postprocess rgb, depth and masks.
    
    RGB-Images get resized.
    
    Depth-Images get resized and transformed to grey images.
    
    Mask-Images get resized and transformed to grey images.
    """
    start_str = f"Start 3xM postprocessing! ({get_time_str()})"
    print(start_str)
    
    start_time = time.time()
    
    # Create all folders and make sure that they are empty
    if os.path.exists(os.path.join(source_path, "rgb-prep")):
        shutil.rmtree(os.path.join(source_path, "rgb-prep"))
    os.makedirs(os.path.join(source_path, "rgb-prep"), exist_ok=True)
    
    if os.path.exists(os.path.join(source_path, "depth-prep")):
        shutil.rmtree(os.path.join(source_path, "depth-prep"))
    os.makedirs(os.path.join(source_path, "depth-prep"), exist_ok=True)
    
    if os.path.exists(os.path.join(source_path, "mask-prep")):
        shutil.rmtree(os.path.join(source_path, "mask-prep"))
    os.makedirs(os.path.join(source_path, "mask-prep"), exist_ok=True)

    # find all images
    all_images = []
    for cur_image in os.listdir(os.path.join(source_path, "rgb")):
        if any([cur_image.endswith(i) for i in [".png", ".jpg"]]):
            all_images += [cur_image]
    total_images = len(all_images)
            
    def process_with_progress(cur_name, idx):
        clear_printing()
        print(start_str)
        print("")
        print_progress(idx, total_images)
        print(f"\n\n      -> Needed: {calc_duration(start_time)}")
        rgb_depth_mask_postprocess(cur_name, source_path, width, height)
        
    # run all tasks as fast as possible
    Parallel(n_jobs=-1)(
        delayed(process_with_progress)(cur_name, idx)
        for idx, cur_name in enumerate(all_images)
    )
    
    if delete_original:
        shutil.rmtree(os.path.join(source_path, "rgb"))
        shutil.rmtree(os.path.join(source_path, "depth"))
        shutil.rmtree(os.path.join(source_path, "mask"))

    print(f"\n\nSuccessfull finsihed 3xM postprocessing! ({get_time_str()})")



################
# Run the code #
################
if __name__ == "__main__":
    
    # Unzip the download files
    if SHOULD_UNZIP:
        pass

    # Postprocessing
    postprocess(source_path=SOURCE_PATH, width=WIDTH, height=HEIGHT)




