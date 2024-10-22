import os
import zipfile
import shutil

def extract_and_consolidate_images(input_folder, output_folder):
    # Create the output subfolders if they don't exist
    rgb_output = os.path.join(output_folder, "rgb")
    depth_output = os.path.join(output_folder, "depth")
    mask_output = os.path.join(output_folder, "mask")

    os.makedirs(rgb_output, exist_ok=True)
    os.makedirs(depth_output, exist_ok=True)
    os.makedirs(mask_output, exist_ok=True)

    # Iterate through all files in the input folder
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith('.zip'):
                zip_path = os.path.join(root, file)
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(input_folder)
                
                # Look for the 'rgb', 'depth', and 'mask' subfolders
                extracted_folder = os.path.splitext(file)[0]  # Folder name after extracting
                extracted_path = os.path.join(input_folder, extracted_folder)
                
                # Define paths to the subfolders
                rgb_folder = os.path.join(extracted_path, 'rgb')
                depth_folder = os.path.join(extracted_path, 'depth')
                mask_folder = os.path.join(extracted_path, 'mask')

                # Move images to the respective output subfolders
                if os.path.exists(rgb_folder):
                    for img_file in os.listdir(rgb_folder):
                        shutil.move(os.path.join(rgb_folder, img_file), rgb_output)

                if os.path.exists(depth_folder):
                    for img_file in os.listdir(depth_folder):
                        shutil.move(os.path.join(depth_folder, img_file), depth_output)

                if os.path.exists(mask_folder):
                    for img_file in os.listdir(mask_folder):
                        shutil.move(os.path.join(mask_folder, img_file), mask_output)

                # Optionally, remove the extracted folder after moving files
                shutil.rmtree(extracted_path)

    print(f"All images have been consolidated into: {output_folder}")



# Usage
if __name__ == "__main__":
    input_folder = '/path/to/your/input/folder'
    output_folder = '/path/to/your/output/folder'
    extract_and_consolidate_images(input_folder, output_folder)


