import os
import shutil
import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
from transform_materials import cv_img_is_none

# Function to calculate SSIM-based image similarity
def calculate_similarity(img_1, img_2):
    if img_1.shape != img_2.shape:
        if np.sum(img_1.shape) < np.sum(img_2.shape):
            print(f"Resizing roughness image from {img_2.shape} to {img_1.shape}")
            img_2 = cv2.resize(img_2, (img_1.shape[1], img_1.shape[0]))
        else:
            print(f"Resizing metal image from {img_1.shape} to {img_2.shape}  ")
            img_1 = cv2.resize(img_1, (img_2.shape[1], img_2.shape[0]))

    score, _ = ssim(cv2.cvtColor(img_1, cv2.COLOR_BGR2GRAY), cv2.cvtColor(img_2, cv2.COLOR_BGR2GRAY), full=True)
    return score

# Iterate through materials and compare them
def compare_materials_and_copy(material_folder, compare_folder, similarity_threshold=0.9, start_index=0, clear=False):
    if os.path.exists(compare_folder) and clear:
        shutil.rmtree(compare_folder)
    os.makedirs(compare_folder, exist_ok=True)
    
    counter = 0
    # go through evey category -> only compare the categories
    for cur_category in os.listdir(material_folder):
        print(f"Next Category: {cur_category}")
        cur_category_path = os.path.join(material_folder, cur_category)

        materials = {}
        # for cur_root_path, cur_dirs, cur_files in os.walk(material_folder):
        for cur_material_folder in os.listdir(cur_category_path):
            cur_material_path = os.path.join(cur_category_path, cur_material_folder)
            # if len(cur_files) > 2:
            if os.path.isdir(cur_material_path):
                material_name = cur_material_folder    # cur_material_path.split("/")[-1]
                material_path =cur_material_path    # "/".join(cur_material_path.split("/")[:-1])
                material_textures = ['normal.jpg', 'color.jpg', 'metal.jpg', 'roughness.jpg']
                textures = {}
                for texture_name in material_textures:
                    texture_path = os.path.join(cur_material_path, texture_name)
                    if os.path.exists(texture_path):
                        if not cv_img_is_none(cv2.imread(texture_path)):
                            textures[texture_name] = texture_path
                materials[material_name] = [textures, material_path]
        
        material_names = list(materials.keys())
        
        # Compare and copy similar materials
        for i in range(len(material_names)):
            for j in range(i + 1, len(material_names)):
                if counter >= start_index:
                    mat_1, path_1 = materials[material_names[i]]
                    mat_2, path_2 = materials[material_names[j]]
                    
                    similarity_scores = []
                    for texture_type in ['normal.jpg', 'color.jpg', 'metal.jpg', 'roughness.jpg']:
                        if texture_type in mat_1 and texture_type in mat_2:
                            img_1 = cv2.imread(mat_1[texture_type])
                            img_2 = cv2.imread(mat_2[texture_type])
                            similarity_score = calculate_similarity(img_1, img_2)
                            similarity_scores.append(similarity_score)
                    average_similarity = np.mean(similarity_scores)
                    print(average_similarity)
                    
                    if average_similarity > similarity_threshold:
                        # Copy similar materials to the compare folder
                        mat1_folder = os.path.join(compare_folder, f"{material_names[i]}-{material_names[j]}", material_names[i])
                        mat2_folder = os.path.join(compare_folder, f"{material_names[i]}-{material_names[j]}", material_names[j])
                        if not os.path.exists(mat1_folder):
                            shutil.copytree(path_1, mat1_folder)
                        if not os.path.exists(mat2_folder):
                            shutil.copytree(path_2, mat2_folder)
                        print(f"Material {material_names[i]} and Material {material_names[j]} are similar with a similarity score of {average_similarity:.2f}")

                counter += 1
                with open(f"./saves/material_sim_last_index_{int(counter%3)}.txt", "w") as index_file:
                    index_file.write(f"Last Index Counter: {counter}")
    # if os.path.exists("./saves/material_sim_last_index.txt"):
    #     os.remove("./saves/material_sim_last_index.txt")

if __name__ == "__main__":
    material_folder = "D:/Informatik/Projekte/3xM/model_material/brian_500_prep_ue" # "/home/tobia/data/3xM/final/materials"  # Path to your materials folder
    compare_folder = "D:/Informatik/Projekte/3xM/model_material/brian_500_compare" # "/home/tobia/data/3xM/materials/compare"  # Path to the comparison folder
    similarity_threshold = 0.8  # Similarity threshold

    compare_materials_and_copy(material_folder, compare_folder, similarity_threshold, start_index=0, clear=False)




