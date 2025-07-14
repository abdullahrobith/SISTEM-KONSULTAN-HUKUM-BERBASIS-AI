import pdfplumber
import os
import json
import re

folder_pdf = "data/peraturan"
output_json = "data/dataset_peraturan.json"

data = []

for filename in os.listdir(folder_pdf):
    if filename.endswith(".pdf"):
        with pdfplumber.open(os.path.join(folder_pdf, filename)) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    data.append({
                        "dokumen": filename,
                        "halaman": page_num,
                        "teks": text.strip()
                    })

# Simpan ke JSON
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Selesai mengekstrak {len(data)} entri dari PDF.")
