import imageio.v2 as imageio
import os

# Create an empty list to store the images
images = []

# Load all the PNGs in the folder
for file_name in sorted(os.listdir('/g/data/er8/lightning/georgia/Bourke_radar')):
    if file_name.endswith('.png'):
        file_path = os.path.join('/g/data/er8/lightning/georgia/Bourke_radar', file_name)
        images.append(imageio.imread(file_path))

# Save the images as a GIF
imageio.mimsave('Bourke.gif', images, fps=2)
