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

# def convert_stl_to_gltf_bin(source_file_path, dest_path, name, ending="gltf", check_closed_mesh=False):
#     """
#     Takes a .stl file from source_file_path and converts it to an gtlf file.
#     Which will be saved on: dest_path/name.glb or dest_path/name.gltf
#     """
#     # Load the STL file using trimesh
#     mesh = trimesh.load(source_file_path)

#     if check_closed_mesh:
#         # Versuche, das Mesh zu reparieren, falls es nicht geschlossen ist
#         if not mesh.is_volume:
#             print(f"Repairing mesh for file: {source_file_path}")
#             mesh.fill_holes()
#             mesh.fix_normals()
        
#         if not mesh.is_volume:
#             raise ValueError("The STL file must describe a valid 3D volume.")

#     # Convert to GLTF
#     gltf = GLTF2()
    
#     # Convert mesh data (vertices, indices) to GLTF-compatible format
#     vertices = mesh.vertices.flatten().tolist()
#     indices = mesh.faces.flatten().tolist()
    
#     # Create buffer
#     buffer_data = bytes(mesh.export(file_type='glb'))  # Get binary data
#     buffer = Buffer(uri=f'{name}.bin', byteLength=len(buffer_data))

#     # Save the bin file
#     bin_file_path = os.path.join(dest_path, f"{name}.bin")
#     with open(bin_file_path, 'wb') as f:
#         f.write(buffer_data)
    
#     # Create BufferView (links the buffer with mesh data)
#     buffer_view = BufferView(buffer=0, byteOffset=0, byteLength=len(buffer_data), target=34963)
    
#     # Create Accessor (for vertices and indices)
#     accessor_positions = Accessor(bufferView=0, byteOffset=0, componentType=5126, count=len(mesh.vertices),
#                                   type="VEC3", max=[mesh.bounds[1].tolist()], min=[mesh.bounds[0].tolist()])
#     accessor_indices = Accessor(bufferView=0, byteOffset=0, componentType=5123, count=len(mesh.faces) * 3,
#                                 type="SCALAR")

#     # Create Mesh
#     primitive = Primitive(attributes={"POSITION": 0}, indices=1)
#     gltf_mesh = Mesh(primitives=[primitive])
    
#     # Add to GLTF
#     gltf.buffers.append(buffer)
#     gltf.bufferViews.append(buffer_view)
#     gltf.accessors.append(accessor_positions)
#     gltf.accessors.append(accessor_indices)
#     gltf.meshes.append(gltf_mesh)

#     # Create Node and Scene
#     node = Node(mesh=0)
#     scene = Scene(nodes=[0])
#     gltf.nodes.append(node)
#     gltf.scenes.append(scene)
    
#     # Set asset metadata
#     gltf.asset = Asset(generator="STL to GLTF Converter", version="2.0")

#     # Save as .glb (binary GLTF) or .gltf (JSON)
#     if ending == "glb":
#         gltf.convert_buffers(BufferFormat.BINARYBLOB)
#         gltf.save(os.path.join(dest_path, f"{name}.glb"))
#     else:
#         # gltf.convert_buffers(BufferFormat.BINARYBLOB)
#         gltf.save_json(os.path.join(dest_path, f"{name}.gltf"))

#     print(f"File successfully converted to {dest_path}/{name}.glb or .gltf")

# def convert_stl_to_gltf_bin(source_file_path, dest_path, name, ending="gltf", check_closed_mesh=False):
#     """
#     Takes a .stl file from source_file_path and converts it to a .gltf file.
#     Saves the file at: dest_path/name.glb or dest_path/name.gltf
#     """
#     # Load the STL file using trimesh
#     mesh = trimesh.load(source_file_path)

#     if check_closed_mesh:
#         # Repair the mesh if it is not closed
#         if not mesh.is_volume:
#             print(f"Repairing mesh for file: {source_file_path}")
#             mesh.fill_holes()
#             mesh.fix_normals()
        
#         if not mesh.is_volume:
#             raise ValueError("The STL file must describe a valid 3D volume.")

#     # Convert to GLTF
#     gltf = GLTF2()

#     # Flatten the vertex and face data
#     vertices = mesh.vertices.flatten().tolist()
#     indices = mesh.faces.flatten().tolist()

#     # Create buffer for vertex and index data
#     buffer_data = mesh.vertices.tobytes() + mesh.faces.tobytes()

#     # Create Buffer
#     buffer = Buffer(uri=f'{name}.bin', byteLength=len(buffer_data))

#     # Save the bin file
#     bin_file_path = os.path.join(dest_path, f"{name}.bin")
#     with open(bin_file_path, 'wb') as f:
#         f.write(buffer_data)

#     # Create BufferViews (separate for vertices and indices)
#     vertex_buffer_view = BufferView(buffer=0, byteOffset=0, byteLength=mesh.vertices.nbytes, target=34962)  # ARRAY_BUFFER
#     index_buffer_view = BufferView(buffer=0, byteOffset=mesh.vertices.nbytes, byteLength=mesh.faces.nbytes, target=34963)  # ELEMENT_ARRAY_BUFFER

#     # Create Accessors for positions (vertices) and indices
#     accessor_positions = Accessor(bufferView=0, byteOffset=0, componentType=5126, count=len(mesh.vertices),
#                                   type="VEC3", max=mesh.bounds[1].tolist(), min=mesh.bounds[0].tolist())
#     accessor_indices = Accessor(bufferView=1, byteOffset=0, componentType=5123 if len(indices) < 65536 else 5125,
#                                 count=len(indices), type="SCALAR")

#     # Create Primitive and Mesh
#     primitive = Primitive(attributes={"POSITION": 0}, indices=1)
#     gltf_mesh = Mesh(primitives=[primitive])

#     # Add data to GLTF
#     gltf.buffers.append(buffer)
#     gltf.bufferViews.append(vertex_buffer_view)
#     gltf.bufferViews.append(index_buffer_view)
#     gltf.accessors.append(accessor_positions)
#     gltf.accessors.append(accessor_indices)
#     gltf.meshes.append(gltf_mesh)

#     # Create Node and Scene
#     node = Node(mesh=0)
#     scene = Scene(nodes=[0])
#     gltf.nodes.append(node)
#     gltf.scenes.append(scene)

#     # Set asset metadata
#     gltf.asset = Asset(generator="STL to GLTF Converter", version="2.0")

#     # Save the file as .glb or .gltf
#     if ending == "glb":
#         gltf.convert_buffers(BufferFormat.BINARYBLOB)
#         gltf.save(os.path.join(dest_path, f"{name}.glb"))
#     else:
#         gltf.save_json(os.path.join(dest_path, f"{name}.gltf"))

#     print(f"File successfully converted to {dest_path}/{name}.{ending}")


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
def thingi10k_formatting(source_dir, dest_dir):
    for cur_file in os.listdir(source_dir):
        cur_file_path = os.path.join(source_dir, cur_file)
        
        os.makedirs(dest_dir, exist_ok=True)

        if os.path.isfile(cur_file_path) and cur_file.endswith(".stl"):
            # Convert .stl to .gltf and .bin
            cur_name = ".".join(cur_file.split(".")[:-1])
            convert_stl_to_gltf_bin(cur_file_path, dest_dir, cur_name)

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


if __name__ == "__main__":
    # Define your source directory containing folders which contains .jpg, .usdc, .obj, and .mtl files
    source_dir = '/home/tobia/data/3xM/models/Thingi10KSorted'
    dest_dir = '/home/tobia/data/3xM/models/Thingi10KSorted_prep'
    # dest_dir = '/home/tobia/data/model_material_mixture_dataset/3xM/models'

    # ambientcg_formatting(source_dir=source_dir, dest_dir=dest_dir,new_folder=False)

    thingi10k_formatting(source_dir=source_dir, dest_dir=dest_dir)

    # extract_gltf_from_subfolder(source_folder="/home/tobia/data/3xM/models/polyhaven", destination_folder="/home/tobia/data/3xM/models/polyhaven_prep", rm_src=False)


