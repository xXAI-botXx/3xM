import os


def count(path, have_subdirs=False):
    """
    Counts all elements and filetypes in a dir with subdirs or without.

    have_subdirs = True:
    /home/user/dir -> searches for folders and files in every folder of this path

    have_subdirs = False:
    /home/user/dir -> searches for folders and files direct in this path
    """
    n_elements = 0
    content = dict()

    if have_subdirs:
        for category in os.listdir(path):
            for cur_elem_dir in os.listdir(os.path.join(path, category)):
                if os.path.isdir(os.path.join(path, category, cur_elem_dir)):
                    n_elements += 1

                    for cur_path, cur_dirs, cur_files in os.walk(os.path.join(path, category, cur_elem_dir)):
                        for cur_file in cur_files:
                            file_type = cur_file.split(".")[-1]
                            if file_type in content.keys():
                                content[file_type] += 1
                            else:
                                content[file_type] = 1
    else:
        for cur_elem_dir in os.listdir(path):
            if os.path.isdir(os.path.join(path, cur_elem_dir)):
                n_elements += 1

                for cur_path, cur_dirs, cur_files in os.walk(os.path.join(path, cur_elem_dir)):
                    for cur_file in cur_files:
                        file_type = cur_file.split(".")[-1]
                        if file_type in content.keys():
                            content[file_type] += 1
                        else:
                            content[file_type] = 1

    print(f"Founded {n_elements} elements.")
    print(f"File-Types:")
    for key, value in sorted(content.items(), key=lambda x:x[1]):
        print(f"    -> '{key}': {value}")


if __name__ == "__main__":
    PATH = "/home/tobia/data/3xM/3xM/"

    print(f"\n {'-'*16}\n    3D-MODELS\n {'-'*16}")
    count(path=os.path.join(PATH, "models"), have_subdirs=False)

    print(f"\n\n {'-'*16}\n    MATERIALS\n {'-'*16}")
    count(path=os.path.join(PATH, "materials"), have_subdirs=False)

    
