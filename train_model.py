import json
import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# Load data pasal bersih
with open("data/dataset_pasal_bermeta.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Gabungkan judul dan isi pasal jadi satu teks per entri
texts = [f"{item['judul']} {item['teks']}" for item in data]

# TF-IDF vektorisasi
vectorizer = TfidfVectorizer(max_features=5000)
X = vectorizer.fit_transform(texts)

# KNN model (bisa ganti ke cosine distance)
model = NearestNeighbors(n_neighbors=3, metric='cosine')
model.fit(X)

# Simpan model dan vectorizer
os.makedirs("model", exist_ok=True)
joblib.dump(vectorizer, "model/tfidf_vectorizer.pkl")
joblib.dump(model, "model/knn_model.pkl")

print(f"✅ Berhasil latih model dengan {len(texts)} pasal dan disimpan ke folder 'model/'")
