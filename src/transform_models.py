import os
import trimesh
import json
from pygltflib import GLTF2
import shutil

# Convert .usdc and .obj to .gltf and .bin (ignoring materials)
def convert_to_gltf_bin(source_path, destination_path):
    for file_name in os.listdir(source_path):
        if file_name.endswith('.obj'):
            base_name = os.path.splitext(file_name)[0]
            gltf_path = os.path.join(destination_path, f'{base_name}.gltf')
            bin_path = os.path.join(destination_path, f'{base_name}.bin')
            
            # Load the .obj file into a Trimesh object
            mesh = trimesh.load(os.path.join(source_path, file_name))

            # Export the mesh to GLTF format (which returns a dictionary with multiple parts)
            gltf_data = trimesh.exchange.gltf.export_gltf(mesh, include_normals=True)

            for key, value in gltf_data.items():
                if key.endswith(".gltf"):
                    # Save the GLTF data to a file
                    with open(gltf_path, 'wb') as f:
                        f.write(value)
                elif key.endswith(".bin"):
                    cur_bin_path = os.path.join(destination_path, key)
                    with open(cur_bin_path, 'wb') as bin_file:
                        bin_file.write(value)
            
            print(f'Converted {file_name} to {gltf_path}')

# Main function to run the conversion
def ambientcg_formatting(source_dir, dest_dir, new_folder=True):
    for cur_dir in os.listdir(source_dir):
        cur_source_dir = os.path.join(source_dir, cur_dir)
        cur_dest_dir = os.path.join(dest_dir, cur_dir)
        
        if os.path.isdir(cur_source_dir):
            os.makedirs(dest_dir, exist_ok=True)

            if new_folder:
                os.makedirs(cur_dest_dir, exist_ok=True)

                # Convert .usdc and .obj to .gltf and .bin
                convert_to_gltf_bin(cur_source_dir, cur_dest_dir)
            else:
                # Convert .usdc and .obj to .gltf and .bin
                convert_to_gltf_bin(cur_source_dir, dest_dir)

def extract_gltf_from_subfolder(source_folder, destination_folder, rm_src=False):

    for cur_dir in os.listdir(source_folder):
        if os.path.isdir(os.path.join(source_folder, cur_dir)):
            for cur_file in os.listdir(os.path.join(source_folder, cur_dir)):
                file_path = os.path.join(source_folder, cur_dir, cur_file)
                if os.path.isfile(file_path):
                    if (cur_file.endswith(".gltf") or cur_file.endswith(".bin")):
                        cur_destination = os.path.join(destination_folder, cur_file)
                        counter = 0
                        while os.path.exists(cur_destination) and os.path.isdir(cur_destination):
                            cur_destination = os.path.join(destination_folder, f'{".".join(cur_file.split(".")[:-1])}_{counter}.gltf')
                        shutil.copyfile(file_path, cur_destination)

            if rm_src:
                shutil.rmtree(os.path.join(source_folder, cur_dir))


if __name__ == "__main__":
    # Define your source directory containing folders which contains .jpg, .usdc, .obj, and .mtl files
    # source_dir = '/home/tobia/data/model_material_mixture_dataset/models/ambientcg'
    # dest_dir = '/home/tobia/data/model_material_mixture_dataset/models/ambientcg_prep'
    # dest_dir = '/home/tobia/data/model_material_mixture_dataset/3xM/models'

    # ambientcg_formatting(source_dir=source_dir, dest_dir=dest_dir,new_folder=False)

    extract_gltf_from_subfolder(source_folder="/home/tobia/data/model_material_mixture_dataset/3xM/models", destination_folder="/home/tobia/data/model_material_mixture_dataset/3xM/models", rm_src=True)


