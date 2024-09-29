import os
import unreal

def import_texture(file_path, destination_path, name):
    # Texture Import Options
    texture_factory = unreal.TextureFactory()
    texture_factory.set_editor_property('compression_settings', unreal.TextureCompressionSettings.TC_DEFAULT)
    # texture_factory.set_editor_property('filter', unreal.TextureFilter.TF_BILINEAR)

    # Asset Import Task
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', file_path)
    task.set_editor_property('destination_path', destination_path)
    task.set_editor_property('destination_name', name)  # Name der Datei ohne Endung
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('automated', True)
    task.set_editor_property('save', True)

    # Import
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

def create_material_with_all_maps(material_name, texture_color, texture_metal, texture_normal, texture_roughness, texture_height, texture_ambient_occlusion):
    # Material-Asset-Pfad
    material_path = '/Game/3xM/Materials/' + material_name
    
    # Material erstellen
    material_factory = unreal.MaterialFactoryNew()
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(material_name, '/Game/3xM/Materials', unreal.Material, material_factory)
    
    # Material-Node-Setup
    material_editor = unreal.MaterialEditingLibrary

    # Base Color
    base_color_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -512, -512)
    base_color_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_color))
    material_editor.connect_material_property(base_color_texture, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)

    # Metallic Map
    metallic_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -512, -512)
    metallic_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_metal))
    material_editor.connect_material_property(metallic_texture, 'RGB', unreal.MaterialProperty.MP_METALLIC)

    # Normal Map
    normal_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -512, -512)
    normal_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_normal))
    material_editor.connect_material_property(normal_texture, 'RGB', unreal.MaterialProperty.MP_NORMAL)

    # Roughness Map
    roughness_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -512, -512)
    roughness_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_roughness))
    material_editor.connect_material_property(roughness_texture, 'RGB', unreal.MaterialProperty.MP_ROUGHNESS)
    
    # # Height Map
    # height_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -512, -512)
    # height_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_height))
    # material_editor.connect_material_property(height_texture, 'R', unreal.MaterialProperty.MP_WORLDDISPLACEMENT)
    
    # # Ambient Occlusion Map
    # ao_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -512, -512)
    # ao_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_ambient_occlusion))
    # material_editor.connect_material_property(ao_texture, 'R', unreal.MaterialProperty.MP_AMBIENTOCCLUSION)

    # Material speichern
    unreal.EditorAssetLibrary.save_asset(material_path)
    unreal.EditorAssetLibrary.save_loaded_asset(material)


print("#"*12)
print("Start Material Import")
MAKE_TEXTURES = False
MAKE_MATERIALS = True
source_path = "D:/Informatik/Projekte/3xM/final_materials_UE"
dest_path = "/Game/3xM/Textures"
ending = ".png"

success = 0
fail = 0
idx = 0
for cur_dir in os.listdir(source_path):
    cur_path = os.path.join(source_path, cur_dir)

    color_path = os.path.join(cur_path, f"color{ending}")
    metal_path = os.path.join(cur_path, f"metal{ending}")
    roughness_path = os.path.join(cur_path, f"roughness{ending}")
    normal_path = os.path.join(cur_path, f"normal{ending}")
    height_path = os.path.join(cur_path, f"height{ending}")
    ao_path = os.path.join(cur_path, f"ambient_occlusion{ending}")

    if os.path.exists(os.path.join(cur_path, color_path)) and \
        os.path.exists(os.path.join(cur_path, metal_path)) and \
        os.path.exists(os.path.join(cur_path, roughness_path)) and \
        os.path.exists(os.path.join(cur_path, normal_path)): # and \
        # os.path.exists(os.path.join(cur_path, height_path)) and \
        # os.path.exists(os.path.join(cur_path, ao_path)):

        # import textures
        if MAKE_TEXTURES:
            import_texture(color_path, f"{dest_path}/{cur_dir}", f"3xM_Color_{idx}")
            import_texture(metal_path, f"{dest_path}/{cur_dir}", f"3xM_Metal_{idx}")
            import_texture(roughness_path, f"{dest_path}/{cur_dir}", f"3xM_Roughness_{idx}")
            import_texture(normal_path, f"{dest_path}/{cur_dir}", f"3xM_Normal_{idx}")
            # import_texture(height_path, f"{dest_path}/{cur_dir}", f"3xM_Height_{idx}")
            # import_texture(ao_path, f"{dest_path}/{cur_dir}", f"3xM_AO_{idx}")

        color_path = f"{dest_path}/{cur_dir}/3xM_Color_{idx}.uasset"
        metal_path = f"{dest_path}/{cur_dir}/3xM_Metal_{idx}.uasset"
        roughness_path = f"{dest_path}/{cur_dir}/3xM_Roughness_{idx}.uasset"
        normal_path = f"{dest_path}s/{cur_dir}/3xM_Normal_{idx}.uasset"
        height_path = f"{dest_path}/{cur_dir}/3xM_Height_{idx}.uasset"
        ao_path = f"{dest_path}s/{cur_dir}/3xM_AO_{idx}.uasset"

        if MAKE_MATERIALS:
            create_material_with_all_maps(
                            material_name=f"3xM_Material_ID_{idx}", 
                            texture_color=color_path, 
                            texture_metal=metal_path, 
                            texture_roughness=roughness_path, 
                            texture_normal=normal_path, 
                            texture_height=height_path, 
                            texture_ambient_occlusion=ao_path)
                    
        idx += 1
        success += 1
    else:
        fail += 1

print(f"Finished Importing: Success: {success}\nFailed: {fail}")

