import streamlit as st
import pandas as pd
import os

# ---------- Helper Functions ----------
def load_product_data(csv_path):
    """Loads product data and ensures required columns exist."""
    if not os.path.exists(csv_path):
        st.error(f"❌ Product CSV not found at: {csv_path}")
        st.stop()
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            st.error("❌ Product CSV is empty!")
            st.stop()

        required_cols = ['product_category', 'color']
        if not all(col in df.columns for col in required_cols):
            missing = [col for col in required_cols if col not in df.columns]
            st.error(f"❌ Missing required columns in CSV: {', '.join(missing)}")
            st.stop()

        # Basic cleaning
        df.dropna(subset=['product_category', 'color'], inplace=True)
        df['color'] = df['color'].astype(str).str.strip()
        df['product_category'] = df['product_category'].astype(str).str.strip()

        # Remove empty strings after stripping
        df = df[df['product_category'] != '']
        df = df[df['color'] != '']

        return df.drop_duplicates()

    except Exception as e:
        st.error(f"❌ Error reading product CSV: {e}")
        st.stop()


def extract_category_colors(df):
    """
    Extracts available color family names for each product category from the DataFrame.
    Returns a dictionary where keys are categories and values are a list of available colors.
    """
    category_colors = {}
    if df is None or df.empty:
        return category_colors

    grouped = df.groupby('product_category')['color'].agg(lambda x: sorted(list(x.dropna().unique()))).to_dict()
    
    for category, colors in grouped.items():
        cleaned_colors = [str(c).strip() for c in colors if str(c).strip()]
        if cleaned_colors:
            category_colors[category] = cleaned_colors

    return category_colors


# ---------- Streamlit App ----------
def main():
    st.set_page_config(page_title="RoomScapes AI - Preferences", layout="wide", initial_sidebar_state="expanded")

    # --- Load CSS ---
    st.markdown("""
    <style>
    .main { background: #fffff; color: #0000000; }
    .stButton>button { border-radius: 8px; background: #7b00ff; color: white; transition: all 0.3s ease; margin-top: 0.5rem; }
    .stButton>button:hover { background: #9d4edd; transform: translateY(-2px); }
    .glow-card { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; margin: 15px 0; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); backdrop-filter: blur(10px); transition: all 0.3s ease; }
    .glow-card:hover { box-shadow: 0 6px 20px rgba(123, 0, 255, 0.3); }
    .section-title { font-size: 24px; font-weight: 700; color: #00000; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }
    .stMultiSelect [data-baseweb="tag"] { background-color: #7b00ff; }
    button[kind="secondary"] { background-color: #ff4b4b !important; color: white !important; border-radius: 5px; padding: 2px 8px !important; margin-left: 10px; font-size: 12px; min-height: 10px !important; line-height: 1.2; }
    button[kind="secondary"]:hover { background-color: #cc0000 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.title(" Customize Your Design Plan")
    st.markdown("Refine your preferences for the selected room elements.", unsafe_allow_html=True)

    # --- Initialize Session State ---
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []
    if "color_prefs" not in st.session_state:
        st.session_state.color_prefs = {}
    if "dominant_colors" not in st.session_state:
        # This would come from your room analysis; default to an empty list here
        st.session_state.dominant_colors = []
    if "budget" not in st.session_state:
        st.session_state.budget = 10000  # default budget

    # --- Handling Budget Section ---
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"> Review Your Budget</div>', unsafe_allow_html=True)
        min_budget = 1000
        new_budget = st.slider(
            "Total Budget (₹)",
            min_value=min_budget, max_value=200000,
            value=st.session_state.budget, step=500, format="₹%d"
        )
        st.session_state.budget = new_budget
        st.markdown(f'<p style="color: #00000;">Current Total Budget: ₹{st.session_state.budget:,}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Load Product Data and Extract Colors ---
    csv_path = "products.csv"  # Ensure the path is correct
    df = load_product_data(csv_path)
    category_colors = extract_category_colors(df)
    all_categories_in_csv = sorted(list(category_colors.keys()))

    # --- Managing Category Selection (Dynamic Add/Remove) ---
    with st.container():
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"> Manage Categories</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Add More Categories:**")
        available_to_add = [cat for cat in all_categories_in_csv if cat not in st.session_state.selected_items]

        if not available_to_add:
            st.caption("All available categories are selected.")
        else:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                new_categories_to_add = st.multiselect(
                    "Select categories to add",
                    options=available_to_add,
                    label_visibility="collapsed"
                )
            with col2:
                if st.button("➕ Add", key="add_categories", use_container_width=True):
                    if new_categories_to_add:
                        current_set = set(st.session_state.selected_items)
                        added_set = set(new_categories_to_add)
                        st.session_state.selected_items = list(st.session_state.selected_items) + list(added_set - current_set)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("**Currently Selected:**")
        if not st.session_state.selected_items:
            st.info("No categories selected yet.")
        else:
            cols = st.columns(4)
            items_to_remove = []
            for i, item in enumerate(st.session_state.selected_items):
                with cols[i % 4]:
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.info(f"{item}")
                    with col2:
                        if st.button("➖", key=f"remove_{item}", help=f"Remove {item}", type="secondary"):
                            items_to_remove.append(item)
            if items_to_remove:
                st.session_state.selected_items = [item for item in st.session_state.selected_items if item not in items_to_remove]
                for item in items_to_remove:
                    st.session_state.color_prefs.pop(item, None)

    # --- Handling Color Preferences ---
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"> Pick Your Colors</div>', unsafe_allow_html=True)
            st.markdown("Select preferred color families. By default, only your room's dominant colors (if any) are selected. If no dominant color is available for a category, then all colors are selected by default.")
            for cat in st.session_state.selected_items:
                st.markdown(f"--- \n#### {cat}")
                available_colors = category_colors.get(cat, [])
                if not available_colors:
                    st.warning(f"No color options found for {cat} in product data.")
                    if cat in st.session_state.color_prefs:
                        st.session_state.color_prefs.pop(cat)
                    continue

                # Default selection logic:
                dominant_defaults = [c for c in st.session_state.dominant_colors if c in available_colors]
                if dominant_defaults:
                    default_selection = dominant_defaults
                else:
                    default_selection = available_colors  # if no dominant colors, select all

                # Use a dedicated widget key for each category's color multiselect.
                widget_key = f"color_family_{cat}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = default_selection

                selected_colors = st.multiselect(
                    label=f"Select colors for {cat}",
                    options=available_colors,
                    key=widget_key,
                    label_visibility="collapsed"
                )
                st.session_state.color_prefs[cat] = selected_colors
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Finalizing: Generate Packages Button ---
    if st.session_state.selected_items:
        with st.container():
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title"> Generate Packages</div>', unsafe_allow_html=True)
            st.markdown("When you are satisfied with your category, color selections, and budget, click the button below to generate your design packages.")
            
            if st.button("Generate Packages", use_container_width=True):
                final_package = {"total_budget": st.session_state.budget, "categories": {}}

                for cat in st.session_state.selected_items:
                    available_set = set(category_colors.get(cat, []))
                    selected_set = set(st.session_state.color_prefs.get(cat, []))
                    # If user removed all colors, treat as all available are selected.
                    if not selected_set:
                        selected_set = available_set
                        not_selected = set()
                    else:
                        not_selected = available_set - selected_set

                    final_package["categories"][cat] = {
                        "selected_colors": list(selected_set),
                        "not_selected_colors": list(not_selected)
                    }

                st.session_state.package_summary = final_package
                st.success("✅ Packages generated! Please navigate to the Packages page to see your final output.")

    else:
        st.info("Select some categories to begin customizing your plan.")


if __name__ == "__main__":
    main()




