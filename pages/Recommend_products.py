import streamlit as st
import pandas as pd

# Load the CSV file
def load_data(file_path):
    return pd.read_csv(file_path)

# Display the products in a horizontal layout with spacing
def display_products_horizontal(df, product_name, price_range):
    st.title("Products Showcase")

    # Add custom CSS for spacing between products
    st.markdown(
        """
        <style>
        .product-column {
            margin: 20px;  /* Add spacing around each product */
            padding: 10px;
            border: 1px solid #ddd; /* Optional: add a border for clarity */
            border-radius: 10px; /* Rounded corners */
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Filter the DataFrame based on the selected product_name and price range
    filtered_df = df[
        (df['product_category'] == product_name) &
        (df['price'] >= price_range[0]) &
        (df['price'] <= price_range[1])
    ]

    if filtered_df.empty:
        st.write("No products found for the selected criteria.")
    else:
        # Display the filtered products
        num_cols = 3  # Number of products per row
        rows = [filtered_df[i:i + num_cols] for i in range(0, len(filtered_df), num_cols)]  # Split into rows

        for row in rows:
            cols = st.columns(num_cols)  # Create a row of columns
            for col, (_, product) in zip(cols, row.iterrows()):
                with col:
                    st.markdown('<div class="product-column">', unsafe_allow_html=True)
                    st.subheader(product['product_name'])
                    st.image(product['image_url'], caption=product['product_name'], use_column_width=True)
                    st.write(f"**Category**: {product['product_category']}")
                    st.write(f"**Price**: ₹{product['price']}")
                    st.write(f"[Product Link]({product['product_url']})")
                    st.write(f"**Description**: {product['description']}")
                    st.markdown("</div>", unsafe_allow_html=True)

# Main app
def main():
    # Load the uploaded CSV
    uploaded_file = "products.csv"  # Replace with the uploaded path
    data = load_data(uploaded_file)

    # Sidebar for filtering options
    st.sidebar.title("Filter Products")
    
    # Dropdown to select the product category
    product = st.sidebar.selectbox(
        label="Select a product category:",
        options=data['product_category'].unique()  # Unique product categories from the data
    )

    # Slider to select price range
    price_range = st.sidebar.slider(
        label="Select a price range:",
        min_value=int(data['price'].min()),
        max_value=int(data['price'].max()),
        value=(int(data['price'].min()), int(data['price'].max())),
        step=100
    )

    # Display filtered products in horizontal layout
    display_products_horizontal(data, product, price_range)

if __name__ == "__main__":
    main()
