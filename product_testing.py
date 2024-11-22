import streamlit as st
import pandas as pd

# Load the CSV file
def main():
    st.title("Product Testing")
    st.write("This is a test file to check the product testing")
    recommeded_objects=["painting","Chair","center-table","curtains"]
    st.session_state["recommeded_objects"]=recommeded_objects
    if st.button("Reommend Products"):
        st.switch_page("pages\Recommend_products.py")

if __name__ == "__main__":
    main()
