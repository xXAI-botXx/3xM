import cv2
import numpy as np

# Function to calculate the mean and variance of an image
def calculate_mean_variance(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean = np.mean(gray_image)
    variance = np.var(gray_image)
    return mean, variance

# Function to calculate means and variances for a list of images
def calculate_values(images):
    means = []
    variances = []
    for image in images:
        mean, variance = calculate_mean_variance(image)
        means.append(mean)
        variances.append(variance)
    return means, variances

# Function to calculate similarity between two sets of images
def calculate_similarity(values1, values2):
    mean_diff = np.sum(np.abs(np.array(values1[0]) - np.array(values2[0])))
    variance_diff = np.sum(np.abs(np.array(values1[1]) - np.array(values2[1])))
    total_diff = mean_diff + variance_diff
    similarity = 1 / (1 + total_diff)  # Avoid infinite similarity
    return similarity

# Function to map textures onto a square or circle
def map_texture(shape, images, canvas_size=(512, 512)):
    # Combine the 5 images into a composite texture
    texture = np.zeros_like(images[0])
    for image in images:
        texture = cv2.addWeighted(texture, 0.2, image, 0.2, 0)
    
    # Create a blank canvas
    canvas = np.zeros((canvas_size[0], canvas_size[1], 3), dtype=np.uint8)
    
    if shape == 'square':
        # Map texture onto a square
        side_length = min(canvas_size) // 2
        start_point = (canvas_size[0] // 4, canvas_size[1] // 4)
        canvas[start_point[0]:start_point[0]+side_length, start_point[1]:start_point[1]+side_length] = texture
    elif shape == 'circle':
        # Map texture onto a circle
        radius = min(canvas_size) // 4
        center = (canvas_size[0] // 2, canvas_size[1] // 2)
        mask = np.zeros_like(canvas[:, :, 0])
        cv2.circle(mask, center, radius, 255, -1)
        texture_resized = cv2.resize(texture, (radius * 2, radius * 2))
        texture_masked = cv2.bitwise_and(texture_resized, texture_resized, mask=mask[center[0] - radius:center[0] + radius, center[1] - radius:center[1] + radius])
        canvas[center[0] - radius:center[0] + radius, center[1] - radius:center[1] + radius] = texture_masked

    return canvas

# Example: Compare two materials with 5 images each and optionally render them
def main(compare_materials=True, render_shapes=True):
    # Load the 5 images for each material
    images_object1 = [cv2.imread(f"image_object1_{i}.jpg") for i in range(1, 6)]
    images_object2 = [cv2.imread(f"image_object2_{i}.jpg") for i in range(1, 6)]
    
    # Calculate means and variances of the images
    values_object1 = calculate_values(images_object1)
    values_object2 = calculate_values(images_object2)
    
    if compare_materials:
        # Calculate similarity
        similarity = calculate_similarity(values_object1, values_object2)
        print(f"Similarity score: {similarity}")

    if render_shapes:
        # Render the materials mapped onto a square and a circle
        square_texture1 = map_texture('square', images_object1)
        circle_texture1 = map_texture('circle', images_object1)
        square_texture2 = map_texture('square', images_object2)
        circle_texture2 = map_texture('circle', images_object2)
        
        # Display the results
        cv2.imshow('Material 1 - Square', square_texture1)
        cv2.imshow('Material 1 - Circle', circle_texture1)
        cv2.imshow('Material 2 - Square', square_texture2)
        cv2.imshow('Material 2 - Circle', circle_texture2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

    # go through every material and check the complete similarity



