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
    {"label": "Age", "non-peritonitis": ">2 yo", "peritonitis": "<2 yo", "p_val": 0.002, "mean": 1.4, "std_dev": (1.73 - 1.14)/4, "mrf": False},
    {"label": "Gender", "non-peritonitis": "Female", "peritonitis": "Male", "p_val": 0.09, "mean": 1.08, "std_dev": (1.18 - 0.99)/4, "mrf": False},
    {"label": "Duration of PD", "non-peritonitis": "<12 mo", "peritonitis": ">12 mo", "p_val": 0.001, "mean": 2.29, "std_dev": (3.07 - 1.70)/4, "mrf": False},
    {"label": "Place of Residence", "non-peritonitis": "Rural", "peritonitis": "Urban", "p_val": 0.08, "mean": 1.22, "std_dev": (1.51 - 0.98)/4, "mrf": False},
    {"label": "Housing", "non-peritonitis": "Good service", "peritonitis": "Fair/poor service", "p_val": 0.77, "mean": 1.086956522, "std_dev": (1.63 - 0.52)/4, "mrf": True},
    {"label": "Socioeconomic", "non-peritonitis": "Good", "peritonitis": "Poor/fair", "p_val": 0.09, "mean": 1.19047619, "std_dev": (1.03 - 0.68)/4, "mrf": True},
    {"label": "Education", "non-peritonitis": "Studies", "peritonitis": "Illiterate", "p_val": 0.48, "mean": 1.21, "std_dev": (2.08 - 0.71)/4, "mrf": False},
    {"label": "Peritonitis in ESI", "non-peritonitis": "No ESI", "peritonitis": "ESI", "p_val": 0.0001, "mean": 1.35, "std_dev": (1.58 - 1.16)/4, "mrf": True},
    {"label": "Nutrition", "non-peritonitis": "Normal Nutrition", "peritonitis": "Poor nutrition", "p_val": 0.19, "mean": 1.123595506, "std_dev": (1.06 - 0.76)/4, "mrf": True},
    {"label": "Cause of ESRD", "non-peritonitis": "Glomerular", "peritonitis": "Non-glomerular", "p_val": 0.04, "mean": 1.13, "std_dev": (1.27 - 1.00)/4, "mrf": False},
    {"label": "Type of Catheter (Shape)", "non-peritonitis": "Coiled/swan neck", "peritonitis": "Straight", "p_val": 0.48, "mean": 1.15, "std_dev": (1.72 - 0.77)/4, "mrf": True},
    {"label": "Type of Catheter (Cuff)", "non-peritonitis": "Double", "peritonitis": "Single cuff", "p_val": 0.32, "mean": 1.33, "std_dev": (2.32 - 0.76)/4, "mrf": True},
    {"label": "Catheter Placement", "non-peritonitis": "Open", "peritonitis": "Laparoscopic", "p_val": 0.85, "mean": 1.03, "std_dev": (1.45 - 0.74)/4, "mrf": True},
    {"label": "Gastrostomy/Intraperitoneal Device", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "mean": 1.282051282, "std_dev": (1.16 - 0.52)/4, "mrf": True},
    {"label": "Performed CAPD", "non-peritonitis": "Patients", "peritonitis": "Parents/others", "p_val": 0.27, "mean": 1.234567901, "std_dev": (1.17 - 0.56)/4, "mrf": True},
    {"label": "Starting PD <2 weeks after catheter placement", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "mean": 1.37, "std_dev": (2.27 - 0.82)/4, "mrf": True},
    {"label": "Catheter Orientation", "non-peritonitis": "Lateral/downward", "peritonitis": "upward", "p_val": 0.12, "mean": 1.515151515, "std_dev": (1.11 - 0.39)/4, "mrf": True},
    {"label": "Stunting", "non-peritonitis": "No stunting", "peritonitis": "Stunting", "p_val": 0.32, "mean": 1.388888889, "std_dev": (1.38 - 0.37)/4, "mrf": True},
]

def hitung_prediksi_randomized_rr(row_pasien):
    mult_rand_cumulative = 1.0

    for var in variables_data:
        pilihan_aktif = str(row_pasien[var['label']]).strip()
        
        random_rr = np.random.normal(loc=var["mean"], scale=var["std_dev"])
        if random_rr <= 0: 
            random_rr = 0.01
            
        if pilihan_aktif.lower() == "tidak diketahui" or pilihan_aktif.lower() == var["non-peritonitis"].lower():
            current_multiplier = 1.0
        else:
            current_multiplier = random_rr
            
        mult_rand_cumulative *= current_multiplier
        
    score_mult_rand = min(mult_rand_cumulative, 100.0)
    
    if score_mult_rand >= 50.0:
        kategori = "Berisiko Tinggi Peritonitis"
    else:
        kategori = "Berisiko Rendah Peritonitis"
        
    return kategori, score_mult_rand

# =====================================================================
# STEP 2: OTOMATISASI EVALUASI BERKAS DATA_PASIEN_BERSIH_4.XLSX
# =====================================================================
file_name = "data_pasien_bersih_4.xlsx"  
df = pd.read_excel(file_name)

np.random.seed(42)

hasil_kategori_list = []
hasil_persentase_list = []
for index, row in df.iterrows():
    prediksi_kategori, prediksi_persentase = hitung_prediksi_randomized_rr(row)
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
print("EVALUASI MODEL MULTIPLICAITIVE - RANDOMIZED RR")
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
    cmap="Oranges", # Kita beri warna oranye untuk membedakan identitas visual antar-skenario
    xticklabels=["Tinggi", "Rendah"], 
    yticklabels=["Tinggi", "Rendah"] 
)
plt.title("Confusion Matrix - Prediksi Risiko Peritonitis (Randomized RR)", fontsize=12, pad=15)
plt.ylabel("Actual", fontsize=10)
plt.xlabel("Predicted", fontsize=10)

waktu_sekarang = datetime.now().strftime("%Y%m%d_%H%M%S")
nama_file_gambar = f"confusion_matrix_randomized_rr_{waktu_sekarang}.png"
plt.savefig(nama_file_gambar, dpi=300, bbox_inches="tight")
print(f"Grafik matriks Randomized RR berhasil disimpan dengan nama '{nama_file_gambar}'.")
plt.show()