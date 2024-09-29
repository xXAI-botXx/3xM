import os
import shutil
import trimesh
import json
from pygltflib import GLTF2, Buffer, BufferView, Accessor, Mesh, Primitive, Node, Scene, Asset, BufferFormat
import bpy

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

def convert_stl_to_glb(source_path, output_path):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    else:
        os.makedirs(output_path, exist_ok=True)

    idx = 0

    for cur_file in os.listdir(source_path):
        cur_path = os.path.join(source_path, cur_file)
        if os.path.isfile(cur_path) and cur_file.endswith(".stl"):
            output_glb_file_path = os.path.join(output_path, f"3xM_Model_ID_{idx}.glb")

            # reset blender scene
            bpy.ops.wm.read_factory_settings(use_empty=True)

            # import stl file
            bpy.ops.wm.stl_import(filepath=cur_path)

            # choose every object
            bpy.ops.object.select_all(action='SELECT')

            # convert to mesh
            bpy.ops.object.convert(target='MESH')

            # export as glb file
            bpy.ops.export_scene.gltf(filepath=output_glb_file_path, export_format='GLB')

            idx += 1

def convert_stl_to_gltf_bin(source_file_path, dest_path, name, export_format="GLTF_SEPARATE"):
    """
    Converts an STL file to a GLTF file using Blender and bpy.
    
    :param source_file_path: Path to the STL file.
    :param dest_path: Directory where the GLTF will be saved.
    :param name: Name for the output file (without extension).
    :param export_format: GLTF export format. Can be 'GLTF_SEPARATE' (default), 'GLTF_EMBEDDED', or 'GLB'.
    """
    # Clear existing meshes in the scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import the STL file
    # bpy.ops.import_mesh.stl(filepath=source_file_path)
    bpy.ops.wm.stl_import(filepath=source_file_path)

    # Set the output file path
    output_file_path = os.path.join(dest_path, f"{name}.gltf" if export_format != "glb" else f"{name}.glb")
    
    # Export the STL as GLTF
    bpy.ops.export_scene.gltf(filepath=output_file_path, export_format=export_format)
    
    print(f"File successfully converted to {output_file_path}")

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

# Main function to run the conversion
def thingi10k_formatting(source_dir, dest_dir, use_ID=False):
    ID = 0
    for cur_file in os.listdir(source_dir):
        cur_file_path = os.path.join(source_dir, cur_file)
        
        os.makedirs(dest_dir, exist_ok=True)

        if os.path.isfile(cur_file_path) and cur_file.endswith(".stl"):
            # Convert .stl to .gltf and .bin
            if use_ID:
                cur_name = f"3xM_Model_ID_{ID}"
            else:
                cur_name = ".".join(cur_file.split(".")[:-1])
            convert_stl_to_gltf_bin(cur_file_path, dest_dir, cur_name)
            ID += 1

def extract_gltf_from_subfolder(source_folder, destination_folder, rm_src=False):

    success = 0
    for root_dir, cur_dirs, cur_files in os.walk(source_folder):
        for cur_file in cur_files:
            file_path = os.path.join(root_dir, cur_file)
            if cur_file.endswith(".gltf") or cur_file.endswith(".bin"):
                cur_destination = os.path.join(destination_folder, cur_file)
                counter = 0
                os.makedirs(destination_folder, exist_ok=True)
                name = cur_file
                type = ".gltf" if cur_file.endswith(".gltf") else ".bin"
                while name in os.listdir(destination_folder):
                    name = f'{".".join(cur_file.split(".")[:-1])}_{counter}{type}'
                    counter += 1
                cur_destination = os.path.join(destination_folder, name)
                shutil.copyfile(file_path, cur_destination)
                success += 1
    print(f"Successfull transfered {success} files.")

            # if rm_src:
            #     shutil.rmtree(os.path.join(source_folder, cur_dir))

def scale_to_size(mesh, target_size):
    # Get current size of the mesh
    current_size = mesh.bounding_box.extents
    # Get the scale-factor with the biggest dimension
    scale_factor = target_size / max(current_size)
    # Scale mesh
    mesh.apply_scale(scale_factor)
    return mesh

def scale_stl(source_path, output_path, target_size=1):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

    for cur_file in os.listdir(source_path):
        if os.path.isfile(cur_file) and cur_file.endswith(".stl"):
            cur_stl_path = os.path.join(source_path, cur_file)

            # load stl model
            mesh = trimesh.load('dein_objekt.stl')

            # Scale mesh to target size
            scale_mesh = scale_to_size(mesh, zielgröße)

            # Save the new sized mesh
            cur_export_stl_path = os.path.join(output_path, cur_file)
            scale_mesh.export(cur_export_stl_path)


if __name__ == "__main__":
    # Define your source directory containing folders which contains .jpg, .usdc, .obj, and .mtl files
    source_dir = '/home/tobia/data/3xM/models/Thingi10KSorted'
    dest_dir = '/home/tobia/data/3xM/models/Thingi10KSorted_prep'
    # dest_dir = '/home/tobia/data/model_material_mixture_dataset/3xM/models'

    # ambientcg_formatting(source_dir=source_dir, dest_dir=dest_dir,new_folder=False)

    # thingi10k_formatting(source_dir=source_dir, dest_dir=dest_dir)
    # thingi10k_formatting(source_dir="D:/Informatik/Projekte/3xM/model_material/Thingi10KSorted", dest_dir="D:/Informatik/Projekte/3xM/model_material/final_models", use_ID=True)

    # extract_gltf_from_subfolder(source_folder="/home/tobia/data/3xM/models/polyhaven", destination_folder="/home/tobia/data/3xM/models/polyhaven_prep", rm_src=False)

    # scale_stl(source_path="D:/Informatik/Projekte/3xM/model_material/Thingi10KSorted", output_path="D:/Informatik/Projekte/3xM/model_material/Thingi10KSortedScaled")

    convert_stl_to_glb(source_path="D:/Informatik/Projekte/3xM/model_material/Thingi10KSorted", output_path="D:/Informatik/Projekte/3xM/model_material/final_models")


