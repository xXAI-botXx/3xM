import os
import unreal

ASSET_PATH = "D:/Informatik/Unreal Engine/SegmentationDataGen/Content"
MODEL_PATH = os.path.join(ASSET_PATH, "Item-Models")
MATERIAL_PATH = os.path.join(ASSET_PATH, "Item-Materials")

COPY_TO_ASSET_FOLDER = True
LOAD_INTO_UNREAL = True


def import_assets_from_directory(directory_path, destination_path):
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_import_tasks = []

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".fbx"):  # Adjust this to match your asset types
                asset_import_task = unreal.AssetImportTask()
                asset_import_task.filename = os.path.join(root, file)
                asset_import_task.destination_path = destination_path
                asset_import_task.automated = True
                asset_import_task.save = True
                asset_import_tasks.append(asset_import_task)

    asset_tools.import_asset_tasks(asset_import_tasks)


def update_data_asset(data_asset_path, asset_folder_path):
    data_asset = unreal.EditorAssetLibrary.load_asset(data_asset_path)
    if not data_asset:
        print(f"Data Asset not found at {data_asset_path}")
        return

    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = asset_registry.get_assets_by_path(asset_folder_path, recursive=True)

    mesh_references = []
    for asset in assets:
        if asset.asset_class == "StaticMesh":
            mesh_references.append(asset.object_path)

    data_asset.meshes = mesh_references
    unreal.EditorAssetLibrary.save_asset(data_asset_path)

def main():
    if COPY_TO_ASSET_FOLDER:
        
        update_data_asset("/Game/YourDataAsset", "/Game/YourFolder")

    if LOAD_INTO_UNREAL:
        import_assets_from_directory("C:/Path/To/Your/Assets", "/Game/YourFolder")

main()


