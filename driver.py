import json
from algorithm import genetic_algorithm

# User preferences (example)
user_preferences = {
    "total_budget": 36860,
    "categories": {
        "chair-wooden": {
            "selected_colors": ["Terracotta", "Beige", "Rust"],
            "not_selected_colors": ["Apricot", "Gray", "Peach", "Cream", "Coral", "Orange"]
        },
        "curtains": {
            "selected_colors": ["Terracotta", "Beige"],
            "not_selected_colors": ["Apricot", "Steel Blue", "Rose", "Bronze", "Blush", "Gray", "Magenta", "Peach", "Slate", "Cream", "Navy", "Turquoise", "White"]
        },
        "frame": {
            "selected_colors": ["Apricot", "Dark Olive", "Rose", "Terracotta", "Sky Blue", "Dusty Rose", "Gray", "Peach", "Taupe", "Slate", "Cream", "White", "Pale Aqua", "Black"],
            "not_selected_colors": []
        },
        "sofa": {
            "selected_colors": ["Beige"],
            "not_selected_colors": ["Gray", "Taupe", "Turquoise", "Lavender"]
        },
        "center-table": {
            "selected_colors": ["Terracotta", "Beige"],
            "not_selected_colors": ["Gold", "Maroon", "Gray", "Cream", "Coral"]
        },
        "ceiling-lights-chandeliers": {
            "selected_colors": ["Gray"],
            "not_selected_colors": []
        },
        "floor-lamps": {
            "selected_colors": ["Rust"],
            "not_selected_colors": ["Apricot", "Gray", "Peach", "Cream", "Black"]
        },
        "wall-clock": {
            "selected_colors": ["Gray", "Steel Blue", "Blue"],
            "not_selected_colors": []
        },
        "tv-stand": {
            "selected_colors": ["Peach"],
            "not_selected_colors": []
        },
        "ceiling-lights": {
            "selected_colors": ["Terracotta", "Beige"],
            "not_selected_colors": ["Sky Blue", "Gray", "Peach", "White", "Turquoise"]
        },
        "handmade-carpets": {
            "selected_colors": ["Terracotta", "Beige"],
            "not_selected_colors": ["Gray", "Peach"]
        },
        "chair-plastic": {
            "selected_colors": ["Rose", "Light Pink", "Sky Blue", "Gray", "White", "Dusty Pink", "Black", "Sage"],
            "not_selected_colors": []
        }
    }
}

# Extract user-selected categories.
user_cats = list(user_preferences["categories"].keys())

# Define extra categories.
extra_cats = ["painting", "cabinet", "couch"]

# Average prices
avg_prices = {
    "center-table": 7263.5455,
    "painting": 2706.1364,
    "handmade-carpets": 11800.3810,
    "curtains": 1970.4833,
    "floor-lamps": 4086.4348,
    "ceiling-lights": 3628.7833,
    "ceiling-lights-chandeliers": 6740.0000,
    "chair-plastic": 1881.8966,
    "chair-wooden": 2956.0952,
    "wall-clock": 1572.1579,
    "cabinet": 42198.4091,
    "couch": 22853.6364,
    "sofa": 88360.4167,
    "frame": 2772.8191,
    "tv-stand": 1682.0000
}

# Minimum and Maximum prices
min_max = {
    "center-table": (899, 21990),
    "painting": (79, 6990),
    "handmade-carpets": (1499, 19990),
    "curtains": (139, 5990),
    "floor-lamps": (799, 9990),
    "ceiling-lights": (299, 9990),
    "ceiling-lights-chandeliers": (4990, 9990),
    "chair-plastic": (299, 3990),
    "chair-wooden": (999, 3990),
    "wall-clock": (229, 4490),
    "cabinet": (7990, 94970),
    "couch": (9990, 29990),
    "sofa": (25000, 277500),
    "frame": (59, 17980),
    "tv-stand": (1649, 1715)
}

total_budget = user_preferences["total_budget"]

# First, check if the budget is sufficient for user-selected categories.
min_required = sum(min_max[cat][0] for cat in user_cats)
if min_required > total_budget:
    print("Budget Insufficient!")
    print(f"Total budget: ₹{total_budget:,}, but minimum required for selected categories is: ₹{min_required:,}")
else:
    packages = genetic_algorithm(user_cats, extra_cats, avg_prices, min_max, total_budget,
                                 population_size=50, generations=100)
    print("Best 5 Packages:")
    for i, pkg in enumerate(packages):
        print(f"Package {i+1}:")
        print(json.dumps(pkg, indent=4))