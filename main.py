"""
 Use this file to download 3xM Dataset and preprocess the data. 
 
 Just go down to the **if __name__ == "__main__":** part 
 and change the variables for your need.
 
 Make sure you have installed the conda env (conda env create -f env.yml)
 and then just run the script.
 
 -> Give the name of the Dataset and the scrpt download from kaggle
"""

import sys
sys.path.append("./src")

import os
import shutil
from enum import Enum
import subprocess
import requests
import gdown

# functions from local python file: 3xM_postprocess.py
from postprocess import mask_postprocess, depth_postprocess



class DATASET(Enum):
    TRIPPLE_M_10_10 = "kaggle link"
    TRIPPLE_M_10_80 = "..."
    
class DOWNLOAD_SOURCE(Enum):
    KAGGLE = lambda path, url: download_from_kaggle(path, url)
    ONEDRIVE = lambda path, url: download_from_onedrive(path, url)
    GOOGLEDRIVE = lambda path, url: download_from_googledrive(path, url)
    
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
 
def main(
    download_path:str, 
    target_path:str, 
    dataset:DATASET, 
    source:DOWNLOAD_SOURCE,
    apply_mask_postprocess=True, 
    apply_depth_postprocess=False):
    # update download path + prepare the folder
    download_path = os.path.join(download_path, "3xM_Cache")
    
    if os.path.exists(download_path):
        shutil.rmtree(download_path)
    os.makedirs(download_path, exist_ok=True)
    
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
    
    # Extract files to Datasetname -> rgb, depth, mask, (mask-prep), (depth-prep)
    # FIXME
    
    # Apply Mask-Postprocess
    if apply_mask_postprocess:
        pass
        # mask_postprocess(mask_source_path=os.path.join(target_path, "mask"), mask_output_path=os.path.join(target_path, "mask-prep"))
        
    # Apply Grey-Postprocess
    if apply_depth_postprocess:
        pass
        # depth_postprocess(depth_source_path=os.path.join(target_path, "depth"), depth_output_path=os.path.join(target_path, "depth-prep"))
        



if __name__ == "__main__":
    download_path = "./"
    target_path = "./3xM"
    dataset = DATASET.TRIPPLE_M_10_10
    apply_mask_postprocess = True
    apply_depth_postprocess = False
    
    main(
        download_path=download_path,
        target_path=target_path,
        dataset=dataset,
        apply_mask_postprocess=apply_mask_postprocess,
        apply_depth_postprocess=apply_depth_postprocess
    )


