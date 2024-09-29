import unreal

def import_fbx_as_static_mesh(fbx_file_path, destination_path):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    fbx_import_options = unreal.FbxImportUI()

    # import settings
    fbx_import_options.import_mesh = True
    fbx_import_options.mesh_type_to_import = unreal.FBXImportType.FBXIT_STATIC_MESH
    
    # import fbx file
    asset_import_task = unreal.AssetImportTask()
    asset_import_task.filename = fbx_file_path
    asset_import_task.destination_path = destination_path
    asset_import_task.options = fbx_import_options
    asset_import_task.automated = True
    
    asset_tools.import_asset_tasks([asset_import_task])
    return asset_import_task.imported_object_paths


fbx_dir = "D:/Informatik/Projekte/3xM/model_material/final_models"
destination = "D:/Informatik/Unreal Engine/dataset_gen_3xM/Content/3xM/3D_models"

for cur_fbx_file in os.listdir(fbx_dir):
    cur_path = os.path.join(fbx_dir, cur_fbx_file)
    if os.path.isfile(cur_path) and cur_path.endswith(".fbx"):
        cur_dest = os.path.join(destination, cur_fbx_file)
        imported_assets = import_fbx_as_static_mesh(cur_path, cur_dest)
        print("Imported assets:", imported_assets)


