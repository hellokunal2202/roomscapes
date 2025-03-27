import streamlit as st
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.layers import GlobalMaxPooling2D
from ultralytics import YOLO
import pickle
import numpy as np
from modules.config import PATHS

@st.cache_resource(show_spinner="🔍 Loading object detection model...")
def load_yolo():
    return YOLO(PATHS['yolo_model'])

@st.cache_resource(show_spinner="🧠 Loading feature extraction model...")
def load_resnet():
    model = ResNet50(weights='imagenet', include_top=False, input_shape=(224,224,3))
    model.trainable = False
    return tf.keras.Sequential([model, GlobalMaxPooling2D()])

@st.cache_resource(show_spinner="📂 Loading design database...")
def load_features():
    with st.spinner("🔢 Processing image embeddings..."):
        feature_list = np.array(pickle.load(open(PATHS['embeddings'], 'rb')))
    with st.spinner("🏷️ Loading design catalog..."):
        filenames = pickle.load(open(PATHS['filenames'], 'rb'))
    return feature_list, filenames