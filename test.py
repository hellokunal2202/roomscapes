import streamlit as st 
from PIL import Image
import os
st.subheader("Item Preferences")
options = st.multiselect(
    label="select existing items you want to keep in your room",
    options=("sofa","table","chair","bed"),
    key="existing_items"

)
budget = st.number_input(
    label="Enter your budget ",
    min_value=1000,
    step=500,
    value=1000
)
st.write(f"Your budget: Rs.{budget}")

uploaded_file = st.file_uploader(
    label="Upload your room image", 
    type=['png', 'jpg', 'jpeg']
)
if uploaded_file is not None:
    # Display image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Room Image", use_column_width=True)
                # Save input image
    input_image_path = os.path.join("uploads", uploaded_file.name)
    image.save(input_image_path)
color = st.color_picker("Pick a color")
if st.button("Submit"):
    st.write(st.session_state["existing_items"])