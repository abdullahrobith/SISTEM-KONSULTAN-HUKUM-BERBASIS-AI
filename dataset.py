from flask import Flask
import pdfplumber
import re
import json
import os

app = Flask(__name__)

def extract_pasal_from_pdf(pdf_path):
    """
    Mengekstrak pasal-pasal dari file PDF umum (tidak hanya KUHP).
    Ini adalah fungsi yang lebih generik.
    Asumsi:
    - Setiap pasal dimulai dengan "Pasal X" atau "Pasal X ayat (Y)", "Pasal XA", dll.
    - Bab dimulai dengan "BAB [ROMAN_NUMERAL]" diikuti judul bab.
    """
    pasals_data = []
    current_pasal = {}
    current_bab = "Bab Umum" # Default jika tidak ada bab ditemukan
    current_judul_bab = "Aturan Umum" # Default jika tidak ada judul bab ditemukan
    pasal_id_counter = 1

    print(f"Memproses file: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    full_text += extracted_text + "\n"

            lines = full_text.split('\n')

            pasal_pattern = re.compile(r'^(Pasal\s+\d+\s*(?:[A-Za-z]\s*)?(?:\(\d+\))?\.?)', re.IGNORECASE)
            bab_pattern = re.compile(r'^(BAB\s+([IVXLCDM]+))\s*$', re.IGNORECASE)
            # Regex untuk menangkap judul bab yang biasanya satu atau dua baris setelah 'BAB Roman Numeral'
            judul_bab_pattern = re.compile(r'^[A-Z\s,]+$') # Mengasumsikan judul bab adalah huruf kapital

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Cek apakah ini awal Bab baru
                bab_match = bab_pattern.match(line)
                if bab_match:
                    # Simpan pasal sebelumnya jika ada
                    if current_pasal and "isi" in current_pasal and current_pasal["isi"]:
                        pasals_data.append(current_pasal)
                    
                    current_pasal = {} # Reset pasal saat ini
                    current_bab = bab_match.group(1).strip() # Ambil "BAB I", "BAB II", dst.
                    current_judul_bab = "" # Reset judul bab

                    # Coba ambil judul bab dari baris-baris berikutnya
                    j = i + 1
                    while j < len(lines):
                        next_line_for_title = lines[j].strip()
                        # Jika baris berikutnya adalah pasal atau bab baru, berarti judul sudah lewat atau tidak ada
                        if pasal_pattern.match(next_line_for_title) or bab_pattern.match(next_line_for_title):
                            break
                        
                        # Jika baris adalah teks kapital yang mungkin judul bab
                        if next_line_for_title and judul_bab_pattern.match(next_line_for_title):
                            current_judul_bab = next_line_for_title
                            break # Judul bab ditemukan
                        j += 1
                    i = j -1 # Sesuaikan indeks i untuk melanjutkan pemrosesan

                # Cek apakah ini awal Pasal baru
                pasal_match = pasal_pattern.match(line)
                if pasal_match:
                    # Simpan pasal sebelumnya jika ada
                    if current_pasal and "isi" in current_pasal and current_pasal["isi"]:
                        pasals_data.append(current_pasal)

                    # Inisialisasi pasal baru
                    current_pasal = {
                        "id": pasal_id_counter,
                        "nomor": pasal_match.group(1).replace('.', '').strip(), # Bersihkan titik di akhir jika ada
                        "bab": current_bab,
                        "judul_bab": current_judul_bab,
                        "isi": [] # Akan diisi dengan baris-baris isi pasal
                    }
                    pasal_id_counter += 1
                    
                    # Lanjutkan ke baris berikutnya untuk isi pasal
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        # Berhenti jika menemukan pasal baru, bab baru, atau baris kosong yang panjang (end of paragraph)
                        if pasal_pattern.match(next_line) or bab_pattern.match(next_line):
                            break
                        
                        # Tambahkan baris ke isi pasal jika bukan kosong
                        if next_line: # Menghindari menambahkan baris kosong
                            current_pasal["isi"].append(next_line)
                        j += 1
                    current_pasal["isi"] = " ".join(current_pasal["isi"]).strip() # Gabungkan semua baris menjadi satu string
                    i = j - 1 # Set 'i' ke posisi sebelum pasal/bab berikutnya

                i += 1
            
            # Simpan pasal terakhir jika ada
            if current_pasal and "isi" in current_pasal and current_pasal["isi"]:
                pasals_data.append(current_pasal)

    except Exception as e:
        print(f"Gagal memproses {pdf_path}: {e}")
    
    return pasals_data

# --- Main Script ---
if __name__ == "__main__":
    base_dir = "data/peraturan" # Direktori tempat file PDF Anda berada
    output_json_file = "dataset_pasal_bermeta.json111" # Nama file output JSON

    all_extracted_pasals = []
    
    # Pastikan direktori ada
    if not os.path.exists(base_dir):
        print(f"Error: Direktori '{base_dir}' tidak ditemukan. Pastikan struktur proyek Anda benar.")
    else:
        # Loop melalui semua file PDF di direktori
        for filename in os.listdir(base_dir):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(base_dir, filename)
                pasals = extract_pasal_from_pdf(pdf_path)
                
                # Tambahkan informasi asal peraturan ke setiap pasal
                for pasal in pasals:
                    pasal['sumber_peraturan'] = filename
                
                all_extracted_pasals.extend(pasals)
        
        if all_extracted_pasals:
            # Simpan semua data yang diekstrak ke dalam satu file JSON
            with open(output_json_file, "w", encoding="utf-8") as f:
                json.dump(all_extracted_pasals, f, indent=4, ensure_ascii=False)
            
            print(f"\n✅ Berhasil mengekstrak {len(all_extracted_pasals)} pasal dari semua PDF.")
            print(f"Data disimpan ke '{output_json_file}'.")
        else:
            print("Tidak ada pasal yang diekstrak. Pastikan file PDF ada dan formatnya dikenali.")

if __name__ == "__main__":
    app.run(debug=True)
