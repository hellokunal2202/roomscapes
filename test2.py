import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import tempfile

st.set_page_config(page_title="RoomEscapes", layout="wide")

def load_model():
    return YOLO('best.pt')

def process_image(image, model):
    results = model.predict(image,save=True)
    return results[0].plot()

def main():
    st.title("RoomEscapes")
    
    confidence = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
    
    col1, col2 = st.columns(2)
    
    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        col1.header("Original Image")
        col1.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Process image and display results
        if col2.button("Detect Objects"):
            model = load_model()
            results = model.predict(image, conf=confidence)[0]
            
            # Plot results
            result_image = results.plot()
            col2.header("Detection Result")
            col2.image(result_image, caption="Detected Objects", use_column_width=True)
            
            # Display detection information
            st.subheader("Detection Details")
            objects=[]
            if len(results.boxes) > 0:
                for box in results.boxes:
                    conf = box.conf.numpy()[0]
                    cls = results.names[int(box.cls.numpy()[0])]
                    st.write(f"Detected {cls} with confidence: {conf:.2f}")
                    objects.append(cls)
            else:
                st.write("No objects detected.")
            st.write(objects) 

if __name__ == "__main__":
    main()