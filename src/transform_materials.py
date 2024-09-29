import os
import shutil
import random

from PIL import Image
import bpy
import json

import numpy as np
import cv2

MATERIAL_PATH = "/home/tobia/data/model_material_mixture_dataset/materials/"

MATERIAL_BLENDER_PATH = os.path.join(MATERIAL_PATH, "raw")
OUTPUT_PATH = "/home/tobia/data/model_material_mixture_dataset/materials/prep"

MATERIAL_NAME_MAP = {
    "color_map": ["color", "diffuse", "albedo", "diff"],
    "height_map": ["height", "displacement", "parallax"],
    "normal_map": ["normal", "nor"], 
    "roughness_map": ["roughness", "rough", "glossiness", "gloss", "smoothness", "smooth"],  
    "metal_map": ["specular", "spec", "metalness", "metal", "reflectivity", "reflect"],
    "bump_map": ["bump"],  # sometimes used equally to normal, but technically different
    "ao_map": ["ambient", "occlusion", "ao"],
    "opacity_map": ["opacity"]
}


def create_material(PATH, OUTPUT_PATH):
    material_name = PATH.split("/")[-1] + ".gltf"
    category = PATH.split("/")[-2]
    OUTPUT_PATH = os.path.join(OUTPUT_PATH, category)

    #################################
    # Load from .blend file
    #################################
    blend_file = None
    for cur_file in os.listdir(PATH):
        if cur_file.endswith(".blend"):
            blend_file = os.path.join(PATH, cur_file)
            break

    if blend_file is not None:
        bpy.ops.wm.open_mainfile(filepath=blend_file)

        # Deselect all objects in the scene
        # bpy.ops.object.select_all(action='DESELECT')


    #################################
    # Load from maps
    #################################
    material_maps = find_material(PATH=PATH)

    if not is_material_empty(material_maps):
        # Create a new material
        material = bpy.data.materials.new(name="GeneratedMaterial")
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Clear all nodes
        for node in nodes:
            nodes.remove(node)

        # Add nodes: Shader, Image Textures, and Normal Map
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        output = nodes.new(type='ShaderNodeOutputMaterial')

        # Set the shader and material output position
        bsdf.location = (0, 0)
        output.location = (300, 0)

        # Link the BSDF node to the Material Output node
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        # Function to add image texture nodes only if the texture exists
        def add_image_texture(image_path, node_input, location):
            if image_path:
                tex_image_node = nodes.new(type='ShaderNodeTexImage')
                tex_image_node.image = bpy.data.images.load(image_path)
                tex_image_node.location = location
                links.new(tex_image_node.outputs['Color'], node_input)
                print(f"Loaded {image_path}")
            else:
                print(f"No texture for {node_input.name}")

        # Add Ambient Occlusion (AO) map if available, multiply it with the color map
        if material_maps["ao_map"] and material_maps["color_map"]:
            # Create a MixRGB node for multiplying the AO map with the base color
            ao_multiply_node = nodes.new(type='ShaderNodeMixRGB')
            ao_multiply_node.blend_type = 'MULTIPLY'
            ao_multiply_node.inputs[0].default_value = 1.0  # Set blend factor to 1 (full influence)
            ao_multiply_node.location = (-600, 0)

            # Add the AO map
            ao_tex_image_node = nodes.new(type='ShaderNodeTexImage')
            ao_tex_image_node.image = bpy.data.images.load(material_maps["ao_map"])
            ao_tex_image_node.location = (-800, 0)

            # Connect the AO texture to the Multiply node
            links.new(ao_tex_image_node.outputs['Color'], ao_multiply_node.inputs[2])

            # Add the color map texture again and link it to the Multiply node
            color_tex_image_node = nodes.new(type='ShaderNodeTexImage')
            color_tex_image_node.image = bpy.data.images.load(material_maps["color_map"])
            color_tex_image_node.location = (-800, 200)
            links.new(color_tex_image_node.outputs['Color'], ao_multiply_node.inputs[1])

            # Link the result of the Multiply node to the BSDF's Base Color
            links.new(ao_multiply_node.outputs['Color'], bsdf.inputs['Base Color'])

            print(f"Loaded AO map: {material_maps['ao_map']}")
        elif material_maps["color_map"]:
            # If no AO map, just use the base color
            add_image_texture(material_maps["color_map"], bsdf.inputs['Base Color'], (-400, 0))

        
        if material_maps["roughness_map"]:
            add_image_texture(material_maps["roughness_map"], bsdf.inputs['Roughness'], (-400, -200))  # Roughness map
        
        # Add normal map if available
        if material_maps["normal_map"]:
            normal_map_node = nodes.new(type='ShaderNodeNormalMap')
            normal_map_node.location = (-400, -400)
            links.new(normal_map_node.outputs['Normal'], bsdf.inputs['Normal'])
            
            normal_tex_image_node = nodes.new(type='ShaderNodeTexImage')
            normal_tex_image_node.image = bpy.data.images.load(material_maps["normal_map"])
            normal_tex_image_node.location = (-600, -400)
            links.new(normal_tex_image_node.outputs['Color'], normal_map_node.inputs['Color'])
            print(f"Loaded normal map: {material_maps['normal_map']}")
        else:
            print("No normal map available")

        # Optionally add other maps (e.g., AO, Metalness, etc.)
        if material_maps["metal_map"]:
            add_image_texture(material_maps["metal_map"], bsdf.inputs['Metallic'], (-400, -600))  # Metallic map

        if material_maps["opacity_map"]:
            add_image_texture(material_maps["opacity_map"], bsdf.inputs['Alpha'], (-400, -1000))  # Opacity map

    # Create a simple object and assign the material
    mesh = bpy.data.meshes.new("TempMesh")
    obj = bpy.data.objects.new("TempObject", mesh)
    bpy.context.collection.objects.link(obj)

    # Iterate through all materials in the file and apply them to the temporary object
    if blend_file is not None:
        for cur_material in bpy.data.materials:
            # Assign the material to the temporary object
            if cur_material.users:  # Only if the material is used by something
                obj.data.materials.append(cur_material)

    if not is_material_empty(material_maps):
        # Assign the material to the object
        obj.data.materials.append(material)

    # Export the object to GLTF
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    save_path = os.path.join(OUTPUT_PATH, material_name)
    bpy.ops.export_scene.gltf(filepath=save_path, export_format="GLTF_SEPARATE", use_selection=True)

    print(f"Exported material and textures to {save_path}")

    # Cleanup: Remove the temporary object from the scene
    bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.meshes.remove(mesh)


def find_material(PATH, should_count_all=False, extract_arm_file=False):
    """
    Tries to find following material attributes:

    ### 1. **color_map** (["color", "diffuse", "albedo"])
    - **Description**: Defines the base color or texture of a material without lighting or shading effects. This map is responsible for how the surface appears in terms of its inherent color.
    - **Common uses**: Texturing surfaces like walls, objects, or characters to give them a unique appearance.

    ### 2. **height_map** (["height", "displacement", "parallax"])
    - **Description**: Stores height or depth information to simulate 3D surface details. Used for displacement mapping or parallax effects to give the illusion of depth on flat surfaces.
    - **Common uses**: Adding surface details such as grooves, cracks, or extrusions without altering the mesh geometry.

    ### 3. **normal_map** (["normal"])
    - **Description**: Encodes surface normal directions to simulate small-scale details and texture depth. Unlike height maps, it manipulates light to fake the appearance of complex geometry.
    - **Common uses**: Adding fine surface details like wrinkles, dents, or texture roughness to models.

    ### 4. **roughness_map** (["roughness", "rough", "glossiness", "gloss", "smoothness", "smooth"])
    - **Description**: Controls how smooth or rough a surface is. Rougher surfaces scatter light more, while smoother ones create sharper reflections. Sometimes inverted as glossiness.
    - **Common uses**: Simulating surfaces like polished metal (smooth) or rugged terrain (rough).

    ### 5. **metal_map** (["specular", "spec", "metalness", "metal", "reflectivity", "reflect"])
    - **Description**: Determines how metallic or reflective a surface is. In metalness workflows, it specifies whether a surface behaves like a metal (high reflection) or a non-metal.
    - **Common uses**: Creating materials like metals, plastics, and glass, which have different reflection properties.

    ### 6. **bump_map** (["bump"])
    - **Description**: Provides height information to create the illusion of surface texture by adjusting the lighting, without altering the actual geometry. Similar to normal maps but less advanced.
    - **Common uses**: Simulating small bumps or irregularities on surfaces like bricks, fabric, or skin.

    ### 7. **ao_map** (["ambient", "occlusion", "ao"])
    - **Description**: Defines areas that should receive less light due to being occluded by surrounding geometry. Used to simulate shadows in crevices and folds to enhance depth perception.
    - **Common uses**: Adding shadow details in corners, crevices, and other areas with ambient light occlusion.

    ### 8. **opacity_map** (["opacity"])
    - **Description**: Controls the transparency of a surface. White areas are fully opaque, while black areas are fully transparent, with grayscale values representing varying degrees of transparency.
    - **Common uses**: Creating transparent materials like glass, leaves, or cloth with holes.
    """
    material = {
        "color_map": None,
        "height_map": None,
        "normal_map": None,
        "roughness_map": None,
        "metal_map": None,
        "bump_map": None,
        "ao_map": None,
        "opacity_map": None,
    }

    material_count = {
        "color_map": 0,
        "height_map": 0,
        "normal_map": 0,
        "roughness_map": 0,
        "metal_map": 0,
        "bump_map": 0,
        "ao_map": 0,
        "opacity_map": 0,
    }

    if extract_arm_file:
        already_extracted_arm = False
        for root_path, cur_dirs, cur_files in os.walk(PATH):
            for cur_file in cur_files:
                cur_file_path = os.path.join(root_path, cur_file)
                if "arm" in cur_file.lower() and os.path.isfile(cur_file_path):
                    extract_arm_channels(cur_file_path, 
                                         os.path.join(root_path, get_standardized_material_name("ao")),
                                         os.path.join(root_path, get_standardized_material_name("roughness")),
                                         os.path.join(root_path, get_standardized_material_name("metal")))
                    already_extracted_arm = True
                    break
            if already_extracted_arm:
                break

    for root_path, cur_dirs, cur_files in os.walk(PATH):
        for cur_file in cur_files:
            for cur_attribute, keys in MATERIAL_NAME_MAP.items():
                if any([i in cur_file.lower() for i in keys]):
                    material[cur_attribute] = os.path.join(root_path, cur_file)
                    if not should_count_all:
                        break
                    else:
                        material_count[cur_attribute] += 1

    if should_count_all:
        return material, material_count
    else:
        return material
    
def extract_arm_channels(arm_image_path, output_ao_path, output_roughness_path, output_metalness_path):
    # Load the ARM image (RGB image where AO is in R, Roughness in G, Metalness in B)
    arm_image = cv2.imread(arm_image_path)

    if arm_image is None:
        print(f"Error: Could not load image {arm_image_path}")
        return

    # Split the ARM image into its Red, Green, and Blue channels
    ao_image, roughness_image, metalness_image = cv2.split(arm_image)

    # Save the individual channel images
    cv2.imwrite(output_ao_path, ao_image)  # AO (Red channel)
    cv2.imwrite(output_roughness_path, roughness_image)  # Roughness (Green channel)
    cv2.imwrite(output_metalness_path, metalness_image)  # Metalness (Blue channel)
    
def get_standardized_material_name(material_name:str):

    material_name_mapping = {
        "color_map": "color.jpg",
        "height_map": "height.jpg",
        "normal_map": "normal.jpg",
        "roughness_map": "roughness.jpg",
        "metal_map": "metal.jpg",
        "bump_map": "bump.jpg",
        "ao_map": "ambient_occlusion.jpg",
        "opacity_map": "opacity.jpg",
    }

    for cur_attribute, keys in MATERIAL_NAME_MAP.items():
        if any([i in material_name.lower() for i in keys]):
            return material_name_mapping[cur_attribute]
    return material_name

def get_readable_material_name(material_name:str):
    material_name_mapping = {
        "color_map": "Base Color",
        "height_map": "Height Map",
        "normal_map": "Normal Map",
        "roughness_map": "Roughness Map",
        "metal_map": "Metalness Map",
        "bump_map": "Bump Map",
        "ao_map": "Ambient Occlusion Map.jpg",
        "opacity_map": "Opacity",
    }

    for cur_attribute, keys in MATERIAL_NAME_MAP.items():
        if any([i in material_name.lower() for i in keys]):
            return material_name_mapping[cur_attribute]

def is_material_empty(material:dict):
    is_empty = True
    for key, value in material.items():
        if value is not None:
            is_empty = False
            break
    
    return is_empty
    
def create_key(file_counter, blend_files, gltf_files, bin_files, images, color, height, normal, roughness, metal, bump, ao, opacity):
    return f"{file_counter},{blend_files},{gltf_files},{bin_files},{images},{color},{height},{normal},{roughness},{metal},{bump},{ao},{opacity}"

def int_or_none_cast(cast_var):
    try:
        cast_var = int(cast_var)
    except Exception:
        cast_var = None

    return cast_var

def read_key(key_str, should_print=False):
    res = dict()
    values = key_str.split(",")

    if len(values) != 13:
        raise ValueError(f"Only {len(values)} Values in keys detected. But expected 13.")

    for i, value in enumerate(values):
        if i == 0:
            res["file_counter"] = int_or_none_cast(value)
        elif i == 1:
            res["blend_files"] = int_or_none_cast(value)
        elif i == 2:
            res["gltf_files"] = int_or_none_cast(value)
        elif i == 3:
            res["bin_files"] = int_or_none_cast(value)
        elif i == 4:
            res["images"] = int_or_none_cast(value)
        elif i == 5:
            res["color"] = int_or_none_cast(value)
        elif i == 6:
            res["height"] = int_or_none_cast(value)
        elif i == 7:
            res["normal"] = int_or_none_cast(value)
        elif i == 8:
            res["roughness"] = int_or_none_cast(value)
        elif i == 9:
            res["metal"] = int_or_none_cast(value)
        elif i == 10:
            res["bump"] = int_or_none_cast(value)
        elif i == 11:
            res["ao"] = int_or_none_cast(value)
        elif i == 12:
            res["opacity"] = int_or_none_cast(value)

    if should_print:
        print("\nMaterial Element:")
        for key, value in res.items():
            print(f"    '{key}': {value}")

    return res

def find_materials(PATH):
    # materials
    n_materials = 0
    n_material_pattern = dict()
    for category in os.listdir(PATH):
        for material in os.listdir(os.path.join(PATH, category)):
            if os.path.isdir(os.path.join(PATH, category, material)):
                n_materials += 1

                file_counter = 0
                blend_files = 0
                gltf_files = 0
                bin_files = 0
                images = 0
                for cur_path, cur_dirs, cur_files in os.walk(os.path.join(PATH, category, material)):
                    for cur_file in cur_files:
                        file_counter += 1
                        if cur_file.endswith(".blend"):
                            blend_files += 1
                        elif cur_file.endswith(".gltf"):
                            gltf_files += 1
                        elif cur_file.endswith(".bin"):
                            bin_files += 1
                        elif cur_file.endswith(".png") or cur_file.endswith(".jpg"):
                            images += 1

                material, n_material = find_material(cur_path, should_count_all=True)

                key = create_key(file_counter=file_counter, blend_files=blend_files, gltf_files=gltf_files, 
                                 bin_files=bin_files, images=images, 
                                 color=n_material["color_map"], height=n_material["height_map"], 
                                 normal=n_material["normal_map"], roughness=n_material["roughness_map"], 
                                 metal=n_material["metal_map"], bump=n_material["bump_map"], 
                                 ao=n_material["ao_map"], opacity=n_material["opacity_map"])
                
                if key in n_material_pattern.keys():
                    n_material_pattern[key] += 1
                else:
                    n_material_pattern[key] = 1

    print(f"Founded {n_materials} materials.")
    print(f"Details:")
    for key, value in sorted(n_material_pattern.items(), key=lambda x:x[0][0]):  # key=lambda x:x[1]
        print(f"    -> '{key}': {value}")

# Function to rename textures
def rename_texture(file_path, new_name):
    image = Image.open(file_path)
    new_texture_path = os.path.join(texture_output_directory, new_name)
    image.save(new_texture_path)
    print(f"Saved {new_texture_path}")

# Step 1: Convert USD (.usdc) to GLTF (.gltf)
def convert_usdc_to_gltf(input_file, output_file):
    # Assuming you have `usdcat` command-line tool installed
    os.system(f'usdcat {input_file} -o {output_file}')
    print(f"Converted {input_file} to {output_file}")

# Step 2: Convert MaterialX (.mtlx) to .bin (example placeholder)
def convert_mtlx_to_bin(input_file, output_file):
    # Placeholder function, you might need a custom converter for .mtlx
    with open(output_file, 'wb') as f:
        f.write(b'')  # Simulate binary conversion
    print(f"Converted {input_file} to {output_file}")

# Step 3: Rename and move textures
def process_textures(input_directory):
    texture_map = {
        'AmbientOcclusion.jpg': 'arm.jpg',
        'Color.jpg': 'diff.jpg',
        'normaldx.jpg': 'normal_gl.jpg',
        'normalfl.jpg': 'normal_gl.jpg',
        'Displacement.jpg': None,  # Unused in this example
        'roughness.jpg': 'arm.jpg'
    }
    
    for texture, new_name in texture_map.items():
        texture_path = os.path.join(input_directory, texture)
        if new_name and os.path.exists(texture_path):
            rename_texture(texture_path, new_name)

# Run conversion process
def img_map_2_gltf(input_directory, output_directory):
    for cur_dir in os.listdir(input_directory):
        cur_path = os.path.join(input_directory, cur_dir)
        if os.path.isdir(cur_path):
            cur_output_directory = cur_path
            cur_texture_output_directory = os.path.join(cur_output_directory, 'textures')

            # Create output directories if they don't exist
            os.makedirs(cur_output_directory, exist_ok=True)
            os.makedirs(cur_texture_output_directory, exist_ok=True)

            # File paths
            mtlx_file = os.path.join(input_directory, 'model.mtlx')
            usdc_file = os.path.join(input_directory, 'model.usdc')

            gltf_output_file = os.path.join(cur_output_directory, 'model.gltf')
            bin_output_file = os.path.join(cur_output_directory, 'model.bin')

            # Convert files
            convert_usdc_to_gltf(usdc_file, gltf_output_file)
            convert_mtlx_to_bin(mtlx_file, bin_output_file)

            # Process textures
            process_textures(input_directory)

def get_input_value(input_socket):
    if input_socket.is_linked:
        # If the input is linked to another node, follow the link
        linked_node = input_socket.links[0].from_node
        if linked_node.type == 'TEX_IMAGE':  # Texture node
            return linked_node.image.filepath
        else:
            return None
    else:
        # Return default value if it's not linked
        value = input_socket.default_value
        if isinstance(value, bpy.types.bpy_prop_array):
            return list(value)
        return value

def blend_to_json(blend_dir_path, export_path):
    for cur_file in os.listdir(blend_dir_path):
        blend_file_path = os.path.join(blend_dir_path, cur_file)
        # blend_file_export_path = os.path.join(export_path, f'{".".join(cur_file.split(".")[:-1])}.gltf')
        blend_file_export_path = os.path.join(export_path, "material_data.json")
        if os.path.isfile(blend_file_path) and cur_file.endswith(".blend"):
            os.makedirs(export_path, exist_ok=True)
            
            # bpy.ops.wm.open_mainfile(filepath=blend_file_path)

            # bpy.ops.export_scene.gltf(
            #     filepath=blend_file_export_path,
            #     export_format='GLTF_SEPARATE',   # Exports separate .gltf, .bin, and texture files
            #     export_materials='EXPORT',       # Exports materials
            #     # export_textures=True,            # Ensures textures are exported
            #     export_normals=True,             # Ensures normals are exported
            #     # export_colors=True               # Ensures vertex colors are exported
            # )

            # Load the .blend file
            bpy.ops.wm.open_mainfile(filepath=blend_file_path)

            # Prepare a dictionary to store material data
            material_data = {}

            # Loop through all materials in the blend file
            for material in bpy.data.materials:
                mat_info = {}
                
                # Get the base color
                if material.use_nodes:  # Check if material uses nodes (which most do)
                    for node in material.node_tree.nodes:
                        if node.type == 'BSDF_PRINCIPLED':  # Get the principled shader
                            # Get base color, roughness, metallic, specular, etc.
                            try:
                                mat_info['base_color'] = get_input_value(node.inputs['Base Color'])
                            except Exception:
                                pass
                            try:
                                mat_info['roughness'] = get_input_value(node.inputs['Roughness'])
                            except Exception:
                                pass
                            try:
                                mat_info['metallic'] = get_input_value(node.inputs['Metallic'])
                            except Exception:
                                pass
                            try:
                                mat_info['specular'] = get_input_value(node.inputs['Specular'])
                            except Exception:
                                pass
                            try:
                                mat_info['emission'] = get_input_value(node.inputs['Emission'])
                            except Exception:
                                pass
                            try:
                                mat_info['clearcoat'] = get_input_value(node.inputs['Clearcoat'])
                            except Exception:
                                pass
                            try:
                                mat_info['sheen'] = get_input_value(node.inputs['Sheen'])
                            except Exception:
                                pass
                            try:
                                mat_info['transmission'] = get_input_value(node.inputs['Transmission'])
                            except Exception:
                                pass
                            try:
                                mat_info['alpha'] = get_input_value(node.inputs['Alpha'])
                            except Exception:
                                pass
                            
                # Add the material data to the dictionary
                material_data[material.name] = mat_info

            # Write material data to a JSON file
            with open(blend_file_export_path, 'w') as json_file:
                json.dump(material_data, json_file, indent=4)

            print(f"Material data saved to {blend_file_export_path}")

def blender_prep(source_path, dest_path):
    for category in os.listdir(source_path):
        for material in os.listdir(os.path.join(source_path, category)):
            if os.path.isdir(os.path.join(source_path, category, material)):
                cur_dest_path = os.path.join(dest_path, category, material)
                blend_to_json(os.path.join(source_path, category, material), cur_dest_path)
                #create_material(PATH=os.path.join(source_path, category, material), OUTPUT_PATH=dest_path)

# Function to create a new material in Blender from JSON data
def create_material_from_json(json_file_path, show=False):
    with open(json_file_path, 'r') as json_file:
        material_data = json.load(json_file)

    json_data = material_data

    # Loop through each material in the JSON data
    for material_name, material_info in json_data.items():
        # Create a new material in Blender
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True  # Enable nodes for the material
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Remove default nodes
        for node in nodes:
            nodes.remove(node)

        # Create Principled BSDF node
        principled_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        principled_bsdf.location = (0, 0)
        
        # Create Material Output node
        material_output = nodes.new(type='ShaderNodeOutputMaterial')
        material_output.location = (400, 0)
        links.new(principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])

        # Set base color, roughness, and other properties
        if 'base_color' in material_info:
            principled_bsdf.inputs['Base Color'].default_value = material_info['base_color']

        if 'roughness' in material_info:
            principled_bsdf.inputs['Roughness'].default_value = material_info['roughness']

        if 'metallic' in material_info:
            principled_bsdf.inputs['Metallic'].default_value = material_info['metallic']

        if 'specular' in material_info:
            principled_bsdf.inputs['Specular'].default_value = material_info['specular']

        if 'emission' in material_info:
            principled_bsdf.inputs['Emission'].default_value = material_info['emission']

        if 'clearcoat' in material_info:
            principled_bsdf.inputs['Clearcoat'].default_value = material_info['clearcoat']

        if 'sheen' in material_info:
            principled_bsdf.inputs['Sheen'].default_value = material_info['sheen']

        if 'transmission' in material_info:
            principled_bsdf.inputs['Transmission'].default_value = material_info['transmission']

        if 'alpha' in material_info:
            principled_bsdf.inputs['Alpha'].default_value = material_info['alpha']

        if show:
            # Assign the material to an object
            if not bpy.data.objects.get("Material_Test_Object"):
                # Create a new object (e.g., a sphere)
                bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
                obj = bpy.context.object
                obj.name = "Material_Test_Object"
            else:
                obj = bpy.data.objects["Material_Test_Object"]
            
            # Apply the material
            if material_name in obj.data.materials:
                obj.data.materials[obj.data.materials.find(material_name)] = mat
            else:
                obj.data.materials.append(mat)

        return mat

def load_random_material(source_path):
    all_materials = []
    for category in os.listdir(source_path):
        for material in os.listdir(os.path.join(source_path, category)):
            if os.path.isdir(os.path.join(source_path, category, material)):
                json_path = os.path.join(source_path, category, material, "material_data.json")
                if os.path.exists(json_path):
                    all_materials += [json_path]

    random_mat = random.choice(all_materials)
    mat = create_material_from_json(random_mat, show=True)

def cv_img_is_none(cv_img):
    return cv_img is None or not isinstance(cv_img, np.ndarray) or cv_img.size == 0

def combine_metal_roughness(metal_path, roughness_path, output_path):
    # Lade die beiden Bilder in Graustufen
    metal_img = cv2.imread(metal_path, cv2.IMREAD_GRAYSCALE)  # Metall in Blau-Kanal
    roughness_img = cv2.imread(roughness_path, cv2.IMREAD_GRAYSCALE)  # Rauheit in Grün-Kanal
    
    # Überprüfe, ob die Bilder geladen wurden
    if cv_img_is_none(metal_img) and cv_img_is_none(roughness_img):
        # raise Exception(f"Could not load metal and roughness texture. Both are None.")
        print(f"Could not load metal and roughness texture. Both are None.")
        return
    if cv_img_is_none(metal_img):
        print(f"Could not load metal texture from {metal_path}")
    if cv_img_is_none(roughness_img):
        print(f"Could not load roughness texture from {roughness_path}")
    
    # Überprüfe, ob die Größen übereinstimmen
    if not cv_img_is_none(metal_img) and not cv_img_is_none(roughness_img):
        if metal_img.shape != roughness_img.shape:
            if np.sum(metal_img.shape) < np.sum(roughness_img.shape):
                print(f"Resizing roughness image from {roughness_img.shape} to {metal_img.shape}")
                roughness_img = cv2.resize(roughness_img, (metal_img.shape[1], metal_img.shape[0]))
            else:
                print(f"Resizing metal image from {metal_img.shape} to {roughness_img.shape}  ")
                metal_img = cv2.resize(metal_img, (roughness_img.shape[1], roughness_img.shape[0]))
    
    # Erstelle ein leeres Bild mit 3 Kanälen (BGR)
    height, width = metal_img.shape if not cv_img_is_none(metal_img) else roughness_img.shape
    combined_img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Weisen den Blau-Kanal der Metal-Textur zu und den Grün-Kanal der Roughness-Textur
    combined_img[:, :, 0] = metal_img if not cv_img_is_none(metal_img) else 0  # Blau für Metalness
    combined_img[:, :, 1] = roughness_img if not cv_img_is_none(roughness_img)  else 0  # Grün für Roughness
    combined_img[:, :, 2] = 0  # Rot bleibt auf 0
    
    # Speichere das kombinierte Bild
    cv2.imwrite(output_path, combined_img)
    print(f"Combined image saved to {output_path}")

def create_material_json(source_path, material_name):
    """
    Creates a Material information in gltf format.

    Example Format:

    {
        "materials": [
            {
                "doubleSided": true,
                "name": "iron galvanized matte",
                "normalTexture": {
                    "index": 0
                },
                "pbrMetallicRoughness": {
                    "baseColorTexture": {
                        "index": 1
                    },
                    "metallicRoughnessTexture": {
                        "index": 2
                    }
                }
            }
        ],
        "textures": [
            {
                "sampler": 0,
                "source": 0
            },
            {
                "sampler": 0,
                "source": 1
            },
            {
                "sampler": 0,
                "source": 2
            }
        ],
        "images": [
            {
                "mimeType": "image/jpeg",
                "name": "iron galvanized matte_normal",
                "uri": "textures/iron%20galvanized%20matte_normal.jpg"
            },
            {
                "mimeType": "image/jpeg",
                "name": "iron galvanized matte_albedo",
                "uri": "textures/iron%20galvanized%20matte_albedo.jpg"
            },
            {
                "mimeType": "image/jpeg",
                "name": "iron galvanized matte_metallic-iron galvanized matte_roughness",
                "uri": "textures/iron%20galvanized%20matte_metallic-iron%20galvanized%20matte_roughness.jpg"
            }
        ]
    }
    """
    materials = []
    textures = []
    images = []
    
    def add_image_and_texture(image_path, image_name):
        if image_path and image_path.endswith(".png"):
            img_type = "png"
        else:
            img_type = "jpeg"
        img_data = {
            "mimeType": f"image/{img_type}",
            "name": image_name,
            # "uri": image_path
            "uri": f"textures/{image_path.split('/')[-1]}" if image_path else image_path
        }
        images.append(img_data)
        
        texture_data = {
            "sampler": 0,  
            "source": len(images) - 1  
        }
        textures.append(texture_data)

    # add image maps and also textures -> also could be hard coded
    material = find_material(source_path)
    for cur_attribute, cur_path in material.items():
        # only add normal, base color and roughness, or also the rest?
        if cur_attribute in ["normal_map", "color_map"]:    # "roughness_map", metal_map
            add_image_and_texture(cur_path, get_readable_material_name(cur_attribute))

    # create json file
    metalroughness = None
    for cur_root, cur_dirs, cur_files in os.walk(source_path):
        if "MetalRoughness.jpg" in cur_files or "MetalRoughness.png" in cur_files:
            metalroughness = os.path.join(cur_root, "MetalRoughness.jpg")
            add_image_and_texture(metalroughness, "MetalRoughness.jpg")

    material_data = {
        "doubleSided": True,
        "name": material_name,
        "normalTexture": {
            "index": 0 if material["normal_map"] else None  # Normalmap (falls vorhanden)
        },
        "pbrMetallicRoughness": {
            "baseColorTexture": {
                "index": 1 if material["color_map"] else None  # Color-Textur
            },
            "metallicRoughnessTexture": {
                # "index": 2 if material["roughness_map"] else None  # Roughness-Textur
                "index": 2 if metalroughness else None  # Roughness-Textur
            }
        }
    }
    materials.append(material_data)

    # remove none values to keep the json clean
    def clean_dict(d):
        return {k: v for k, v in d.items() if v is not None}
    
    materials = [clean_dict(material) for material in materials]

    return {
            "materials": materials,
            "textures": textures,
            "images": images
            }

def prep_images(source_path, output_path):
    """
    Converts images to a specific format with info file:

    material_data.json -> contains the paths to te textures in gltf format
    texture/
        color.jpg
        ...
    """
    counter = 0
    for cur_category in os.listdir(source_path):
        for cur_dir in os.listdir(os.path.join(source_path, cur_category)):
            cur_path = os.path.join(source_path, cur_category, cur_dir)
            if os.path.isdir(cur_path):
                # get all material files
                material = find_material(cur_path, extract_arm_file=True)

                # copy all files to new output path
                cur_output_path = os.path.join(output_path, cur_category, cur_dir)
                cur_output_material_path = os.path.join(cur_output_path, "textures")
                if os.path.exists(cur_output_path):
                    shutil.rmtree(cur_output_path)
                os.makedirs(cur_output_material_path, exist_ok=True)

                for key, value in material.items():
                    if value:
                        # could also give key in material_name_mapping and should get standardized name
                        name = get_standardized_material_name(value.split("/")[-1])
                        new_output_material_path = os.path.join(cur_output_material_path, name)
                        shutil.copy(value, new_output_material_path)

                if "roughness_map" in material.keys() and "metal_map" in material.keys():
                    combine_metal_roughness(metal_path=material["metal_map"], roughness_path=material["roughness_map"],
                                             output_path=os.path.join(cur_output_material_path, "MetalRoughness.jpg"))

                # create material_data.json file (in cur_output_path)
                name = cur_dir.replace("-Unreal-Engine", "").replace("-ue", "")
                json_file_content = create_material_json(cur_output_path, name)

                with open(os.path.join(cur_output_path, 'material_data.json'), 'w') as json_file:
                    json.dump(json_file_content, json_file, indent=4)

                print(f"Successfull created new Json file and textures at {cur_output_path}!")
                counter += 1

    print(f"\n Finish! Successfull transformed {counter} materials!")

def unreal_prep_images(source_path, output_path):
    """
    Converts images to a standaridzed name
    """
    counter = 0
    for cur_category in os.listdir(source_path):
        for cur_dir in os.listdir(os.path.join(source_path, cur_category)):
            cur_path = os.path.join(source_path, cur_category, cur_dir)
            if os.path.isdir(cur_path):
                # get all material files
                material = find_material(cur_path, extract_arm_file=True)

                # copy all files to new output path
                cur_output_path = os.path.join(output_path, cur_category, cur_dir)
                if os.path.exists(cur_output_path):
                    shutil.rmtree(cur_output_path)
                os.makedirs(cur_output_path, exist_ok=True)

                for key, value in material.items():
                    if value:
                        # could also give key in material_name_mapping and should get standardized name
                        name = get_standardized_material_name(value.split("/")[-1])
                        new_output_material_path = os.path.join(cur_output_path, name)
                        shutil.copy(value, new_output_material_path)

                print(f"Successfull created standardized textures at {cur_output_path}!")
                counter += 1

    print(f"\n Finish! Successfull transformed {counter} materials!")

def unreal_renameing(source_path, output_path):
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    else:
        os.makedirs(output_path, exist_ok=True)
    
    counter = 0

    for cur_category in os.listdir(source_path):
        for cur_material in os.listdir(os.path.join(source_path, cur_category)):
            cur_path = os.path.join(source_path, cur_category, cur_material)
            if os.path.isdir(cur_path):
                # get all material files
                material = find_material(cur_path, extract_arm_file=True)

                # copy all files to new output path
                cur_output_path = os.path.join(output_path, f"3xM_Material_ID_{counter}")
                if os.path.exists(cur_output_path):
                    shutil.rmtree(cur_output_path)
                os.makedirs(cur_output_path, exist_ok=True)

                for key, value in material.items():
                    if value:
                        # could also give key in material_name_mapping and should get standardized name
                        name = get_standardized_material_name(value.split("/")[-1])
                        new_output_material_path = os.path.join(cur_output_path, name)
                        shutil.copy(value, new_output_material_path)

                print(f"Successfull created standardized textures at {cur_output_path}!")
                counter += 1

    print(f"\n Finish! Successfull renamed {counter} materials!")

if __name__ == "__main__":
    # img_map_2_gltf(path="/home/tobia/")

    # find_materials(PATH=MATERIAL_PATH)

    #blender_prep("/home/tobia/data/3xM/materials/blenderkit/raw", "/home/tobia/data/3xM/materials/blenderkit/prep")

    # load_random_material("/home/tobia/data/3xM/materials/blenderkit/prep")

    # prep_images(source_path="/home/tobia/data/3xM/materials/brian_500", output_path="/home/tobia/data/3xM/materials/brian_500_prep_ue")
    
    # unreal_prep_images(source_path="/home/tobia/data/3xM/materials/brian_500", output_path="/home/tobia/data/3xM/materials/brian_500_prep_ue")

    unreal_renameing(source_path="D:/Informatik/Projekte/3xM/model_material/brian_500_prep_ue_ssim_index", output_path="D:/Informatik/Projekte/3xM/final_materials")


