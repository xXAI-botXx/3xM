import trimesh
import numpy as np
from scipy.spatial import distance

def load_model(file_path):
    # Load a 3D model (STL file in this case) using trimesh
    return trimesh.load(file_path)

def calculate_hausdorff_distance(mesh1, mesh2):
    # Extract the vertices (point clouds) from the two models
    vertices1 = mesh1.vertices
    vertices2 = mesh2.vertices
    
    # Compute the Hausdorff distance between the point clouds
    dist_A_to_B = distance.cdist(vertices1, vertices2, 'euclidean').min(axis=1).max()
    dist_B_to_A = distance.cdist(vertices2, vertices1, 'euclidean').min(axis=1).max()
    
    return max(dist_A_to_B, dist_B_to_A)

def compare_models(model_paths):
    # Load all models (STL in this case)
    models = [load_model(path) for path in model_paths]
    num_models = len(models)
    
    # Matrix to store pairwise similarity (Hausdorff distances)
    similarity_matrix = np.zeros((num_models, num_models))
    
    # Compute similarity (Hausdorff distance) pairwise
    for i in range(num_models):
        for j in range(i + 1, num_models):
            dist = calculate_hausdorff_distance(models[i], models[j])
            similarity_matrix[i, j] = dist
            similarity_matrix[j, i] = dist  # Distance is symmetric
    
    return similarity_matrix

# Example file paths to your STL models
model_paths = ['model1.stl', 'model2.stl', 'model3.stl']

# Calculate the similarity between all models
similarity_matrix = compare_models(model_paths)

# Print the results
print("Similarity Matrix (Hausdorff Distance):")
print(similarity_matrix)



