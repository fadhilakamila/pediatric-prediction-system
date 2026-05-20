import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.metrics import confusion_matrix, classification_report

# =====================================================================
# STEP 1: DEFINISI LOGIKA HITUNG SKOR (EKSTRAKSI DARI app.py PERITONITIS)
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

def hitung_prediksi_web(row_pasien):
    """Fungsi imitasi untuk menghitung hasil kalkulator web secara otomatis"""
    total_wi_xi = 0
    total_wi = 0

    for var in variables_data:
        weight = 2 if var['p_val'] < 0.05 else 1
        nilai_pasien = row_pasien[var['label']]
        x_val = 1 if nilai_pasien == var['peritonitis'] else 0
        
        total_wi_xi += (weight * x_val)
        total_wi += weight

    peritonitis_risk_rate = (total_wi_xi / total_wi) * 100
    
    # OUTPUT SUDAH MENGGUNAKAN TEKS LENGKAP UNTUK EXCEL
    if peritonitis_risk_rate >= 50:
        kategori = "Berisiko Tinggi Peritonitis"
    else:
        kategori = "Berisiko Rendah Peritonitis"
    return kategori, peritonitis_risk_rate

# =====================================================================
# STEP 2: OTOMATISASI PENGISIAN & EVALUASI DATA EXCEL
# =====================================================================
file_name = "data_pasien_bersih.xlsx" 
df = pd.read_excel(file_name)

hasil_kategori_list = []
hasil_persentase_list = []
for index, row in df.iterrows():
    prediksi_kategori, prediksi_persentase = hitung_prediksi_web(row)
    hasil_kategori_list.append(prediksi_kategori)
    hasil_persentase_list.append(f"{prediksi_persentase:.2f}%")

# Masukkan hasil teks lengkap langsung ke dalam tabel Excel kerja kamu
df["Hasil Prediksi (Kategori)"] = hasil_kategori_list
df["Hasil Prediksi (Risk Rate %)"] = hasil_persentase_list

# Ambil nilai langsung dari kolom asli tanpa perlu melakukan transform teks lagi
y_true = df["Outcome Data Riil"]
y_pred = df["Hasil Prediksi (Kategori)"]

# =====================================================================
# STEP 3: HITUNG & TAMPILKAN CONFUSION MATRIX
# =====================================================================
# Evaluasi matriks menggunakan nama label teks lengkap agar sesuai dengan isi data
labels = ["Berisiko Tinggi Peritonitis", "Berisiko Rendah Peritonitis"]
cm = confusion_matrix(y_true, y_pred, labels=labels)
tp, fn, fp, tn = cm.ravel()

print("\n======================================")
print("EVALUASI PERFORMA KALKULATOR PERITONITIS")
print("======================================")
print(f" True Positive (TP)  : {tp} pasien")
print(f" False Positive (FP) : {fp} pasien")
print(f" False Negative (FN) : {fn} pasien")
print(f" True Negative (TN)  : {tn} pasien")
print("--------------------------------------")

accuracy = (tp + tn) / (tp + tn + fp + fn)
sensitivity = tp / (tp + fn)
spesificity = tn / (tn + fp)
precision = tp / (tp + fp)

print(f" Accuracy           : {accuracy:.2%}")
print(f" Sensitivity/Recall : {sensitivity:.2%}")
print(f" Specificity        : {spesificity:.2%}")
print(f" Precision          : {precision:.2%}")
print("======================================\n")

# Simpan tabel kembali ke Excel (Data tersimpan rapi dalam format teks lengkap)
df.to_excel(file_name, index=False)
print(f"🔥 Sukses! Hasil Prediksi (Kategori) telah terisi otomatis di file '{file_name}'.")

# =====================================================================
# STEP 4: MEMBUAT GRAFIK HEATMAP
# =====================================================================
plt.figure(figsize=(6, 5))
sns.heatmap(
    cm, 
    annot=True, 
    fmt="d", 
    cmap="Blues", 
    xticklabels=["Tinggi", "Rendah"], 
    yticklabels=["Tinggi", "Rendah"] 
)
plt.title("Confusion Matrix - Prediksi Risiko Peritonitis", fontsize=12, pad=15)
plt.ylabel("Hasil Prediksi Aplikasi", fontsize=10)
plt.xlabel("Kondisi Riil", fontsize=10)

waktu_sekarang = datetime.now().strftime("%Y%m%d_%H%M%S")
nama_file_gambar = f"confusion_matrix_{waktu_sekarang}.png"
plt.savefig(nama_file_gambar, dpi=300, bbox_inches="tight")
print(f"Grafik matriks berhasil disimpan dengan nama '{nama_file_gambar}'.")
plt.show()