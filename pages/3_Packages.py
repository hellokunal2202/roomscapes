import streamlit as st
import pandas as pd
import random
import os
from algorithm import genetic_algorithm

st.set_page_config(
    page_title="RoomScapes AI - Packages", 
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://roomscapesai.com/help',
        'Report a bug': "https://roomscapesai.com/bug",
        'About': "# RoomScapes AI - AI-Powered Interior Design"
    }
)

# Enhanced CSS with animations and modern styling
st.markdown("""
<style>
  body {
    background: #f4f4f9; 
  }

 

  @keyframes cardHover {
    0% { transform: translateY(0); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }
    100% { transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2); }
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  .stApp {
    background: #ffffff;
  }

  /* Main title styling */
  h1 {
    font-size: 2.8rem !important; /* Increased size */
    color: #4b7bec; /* Light blue color */
    margin-bottom: 2rem !important;
    animation: fadeIn 0.8s ease-out;
  }

  /* Package expander styling */
  .stExpander {
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    margin-bottom: 25px !important;
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
    overflow: hidden;
    animation: fadeIn 0.6s ease-out;
  }

  .stExpander:hover {
    animation: cardHover 0.3s forwards;
    border-color: rgba(74, 142, 255, 0.5) !important;
  }

  .stExpander header {
    font-size: 1.5rem !important; /* Increased size */
    font-weight: 600 !important;
    color: #333333 !important;
    padding: 18px 25px !important;
    background: rgba(74, 142, 255, 0.1) !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  }

  .stExpander [data-testid="stExpanderDetails"] {
    padding: 25px !important;
    background-color: transparent !important;
  }

  /* Product card styling with fixed height */
  .product-card {
    padding: 20px;
    margin: 10px 0;
    border-radius: 14px;
    background: #ffffff;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    height: 480px; /* Fixed height for all cards */
    display: flex;
    flex-direction: column;
    border: 1px solid #dcdfe6;
    animation: fadeIn 0.5s ease-out;
    overflow: hidden; /* Hide overflow */
  }

  .product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    border-color: rgba(74, 142, 255, 0.3);
  }

  .product-title a {
    color: #333333 !important;
    text-decoration: none !important;
    transition: all 0.2s ease;
  }

  .product-title a:hover {
    color: #4b7bec !important;
    text-decoration: none !important;
  }

  .product-image-container {
    flex-shrink: 0; /* Prevent image from shrinking */
  }

  .product-image {
    border-radius: 12px;
    width: 100%;
    height: 250px;
    object-fit: cover;
    margin-bottom: 15px;
    border: 1px solid #d1d5db;
    transition: all 0.3s ease;
  }

  .product-image:hover {
    transform: scale(1.05);
  }

  .product-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden; /* Enable scrolling if needed */
  }

  .price-tag {
    background: linear-gradient(45deg, #6c5ce7, #8a7cff);
    color: white;
    padding: 10px 20px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 1rem;
    margin-top: 12px;
    display: inline-block;
    align-self: flex-start;
    box-shadow: 0 2px 10px rgba(108, 92, 231, 0.2);
    flex-shrink: 0; /* Prevent price tag from shrinking */
  }

  .product-description {
    font-size: 1rem !important;
    color: #555555;
    margin: 12px 0;
    line-height: 1.6;
    flex: 1;
    overflow-y: auto; /* Add scroll for long descriptions */
    padding-right: 5px; /* Space for scrollbar */
  }

  .product-category {
    font-size: 1rem !important;
    color: #777777;
    margin-top: 8px;
    text-transform: capitalize;
  }

  .product-title {
    font-weight: 600;
    font-size: 1.25rem;
    margin-bottom: 8px;
  }

  /* Custom scrollbar styling */
  .product-description::-webkit-scrollbar {
    width: 4px;
  }
  .product-description::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 2px;
  }
  .product-description::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 2px;
  }

  /* Section titles */
  .section-title {
    color: #4b7bec;
    font-size: 2rem !important; /* Increased size */
    font-weight: 600;
    margin: 30px 0 20px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(74, 142, 255, 0.3);
    width: fit-content;
    position: relative;
  }

  .section-title:after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 50%;
    height: 2px;
    background: linear-gradient(90deg, #6c5ce7, transparent);
  }

  /* Budget display */
  .budget-display {
    font-size: 1.5rem !important; /* Increased size */
    font-weight: 600;
    color: #6c5ce7;
    padding: 12px 20px;
    border-radius: 10px;
    background: rgba(108, 92, 231, 0.1);
    border-left: 4px solid #6c5ce7;
    margin: 20px 0;
    display: inline-block;
  }

  /* Buttons */
  .stButton>button {
            color:#ffffff;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-size: 1.1rem !important; /* Increased size */
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border: none !important;
  }

  .stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3) !important;
            color:#ffffff;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    .product-card {
      padding: 15px;
    }

    .product-image {
      height: 200px;
    }

    .stExpander header {
      font-size: 1.2rem !important; /* Increased size */
      padding: 15px 20px !important;
    }
  }
</style>

""", unsafe_allow_html=True)

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

# Main title with animation
st.markdown("""
<div style="animation: fadeIn 0.8s ease-out; ">
    <h1>Your RoomScapes Design Packages</h1>
</div>


""", unsafe_allow_html=True)

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
    description = product.get("description", "")
    price = product.get("price", 0)
    formatted_price = f"₹ {price:,.2f}"

    # Product image section
    image_section = (
        f'<a href="{url}" target="_blank" title="View Product: {name}" style="display: block;">'
        f'<img src="{image_url}" class="product-image" alt="{alt_text}" '
        'onerror="this.src=\'https://via.placeholder.com/300x200?text=No+Image\';'
        'this.style.objectFit=\'contain\';this.style.backgroundColor=\'#1f2937\';">'
        '</a>'
    ) if image_url != "" else (
        '<div class="product-image" style="background-color: #1f2937; display: flex; '
        'align-items: center; justify-content: center; color: #9ca3af; font-size: 0.9rem;">'
        'No Image Available</div>'
    )

    # Main product card HTML
    card_html = f"""
        <div class="product-card" style="display: flex; flex-direction: column; justify-content: space-between; height: 100%; padding: 1rem; border-radius: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1); background-color: white;">
            {image_section}
            <div style="flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-start; margin-top: 1rem;">
                <div class="product-title" style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem;">
                    <a href="{url}" target="_blank" style="text-decoration: none; color: black;" title="View Product: {name}">
                        {name}
                    </a>
                </div>
                <div class="product-description" style="color: #4b5563; font-size: 0.95rem; line-height: 1.4; min-height: 48px;">
                    {description}
                </div>
                <div class="product-category" style="color: #6b7280; font-size: 0.9rem; margin-top: auto;">
                    {category.replace("-", " ").title()}
                </div>
            </div>
            <div class="price-tag" style="margin-top: 1rem; align-self: flex-start; padding: 0.6rem 1.2rem; border-radius: 999px; color: white; font-weight: 600; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);">
                {formatted_price}
            </div>
        </div>
    """

    st.markdown(card_html, unsafe_allow_html=True)

# Check for package data
if "package_summary" not in st.session_state or not st.session_state.package_summary:
    st.error("❗ No design package found")
    st.markdown("""
    <div style="background: rgba(220, 53, 69, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #dc3545; margin: 20px 0;">
        <p>Please generate a design plan from the Preferences page first.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ Go to Preferences", key="go_to_prefs"):
        st.switch_page("pages/user_preference.py")
    st.stop()
else:
    summary = st.session_state.package_summary
    total_budget = summary.get("total_budget", 0)
    
    # Animated budget display
    st.markdown(f"""
    <div style="animation: fadeIn 0.8s ease-out;">
        <div class="budget-display">
            💰 Budget Allocated: ₹ {total_budget:,}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if 'categories' not in summary or type(summary['categories']) is not dict:
        st.error("❌ Invalid package format")
        st.stop()
    
    selected_categories = list(summary["categories"].keys())
    all_categories = products_df['product_category'].unique().tolist()
    extra_categories = [cat for cat in all_categories if cat not in selected_categories]
    
    # Calculate average prices and min/max
    avg_prices = products_df.groupby('product_category')['price'].mean().to_dict()
    min_max_df = products_df.groupby('product_category')['price'].agg(['min', 'max'])
    min_max = {cat: (min_max_df.loc[cat]['min'], min_max_df.loc[cat]['max']) for cat in min_max_df.index}
    
    # Set defaults for missing categories
    for cat in all_categories:
        if cat not in avg_prices:
            avg_prices[cat] = 1000
        if cat not in min_max:
            min_max[cat] = (100, 10000)
    
    # Generate packages with loading animation
    with st.spinner("🧬 Generating personalized design packages..."):
        packages = genetic_algorithm(
            selected_categories, 
            extra_categories, 
            avg_prices, 
            min_max, 
            total_budget, 
            population_size=50, 
            generations=100
        )
    
    if not packages:
        st.warning("⚠️ No packages generated with current constraints")
        st.markdown("""
        <div style="background: rgba(255, 193, 7, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #ffc107; margin: 20px 0;">
            <p style="color: #f9fafb; margin-bottom: 0;">Try adjusting your budget or preferences for better results.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Packages section
    st.markdown("""
    <div style="animation: fadeIn 1s ease-out;">
        <h2 style="color: #000000; margin-top: 40px; margin-bottom: 20px;">✨ Your Curated Collections</h2>
        <p style="color: #000000; margin-bottom: 30px;">Click to explore each design package. Product images and titles are clickable.</p>
    </div>
    """, unsafe_allow_html=True)
    
    used_products = set()
    
    if packages:
        count = 0
        for pkg in packages[:5]:  # Limit to 5 packages
            bundle = create_bundle(pkg, summary, used_products, min_max)
            total_cost = sum(item.get('price', 0) for cat in bundle.values() for item in cat.values())
            
            expander_label = f"Package #{count + 1} • ₹ {total_cost:,.2f}"
            with st.expander(expander_label, expanded=(count == 0)):
                # Essential Pieces section
                essentials = [(cat, bundle['user'][cat]) for cat in bundle.get('user', {})]
                if essentials:
                    st.markdown('<div class="section-title">Essential Pieces</div>', unsafe_allow_html=True)
                    cols = st.columns(min(3, len(essentials)))
                    for idx, (cat, product) in enumerate(essentials):
                        with cols[idx % len(cols)]:
                            display_product_card(product, cat)
                
                # Premium Add-ons section
                addons = [(cat, bundle['extra'][cat]) for cat in bundle.get('extra', {})]
                if addons:
                    st.markdown('<div class="section-title">Premium Add-ons</div>', unsafe_allow_html=True)
                    addon_cols = st.columns(min(3, len(addons)))
                    for idx, (cat, product) in enumerate(addons):
                        with addon_cols[idx % len(addon_cols)]:
                            display_product_card(product, cat)
            count += 1
    
    # Footer with browse button
    st.markdown("---")
    if st.button("Browse All Products ➡️", key="browse_all", use_container_width=True):
        st.switch_page("pages/4_Explore.py")