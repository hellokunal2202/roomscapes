import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import tempfile
import pandas as pd
import ast

import pickle
import tensorflow
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPooling2D
from tensorflow.keras.applications.resnet50 import ResNet50,preprocess_input
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm

st.set_page_config(page_title="RoomEscapes", layout="wide")

st.sidebar.title("Improvise Now!")

detected_objects = set()
uploaded_file = None
feature_list = np.array(pickle.load(open('embeddings.pkl','rb')))
filenames = pickle.load(open('filenames.pkl','rb'))

model = ResNet50(weights='imagenet',include_top=False,input_shape=(224,224,3))
model.trainable = False

model = tensorflow.keras.Sequential([
    model,
    GlobalMaxPooling2D()
])
def save_uploaded_file(uploaded_file):
    try:
        with open(os.path.join('uploads',uploaded_file.name),'wb') as f:
            f.write(uploaded_file.getbuffer())  
        return 1
    except:
        return 0

def feature_extraction(img_path,model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result / norm(result)

    return normalized_result

def recommend(features,feature_list):
    neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
    neighbors.fit(feature_list)

    distances, indices = neighbors.kneighbors([features])

    return indices

@st.cache_resource
def detect(_image):
    model = YOLO('best.pt')
    confidence = 0.05
    results = model.predict(_image, conf=confidence)[0]
    return results
    


def process_image(image, model):
    results = model.predict(image,save=True)
    return results[0].plot()

@st.cache_resource
def recommendation(uploaded_file):
        # feature extract
        features = feature_extraction(os.path.join("uploads",uploaded_file.name),model)
        #st.text(features)
        # recommendention
        indices = recommend(features,feature_list)
        # show
        col1,col2,col3,col4,col5 = st.columns(5)
        detected_img = []
        with col1:
            st.image(filenames[indices[0][0]])
            detected_img.append(str(filenames[indices[0][0]]).split('\\')[1])
        with col2:
            st.image(filenames[indices[0][1]])
            detected_img.append(str(filenames[indices[0][1]]).split('\\')[1])
        with col3:
            st.image(filenames[indices[0][2]])
            detected_img.append(str(filenames[indices[0][2]]).split('\\')[1])
        with col4:
            st.image(filenames[indices[0][3]])
            detected_img.append(str(filenames[indices[0][3]]).split('\\')[1])
        with col5:
            st.image(filenames[indices[0][4]])
            detected_img.append(str(filenames[indices[0][4]]).split('\\')[1])
        # st.sess
        st.session_state["detected_image"]=detected_img




def recommeded_objects():
    detected_img = st.session_state["detected_image"]
    df = pd.read_csv('detected_objects.csv')
    df['detected_objects'] = df['detected_objects'].apply(ast.literal_eval)
    options = df[df['image'].isin(detected_img)]['detected_objects'].values
    # options = set(np.concatenate(options))
    recommended_object=set()
    for obj_set in options:
        for obj in obj_set:
            recommended_object.add(obj)
    st.session_state["recommeded_objects"]=recommeded_objects


        

def main():
    st.title("RoomScapes")
    
    budget = st.sidebar.number_input(
        label="Enter your budget:",
        min_value=1000,
        step=500,
        value=1000
    )
    
    uploaded_file = st.sidebar.file_uploader(
        label="Upload your room image", 
        type=['png', 'jpg', 'jpeg']
    )

    if uploaded_file is not None:
        # Display image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Room Image", use_column_width=False, width=500)
                    # Save input image
        input_image_path = os.path.join("uploads", uploaded_file.name)
        image.save(input_image_path)        
        results = detect(image)
        ## result_image = results.plot()
        
        if len(results.boxes) > 0:
            for box in results.boxes:
                conf = box.conf.numpy()[0]
                cls = results.names[int(box.cls.numpy()[0])]
                detected_objects.add(cls)
        else:
            st.write("No objects detected.")

        st.sidebar.subheader("Item Preferences")
        options = st.sidebar.multiselect(
            label="Select  items you want to change in your room",
            options=list(detected_objects),
            key="items"

        )
        if st.sidebar.button("Recommend", key="recommend_button"):
            recommendation(uploaded_file)
            recommeded_objects()
        if st.button("Recommend Products"):
            st.switch_page("pages\Recommend_products.py")
    



        
        


if __name__ == "__main__":
    main()