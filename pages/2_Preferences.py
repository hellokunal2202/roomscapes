import streamlit as st
from modules.utils import load_product_data
from modules.color_util import extract_category_colors
from modules.components import render_css_user_pref, render_title_user_pref

def initialize_session_state():
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = []
    if "color_prefs" not in st.session_state:
        st.session_state.color_prefs = {}
    if "dominant_colors" not in st.session_state:
        st.session_state.dominant_colors = []
    if "budget" not in st.session_state:
        st.session_state.budget = 10000

def budget_section():
    with st.container():
        st.markdown("### 💰 Review Your Budget")
        
        new_budget = st.slider(
            "Total Budget (₹)", 
            min_value=1000, 
            max_value=200000,
            value=st.session_state.budget, 
            step=500, 
            format="₹%d"
        )
        
        st.session_state.budget = new_budget
        
        st.markdown(f"""
        <div style="
            font-size: 1rem;
            font-weight: 500;
            color: #6a11cb;
            padding: 10px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            margin: 10px 0;
        ">
            Current Budget: ₹{st.session_state.budget:,}
        </div>
        """, unsafe_allow_html=True)

def category_selection_section(category_colors):
    all_categories = sorted(list(category_colors.keys()))
    with st.container():
        st.markdown("###  Manage Categories")
        
        st.write("**Add More Categories:**")
        
        available = [cat for cat in all_categories if cat not in st.session_state.selected_items]
        if not available:
            st.info("All available categories are selected.")
        else:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                new_cats = st.multiselect(
                    "Select categories to add", 
                    options=available, 
                    label_visibility="collapsed"
                )
            with col2:
                
                if st.button(
                    "Add", 
                    key="add_categories",
                    use_container_width=True,
                    type="primary"
                ) and new_cats:
                    for cat in new_cats:
                        if cat not in st.session_state.selected_items:
                            st.session_state.selected_items.append(cat)
                    st.rerun()
        
        st.divider()
        st.write("**Currently Selected:**")
        
        if not st.session_state.selected_items:
            st.info("No categories selected yet.")
        else:
            num_cols = 3
            cols = st.columns(num_cols)
            for i, item in enumerate(st.session_state.selected_items):
                with cols[i % num_cols]:
                    # Adjusted columns ratio to reduce right margin
                    col1, col2 = st.columns([0.75, 0.25])
                    with col1:
                        st.markdown(f"""
                        <div style="
                            padding: 8px 12px;
                            margin-bottom: 8px;
                            border-radius: 8px;
                            background: rgba(123, 0, 255, 0.1);
                        ">
                            {item}
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        # Remove button with tighter spacing
                        if st.button(
                            "×",  # Using multiplication symbol as close icon
                            key=f"remove_{item}",
                            type="secondary",
                            help=f"Remove {item}",
                            use_container_width=True
                        ):
                            st.session_state.selected_items.remove(item)
                            st.session_state.color_prefs.pop(item, None)
                            st.rerun()

def color_preferences_section(category_colors):
    if st.session_state.selected_items:
        with st.container():
            st.markdown("### 🎨 Pick Your Colors")
            st.caption("Select your favorite color families. If no dominant color is set, all options will be chosen by default.")
            
            for cat in st.session_state.selected_items:
                st.divider()
                st.markdown(f"#### {cat}")
                
                colors = category_colors.get(cat, [])
                if not colors:
                    st.warning(f"No color options found for {cat}.")
                    st.session_state.color_prefs.pop(cat, None)
                    continue
                
                defaults = [c for c in st.session_state.dominant_colors if c in colors] or colors
                key = f"color_family_{cat}"
                if key not in st.session_state:
                    st.session_state[key] = defaults
                
                st.multiselect(
                    f"Select colors for {cat}", 
                    options=colors, 
                    key=key, 
                    label_visibility="collapsed"
                )
                st.session_state.color_prefs[cat] = st.session_state[key]

def generate_packages(category_colors, df):
    if st.session_state.selected_items:
        with st.container():
            st.markdown("### 🚀 Generate Packages")
            st.caption("Once you're happy with your selections, click below to generate your design packages.")

            budget_error_placeholder = st.empty()

            if st.button(
                "Generate Packages", 
                key="generate_final", 
                use_container_width=True,
                type="primary"
            ):
                selected_categories = st.session_state.selected_items
                min_required_budget = 0
                missing_categories = []

                for cat in selected_categories:
                    cat_products = df[df['product_category'] == cat]
                    if not cat_products.empty:
                        min_price = cat_products['price'].min()
                        min_required_budget += min_price
                    else:
                        missing_categories.append(cat)

                if st.session_state.budget < min_required_budget:
                    budget_error_placeholder.error(
                        f"❌ Insufficient budget! Minimum required: ₹{min_required_budget:,.2f}"
                    )
                    return  
                elif missing_categories:
                    budget_error_placeholder.warning(
                        f"⚠️ No products found for: {', '.join(missing_categories)}"
                    )
                    return

                package = {"total_budget": st.session_state.budget, "categories": {}}
                for cat in selected_categories:
                    available = set(category_colors.get(cat, []))
                    selected = set(st.session_state.get(f"color_family_{cat}", []))
                    if not selected and available:
                        selected = available
                    package["categories"][cat] = {
                        "selected_colors": list(selected),
                        "not_selected_colors": list(available - selected)
                    }

                st.session_state.package_summary = package
                st.success("✅ Packages generated! Redirecting...")
                st.switch_page("pages/3_Packages.py")
    else:
        st.info("Select some categories to start customizing your plan.")

# ... (previous imports remain the same)

def main():
    st.set_page_config(
        page_title="RoomScapes AI - Preferences", 
        layout="wide", 
        initial_sidebar_state="expanded"
    )
    
    # Updated CSS with gradient buttons
    st.markdown("""
    <style>
        /* Primary button styling with gradient */
        .stButton>button {
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s;
            margin-right: 0 !important;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(106, 17, 203, 0.2) !important;
            opacity: 0.9;
        }
        
        /* Secondary button style with gradient */
        .stButton>button[kind="secondary"] {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
            min-width: auto;
            padding: 4px 8px;
            opacity: 0.8;
                font-size: 0.85rem;
        }
        
        .stButton>button[kind="secondary"]:hover {
            opacity: 1;
            box-shadow: 0 2px 6px rgba(106, 17, 203, 0.2) !important;
        }
        
        /* Focus state */
        .stButton>button:focus {
            box-shadow: 0 0 0 0.2rem rgba(118, 75, 162, 0.5) !important;
        }
        
        /* Active state */
        .stButton>button:active {
            transform: translateY(1px);
        }
        
        /* Category item container */
        [data-testid="column"] {
            padding-right: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    render_css_user_pref()
    render_title_user_pref()
    initialize_session_state()

    csv_path = "products.csv"
    df = load_product_data(csv_path)
    category_colors = extract_category_colors(df)

    budget_section()
    category_selection_section(category_colors)
    color_preferences_section(category_colors)
    generate_packages(category_colors, df)

if __name__ == "__main__":
    main()