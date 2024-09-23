# run this file in Blender

import os
import bpy

def load_material_in_blend(color_path, normal_path, roughness_path, metal_path):
    # Objekt auswählen
    obj = bpy.context.active_object
    
    # Aktuelles Material entfernen
    if obj.data.materials:
        obj.data.materials.clear()  # Entfernt alle Materialien
    
    # Neues Material erstellen
    mat = bpy.data.materials.new(name="Material")
    obj.data.materials.append(mat)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Image-Texturen laden und verbinden
    textures = {
        "albedo": color_path,
        "roughness": roughness_path,
        "normal": normal_path,
        "metal": metal_path
    }

    for tex_type, tex_path in textures.items():
        if os.path.exists(tex_path):
            tex_image = nodes.new(type='ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(tex_path)
            if tex_type == "albedo":
                mat.node_tree.links.new(tex_image.outputs['Color'], nodes['Principled BSDF'].inputs['Base Color'])
            elif tex_type == "roughness":
                mat.node_tree.links.new(tex_image.outputs['Color'], nodes['Principled BSDF'].inputs['Roughness'])
            elif tex_type == "metal":
                mat.node_tree.links.new(tex_image.outputs['Color'], nodes['Principled BSDF'].inputs['Metallic'])
            elif tex_type == "normal":
                normal_map = nodes.new(type='ShaderNodeNormalMap')
                mat.node_tree.links.new(tex_image.outputs['Color'], normal_map.inputs['Color'])
                mat.node_tree.links.new(normal_map.outputs['Normal'], nodes['Principled BSDF'].inputs['Normal'])

def load_material_next_by_next(path, cur_number=0):
    counter = 0
    for cur_path, cur_dirs, cur_files in os.walk(path):
        if len(cur_files) > 3 and counter >= cur_number:
            print(f"/nLoad {cur_path}")
            color_path = os.path.join(cur_path, "color.jpg")
            normal_path = os.path.join(cur_path, "normal.jpg")
            metal_path = os.path.join(cur_path, "metal.jpg")
            roughness_path = os.path.join(cur_path, "roughness.jpg")  # Korrigiert
            load_material_in_blend(color_path=color_path, normal_path=normal_path, roughness_path=roughness_path, metal_path=metal_path)
            #user_input = input("next:")
            return

        if len(cur_files) > 3:
            counter += 1

source_path = "/home/tobia/data/3xM/final/materials"
load_material_next_by_next(source_path, cur_number=0)



