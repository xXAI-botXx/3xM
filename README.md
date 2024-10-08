
https://github.com/user-attachments/assets/9b8a02d3-8ced-48ac-8530-703bb0be2ecf


# 3xM
Model-Material-Mixture Dataset for Instance-Segmentation

This project contains:
- This project contains helper tools for working with Materials and 3D-Models
- The generated Dataset and Information about it (link)
- The Unreal Engine 5 Datageneration Project
- (The Materials)
- (The 3D-Models)

Before you use any of my work, please check my [license](./LICENSE) and [my section for license](#license).

### In Short
I created a dataset to analyze the behaviour of 3D-Models and Materials to the accuracy of instance segmentation.

Feel free to use my Unreal Engine 5 project, to create your own dataset for instance segmentation. You can add your own 3D-Models and Materials and also control the used amount of Materials/3D-Models.


### Explanation
(reference to your bachelor work)


### Unreal Engine 5 Datagenerator
You can download my UE5 project [here](https://drive.google.com/drive/folders/1oR5vuiZkV9cdTlgUpzvDcJ6WtvkyXvRa?usp=sharing).

You have to download and install UE5. Following I will give you a small guide for the installation.
- Windows:
    - For Windows you can simply download the setup.exe and this will lead you through every step. 
    - https://www.unrealengine.com/en-US/download 
    - Then you can choose the Unreal Engine version **5.4.4**


To start the traingeneration, you have to start the UE5 Editor, then open the project (you can just move the downloaded UE5 project to the official project folder from your UE5 Editor).<br>After this step you click on "Content Drawer" and then click on the "data_gen" Level. This will open the Level for datageneration.<br>On the left will be the variables and some of them should be set by yourself. I list them following (the first 8 Variables):
- **ModelAmounts**<br>An array with integer values how many 3D-Models should be used for every dataset
- **MaterialAmounts** <br>An array with integer values how many Materials should be used for every dataset
- **ObjectAmountMIN** <br>Minimum amount of objects/items per scene.
- **ObjectAmountMAX** <br>Minimum amount of objects/items per scene.
- **DataAmountPerDataset** <br>Defines the numbers of images/scenes created for one dataset.
- **ImageWidth** <br>Width of the ceated images from the scene (raw and mask).
- **ImageHeight** <br>Height of the ceated images from the scene (raw and mask).
- **DataSavePath** <br>Path to the folder, where the datasets should get created.


Update: The project is **only available in Windows** because of a used Plugin, called [Victory BP by Rama](https://forums.unrealengine.com/t/ramas-extra-blueprint-nodes-for-ue5-no-c-required/231476).

To add your own Materials and 3D-Models you have to edit the material_data_table and the model_data_tables. 

And to clear a confusion about the **ModelAmounts** and about **MaterialAmounts**, this datagenerator is created to generate multiple datasets with different amounts of materials and 3D-Models. If you just want to generate a random dataset just give these arrays one value with the max amount of your available materials and models.

At least very important are the random/changing factors for the datageneration. Here are all changing elements:
- Bin-Material
- Ground-Material
- Position of the objects
- Amount of objects
- The camera position
  - There are 3 fix camera positions and in the top camera the camera will randomly rotate in the Z-axis
- 3D-Models of the objects (depends on the ModelAmounts parameter)
- Materials of the objects (depends on the MaterialAmounts parameter)

-> You can change all of these factors. The camera will be a bit more tricky (you have to add a new cinematic camera and add a "05_camera" tag -> search for "tag" in the properties and set both tags to "05_camera", then it should be included in the random selection). For the other parameters you can just change the variables and the data-tables in the content browser.



<details>
  <summary>Here is the Linux installation of UE5 if you want... (not recommend)</summary>

- Linux:
    - First install all imortant requirements:
    ```terminal
    sudo apt update
    sudo apt upgrade

    sudo apt install mesa-vulkan-drivers vulkan-utils

    sudo apt-get install build-essential clang-12 python3-pip git cmake ninja-build libgtk-3-dev
    sudo apt-get install libxcb-xinerama0 libxcb1 libxkbcommon-x11-0 libxrandr2 libxcomposite1
    sudo apt-get install libgl1-mesa-dev

    # for nvidia gpu
    sudo apt-get install nvidia-driver-525 nvidia-utils-525

    # for amd gpu
    sudo apt install radeontop
    sudo apt-get install mesa-vulkan-drivers mesa-vulkan-drivers:i386

    sudo apt update
    sudo apt upgrade

    sudo reboot
    ```
    - test Installation with:
    
    NVIDIA-GPU:
    ```terminal
    vulkaninfo
    nvidia-smi
    ```
    AMD GPU:
    ```terminal
    vulkaninfo
    radeontop
    ```
    - Download Unreal Engine **5.4.4** zip file from [here](https://www.unrealengine.com/en-US/linux)
    - Extract the zip-file in the home folder (or whether you want it)
    - Run UE5 with:
    ```terminal
    cd ~/Linux_Unreal_Engine_5.4.4
    ./Engine/Binaries/Linux/UnrealEditor
    ```
</details>

### 3xM Dataset

In the dataset structure every dataset get his own top folder with a ID (most likely not relevant) and the amount of (unique) 3D-Models followed by the amount of used (unique) Materials in the whole dataset. Then every scene have it's own subfolder with the mask file and the normal rgb-image:
Folder-Names = 3xM_dataset-ID_model-amount_material-amount

```
----| 3xM_0_1_1
------------| cam_0
-------------------- mask_0.png
-------------------- raw_0.png
------------| cam_1
-------------------- mask_1.png
-------------------- raw_1.png
------------| ...
-------------------- ...
-------------------- ...
----| 3xM_1_1_2
...
```

The Mask-Images are basic RGB Images. Where all pixel values with the value 0 are the background and every other pixel value stand for one object. Every object have a unique pixel value.<br>You can also transfom the dataset to a grey image, where 0 is again the background and every pixel is also again one object, but now with only one channel and the numbers are increasing (1, 2, 3, 4, ...).

For this mask postprocess (reommended), just run the [3xM_mask_postprocess.py](./src/3xM_mask_postrocess.py). You can use anaconda to install a working python environment for that postprocess: conda create -f ./windows_env.yml


### Data-Source

Subset of [Thingi10k](https://ten-thousand-models.appspot.com/), please see the [Thingi10k Summary.xlsx](Thingi10K Summary.xlsx) to see the creator of these models. I also used a few 3D-models from [polyhaven](https://polyhaven.com/).

The process of finding good fitting models:
- only unique 3D-Models (no double or too similar models)
- the 3D-Model have to be connected (not 2 or more seperated parts)

For Materials I used the paid version from [Brian](https://freepbr.com/).


### License

All my work can be used with GNU Public License. All rights on the 3D-Models are reserved from other people. See the [Thinngi10k Summary.xlsx](./Thingi10K%20Summary.xlsx) for the persons and the rights. And check out the [License-3D-Models.md](./License-3D-Models.md) for finding the right ID for the model. All Material rights are also reserved. You have to buy them on [https://freepbr.com/](https://freepbr.com/) if you want to use them commercially.




