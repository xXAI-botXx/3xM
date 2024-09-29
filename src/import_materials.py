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



def create_material_with_image_maps(material_name, texture_color, texture_metal, texture_normal, texture_roughness, texture_height, texture_ambient_occlusion):
    material_path = '/Game/3xM/Materials/' + material_name

    # Material erstellen
    material_factory = unreal.MaterialFactoryNew()
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(material_name, '/Game/3xM/Materials', unreal.Material, material_factory)
    
    material_editor = unreal.MaterialEditingLibrary

    # Base Color (Farbe)
    if texture_color:
        base_color_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, 0)
        base_color_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_color))
        material_editor.connect_material_property(base_color_texture, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)

    # Metallic
    if texture_metal:
        metallic_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -150)
        metallic_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_metal))
        material_editor.connect_material_property(metallic_texture, 'RGB', unreal.MaterialProperty.MP_METALLIC)

    # Normal Map
    if texture_normal:
        normal_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -300)
        normal_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_normal))
        material_editor.connect_material_property(normal_texture, 'RGB', unreal.MaterialProperty.MP_NORMAL)

    # Roughness Map
    if texture_roughness:
        roughness_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -450)
        roughness_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_roughness))
        material_editor.connect_material_property(roughness_texture, 'RGB', unreal.MaterialProperty.MP_ROUGHNESS)
    
    # Height Map
    if texture_height:
        height_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -600)
        height_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_height))
        material_editor.connect_material_property(height_texture, 'R', unreal.MaterialProperty.MP_WORLDDISPLACEMENT)
    
    # Ambient Occlusion Map
    if texture_ambient_occlusion:
        ao_texture = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -750)
        ao_texture.set_editor_property('texture', unreal.EditorAssetLibrary.load_asset(texture_ambient_occlusion))
        material_editor.connect_material_property(ao_texture, 'R', unreal.MaterialProperty.MP_AMBIENTOCCLUSION)

    # Material speichern
    unreal.EditorAssetLibrary.save_asset(material_path)
    unreal.EditorAssetLibrary.save_loaded_asset(material)



def create_material_with_uasset_maps(material_name, base_color_asset_path, metallic_asset_path, normal_asset_path, roughness_asset_path, ao_asset_path):
    BASE_PATH = "/Game/3xM/Materials/"

    unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(["/Game/3xM/Textures"])

    
    # create new material
    material_path = BASE_PATH + material_name
    material_factory = unreal.MaterialFactoryNew()
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(material_name, BASE_PATH, unreal.Material, material_factory)
    
    material_editor = unreal.MaterialEditingLibrary

    # load the texture
    base_color_texture = unreal.EditorAssetLibrary.load_asset(base_color_asset_path) if base_color_asset_path else None
    metallic_texture = unreal.EditorAssetLibrary.load_asset(metallic_asset_path) if metallic_asset_path else None
    normal_texture = unreal.EditorAssetLibrary.load_asset(normal_asset_path) if normal_asset_path else None
    roughness_texture = unreal.EditorAssetLibrary.load_asset(roughness_asset_path) if roughness_asset_path else None
    ao_texture = unreal.EditorAssetLibrary.load_asset(ao_asset_path) if ao_asset_path else None

    if base_color_texture:
        base_color_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, 0)
        base_color_sample.set_editor_property('texture', base_color_texture)
        material_editor.connect_material_property(base_color_sample, '', unreal.MaterialProperty.MP_BASE_COLOR)

    if metallic_texture:
        metallic_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -150)
        metallic_sample.set_editor_property('texture', metallic_texture)
        material_editor.connect_material_property(metallic_sample, '', unreal.MaterialProperty.MP_METALLIC)

    if normal_texture:
        normal_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -300)
        normal_sample.set_editor_property('texture', normal_texture)
        material_editor.connect_material_property(normal_sample, '', unreal.MaterialProperty.MP_NORMAL)

    if roughness_texture:
        roughness_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -450)
        roughness_sample.set_editor_property('texture', roughness_texture)
        material_editor.connect_material_property(roughness_sample, '', unreal.MaterialProperty.MP_ROUGHNESS)

    if ao_texture:
        ao_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -600)
        ao_sample.set_editor_property('texture', ao_texture)
        material_editor.connect_material_property(ao_sample, '', unreal.MaterialProperty.MP_AMBIENTOCCLUSION)

    # save material
    unreal.EditorAssetLibrary.save_asset(material_path)
    unreal.EditorAssetLibrary.save_loaded_asset(material)



def create_material_with_uasset_maps_by_names(material_name, base_color_asset_name, metallic_asset_name, normal_asset_name, roughness_asset_name, ao_asset_name):
    BASE_PATH = "/Game/3xM/Materials/"

    unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(["/Game/3xM/Textures"])

    
    # create new material
    material_path = BASE_PATH + material_name
    material_factory = unreal.MaterialFactoryNew()
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(material_name, BASE_PATH, unreal.Material, material_factory)
    
    material_editor = unreal.MaterialEditingLibrary

    # load the texture
    base_color_texture = find_and_load_asset_by_name(base_color_asset_name) if base_color_asset_name else None
    metallic_texture = find_and_load_asset_by_name(metallic_asset_name) if metallic_asset_name else None
    normal_texture = find_and_load_asset_by_name(normal_asset_name) if normal_asset_name else None
    roughness_texture = find_and_load_asset_by_name(roughness_asset_name) if roughness_asset_name else None
    ao_texture = find_and_load_asset_by_name(ao_asset_name) if ao_asset_name else None

    if base_color_texture:
        base_color_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, 0)
        base_color_sample.set_editor_property('texture', base_color_texture)
        material_editor.connect_material_property(base_color_sample, '', unreal.MaterialProperty.MP_BASE_COLOR)

    if metallic_texture:
        metallic_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -150)
        metallic_sample.set_editor_property('texture', metallic_texture)
        material_editor.connect_material_property(metallic_sample, '', unreal.MaterialProperty.MP_METALLIC)

    if normal_texture:
        normal_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -300)
        normal_sample.set_editor_property('texture', normal_texture)
        material_editor.connect_material_property(normal_sample, '', unreal.MaterialProperty.MP_NORMAL)

    if roughness_texture:
        roughness_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -450)
        roughness_sample.set_editor_property('texture', roughness_texture)
        material_editor.connect_material_property(roughness_sample, '', unreal.MaterialProperty.MP_ROUGHNESS)

    if ao_texture:
        ao_sample = material_editor.create_material_expression(material, unreal.MaterialExpressionTextureSample, -384, -600)
        ao_sample.set_editor_property('texture', ao_texture)
        material_editor.connect_material_property(ao_sample, '', unreal.MaterialProperty.MP_AMBIENTOCCLUSION)

    # save material
    unreal.EditorAssetLibrary.save_asset(material_path)
    unreal.EditorAssetLibrary.save_loaded_asset(material)



def find_and_load_asset_by_name(asset_name, class_name=["Texture2D"]):
    # create reference to  Asset-Registry
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    # filter to search texture
    search_filter = unreal.ARFilter(class_names=class_name, package_paths=["/Game/"], recursive_paths=True)
    
    # search for assets
    assets = asset_registry.get_assets(search_filter)
    
    # go through results -> should only get one result
    for asset_data in assets:
        if asset_name.lower() in str(asset_data.asset_name).lower():
            asset_path = str(asset_data.package_name)
            print(f"Asset found: {asset_path}")
            
            # load asset
            asset = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            if asset:
                print(f"Asset successfull loaded: {asset}")
                return asset
            else:
                print(f"Failed loading Asset: {asset_name}")
    
    print(f"No Asset with name {asset_name} found.")
    return None



print("#"*12)
print("Start Material Import")
MAKE_TEXTURES = False
MAKE_MATERIALS = False
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

        if MAKE_TEXTURES:
            cur_idx = idx
        else:
            cur_idx = cur_dir.split("_")[-1]
        color_path = f"{dest_path}/{cur_dir}/3xM_Color_{cur_idx}.uasset"
        metal_path = f"{dest_path}/{cur_dir}/3xM_Metal_{cur_idx}.uasset"
        roughness_path = f"{dest_path}/{cur_dir}/3xM_Roughness_{cur_idx}.uasset"
        normal_path = f"{dest_path}s/{cur_dir}/3xM_Normal_{cur_idx}.uasset"
        ao_path = f"{dest_path}s/{cur_dir}/3xM_AO_{cur_idx}.uasset"

        if MAKE_MATERIALS:
            # create_material_with_image_maps(
            create_material_with_uasset_maps_by_names(
                            material_name=f"3xM_Material_ID_{idx}", 
                            base_color_asset_name=f"3xM_Color_{cur_idx}", 
                            metallic_asset_name=f"3xM_Metal_{cur_idx}", 
                            roughness_asset_name=f"3xM_Roughness_{cur_idx}", 
                            normal_asset_name=f"3xM_Normal_{cur_idx}", 
                            ao_asset_name=None)
                    
        idx += 1
        success += 1
    else:
        fail += 1

print(f"Finished Importing: Success: {success}\nFailed: {fail}")

