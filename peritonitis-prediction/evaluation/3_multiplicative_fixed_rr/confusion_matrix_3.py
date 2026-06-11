import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.metrics import confusion_matrix

# ====================
# STEP 1: DEFINE
# ====================
variables_data = [
    {"label": "Age", "non-peritonitis": ">2 yo", "peritonitis": "<2 yo", "p_val": 0.002, "rr": 1.4, "mrf": False},
    {"label": "Gender", "non-peritonitis": "Female", "peritonitis": "Male", "p_val": 0.09, "rr": 1.08, "mrf": False},
    {"label": "Duration of PD", "non-peritonitis": "<12 mo", "peritonitis": ">12 mo", "p_val": 0.001, "rr": 2.29, "mrf": False},
    {"label": "Place of Residence", "non-peritonitis": "Rural", "peritonitis": "Urban", "p_val": 0.08, "rr": 1.22, "mrf": False},
    {"label": "Housing", "non-peritonitis": "Good service", "peritonitis": "Fair/poor service", "p_val": 0.77, "rr": 1.086956522, "mrf": True}, # Nilai rr diselaraskan dengan database real app5.py
    {"label": "Socioeconomic", "non-peritonitis": "Good", "peritonitis": "Poor/fair", "p_val": 0.09, "rr": 1.19047619, "mrf": True},    # Nilai rr diselaraskan dengan database real app5.py
    {"label": "Education", "non-peritonitis": "Studies", "peritonitis": "Illiterate", "p_val": 0.48, "rr": 1.21, "mrf": False},
    {"label": "Peritonitis in ESI", "non-peritonitis": "No ESI", "peritonitis": "ESI", "p_val": 0.0001, "rr": 1.35, "mrf": True},
    {"label": "Nutrition", "non-peritonitis": "Normal Nutrition", "peritonitis": "Poor nutrition", "p_val": 0.19, "rr": 1.123595506, "mrf": True}, # Nilai rr diselaraskan dengan database real app5.py
    {"label": "Cause of ESRD", "non-peritonitis": "Glomerular", "peritonitis": "Non-glomerular", "p_val": 0.04, "rr": 1.13, "mrf": False},
    {"label": "Type of Catheter (Shape)", "non-peritonitis": "Coiled/swan neck", "peritonitis": "Straight", "p_val": 0.48, "rr": 1.15, "mrf": True},
    {"label": "Type of Catheter (Cuff)", "non-peritonitis": "Double", "peritonitis": "Single cuff", "p_val": 0.32, "rr": 1.33, "mrf": True},
    {"label": "Catheter Placement", "non-peritonitis": "Open", "peritonitis": "Laparoscopic", "p_val": 0.85, "rr": 1.03, "mrf": True},
    {"label": "Gastrostomy/Intraperitoneal Device", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "rr": 1.282051282, "mrf": True}, # Nilai rr diselaraskan dengan database real app5.py
    {"label": "Performed CAPD", "non-peritonitis": "Patients", "peritonitis": "Parents/others", "p_val": 0.27, "rr": 1.234567901, "mrf": True},    # Nilai rr diselaraskan dengan database real app5.py
    {"label": "Starting PD <2 weeks after catheter placement", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "rr": 1.37, "mrf": True},
    {"label": "Catheter Orientation", "non-peritonitis": "Lateral/downward", "peritonitis": "upward", "p_val": 0.12, "rr": 1.515151515, "mrf": True}, # Nilai rr diselaraskan dengan database real app5.py
    {"label": "Stunting", "non-peritonitis": "No stunting", "peritonitis": "Stunting", "p_val": 0.32, "rr": 1.388888889, "mrf": True}, # Nilai rr diselaraskan dengan database real app5.py
]

def hitung_prediksi_fixed_rr(row_pasien):
    mult_fixed_cumulative = 1.0

    for var in variables_data:
        nilai_pasien = str(row_pasien[var['label']]).strip()
        
        if nilai_pasien.lower() == "tidak diketahui":
            current_multiplier = 1.0
        elif nilai_pasien.lower() == var["non-peritonitis"].lower():
            current_multiplier = 1.0
        else:
            current_multiplier = var["rr"]
            
        mult_fixed_cumulative *= current_multiplier

    if mult_fixed_cumulative >= 50.0:
        kategori = "Berisiko Tinggi Peritonitis"
    else:
        kategori = "Berisiko Rendah Peritonitis"
        
    return kategori, mult_fixed_cumulative

# =====================================================================
# STEP 2: OTOMATISASI EVALUASI BERKAS DATA_PASIEN_BERSIH_3.XLSX
# =====================================================================
file_name = "data_pasien_bersih_3.xlsx"  
df = pd.read_excel(file_name)

hasil_kategori_list = []
hasil_persentase_list = []
for index, row in df.iterrows():
    prediksi_kategori, prediksi_persentase = hitung_prediksi_fixed_rr(row)
    hasil_kategori_list.append(prediksi_kategori)
    hasil_persentase_list.append(f"{prediksi_persentase:.2f}%")

df["Hasil Prediksi (Kategori)"] = hasil_kategori_list
df["Hasil Prediksi (Risk Rate %)"] = hasil_persentase_list

y_true = df["Outcome Data Riil"].str.strip()
y_pred = df["Hasil Prediksi (Kategori)"].str.strip()

# ====================================================
# STEP 3: HITUNG & TAMPILKAN CONFUSION MATRIX 
# ====================================================
labels = ["Berisiko Tinggi Peritonitis", "Berisiko Rendah Peritonitis"]
cm = confusion_matrix(y_true, y_pred, labels=labels)
tp, fn, fp, tn = cm.ravel()

print("\n======================================================")
print("EVALUASI MODEL MULTIPLICAITIVE - FIXED RR")
print("======================================================")
print(f" True Positive (TP)  : {tp} pasien")
print(f" False Negative (FN) : {fn} pasien")
print(f" False Positive (FP) : {fp} pasien")
print(f" True Negative (TN)  : {tn} pasien")
print("------------------------------------------------------")

accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0

print(f" Accuracy           : {accuracy:.2%}")
print(f" Sensitivity/Recall : {sensitivity:.2%}")
print(f" Specificity        : {specificity:.2%}")
print(f" Precision          : {precision:.2%}")
print("======================================================\n")

df.to_excel(file_name, index=False)
print(f"🔥 Sukses! Hasil sinkronisasi matriks otomatis disimpan ke '{file_name}'.")

# ================================
# STEP 4: GRAFIK HEATMAP 
# ================================
plt.figure(figsize=(6, 5))
sns.heatmap(
    cm, 
    annot=True, 
    fmt="d", 
    cmap="Greens", # Aksen warna hijau solid untuk metode utama Lewis
    xticklabels=["Tinggi", "Rendah"], 
    yticklabels=["Tinggi", "Rendah"] 
)
plt.title("Confusion Matrix - Prediksi Risiko Peritonitis (Fixed RR)", fontsize=12, pad=15)
plt.ylabel("Actual", fontsize=10)
plt.xlabel("Predicted", fontsize=10)

waktu_sekarang = datetime.now().strftime("%Y%m%d_%H%M%S")
nama_file_gambar = f"confusion_matrix_fixed_rr_{waktu_sekarang}.png"
plt.savefig(nama_file_gambar, dpi=300, bbox_inches="tight")
print(f"Grafik matriks Fixed RR berhasil disimpan dengan nama '{nama_file_gambar}'.")
plt.show()