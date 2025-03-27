import streamlit as st
from modules import components

def main():
    components.inject_css()
    
    st.title("✨ Recommended Products")
    
    # Retrieve data from session state
    selected_items = st.session_state.get("selected_items", [])
    dominant_colors = st.session_state.get("dominant_colors", [])
    budget = st.session_state.get("budget", 1000)
    
    # Display the selections
    st.subheader("Your Design Preferences")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Selected Items:**")
        for item in selected_items:
            st.write(f"- {item}")
    
    with col2:
        st.markdown("**Color Palette:**")
        cols = st.columns(len(dominant_colors))
        for i, color in enumerate(dominant_colors):
            with cols[i]:
                st.markdown(
                    f'<div style="background-color:{color}; height:60px; border-radius:5px;"></div>',
                    unsafe_allow_html=True
                )
                st.caption(color)
    
    st.markdown(f"**Budget:** ₹{budget:,}")
    
    # Here you would add your product recommendation logic
    # using the selected_items and dominant_colors
    
if __name__ == "__main__":
    main()