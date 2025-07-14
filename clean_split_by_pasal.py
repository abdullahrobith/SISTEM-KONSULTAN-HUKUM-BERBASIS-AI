import json
import re
from collections import defaultdict

# Baca file JSON mentah
with open('data/dataset_peraturan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

hasil = []

# Gabungkan semua teks jadi satu string
gabungan_teks = ""
for item in data:
    gabungan_teks += item["teks"] + "\n"

# Pre-cleaning dasar
gabungan_teks = re.sub(r'\n+', '\n', gabungan_teks)
gabungan_teks = re.sub(r'-\n', '', gabungan_teks)  # sambungan antar kata
gabungan_teks = re.sub(r'\s+', ' ', gabungan_teks)

# Split berdasarkan Pasal, Bagian, atau Bab
potongan = re.split(r'(?=Pasal\s+\d+|Bagian\s+\w+|Bab\s+\w+)', gabungan_teks)


# Gabungkan kembali supaya dapat [judul_pasal, isi_pasal, judul, isi, ...]
pasal_list = []
for p in potongan:
    if p.strip().startswith("Pasal"):
        bagian = p.strip().split("\n", 1)
        judul = bagian[0]
        isi = bagian[1] if len(bagian) > 1 else ""
        pasal_list.append({
            "judul": judul,
            "teks": isi.strip()
        })

# Simpan ke file baru
with open("data/dataset_pasal_bersih.json", "w", encoding="utf-8") as f:
    json.dump(pasal_list, f, ensure_ascii=False, indent=4)

print(f"✅ Berhasil memproses {len(pasal_list)} pasal dan menyimpannya.")
