import pandas as pd
import numpy as np
import os
import random

# Load product data
def load_product_data(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError("Product CSV not found!")
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("Product CSV is empty!")
    required_cols = ['product_category', 'price', 'color']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Missing required columns: {', '.join(required_cols)}")
    return df

# Genetic Algorithm for Budget Allocation
def allocate_budget(selected_categories, total_budget, product_csv, user_colors={}):
    df = load_product_data(product_csv)
    avg_prices = df.groupby('product_category')['price'].mean().to_dict()
    high_priority = {cat: avg_prices.get(cat, 5000) for cat in selected_categories}
    low_priority = {cat: avg_prices.get(cat, 3000) for cat in avg_prices if cat not in selected_categories}
    high_budget = total_budget * 0.8
    low_budget = total_budget * 0.2
    
    def fitness(allocation):
        return -abs(sum(allocation.values()) - total_budget)
    
    def mutate(allocation):
        key = random.choice(list(allocation.keys()))
        allocation[key] *= random.uniform(0.85, 1.15)
        return allocation
    
    population = []
    for _ in range(50):
        allocation = {cat: (val / sum(high_priority.values())) * high_budget for cat, val in high_priority.items()}
        allocation.update({cat: (val / sum(low_priority.values())) * low_budget for cat, val in low_priority.items()})
        scale_factor = total_budget / sum(allocation.values())
        population.append({cat: val * scale_factor for cat, val in allocation.items()})
    
    for _ in range(100):
        population.sort(key=fitness, reverse=True)
        new_population = population[:25]
        while len(new_population) < 50:
            new_population.append(mutate(random.choice(new_population).copy()))
        population = new_population
    
    best_allocation = population[0]
    
    final_products = {}
    for category, budget in best_allocation.items():
        color_filter = user_colors.get(category, None)
        filtered_df = df[df['product_category'] == category]
        if color_filter:
            filtered_df = filtered_df[filtered_df['color'].isin(color_filter)]
        if filtered_df.empty:
            continue
        chosen_product = filtered_df.loc[(filtered_df['price'] - budget).abs().idxmin()]
        final_products[category] = {'product_name': chosen_product['product_name'], 'price': chosen_product['price']}
    
    return final_products

# Example Usage
selected_categories = ["sofa", "painting", "curtains"]
total_budget = 100000
product_csv = "products.csv"
user_colors = {"sofa": ["blue", "grey"], "painting": ["red"]}
allocated_products = allocate_budget(selected_categories, total_budget, product_csv, user_colors)
print(allocated_products)
