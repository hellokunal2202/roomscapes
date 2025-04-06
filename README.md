# 🛋️ RoomScapes - Personalized Room Decor Recommendations within budget constraints

RoomScapes is a smart interior design recommendation system that allows users to upload images of their rooms, identify existing furniture using object detection (YOLOv8), and receive curated product suggestions that fit within a selected budget and style preferences.

Our system also uses a **genetic algorithm for smart budget allocation**, ensuring the best possible combination of items based on the user’s preferences and financial constraints.

---

## ✨ Features

- 🖼 Upload room images and detect existing furniture using YOLOv8
- 🪑 Identify objects like sofa, clock, painting, etc.
- ✅ Choose to keep or replace each detected item.
- 💰 Provide a total budget — system distributes it intelligently across needed items using a **genetic algorithm**.
- 🛍 Get top product recommendations for each category from IKEA-style scraped product databases.
- 🎨 Suggest visually similar room styles using ResNet embeddings.
- 🌐 Web app built with Streamlit for easy interaction.

---

## 🧠 Tech Stack

| Component              | Library/Tool                          |
|------------------------|----------------------------------------|
| Object Detection       | [YOLOv8 (Ultralytics)](https://github.com/ultralytics/ultralytics) |
| Visual Similarity      | ResNet + NearestNeighbors              |
| Recommendation Logic   | Genetic Algorithm                      |
| Image Processing       | OpenCV, Pillow, NumPy                  |
| Web App                | Streamlit                              |
| Data Handling          | Pandas, scikit-learn                   |
| Product DB             | CSV (scraped from IKEA/Pepperfry)      |

---
## 🛠️ Setup Instructions
#### 1. Clone the repository <br>
   ```git clone https://github.com/hellokunal2202/roomscapes.git``` <br>
   ```cd roomscapes```
   
#### 2. Create a virtual environment (Windows) <br>
   ```python -m venv venv```<br>
   ```venv\Scripts\activate```
   
#### 3. Install dependencies <br>
```pip install -r requirements.txt``` <br>

#### 4. Run the application <br>
```streamlit run main.py```
