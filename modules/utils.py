import os
import numpy as np
import pandas as pd
import ast
from PIL import Image
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm

from .config import PATHS

def save_uploaded_file(uploaded_file):
    try:
        upload_dir = os.path.join('uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        raise RuntimeError(f"File save error: {e}")

def feature_extraction(img_path, model):
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        expanded_img_array = np.expand_dims(img_array, axis=0)
        preprocessed_img = preprocess_input(expanded_img_array)
        result = model.predict(preprocessed_img, verbose=0).flatten()
        return result / norm(result)
    except Exception as e:
        raise RuntimeError(f"Feature extraction error: {e}")

def recommend(features, feature_list):
    neighbors = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
    neighbors.fit(feature_list)
    distances, indices = neighbors.kneighbors([features])
    return indices[0]

def detect_objects(image_path, model):
    results = model.predict(image_path, conf=0.3)[0]
    return results

def get_recommended_objects(detected_img):
    try:
        df = pd.read_csv(PATHS['objects_csv'])
        df['detected_objects'] = df['detected_objects'].apply(ast.literal_eval)
        options = df[df['image'].isin(detected_img)]['detected_objects'].values
        return set().union(*options)
    except Exception as e:
        raise RuntimeError(f"Object recommendation error: {e}")