from flask import Flask, render_template, request
import json
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import re
from markupsafe import Markup
import google.generativeai as genai

app = Flask(__name__)

# Konfigurasi API Gemini
genai.configure(api_key="AIzaSyDKi-H5IgQBCE2bkKztV3XW-k1LcXUbMBI")  
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

# Load data lokal
with open("data/dataset_pasal_bermeta.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [f"{item['judul']} {item['teks']}" for item in data]
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")
X = vectorizer.transform(texts)

# Deteksi topik sederhana
def deteksi_topik_dari_input(teks):
    teks = teks.lower()
    if "suap" in teks or "gratifikasi" in teks:
        return "suap"
    if "korupsi" in teks:
        return "korupsi"
    if "pemalsuan" in teks:
        return "pemalsuan"
    if "penipuan" in teks:
        return "penipuan"
    if "judi" in teks:
        return "judi"
    return None

# Highlight query
def highlight(teks, query):
    kata = re.escape(query.strip())
    hasil = re.sub(f'({kata})', r'<mark>\1</mark>', teks, flags=re.IGNORECASE)
    return Markup(hasil)

# Fungsi: panggil Gemini untuk memperbaiki jawaban
def perbaiki_jawaban_dengan_gemini(pertanyaan):
    try:
        prompt = f"""
Saya sedang membuat sistem konsultasi hukum. Pengguna menanyakan:

"{pertanyaan}"

Silakan berikan jawaban hukum yang sesuai dan jelas berdasarkan hukum positif di Indonesia. Sertakan penjelasan yang ringkas, tidak terlalu kaku, dan mudah dipahami oleh masyarakat awam.

Tampilkan hasil akhir dalam format:
 
[Penjelasan akhir yang sudah disempurnakan dan relevan]

Jangan menyebutkan bahwa kamu AI. Hindari menggunakan format Markdown (tidak perlu **bold**, *italic*, atau tanda bintang).
"""

        response = model.generate_content(prompt)
        if response and response.text:
            teks = response.text.strip()
            teks = re.sub(r'\*\*(.*?)\*\*', r'\1', teks)
            teks = re.sub(r'\*(.*?)\*', r'\1', teks)
            teks = teks.replace('*', '')
            return {
                "dokumen": "Gemini AI",
                "judul": "💡 Ringkasan Penjelasan Hukum",
                "teks": teks
            }
        else:
            return None
    except Exception:
        return None

@app.route("/")
def home():
    return render_template("home.html")

# ROUTE utama
@app.route("/konsultasi", methods=["GET", "POST"])
def index():
    hasil = []
    query = ""

    if request.method == "POST":
        query = request.form["question"]
        topik = deteksi_topik_dari_input(query)

        # Cari berdasarkan topik
        if topik:
            for item in data:
                if item.get("topik") == topik:
                    item_copy = item.copy()
                    item_copy["teks"] = highlight(item["teks"], query)
                    hasil.append(item_copy)

        # Fallback ke pencarian semantik
        if not hasil:
            q_vec = vectorizer.transform([query])
            sim = cosine_similarity(q_vec, X)
            top_idxs = sim[0].argsort()[-3:][::-1]
            for i in top_idxs:
                item = data[i]
                item_copy = item.copy()
                item_copy["teks"] = highlight(item["teks"], query)
                hasil.append(item_copy)

        # Tambahkan hasil dari Gemini
        jawaban_gemini = perbaiki_jawaban_dengan_gemini(query)
        if jawaban_gemini:
            hasil.insert(0, jawaban_gemini)

    return render_template("konsul.html", query=query, hasil=hasil)

# Main
if __name__ == "__main__":
    app.run(debug=True)