import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')

PATHS = {
    'embeddings': os.path.join(ASSETS_DIR, 'embeddings.pkl'),
    'filenames': os.path.join(ASSETS_DIR, 'filenames.pkl'),
    'yolo_model': os.path.join(ASSETS_DIR, 'best.pt'),
    'objects_csv': os.path.join(ASSETS_DIR, 'detected_objects.csv')
}