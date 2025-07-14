import json

# Load file pasal bersih
with open("data/dataset_pasal_bersih.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Atur metadata dasar
default_dokumen = "UU No. 1 Tahun 2023"

# Kata kunci untuk deteksi topik & jenis hukum
topik_kata_kunci = {
    "suap": ["gratifikasi", "suap", "penyuapan"],
    "korupsi": ["korupsi", "kpk", "gratifikasi"],
    "penipuan": ["penipuan", "tipu"],
    "pemalsuan": ["palsu", "pemalsuan", "dokumen palsu"],
    "penghinaan": ["penghinaan", "fitnah"],
    "tindak pidana": ["tindak pidana", "pidana", "pelaku", "hukuman", "pidananya"],
    "perdata": ["perdata", "perjanjian", "utang", "ganti rugi"]
}

def deteksi_topik(teks):
    teks_l = teks.lower()
    for topik, kata_kunci in topik_kata_kunci.items():
        for kata in kata_kunci:
            if kata in teks_l:
                return topik
    return "umum"

def deteksi_jenis_hukum(teks):
    teks_l = teks.lower()
    if any(k in teks_l for k in ["pidana", "tindak pidana", "penjara", "hukuman"]):
        return "Pidana"
    elif any(k in teks_l for k in ["perdata", "ganti rugi", "kontrak"]):
        return "Perdata"
    else:
        return "Umum"

# Tambahkan metadata ke setiap entri
for item in data:
    teks = f"{item['judul']} {item['teks']}"
    item["dokumen"] = default_dokumen
    item["topik"] = deteksi_topik(teks)
    item["jenis_hukum"] = deteksi_jenis_hukum(teks)

# Simpan file baru
with open("data/dataset_pasal_bermeta.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Metadata berhasil ditambahkan ke {len(data)} pasal.")
print("📁 Hasil disimpan sebagai: data/dataset_pasal_bermeta.json")
