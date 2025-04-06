import streamlit as st
import pandas as pd
import random
import os

# Assuming genetic_algorithm is defined elsewhere
try:
    from algorithm import genetic_algorithm
except ImportError:
    st.error("❌ Failed to import `genetic_algorithm` from `algorithm.py`. Make sure the file exists and is in the correct path.")
    st.stop()

st.set_page_config(page_title="RoomScapes AI - Packages", layout="wide", initial_sidebar_state="expanded")

# --- Load Product Data ---
@st.cache_data
def load_products(csv_path="products.csv"):
    if not os.path.exists(csv_path):
        st.error(f"❌ Product data file not found at: {csv_path}")
        st.stop()
    try:
        df = pd.read_csv(csv_path)
        required_cols = ['product_category', 'price', 'color', 'product_name', 'image_url', 'product_url']
        optional_cols = ['description']
        missing_required = [col for col in required_cols if col not in df.columns]
        if missing_required:
             st.error(f"❌ Product CSV is missing required columns: {', '.join(missing_required)}.")
             st.stop()
        for col in optional_cols:
            if col not in df.columns: df[col] = ""
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df.dropna(subset=['price'], inplace=True)
        df['product_url'] = df['product_url'].fillna('#')
        df['description'] = df['description'].fillna('').astype(str)
        return df
    except Exception as e:
        st.error(f"❌ Error loading product data: {e}")
        st.stop()

products_df = load_products()

# --- Dark Mode CSS ---
st.markdown("""
<style>
    /* Base Dark Theme */
    body { color: #e5e7eb; }
    .stApp { background: #fffff); }

    /* Expander Styling */
    .stExpander { border-radius: 15px !important; border: 1px solid #374151 !important; margin-bottom: 25px !important; background: #1f2937 !important; box-shadow: 0 6px 30px rgba(0,0,0,0.2) !important; transition: all 0.3s ease !important; overflow: hidden; }
    .stExpander:hover { transform: translateY(-5px); box-shadow: 0 8px 35px rgba(0,0,0,0.3) !important; border-color: #4b5563 !important; }
    .stExpander header { font-size: 18px !important; font-weight: 600 !important; color: #f9fafb !important; padding-top: 15px !important; padding-bottom: 15px !important; border-radius: 15px 15px 0 0 !important; background-color: transparent !important; border-bottom: 1px solid #374151 !important; }
    .stExpander [data-testid="stExpanderDetails"] { padding: 25px !important; background-color: transparent !important; }

    /* Product Card Styling */
    /* Remove link styling from here, apply directly if needed */
    .product-card { padding: 20px; margin: 10px 0; border-radius: 12px; background: #252a38; box-shadow: 0 3px 15px rgba(0,0,0,0.15); transition: all 0.3s ease; height: 100%; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #374151; }
    /* Hover effect directly on card now */
     .product-card:hover { transform: translateY(-3px); box-shadow: 0 5px 20px rgba(0,0,0,0.25); border-color: #4b5563; }
    /* Make title link inherit color and remove underline */
    .product-title a { color: inherit !important; text-decoration: none !important; }
    .product-title a:hover { text-decoration: underline !important; } /* Optional: underline on hover */


    .product-image { border-radius: 8px; width: 100%; height: 180px; object-fit: cover; margin-bottom: 12px; border: 1px solid #4b5563; }
    .price-tag { background: linear-gradient(45deg, #6c5ce7, #8a7cff); color: white; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; margin-top: 8px; display: inline-block; align-self: flex-start; }
    .product-description { font-size: 0.9em; color: #d1d5db; margin-top: 8px; flex-grow: 1; }
    .product-category { font-size: 0.85em; color: #9ca3af; margin-top: 5px; }
    .product-title { font-weight: 600; color: #f9fafb; margin-bottom: 5px; }
    .section-title { color: #a78bfa; font-size: 20px; font-weight: 600; margin: 0 0 15px 0; padding-bottom: 8px; border-bottom: 2px solid #6c5ce7; width: fit-content; }
    h1, h2, h3, .stMarkdown p { color: #f9fafb; }
    .stSuccess { background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.5); border-radius: 8px; }
    .stSuccess p { color: #a7f3d0; }

</style>
""", unsafe_allow_html=True)

st.title("🛍️ RoomScapes Design Packages")

# --- Function to create a bundle ---
def create_bundle(package, package_summary, used_products, min_max):
    bundle = {'user': {}, 'extra': {}}
    local_used_products = used_products.copy()
    user_categories_in_package = package.get('user', {})
    for category, budget in user_categories_in_package.items():
        if budget <= 0: continue
        if category not in package_summary.get('categories', {}) or 'selected_colors' not in package_summary['categories'].get(category, {}): continue
        selected_colors = package_summary['categories'][category]['selected_colors']
        min_price = min_max.get(category, (0, float('inf')))[0]
        filtered = products_df[ (products_df['product_category'] == category) & (products_df['price'] <= budget) & (products_df['price'] >= min_price) & (products_df['color'].isin(selected_colors)) & (~products_df['product_name'].isin(local_used_products)) ]
        if filtered.empty: filtered = products_df[ (products_df['product_category'] == category) & (products_df['price'] <= budget) & (products_df['price'] >= min_price) & (products_df['color'].isin(selected_colors)) ]
        if filtered.empty: filtered = products_df[ (products_df['product_category'] == category) & (products_df['price'] <= budget) & (products_df['price'] >= min_price) ]
        if not filtered.empty:
            product = filtered.sample(1).iloc[0]
            bundle['user'][category] = product.to_dict()
            local_used_products.add(product['product_name'])
    extra_categories_in_package = package.get('extra', {})
    for category, budget in extra_categories_in_package.items():
        if budget <= 0: continue
        min_price = min_max.get(category, (0, float('inf')))[0]
        filtered = products_df[ (products_df['product_category'] == category) & (products_df['price'] <= budget) & (products_df['price'] >= min_price) & (~products_df['product_name'].isin(local_used_products)) ]
        if filtered.empty: filtered = products_df[ (products_df['product_category'] == category) & (products_df['price'] <= budget) & (products_df['price'] >= min_price) ]
        if not filtered.empty:
            product = filtered.sample(1).iloc[0]
            bundle['extra'][category] = product.to_dict()
            local_used_products.add(product['product_name'])
    used_products.update(local_used_products)
    return bundle

# --- NEW Function to display a product card (with clickable image/title) ---
def display_product_card(product, category):
    product_url = product.get('product_url', '#')
    image_url = product.get('image_url', '')
    product_name = product.get('product_name', 'N/A')
    alt_text = f"Image of {product_name}"

    # Start product card div
    st.markdown('<div class="product-card">', unsafe_allow_html=True)

    # --- Clickable Image ---
    if image_url: # Only show image tag if URL exists
        st.markdown(f'<a href="{product_url}" target="_blank" title="View Product: {product_name}" style="display: block;">'
                    f'<img src="{image_url}" class="product-image" alt="{alt_text}">'
                    f'</a>', unsafe_allow_html=True)
    else:
        # Placeholder if no image
         st.markdown(f'<div class="product-image" style="background-color: #374151; display: flex; align-items: center; justify-content: center; color: #9ca3af;">No Image</div>', unsafe_allow_html=True)

    # --- Text Content ---
    st.markdown('<div>', unsafe_allow_html=True)
    # Clickable Title
    st.markdown(f'<a href="{product_url}" target="_blank" style="text-decoration: none; color: inherit;" title="View Product: {product_name}">'
                 f"<div class='product-title'>{product_name}</div>"
                 f'</a>', unsafe_allow_html=True)
    # Description and Category
    st.markdown(f"<div class='product-description'>{product.get('description', '')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='product-category'>Category: {category.replace('-', ' ').title()}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # Close text div

    # Price Tag
    st.markdown(f"<div class='price-tag'>₹ {product.get('price', 0):,.2f}</div>", unsafe_allow_html=True)

    # Close product-card div
    st.markdown('</div>', unsafe_allow_html=True)
# --- End display_product_card ---


# --- Main Logic ---
if "package_summary" not in st.session_state or not st.session_state.package_summary:
    st.error("❗️ No design summary found in session state.")
    st.info("Please generate a design plan from the 'Preferences' page first.")
    if st.button("⬅️ Go to Preferences"):
         try:
             st.switch_page("pages/user_preference.py")
         except Exception as e:
              st.error(f"Navigation Error: {e}")
    st.stop()
else:
    package_summary = st.session_state.package_summary
    budget = package_summary.get("total_budget", 0)
    st.markdown(f"<h3 style='color: #a7f3d0;'>Budget Used for Generation: ₹ {budget:,}</h3>", unsafe_allow_html=True)

    if 'categories' not in package_summary or not isinstance(package_summary['categories'], dict):
         st.error("❌ Invalid format for 'categories' in package summary.")
         st.stop()

    user_cats = list(package_summary["categories"].keys())
    all_cats = products_df['product_category'].unique().tolist()
    extra_cats = [cat for cat in all_cats if cat not in user_cats]

    avg_prices = products_df.groupby('product_category')['price'].mean().to_dict()
    min_max_df = products_df.groupby('product_category')['price'].agg(['min', 'max'])
    min_max = {cat: (row['min'], row['max']) for cat, row in min_max_df.iterrows()}
    for cat in all_cats:
         if cat not in avg_prices: avg_prices[cat] = 1000
         if cat not in min_max: min_max[cat] = (100, 10000)

    with st.spinner("🧬 Generating design packages using Genetic Algorithm..."):
        try:
            packages = genetic_algorithm( user_cats, extra_cats, avg_prices, min_max, budget, population_size=50, generations=100 )
        except Exception as e:
            st.error(f"❌ Error running genetic algorithm: {e}")
            packages = []

    if not packages:
         st.warning("Could not generate any design packages. Check algorithm parameters or input data.")
         # Don't stop here, allow Browse all products maybe? Or show message.
         # st.stop() # Decide if stopping is right or just show message + browse button
         st.info("No custom packages could be generated with the current constraints.")

    st.markdown("--- \n ## ✨ Your Curated Design Collections")
    st.caption("Click on a design package to see the curated products. Click product images or titles to view them.")

    used_products = set()

    if not packages:
        st.info("No packages were generated by the algorithm.")
    else:
        for i, package in enumerate(packages[:5]):
            try:
                bundle = create_bundle(package, package_summary, used_products, min_max)
            except Exception as e:
                 st.error(f"Error creating bundle #{i+1}: {e}")
                 continue

            total_cost = sum(p['price'] for p_dict in bundle.values() for p in p_dict.values())
            expander_label = f"Design Package #{i+1} - Total Price: ₹ {total_cost:,.2f}"

            with st.expander(expander_label, expanded=(i == 0)):
                # Essential Pieces
                essentials = list(bundle.get('user', {}).items())
                if essentials:
                    st.markdown('<div class="section-title">Essential Pieces</div>', unsafe_allow_html=True)
                    cols = st.columns(min(len(essentials), 3))
                    for idx, (category, product) in enumerate(essentials):
                        with cols[idx % 3]:
                            display_product_card(product, category) # Use NEW helper function

                # Premium Add-ons
                addons = list(bundle.get('extra', {}).items())
                if addons:
                    st.markdown('<div class="section-title">Premium Add-ons</div>', unsafe_allow_html=True)
                    cols = st.columns(min(len(addons), 3))
                    for idx, (category, product) in enumerate(addons):
                        with cols[idx % 3]:
                           display_product_card(product, category) # Use NEW helper function

    # --- Navigation Button ---
    st.markdown("---")
    if st.button("➡️ Browse All Products", use_container_width=True):
        try:
            st.switch_page("pages/page_all_products.py")
        except Exception as e:
            st.error(f"Navigation Error: {e}. Make sure 'pages/page_all_products.py' exists.")