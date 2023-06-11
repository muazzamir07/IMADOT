#@title *3DPLOT*

import base64
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt
import os
import pydicom
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def ploting(image):
    # Calculate the threshold value as the average of the minimum and maximum pixel values
    threshold = (image.min() + image.max()) / 2.0
    # Construct the 3D mesh
    verts, faces, _, _ = measure.marching_cubes(image, threshold)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    # Set the viewing angle
    ax.view_init(30, 30)
    # Plot the mesh
    mesh = Poly3DCollection(verts[faces], alpha=0.3)
    face_color = [0.2, 0.2, 0.1]
    mesh.set_facecolor(face_color)
    ax.add_collection3d(mesh)
    ax.set_xlim(0, image.shape[0])
    ax.set_ylim(0, image.shape[1])
    ax.set_zlim(0, image.shape[2])
    #plt.show()
    #plt.savefig('3DOutput')

    canvas = FigureCanvas(fig)
    png_output = io.BytesIO()
    canvas.print_png(png_output)
    # Return the PNG image data as a byte string
    return png_output.getvalue()


def Plot3D(ct_folder, pet_folder):
    print("Reached 3d plot function")
    # Loop through all DICOM files in the input directory
    for filename in os.listdir(ct_folder):
        # Read the DICOM file
        ds = pydicom.read_file(os.path.join(ct_folder, filename))

        # Get the pixel data as a NumPy array
        pixel_data = ds.pixel_array.astype(float)

        # Check if the Slope and Intercept attributes are present
        if hasattr(ds, 'Slope') and hasattr(ds, 'Intercept'):
            # Apply the Slope and Intercept values to the pixel data
            pixel_data = pixel_data * ds.Slope + ds.Intercept
        else:
            # If the Slope and Intercept attributes are not present,
            # assume that the pixel data has already been rescaled
            print('pewpew')

    # Send the 3D model to path_3d function
    #plot_3d(pixel_data)

    plot_data = ploting(pixel_data)
    # Return the plot data as a base64-encoded string
    return base64.b64encode(plot_data).decode('utf-8')    