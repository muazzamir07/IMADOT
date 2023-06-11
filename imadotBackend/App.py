'''
from flask import Flask, Response, request
from flask_cors import CORS
from Models.FusionFunctions import FusionPrediction
from Models.UNETFunctions import UNETPrediction

app = Flask(__name__)
CORS(app)

@app.route('/api/predict', methods=['POST'])
def predict():
    print("Processing ...")

    ct_folder = None
    pet_folder = None

    # Check if ct and pet folders are provided in the request
    if 'ctFolder' in request.files:
        ct_folder = request.files['ctFolder']
    if 'petFolder' in request.files:
        pet_folder = request.files['petFolder']

    # If either folder is missing, return an error message
    if ct_folder is None or pet_folder is None:
        return {'message': 'Both CT and PET folders are required.'}, 400

    ###########################################################
    
    
    # RETURNS SEGMENTED PNG IMAGE

    # HAVE TO RETURN DICE COEFF TOO SUBHA

    segmented_png = UNETPrediction(ct_folder, pet_folder)

    #response = Response(segmented_png, mimetype="image/PNG")


    ############################################################

    # DO FUSION STUFF
    fusion_output = FusionPrediction(ct_folder, pet_folder)

    response = Response(fusion_output)

    # RETURN TO FRONT END 
    # HAVE TO RETURN SEGMENTED IMG, DICE COEFF, FUSION RESULTS

    return response
    #return {'message': 'Prediction successful.'}, 200

    


@app.route('/api/plot3D', methods=['POST'])
def plot3D():
    print("Processing ...")

    ct_folder = None
    pet_folder = None
    # Check if ct and pet folders are provided in the request
    if 'ctFolder' in request.files:
        ct_folder = request.files['ctFolder']
    if 'petFolder' in request.files:
        pet_folder = request.files['petFolder']

    # If either folder is missing, return an error message
    if ct_folder is None or pet_folder is None:
        return {'message': 'Both CT and PET folders are required.'}, 400

    ###########################################################
    
    # RETURNS 3D PLOT PNG IMAGE
    plot_png = plot3D(ct_folder, pet_folder)

    # recieving base64-encoded string. Need to send back png. 
    # Figure how to do it
    response = Response(plot_png, mimetype="image/PNG")
    return response



if __name__ == "__main__":
    app.run(debug=True)
'''

import base64
import json
import os
import io
from flask import Flask, Response, make_response, request, jsonify, send_file
from flask_cors import CORS
import tensorflow as tf
from Models.FusionFunctions import IntermediateFusionPrediction, LateFusionPrediction
from Models.UNETFunctions import UNETPrediction
import numpy as np, cv2 as cv
from PIL import Image
app = Flask(__name__)
CORS(app)

CORS(app, origins=['http://localhost:4200'])


# LOADING MODELS AT THE START
@app.before_first_request
def initialize_variable():
    # LOADING MODELS
    global ct_model
    global pt_model
    global final_model
    ct_model = tf.keras.models.load_model('./static/ct_model')
    pt_model = tf.keras.models.load_model('./static/pt_model')
    final_model = tf.keras.models.load_model('./static/model1')


@app.route('/api/predict', methods=['POST'])
def predict():
    print("=================")
    print("PROCESSING STARTS")
    print("=================")

    ct_folder = None
    pet_folder = None

    # Check if ct and pet folders are provided in the request
    if 'ctFolder' in request.files:
        ct_folder = request.files.getlist('ctFolder')
    if 'petFolder' in request.files:
        pet_folder = request.files.getlist('petFolder')

    # If either folder is missing, return an error message
    if ct_folder is None or pet_folder is None:
        return {'message': 'Both CT and PET folders are required.'}, 400

    CT_IMAGES = []
    counter = 0
    for image in ct_folder:
        counter+=1
        image = image.read()
        img = np.frombuffer(image, np.uint8)
        img = cv.imdecode(img, cv.IMREAD_GRAYSCALE)
        #img = cv.resize(img, (128, 128))
        cv.imwrite("Testing/" + str(counter) + ".jpeg", img)
        CT_IMAGES.append(img)

    # print("CT IMAGES = ", counter)
    # print(CT_IMAGES)

    PET_IMAGES = []
    counter = 0
    for image in pet_folder:
        counter+=1
        
        image = image.read()
        img = np.frombuffer(image, np.uint8)
        img = cv.imdecode(img, cv.IMREAD_GRAYSCALE)
        #img = cv.resize(img, (128, 128))
        cv.imwrite("Testing/" + str(counter) + ".jpeg", img)
        PET_IMAGES.append(img)

    #print("PET IMAGES = ", counter)

    segmented_np = UNETPrediction(CT_IMAGES, PET_IMAGES)
    # print(segmented_png)


    print("=================")
    print("STARTING INTERMEDIATE FUSION")
    print("=================")
    int_tumor_type, int_tumor_prob = IntermediateFusionPrediction(CT_IMAGES, PET_IMAGES, ct_model, pt_model, final_model)

    print("=================")
    print("STARTING LATE FUSION")
    print("=================")
    late_tumor_prob = LateFusionPrediction(CT_IMAGES, PET_IMAGES, ct_model, pt_model, final_model)

    # Create response object
    #response = Response()

    # Set response data and headers
    #response = make_response(b'success')
    #response.headers['Content-Type'] = 'text/plain'
    #response.headers['tumor_type'] = str(int_tumor_type)
    #response.headers['tumor_prob'] = str(int_tumor_prob)

    #print(response.headers['tumor_type'])
    #print(str(int_tumor_type))
    #print(str(int_tumor_prob))
    


    retImg, buffer = cv.imencode('.jpg', segmented_np)
    img_bytes = buffer.tobytes()
            
    response = Response(img_bytes, mimetype="image/jpeg")

    response.headers['tumor_type'] = int_tumor_type
    response.headers['tumor_prob'] = int_tumor_prob
    response.headers['tumor_prob_late'] = late_tumor_prob

    response.headers.add('Access-Control-Expose-Headers', 'tumor_type')
    response.headers.add('Access-Control-Expose-Headers', 'tumor_prob')
    response.headers.add('Access-Control-Expose-Headers', 'tumor_prob_late')
    
    print("=================")
    print("RETURNING")
    print("=================")

    return response

#    tumor_detail = [int_tumor_type, int_tumor_prob]

#    retImg, buffer = cv.imencode('.PNG', segmented_png)
#    img_bytes = buffer.tobytes()
            
#    response = Response(img_bytes, mimetype="image/PNG")
#    response.headers['tumor_detail'] = tumor_detail

#    response.headers.add('Access-Control-Expose-Headers', 'tumor_detail')

#    return response






    # Return the PNG image as a response
#    response = {'int_tumor_type': int_tumor_type, 'int_tumor_prob': int_tumor_prob}
    #return send_file(segmented_png, mimetype='image/png', as_attachment=False), jsonify(response)

#    return jsonify({
#        "int_tumor_type": int_tumor_type,
#        "int_tumor_prob": int_tumor_prob
#    })



    ###########################################################
    
    # RETURNS SEGMENTED PNG IMAGE

    # HAVE TO RETURN DICE COEFF TOO SUBHA

    #segmented_png = UNETPrediction(ct_folder, pet_folder)

    #response = Response(segmented_png, mimetype="image/PNG")


    ############################################################

    # DO FUSION STUFF
    #fusion_output = FusionPrediction(ct_folder, pet_folder)

    #response = Response(fusion_output)

    # RETURN TO FRONT END 
    # HAVE TO RETURN SEGMENTED IMG, DICE COEFF, FUSION RESULTS

    #return response
    #return {'message': 'Prediction successful.'}, 200

    


@app.route('/api/plot3D', methods=['POST'])
def plot3D():
    print("Processing ...")

    ct_folder = None
    pet_folder = None
    # Check if ct and pet folders are provided in the request
    if 'ctFolder' in request.files:
        ct_folder = request.files.getlist('ctFolder')
    if 'petFolder' in request.files:
        pet_folder = request.files.getlist('petFolder')

    # If either folder is missing, return an error message
    if ct_folder is None or pet_folder is None:
        return {'message': 'Both CT and PET folders are required.'}, 400

    CT_IMAGES = []
    counter = 0
    for image in ct_folder:
        counter+=1
        image = image.read()
        img = np.frombuffer(image, np.uint8)
        img = cv.imdecode(img, cv.IMREAD_COLOR)
        img = cv.resize(img, (128, 128))
        # cv.imwrite("Testing/" + str(counter) + ".jpeg", img)
        CT_IMAGES.append(img)

    print("CT IMAGES = ", counter)

    PET_IMAGES = []
    counter = 0
    for image in pet_folder:
        counter+=1
        image = image.read()
        img = np.frombuffer(image, np.uint8)
        img = cv.imdecode(img, cv.IMREAD_COLOR)
        img = cv.resize(img, (128, 128))
        # cv.imwrite("Testing/" + str(counter) + ".jpeg", img)
        PET_IMAGES.append(img)

    print("PET IMAGES = ", counter)

    ###########################################################
    
    # RETURNS 3D PLOT PNG IMAGE
    plot_png = plot3D(ct_folder, pet_folder)

    # recieving base64-encoded string. Need to send back png. 
    # Figure how to do it
    response = Response(plot_png, mimetype="image/PNG")
    return response



if __name__ == "__main__":
    app.run(debug=True)