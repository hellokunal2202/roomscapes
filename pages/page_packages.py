import streamlit as st
import pandas as pd
import random
import os

from algorithm import genetic_algorithm

st.set_page_config(page_title="RoomScapes AI - Packages", layout="wide", initial_sidebar_state="expanded")


@st.cache_data
def load_products(csv_path="products.csv"):
    df = pd.read_csv(csv_path)
    required_cols = ['product_category', 'price', 'color', 'product_name', 'image_url', 'product_url', 'description']
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['price'], inplace=True)
    df['product_url'] = df['product_url'].fillna('#')
    df['description'] = df['description'].fillna('').astype(str)
    return df


products_df = load_products()


st.markdown("""
<style>
    body { color: #e5e7eb; }

    .stApp { background: #fffff); }

    /* Expander Styling */

    .stExpander { border-radius: 15px !important; border: 1px solid #374151 !important; margin-bottom: 25px !important; background: #1f2937 !important; box-shadow: 0 6px 30px rgba(0,0,0,0.2) !important; transition: all 0.3s ease !important; overflow: hidden; }
    .stExpander:hover { transform: translateY(-5px); box-shadow: 0 8px 35px rgba(0,0,0,0.3) !important; border-color: #4b5563 !important; }
    .stExpander header { font-size: 18px !important; font-weight: 600 !important; color: #f9fafb !important; padding-top: 15px !important; padding-bottom: 15px !important; border-radius: 15px 15px 0 0 !important; background-color: transparent !important; border-bottom: 1px solid #374151 !important; }
    .stExpander [data-testid="stExpanderDetails"] { padding: 25px !important; background-color: transparent !important; }
    .product-card { padding: 20px; margin: 10px 0; border-radius: 12px; background: #252a38; box-shadow: 0 3px 15px rgba(0,0,0,0.15); transition: all 0.3s ease; height: 100%; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid #374151; }
    .product-card:hover { transform: translateY(-3px); box-shadow: 0 5px 20px rgba(0,0,0,0.25); border-color: #4b5563; }
    .product-title a { color: inherit !important; text-decoration: none !important; }
    .product-title a:hover { text-decoration: underline !important; }
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


def create_bundle(pkg, summary, used_products, min_max):
    bundle = {'user': {}, 'extra': {}}
    current_used = used_products.copy()

    user_pkg = pkg.get('user', {})
    for category in user_pkg:
        budget = user_pkg[category]
        if budget <= 0:
            continue
        if category not in summary.get('categories', {}):
            continue
        cat_info = summary['categories'].get(category, {})
        if 'selected_colors' not in cat_info:
            continue
        colors = cat_info['selected_colors']
        min_price = min_max.get(category, (0, float('inf')))[0]
        filtered = products_df[
            (products_df['product_category'] == category) &
            (products_df['price'] <= budget) &
            (products_df['price'] >= min_price)
        ]
        rows = []
        for _, row in filtered.iterrows():
            if row['color'] in colors and row['product_name'] not in current_used:
                rows.append(row)
        if len(rows) == 0:
            rows = []
            for _, row in filtered.iterrows():
                if row['color'] in colors:
                    rows.append(row)
        if len(rows) == 0:
            rows = []
            for _, row in filtered.iterrows():
                rows.append(row)
        if len(rows) > 0:
            chosen = random.choice(rows)
            bundle['user'][category] = chosen.to_dict()
            current_used.add(chosen['product_name'])

    extra_pkg = pkg.get('extra', {})
    for category in extra_pkg:
        budget = extra_pkg[category]
        if budget <= 0:
            continue
        min_price = min_max.get(category, (0, float('inf')))[0]
        filtered = products_df[
            (products_df['product_category'] == category) &
            (products_df['price'] <= budget) &
            (products_df['price'] >= min_price)
        ]
        rows = []
        for _, row in filtered.iterrows():
            if row['product_name'] not in current_used:
                rows.append(row)
        if len(rows) == 0:
            rows = []
            for _, row in filtered.iterrows():
                rows.append(row)
        if len(rows) > 0:
            chosen = random.choice(rows)
            bundle['extra'][category] = chosen.to_dict()
            current_used.add(chosen['product_name'])

    used_products.update(current_used)
    return bundle


def display_product_card(product, category):
    url = product.get('product_url', '#')
    image_url = product.get('image_url', '')
    name = product.get('product_name', 'N/A')
    alt_text = "Image of " + name

    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    if image_url != "":
        st.markdown(
            '<a href="' + url + '" target="_blank" title="View Product: ' + name + '" style="display: block;">' +
            '<img src="' + image_url + '" class="product-image" alt="' + alt_text + '">' +
            '</a>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="product-image" style="background-color: #374151; display: flex; align-items: center; justify-content: center; color: #9ca3af;">No Image</div>',
            unsafe_allow_html=True
        )
    st.markdown('<div>', unsafe_allow_html=True)
    st.markdown(
        '<a href="' + url + '" target="_blank" style="text-decoration: none; color: inherit;" title="View Product: ' + name + '">' +
        "<div class='product-title'>" + name + "</div></a>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='product-description'>" + product.get('description', '') + "</div>", unsafe_allow_html=True)
    st.markdown("<div class='product-category'>Category: " + category.replace('-', ' ').title() + "</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<div class='price-tag'>₹ " + format(product.get('price', 0), ",.2f") + "</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if "package_summary" not in st.session_state or not st.session_state.package_summary:
    st.error("❗️ No design summary found in session state.")
    st.info("Please generate a design plan from the 'Preferences' page first.")
    if st.button("⬅️ Go to Preferences"):
        st.switch_page("pages/user_preference.py")
    st.stop()
else:
    summary = st.session_state.package_summary
    total_budget = summary.get("total_budget", 0)
    st.markdown("<h3 style='color: #a7f3d0;'>Budget Used for Generation: ₹ " + format(total_budget, ",") + "</h3>", unsafe_allow_html=True)
    
    if 'categories' not in summary or type(summary['categories']) is not dict:
        st.error("❌ Invalid format for 'categories' in package summary.")
        st.stop()
    
    selected_categories = []
    for key in summary["categories"]:
        selected_categories.append(key)
    
    all_categories = []
    for cat in products_df['product_category'].unique().tolist():
        all_categories.append(cat)
    
    extra_categories = []
    for cat in all_categories:
        if cat in selected_categories:
            pass
        else:
            extra_categories.append(cat)
    
    avg_prices = {}
    grouped = products_df.groupby('product_category')['price']
    for cat in grouped.groups.keys():
        avg_prices[cat] = grouped.get_group(cat).mean()
    min_max_df = products_df.groupby('product_category')['price'].agg(['min', 'max'])
    min_max = {}
    for cat in min_max_df.index:
        row = min_max_df.loc[cat]
        min_max[cat] = (row['min'], row['max'])
    for cat in all_categories:
        if cat not in avg_prices:
            avg_prices[cat] = 1000
        if cat not in min_max:
            min_max[cat] = (100, 10000)
    
    st.spinner("🧬 Generating design packages using Genetic Algorithm...")
    packages = genetic_algorithm(selected_categories, extra_categories, avg_prices, min_max, total_budget, population_size=50, generations=100)
    
    if not packages:
        st.warning("Could not generate any design packages. Check algorithm parameters or input data.")
        st.info("No custom packages could be generated with the current constraints.")
    
    st.markdown("--- \n ## ✨ Your Curated Design Collections")
    st.caption("Click on a design package to see the curated products. Click product images or titles to view them.")
    
    used_products = set()
    
    if not packages:
        st.info("No packages were generated by the algorithm.")
    else:
        count = 0
        for pkg in packages:
            if count >= 5:
                break
            bundle = create_bundle(pkg, summary, used_products, min_max)
            total_cost = 0
            for category in bundle:
                cat_bundle = bundle[category]
                for key in cat_bundle:
                    total_cost += cat_bundle[key].get('price', 0)
            expander_label = "Design Package #" + str(count + 1) + " - Total Price: ₹ " + format(total_cost, ",.2f")
            with st.expander(expander_label, expanded=(count == 0)):
                essentials = []
                for cat in bundle.get('user', {}):
                    essentials.append((cat, bundle['user'][cat]))
                if len(essentials) > 0:
                    st.markdown('<div class="section-title">Essential Pieces</div>', unsafe_allow_html=True)
                    num_cols = len(essentials)
                    if num_cols > 3:
                        num_cols = 3
                    cols = st.columns(num_cols)
                    idx = 0
                    for item in essentials:
                        with cols[idx % num_cols]:
                            display_product_card(item[1], item[0])
                        idx += 1
                addons = []
                for cat in bundle.get('extra', {}):
                    addons.append((cat, bundle['extra'][cat]))
                if len(addons) > 0:
                    st.markdown('<div class="section-title">Premium Add-ons</div>', unsafe_allow_html=True)
                    addon_cols = st.columns(min(len(addons), 3))
                    idx2 = 0
                    for item in addons:
                        with addon_cols[idx2 % len(addon_cols)]:
                            display_product_card(item[1], item[0])
                        idx2 += 1
            count += 1
    
    st.markdown("---")
    if st.button("➡️ Browse All Products", use_container_width=True):
        st.switch_page("pages/page_all_products.py")