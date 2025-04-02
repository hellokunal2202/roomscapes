import streamlit as st

st.set_page_config(page_title="RoomScapes AI - Packages", layout="wide", initial_sidebar_state="expanded")
st.title("🎁 Your Design Packages")

if "package_summary" not in st.session_state:
    st.error("No design packages generated. Please go back to the Preferences page and generate packages first.")
else:
    st.markdown("### Final Output Summary")
    st.json(st.session_state.package_summary)
