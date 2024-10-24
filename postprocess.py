"""
Your Toolkit for 3xM Dataset

You can install the needed libs by installing the '3xm' conda env:
conda env create -f env.yml

- Downloading Datasets
- Extracting Datasets
- Postprocessing Datasets
    - Resizing
    - Extract Depth Image
    - RGB Mask to Grey Mask
    
By Tobia Ippolito <3
"""

# just some pre definitions, so they can be used. Go to the user variables to set your settings
from enum import Enum

class DATASET(Enum):
    TRIPPLE_M_10_10 = "https://drive.google.com/drive/folders/1Mjb_jZNVumyeDrmD8S3hCO1sG0UFpBCs?usp=sharing"
    TRIPPLE_M_10_80 = "https://drive.google.com/drive/folders/1swAx8cONBohY0ojsE4DZlmY-YK0ieRRI?usp=sharing"
    
class DOWNLOAD_SOURCE(Enum):
    KAGGLE = lambda path, url: download_from_kaggle(path, url)
    ONEDRIVE = lambda path, url: download_from_onedrive(path, url)
    GOOGLEDRIVE = lambda path, url: download_from_googledrive(path, url)

##################
# User Variables #
##################
SHOULD_DOWNLOAD = False
TARGET_PATH = ""
DATSET_FOR_DOWNLOAD = DATASET.TRIPPLE_M_10_10
SOURCE_FOR_DOWNLOAD = DOWNLOAD_SOURCE.GOOGLEDRIVE

SHOULD_UNZIP = False
DOWNLOAD_UNZIP_PATH = "/home/local-admin/Downloads/"

# Goal for unzipping and source for postproces
SOURCE_PATH = "/home/local-admin/data/3xM/3xM_Dataset_10_10"

SHOULD_POST_PROCESS = True
ONLY_MASK_CONVERTION = True
DELETE_ORIGINAL = True
WIDTH = 1920
HEIGHT =  1080



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

import zipfile
import py7zr

import subprocess
import requests
import gdown


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

# Functions for Downloading
def download_from_kaggle(target_path: str, download_url: str):
    """Downloads the dataset from Kaggle using the Kaggle API."""
    try:
        # Make sure Kaggle is installed: conda install -c conda-forge kaggle
        subprocess.run(
            ['kaggle', 'datasets', 'download', '-d', download_url, '-p', target_path],
            shell=True, 
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error downloading dataset: {e}")
        raise
    
def download_from_onedrive(target_path:str, download_url:str):
    response = requests.get(download_url)
    with open(target_path, "wb") as f:
        f.write(response.content)
        
def download_from_googledrive(target_path:str, download_url:str):
    gdown.download_folder(download_url, output=target_path, quiet=False)
    
def download_dataset(
                target_path:str, 
                dataset:DATASET, 
                source:DOWNLOAD_SOURCE
            ):
    
    # create and update target path
    shapes, textures = dataset.name.split("_")[-2:]
    dataset_name = f"3xM_Dataset_{shapes}_{textures}"
    target_path = os.path.join(target_path, dataset_name)
    
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    os.makedirs(target_path, exist_ok=True)
    
    # download the files from kaggle, onedrive or googledrive
    if source == DOWNLOAD_SOURCE.KAGGLE:
        download_from_kaggle(target_path=target_path, download_url=dataset.value)
    elif source == DOWNLOAD_SOURCE.ONEDRIVE:
        target_path = os.path.join(target_path, f"{dataset_name}.zip")
        download_from_onedrive(target_path=target_path, download_url=dataset.value)
    elif source == DOWNLOAD_SOURCE.GOOGLEDRIVE:
        download_from_googledrive(target_path=target_path, download_url=dataset.value)

# Functions for Zip Extraction
def move_all_files(source_dir, destination_dir):
    if os.path.exists(source_dir):
        for filename in os.listdir(source_dir):
            source_file = os.path.join(source_dir, filename)
            
            if os.path.isfile(source_file):
                destination_file = os.path.join(destination_dir, filename)
                shutil.move(source_file, destination_file)

def extract_zip_folders(source_dir, destination_dir):
    print("Start dataset extraction...")
    
    # Check if source and destination directories exist
    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Source directory '{source_dir}' does not exist.")
        return
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    else:
        shutil.rmtree(destination_dir)
        
    rgb_path = os.path.join(destination_dir, "rgb")
    os.makedirs(rgb_path)
    depth_path = os.path.join(destination_dir, "depth")
    os.makedirs(depth_path)
    mask_path = os.path.join(destination_dir, "mask")
    os.makedirs(mask_path)


    # start extracting
    error_files = []
    successfull = 0
    
    # Iterate over all files in the source directory
    for file_name in os.listdir(source_dir):
        # Check if the file is a zip file
        if file_name.endswith(".zip") or file_name.endswith(".7z"):
            file_path = os.path.join(source_dir, file_name)
            
            # Create a folder with the same name as the zip file (without .zip) in the destination directory
            extract_folder = os.path.join(source_dir, ".".join(file_name.split(".")[:-1]))
            if not os.path.exists(extract_folder):
                os.makedirs(extract_folder)
            else:
                shutil.rmtree(extract_folder)
            
            try:
                if file_name.endswith(".zip"):
                    # Unzip the file
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                elif file_name.endswith(".7z"):
                    with py7zr.SevenZipFile(file_path, mode='r') as zip_ref:
                        zip_ref.extractall(path=extract_folder)
                        
                # move files to target
                inner_folder_name  = os.listdir(extract_folder)[0]
                source_rgb_path = os.path.join(extract_folder, inner_folder_name, "rgb")
                source_depth_path = os.path.join(extract_folder, inner_folder_name, "depth")
                source_mask_path = os.path.join(extract_folder, inner_folder_name, "mask")
                move_all_files(source_rgb_path, rgb_path)
                move_all_files(source_depth_path, depth_path)
                move_all_files(source_mask_path, mask_path)

                successfull += 1
            except Exception as e:
                error_files += [file_path]
                print(f"Error during extracting {file_name} to {extract_folder}")
                continue
            
            print(f"Extracted: {file_name} to {destination_dir}")
        else:
            error_files += [file_path]
            print(f"Error during extracting {file_name} = (is not a supported zip-format)")

    shutil.rmtree(source_dir)

    print(f"\n\nErrors: {len(error_files)}")
    for cur_err_file in error_files:
        print(f"    -> {cur_err_file}")

    print(f"\nSuccesfull: {successfull}")

# functions for postprocessing
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
    
def mask_postprocess(mask_name, source, output, width, height, should_resize=False):
    source_path = os.path.join(source, mask_name)
    output_path = os.path.join(output, mask_name)
    
    mask_rgb_img = cv2.imread(source_path, cv2.IMREAD_UNCHANGED)
    if mask_rgb_img is not None:
        grey_mask = rgb_mask_to_grey_mask(mask_rgb_img)
        if should_resize:
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

def rgb_depth_mask_postprocess(name, source, width, height, only_mask_convertion):
    
    if only_mask_convertion == False:
        rgb_postprocess(name, os.path.join(source, "rgb"), os.path.join(source, "rgb-prep"), width, height)
        depth_postprocess(name, os.path.join(source, "depth"), os.path.join(source, "depth-prep"), width, height)
    mask_postprocess(name, os.path.join(source, "mask"), os.path.join(source, "mask-prep"), width, height, should_resize=(not only_mask_convertion))


def postprocess(source_path, width, height, only_mask_convertion=True, delete_original=False):
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
    if only_mask_convertion == False:
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
    for cur_image in os.listdir(os.path.join(source_path, "mask")):
        if any([cur_image.endswith(i) for i in [".png", ".jpg"]]):
            all_images += [cur_image]
    total_images = len(all_images)
            
    def process_with_progress(cur_name, idx):
        clear_printing()
        print(start_str)
        print("")
        print_progress(idx, total_images)
        print(f"\n\n      -> Needed: {calc_duration(start_time)}")
        if cur_name is not None:
            rgb_depth_mask_postprocess(cur_name, source_path, width, height, only_mask_convertion)
        
    # run all tasks as fast as possible
    Parallel(n_jobs=-1)(
        delayed(process_with_progress)(cur_name, idx)
        for idx, cur_name in enumerate(all_images)
    )
    
    if delete_original:
        if only_mask_convertion == False:
            shutil.rmtree(os.path.join(source_path, "rgb"))
            shutil.rmtree(os.path.join(source_path, "depth"))
        shutil.rmtree(os.path.join(source_path, "mask"))

    process_with_progress(None, total_images)
    print(f"\n\nSuccessfull finsihed 3xM postprocessing! ({get_time_str()})")



################
# Run the code #
################
if __name__ == "__main__":
    
    if SHOULD_DOWNLOAD or SHOULD_UNZIP:
        DOWNLOAD_UNZIP_PATH = os.path.join(DOWNLOAD_UNZIP_PATH, "3xM_Cache")
    
        if os.path.exists(DOWNLOAD_UNZIP_PATH):
            shutil.rmtree(DOWNLOAD_UNZIP_PATH)
        os.makedirs(DOWNLOAD_UNZIP_PATH, exist_ok=True)
    
    # Download Dataset
    if SHOULD_DOWNLOAD:
        download_dataset(target_path=DOWNLOAD_UNZIP_PATH, dataset=DATSET_FOR_DOWNLOAD, source=SOURCE_FOR_DOWNLOAD)
    
    # Unzip the download files
    if SHOULD_UNZIP:
        extract_zip_folders(source_dir=DOWNLOAD_UNZIP_PATH, destination_dir=SOURCE_PATH)

    # Postprocessing
    if SHOULD_POST_PROCESS:
        postprocess(source_path=SOURCE_PATH, width=WIDTH, height=HEIGHT, 
                    only_mask_convertion=ONLY_MASK_CONVERTION, delete_original=DELETE_ORIGINAL)




