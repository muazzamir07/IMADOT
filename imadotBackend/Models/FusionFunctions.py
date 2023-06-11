#@title *Feature Fusion*

import os
import numpy as np
import tensorflow as tf
import cv2
from numpy.ma.core import argmax
from tensorflow import keras
from tensorflow.keras import Model 


def LateFusionPrediction(ct_folder, pet_folder, ct_model, pt_model, final_model):
    print("=================")
    print("STARTING LATE FUSION")
    print("=================")
    tumor_type=['A','B','G']

    # Load the image
#    ct_img = ct_folder[1]
#    pt_img = pet_folder[1]

#    ct_img_resized = tf.image.resize(ct_img, [256, 256])
#    pt_img_resized = tf.image.resize(ct_img, [256, 256])

    # Normalize the image
#    ct_img_normalized = ct_img_resized / 255.0
#    pt_img_normalized = pt_img_resized / 255.0

    # Add batch dimension
#    ct_img = tf.expand_dims(ct_img_normalized, axis=0)
#    pt_img = tf.expand_dims(pt_img_normalized, axis=0)


        
    ct_img_resized = tf.image.resize(tf.expand_dims(ct_folder[1], axis=0), [256, 256])
    pt_img_resized = tf.image.resize(tf.expand_dims(pet_folder[1], axis=0), [256, 256])

    # Normalize the image
    ct_img_normalized = ct_img_resized / 255.0
    pt_img_normalized = pt_img_resized / 255.0

    # Add batch dimension
    ct_img_batch = tf.expand_dims(ct_img_normalized, axis=0)
    pt_img_batch = tf.expand_dims(pt_img_normalized, axis=0)

    print("=================")
    print("SHAPE")
    print(ct_img_batch.shape)
    print(pt_img_batch.shape)
    print("=================")

    ct_image_shape = (ct_img_batch.shape[0], ct_img_batch.shape[1], ct_img_batch.shape[2], 3)
    ct_image = ct_img_batch[..., :3] # keep only the first 3 channels, i.e. the RGB channels
    ct_image = np.reshape(ct_image, ct_image_shape)

    pt_image_shape = (pt_img_batch.shape[0], pt_img_batch.shape[1], pt_img_batch.shape[2], 3)
    pt_image = pt_img_batch[..., :3] # keep only the first 3 channels, i.e. the RGB channels
    pt_image = np.reshape(pt_image, pt_image_shape)

    print("=================")
    print("NEW SHAPE")
    print(ct_image.shape)
    print(pt_image.shape)
    print("=================")


    #predict image from both the models
    ct=ct_model.predict(ct_image)
    pt=pt_model.predict(pt_image)

    from scipy.special import softmax

    # Apply Softmax to get confidence 
    c=softmax(ct)
    p=softmax(pt)

    c = c*1.2
    x = c+p

    output = argmax(x) 

    print("=================")
    print("OUTPUT")
    print(tumor_type[output])

    max_index = np.argmax(output)
    print("TUMOR TYPE")
    print(tumor_type[max_index])
    print("=================")    

    return max_index




#########################################################



def IntermediateFusionPrediction(ct_folder, pet_folder, ct_model, pt_model, final_model):

    print("=================")
    print("STARTING INTERMEDIATE FUSION")
    print("=================")
    tumor_type=['A','B','G']

    # LOADING MODELS
    #ct_model = tf.keras.models.load_model('./static/ct_model')
    #pt_model = tf.keras.models.load_model('./static/pt_model')
    #final_model = tf.keras.models.load_model('./static/model1')

    ##############################################################

    # MAY NEED TO FIX PATHS

    # Load the image
    # filename = "1.jpg"
    # ct_path = os.path.join(ct_folder, filename)
    # pet_path = os.path.join(pet_folder, filename)
    # ct_img = cv2.imread(ct_path)
    # pt_img = cv2.imread(pet_path)

    #ct_img_resized = tf.image.resize(ct_folder[0], [256, 256])
    #pt_img_resized = tf.image.resize(pet_folder[0], [256, 256])
    

    
    ct_img_resized = tf.image.resize(tf.expand_dims(ct_folder[1], axis=0), [256, 256])
    pt_img_resized = tf.image.resize(tf.expand_dims(pet_folder[1], axis=0), [256, 256])

    # Normalize the image
    ct_img_normalized = ct_img_resized / 255.0
    pt_img_normalized = pt_img_resized / 255.0

    # Add batch dimension
    ct_img_batch = tf.expand_dims(ct_img_normalized, axis=0)
    pt_img_batch = tf.expand_dims(pt_img_normalized, axis=0)

    print("=================")
    print("SHAPE")
    print(ct_img_batch.shape)
    print(pt_img_batch.shape)
    print("=================")

    ct_image_shape = (ct_img_batch.shape[0], ct_img_batch.shape[1], ct_img_batch.shape[2], 3)
    ct_image = ct_img_batch[..., :3] # keep only the first 3 channels, i.e. the RGB channels
    ct_image = np.reshape(ct_image, ct_image_shape)

    pt_image_shape = (pt_img_batch.shape[0], pt_img_batch.shape[1], pt_img_batch.shape[2], 3)
    pt_image = pt_img_batch[..., :3] # keep only the first 3 channels, i.e. the RGB channels
    pt_image = np.reshape(pt_image, pt_image_shape)

    print("=================")
    print("NEW SHAPE")
    print(ct_image.shape)
    print(pt_image.shape)
    print("=================")


    print("GETTING CT & PET RESULTS")
    print("=================")    
    ct_feature_output = Model(ct_model.layers[0].input, ct_model.layers[len(ct_model.layers)-2].output)
    #ct_output = ct_feature_output.predict(ct_img_batch)
    ct_output = ct_feature_output.predict(ct_image)


    pt_feature_output = Model(pt_model.layers[0].input, pt_model.layers[len(pt_model.layers)-2].output)
    #pt_output = pt_feature_output.predict(pt_img_batch)
    pt_output = pt_feature_output.predict(pt_image)
    
    
    print("=================")
    print("CONCATENATING RESULTS FOR INTERMEDIATE FUSION")
    print("=================")

    fused_output = np.concatenate((ct_output, pt_output),axis=1)
    final_output = final_model.predict(fused_output)  

    print("=================")
    print("OUTPUT")
    #print(final_output)
    print("Probability of Type A: ")
    print(final_output[0][0]) 
    print("Probability of Type B: ")
    print(final_output[0][1]) 
    print("Probability of Type G: ")
    print(final_output[0][2]) 

    print("=================")    

    max_index = np.argmax(final_output)
    print("TUMOR TYPE")
    print(tumor_type[max_index])
    print("=================")    

    # get the actual maximum value
    max_prob = final_output[0][max_index]

    return tumor_type[max_index], max_prob
