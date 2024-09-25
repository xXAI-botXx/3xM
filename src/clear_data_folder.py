import os

print(f"{'-'*12}\nStarted clearing Screenshot Folder...")

# PROJECT_NAME = "dataset_gen_3xM"

ABSOLUTE_PROJECT_PATH = "D:/Informatik/Projekte/3xM/3xM/"

# # find Unreal Project
# if ABSOLUTE_PROJECT_PATH:
#     PROJECT_PATH = os.path.join(ABSOLUTE_PROJECT_PATH, PROJECT_NAME)
# else:
#     if PROJECT_NAME in os.listdir("./"):
#         PROJECT_PATH = f"./{PROJECT_NAME}"
#     elif PROJECT_NAME in os.listdir("../"):
#         PROJECT_PATH = f"../{PROJECT_NAME}"
#     else:
#         raise FileNotFoundError(f"Can't find Unreal project '{PROJECT_NAME}'.\n   -> Make sure that you have this file in your project or one dir over your Unreal Project!")
# 
# # find Screenshot Path
# IMAGE_SAVE_PATH = os.path.join(PROJECT_PATH, "Saved", "Screenshots")

# print(f"Founded Screenshot-folder at: {IMAGE_SAVE_PATH}")

# delete all files in Screenshot folder, but not the folders
print("\nStart deleting...")
success = 0
fail = 0
for cur_dir_path, cur_dirs, cur_files in os.walk(ABSOLUTE_PROJECT_PATH):
    for cur_file in cur_files:
        file_path = os.path.join(cur_dir_path, cur_file)
        try:
            os.remove(file_path)
            success += 1
            print(f"{file_path} has been deleted.")
        except FileNotFoundError:
            print(f"The file {file_path} does not exist.")
            fail += 1
        except PermissionError:
            print(f"Permission denied: unable to delete {file_path}.")
            fail += 1
        except Exception as e:
            print(f"Error: {e}")
            fail += 1

print(f"{'-'*12}\nFounded {success+fail} Files.\n    -> Successfull Cleared: {success}\n    -> Failed Cleared: {fail}") 

