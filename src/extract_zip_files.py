import os
import zipfile
import py7zr

def unzip_files(source_dir, destination_dir):
    # Check if source and destination directories exist
    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    error_files = []
    successfull = 0
    
    # Iterate over all files in the source directory
    for file_name in os.listdir(source_dir):
        # Check if the file is a zip file
        if file_name.endswith(".zip") or file_name.endswith(".7z"):
            file_path = os.path.join(source_dir, file_name)
            # Create a folder with the same name as the zip file (without .zip) in the destination directory
            extract_folder = os.path.join(destination_dir, ".".join(file_name.split(".")[:-1]))
            os.makedirs(extract_folder, exist_ok=True)
            
            try:
                if file_name.endswith(".zip"):
                    # Unzip the file
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                elif file_name.endswith(".7z"):
                    with py7zr.SevenZipFile(file_path, mode='r') as zip_ref:
                        zip_ref.extractall(path=extract_folder)

                successfull += 1
            except Exception:
                error_files += [file_path]
                print(f"Error during extracting {file_name} to {extract_folder}")
                continue
            
            print(f"Extracted: {file_name} to {extract_folder}")
        else:
            error_files += 1
            print(f"Error during extracting {file_name} = (is not a supported zip-format)")

    print(f"\n\nErrors: {len(error_files)}")
    for cur_err_file in error_files:
        print(f"    -> {cur_err_file}")

    print(f"\nSuccesfull: {successfull}")

if __name__ == "__main__":
    # Example usage:
    source_directory = '/home/tobia/Downloads/3xM'
    # destination_directory = '/home/tobia/data/3xM/models/polyhaven'
    # destination_directory = '/home/tobia/data/3xM/models/ambientcg'
    destination_directory = '/home/tobia/data/3xM/models/ABC'

    unzip_files(source_directory, destination_directory)



