import pandas as pd

# =====================================================================
# 1. BACA DATA EXCEL (DIARAHKAN KE DATA PASIEN BERSIH SKENARIO 2)
# =====================================================================
file_path = 'data_pasien_bersih_2.xlsx'
df = pd.read_excel(file_path)

# Nama kolom target hasil akhir data riil dari rumah sakit
kolom_outcome_riil = 'Outcome Data Riil' 

# =====================================================================
# 2. DATA VARIABEL LENGKAP (BASELINE 18 VARIABEL)
# =====================================================================
variables_data = [
    {"label": "Age", "non-peritonitis": ">2 yo", "peritonitis": "<2 yo", "p_val": 0.002, "rr": 1.4, "mrf": False},
    {"label": "Gender", "non-peritonitis": "Female", "peritonitis": "Male", "p_val": 0.09, "rr": 1.08, "mrf": False},
    {"label": "Duration of PD", "non-peritonitis": "<12 mo", "peritonitis": ">12 mo", "p_val": 0.001, "rr": 2.29, "mrf": False},
    {"label": "Place of Residence", "non-peritonitis": "Rural", "peritonitis": "Urban", "p_val": 0.08, "rr": 1.22, "mrf": False},
    {"label": "Housing", "non-peritonitis": "Good service", "peritonitis": "Fair/poor service", "p_val": 0.77, "rr": 0.92, "mrf": True},
    {"label": "Socioeconomic", "non-peritonitis": "Good", "peritonitis": "Poor/fair", "p_val": 0.09, "rr": 0.84, "mrf": True},
    {"label": "Education", "non-peritonitis": "Studies", "peritonitis": "Illiterate", "p_val": 0.48, "rr": 1.21, "mrf": False},
    {"label": "Peritonitis in ESI", "non-peritonitis": "No ESI", "peritonitis": "ESI", "p_val": 0.0001, "rr": 1.35, "mrf": True},
    {"label": "Nutrition", "non-peritonitis": "Normal Nutrition", "peritonitis": "Poor nutrition", "p_val": 0.19, "rr": 0.89, "mrf": True},
    {"label": "Cause of ESRD", "non-peritonitis": "Glomerular", "peritonitis": "Non-glomerular", "p_val": 0.04, "rr": 1.13, "mrf": False},
    {"label": "Type of Catheter (Shape)", "non-peritonitis": "Coiled/swan neck", "peritonitis": "Straight", "p_val": 0.48, "rr": 1.15, "mrf": True},
    {"label": "Type of Catheter (Cuff)", "non-peritonitis": "Double", "peritonitis": "Single cuff", "p_val": 0.32, "rr": 1.33, "mrf": True},
    {"label": "Catheter Placement", "non-peritonitis": "Open", "peritonitis": "Laparoscopic", "p_val": 0.85, "rr": 1.03, "mrf": True},
    {"label": "Gastrostomy/Intraperitoneal Device", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "rr": 0.78, "mrf": True},
    {"label": "Performed CAPD", "non-peritonitis": "Patients", "peritonitis": "Parents/others", "p_val": 0.27, "rr": 0.81, "mrf": True},
    {"label": "Starting PD <2 weeks after catheter placement", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "rr": 1.37, "mrf": True},
    {"label": "Catheter Orientation", "non-peritonitis": "Lateral/downward", "peritonitis": "upward", "p_val": 0.12, "rr": 0.66, "mrf": True},
    {"label": "Stunting", "non-peritonitis": "No stunting", "peritonitis": "Stunting", "p_val": 0.32, "rr": 0.72, "mrf": True},
]

# =====================================================================
# 3. PROSES AUDIT EVALUASI AKURASI INDIVIDU VARIABEL
# =====================================================================
hasil_evaluasi = []

print("=" * 75)
print("  PROSES AUDIT VARIABEL BERDASARKAN BOBOT P-VALUE & SINKRONISASI PESIMIS")
print("=" * 75)

for var in variables_data:
    kolom_nama = var['label']
    kondisi_peritonitis = var['peritonitis']
    p_val = var['p_val']
    
    # Aturan baseline awal: Jika P-Value < 0.05 maka bobotnya 2, jika tidak maka 1
    bobot_kalkulator = 2 if p_val < 0.05 else 1
    status_signifikansi = "Signifikan (*)" if p_val < 0.05 else "Tidak Signifikan"
    
    if kolom_nama in df.columns:
        df_clean = df.dropna(subset=[kolom_nama, kolom_outcome_riil]).copy()
        
        if len(df_clean) == 0:
            continue
            
        # --- REVISI LOGIKA AMAN SINKRON: Tangkap kata "Tidak Diketahui" menjadi Pesimis (Peritonitis)
        def evaluasi_pesimis_individu(sel_value):
            val_str = str(sel_value).strip().lower()
            if val_str == "tidak diketahui" or val_str == kondisi_peritonitis.lower():
                return "Berisiko Tinggi Peritonitis"
            else:
                return "Berisiko Rendah Peritonitis"
        
        tebakan_mesin = df_clean[kolom_nama].apply(evaluasi_pesimis_individu)
        
        total_cocok = (tebakan_mesin == df_clean[kolom_outcome_riil]).sum()
        total_pasien = len(df_clean)
        akurasi = (total_cocok / total_pasien) * 100
        
        hasil_evaluasi.append({
            "Variabel (Feature)": kolom_nama,
            "Akurasi (%)": round(akurasi, 2),
            "P-Value": p_val,
            "Bobot Sistem": bobot_kalkulator,
            "Status": status_signifikansi
        })

# =====================================================================
# 4. TAMPILKAN PAPAN PERINGKAT HASIL AUDIT
# =====================================================================
df_hasil = pd.DataFrame(hasil_evaluasi)
df_hasil = df_hasil.sort_values(by="Akurasi (%)", ascending=True).reset_index(drop=True)

print("\n" + "=" * 75)
print("=== PAPAN PERINGKAT AUDIT (URUTAN TOXIC/LEMAH KE KONSISTEN/KUAT) ===")
print("=" * 75)
print("Cara Analisis Data untuk Bab 4 Skripsi:")
print("1. Variabel Toxic/Menyesatkan: Akurasi sangat RENDAH di dataset lokal rumah sakit.")
print("   Meskipun di jurnal dianggap ada hubungan, variabel ini merusak akurasi aplikasi.")
print("2. Variabel Inti Kuat: Akurasi TINGGI, membuktikan variabel tersebut konsisten antara")
print("   teori jurnal dan data riil di lapangan.\n")

kolom_tampilan = ["Variabel (Feature)", "Akurasi (%)", "P-Value", "Bobot Sistem", "Status"]
print(df_hasil[kolom_tampilan].to_string(index=False))
print("=" * 75)