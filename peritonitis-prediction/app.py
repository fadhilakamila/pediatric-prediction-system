import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import hashlib
import hmac
import os
import pytz
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection


st.set_page_config(page_title="Pediatric Prediction System", layout="wide", page_icon="🧮")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        /* 1. LATAR BELAKANG GLOBAL & SIDEBAR */
        .stApp {
            background-color: #F1F5F9 !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E2E8F0;
            box-shadow: 2px 0 12px rgba(0,0,0,0.02);
        }

        /* 2. TIPOGRAFI HURUF GLOBAL */
        html, body, .stApp, p, li, label, h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
        }

        /* 3. JUDUL EXTRABOLD */
        h1 {
            font-weight: 800 !important;
            color: #0F172A !important;
            letter-spacing: -0.03em !important;
        }
        
        h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        /* CSS: SOFT PREMIUM SHADOW */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 16px !important;
            /* Efek bayangan berlapis (layered ambient shadow) tren SaaS 2026 */
            box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.03), 
                        0 4px 6px -1px rgba(15, 23, 42, 0.05), 
                        0 10px 15px -3px rgba(15, 23, 42, 0.03), 
                        0 20px 25px -5px rgba(15, 23, 42, 0.01) !important;
            padding: 32px !important; /* Padding seimbang agar isi form memiliki ruang bernapas */
            margin-bottom: 25px !important;
        }

        /* 4. DROPDOWN & TEXT INPUT */
        div[data-testid="stTextInput"] > div, 
        div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
            border: 1px solid #CBD5E1 !important;
            border-radius: 12px !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
            transition: all 0.2s ease-in-out !important;
        }

        .stTextInput input, div[data-baseweb="select"] > div {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }

        div[data-testid="stTextInput"]:focus-within > div, 
        div[data-testid="stSelectbox"] > div[data-baseweb="select"]:focus-within {
            border-color: #1E3A8A !important;
            box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.15) !important;
            outline: none !important;
        }

        /* FORM LOGIN */
        div[data-testid="stForm"] {
            border-radius: 16px !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05) !important;
            padding: 32px !important;
        }

        /* 5. MENU SIDEBAR NAVIGATION */
        .nav-link {
            background-color: #F1F5F9 !important;
            color: #334155 !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            margin-bottom: 5px !important;
        }
        .nav-link.active {
            background-color: #1E3A8A !important;
            color: #FFFFFF !important;
        }

        /* 6. TOMBOL UTAMA */
        .stButton button {
            border-radius: 12px !important;
            box-shadow: 0 4px 6px -1px rgba(30, 58, 138, 0.2) !important;
        }
        .stButton button p {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em !important;
        }

        /* IKON SIDEBAR & DOWNLOAD */
        .material-symbols-rounded, 
        .material-icons, 
        .stIcon,
        span[class*="icon"] {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# SISTEM AUTENTIKASI 
# ==============================================================================
def check_password():
    def password_entered():
        if st.session_state["username"] in st.secrets["password"] and hmac.compare_digest(
            st.session_state["password"], st.secrets["password"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True
    
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E3A8A !important; -webkit-text-fill-color: #1E3A8A !important; font-size: 3.5rem !important; font-weight: 900 !important; letter-spacing: -0.04em !important; line-height: 1.2; margin-bottom: 8px;'>Pediatric Prediction System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 15px; font-weight: 400; margin-bottom: 32px; line-height: 1.5;'>Selamat Datang di Pediatric Prediction System!</p>", unsafe_allow_html=True)
        
    log_col1, log_col2, log_col3 = st.columns([1.3, 1.0, 1.3])
    
    with log_col2:
        with st.form("Credentials", clear_on_submit=False):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            
            st.form_submit_button("Login", on_click=password_entered, use_container_width=True, type="primary")
            
        if st.session_state.get("password_correct") is False:
            st.error("Username atau password salah.")
            
    return False

if not check_password():
    st.stop()

# ==============================================================================
# DATABASE CONNECTIVITY
# ==============================================================================
@st.cache_data(ttl=3600)  
def load_data_cached(module_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=module_name)
        if df is not None:
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    except Exception as e:
        return None

def save_prediction(user_selections, score_fixed, score_rand, score_wa, score_wa_opt, outcome, module_name, protective_factors=None, risk_factors=None, mrf_list=None, mrf_dict=None):
    file_path = 'PeritonitisPrediction_Database.xlsx' if module_name == "Peritonitis" else 'PredictCRRTforKids_Database.xlsx'
    tz_jkt = pytz.timezone('Asia/Jakarta')
    timestamp = datetime.now(pytz.utc).astimezone(tz_jkt).strftime("%Y-%m-%d %H:%M:%S")
    raw_name = user_selections.get("Nama Pasien", "Unknown")
    patient_id = hashlib.sha256(raw_name.encode()).hexdigest()[:8].upper()
    
    if module_name == "Peritonitis":
        mrf_full_text = ""
        if mrf_list and mrf_dict:
            mrf_full_text = " | ".join([f"{mrf}: {mrf_dict.get(mrf, '')}" for mrf in mrf_list])
            
        new_data = {
            "Module": module_name, "Timestamp": timestamp, "Patient_ID": patient_id,
            "Age": user_selections.get("Age", "Tidak Diketahui"),
            "Gender": user_selections.get("Gender", "Tidak Diketahui"),
            "Duration of PD": user_selections.get("Duration of PD", "Tidak Diketahui"),
            "Place of Residence": user_selections.get("Place of Residence", "Tidak Diketahui"),
            "Housing": user_selections.get("Housing", "Tidak Diketahui"),
            "Socioeconomic": user_selections.get("Socioeconomic", "Tidak Diketahui"),
            "Education": user_selections.get("Education", "Tidak Diketahui"),
            "Peritonitis in ESI": user_selections.get("Peritonitis in ESI", "Tidak Diketahui"),
            "Nutrition": user_selections.get("Nutrition", "Tidak Diketahui"),
            "Cause of ESRD": user_selections.get("Cause of ESRD", "Tidak Diketahui"),
            "Type of Catheter (Shape)": user_selections.get("Type of Catheter (Shape)", "Tidak Diketahui"),
            "Type of Catheter (Cuff)": user_selections.get("Type of Catheter (Cuff)", "Tidak Diketahui"),
            "Catheter Placement": user_selections.get("Catheter Placement", "Tidak Diketahui"),
            "Gastrostomy/Intraperitoneal Device": user_selections.get("Gastrostomy/Intraperitoneal Device", "Tidak Diketahui"),
            "Performed CAPD": user_selections.get("Performed CAPD", "Tidak Diketahui"),
            "Starting PD <2 weeks after PD catheter placement": user_selections.get("Starting PD <2 weeks after PD catheter placement", "Tidak Diketahui"),
            "Catheter Orientation": user_selections.get("Catheter Orientation", "Tidak Diketahui"),
            "Stunting": user_selections.get("Stunting", "Tidak Diketahui"),
            "Outcome_Category": outcome,
            "Peritonitis_Risk_Rate_Fixed_RR": f"{score_fixed:.2f}%",
            "Peritonitis_Risk_Rate_Randomized_RR": f"{score_rand:.2f}%",
            "Peritonitis_Risk_Rate_Weighted_Average": f"{score_wa:.2f}%",
            "Peritonitis_Risk_Rate_Weighted_Average_Opt": f"{score_wa_opt:.2f}%",
            "Protective_Factors": ", ".join(protective_factors) if protective_factors else "",
            "Risk_Factors": ", ".join(risk_factors) if risk_factors else "",
            "Modifiable_Risk_Factors_Advice": mrf_full_text if mrf_full_text else "Tidak ada intervensi MRF aktif."
        }
    else:
        new_data = {
            "Module": module_name, "Timestamp": timestamp, "Patient_ID": patient_id,
            **{k: v for k, v in user_selections.items() if k != "Nama Pasien"},
            "survival probability": f"{score_fixed:.2f}%", "Outcome": outcome
        }
    
    new_df = pd.DataFrame([new_data])
    
    try:
        if os.path.exists(file_path):
            existing_df = pd.read_excel(file_path)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else: updated_df = new_df
        updated_df.to_excel(file_path, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan backup lokal: {e}")

    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        existing_gsheet = conn.read(worksheet=module_name)
        
        if existing_gsheet is not None and not existing_gsheet.empty:
            updated_gsheet = pd.concat([existing_gsheet, new_df], ignore_index=True)
        else:
            updated_gsheet = new_df
            
        conn.update(worksheet=module_name, data=updated_gsheet)
    except Exception as e:
        st.warning(f"Gagal sinkronisasi ke Google Sheets (Mode Offline Aktif): {e}")

    return patient_id

# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.title("Menu")
    
    selection = option_menu(
        menu_title=None,
        options=["Peritonitis Prediction", "CRRT Prediction"], 
        menu_icon="cast", 
        default_index=0,
    )
    
    developer = "Fadhila Kamila Ismail" if selection == "Peritonitis Prediction" else "Zulfan Zidni Ilhama"

    st.markdown(f"""
        <div style="line-height: 1.4; font-size: 0.85rem; background-color: #FFFFFF; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
            <span style="color: #64748B; display: block;">Developed by</span>
            <strong style="color: #0F172A; display: block; margin-bottom: 8px;">{developer}</strong>       
            <span style="color: #64748B; display: block;">Supervised by</span>
            <strong style="color: #0F172A; display: block; margin-bottom: 8px;">Retno Aulia Vinarti, M.Kom., Ph.D.</strong>
            <span style="color: #64748B; display: block;">Expert Advisor</span>
            <strong style="color: #0F172A; display: block;">dr. Reza Fahlevi, Sp.A(K)</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        if "password_correct" in st.session_state:
            del st.session_state["password_correct"]
        st.toast("Anda berhasil logout!")
        import time
        time.sleep(1.5)
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if selection == "Peritonitis Prediction":
        st.markdown(f"""
        <div style="
            background-color: #EFF6FF; 
            padding: 16px; 
            border-radius: 12px; 
            border: 1px solid #DBEAFE;
            border-left: 5px solid #1A73E8;
            color: #1E40AF;
            font-size: 0.9rem;
            line-height: 1.4;
            box-shadow: 0 1px 2px rgba(0,0,0,0.01);
        ">
            <strong>⚠️ Peringatan</strong><br>
            Sistem ini menggunakan knowledge base dari meta-analisis studi peritonitis pediatri.<br>
            Aplikasi ini hanya alat bantu dan bukan pengganti keputusan akhir dari Dokter Spesialis Anak Konsultan Nefrologi.
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# ========================== PERITONITIS PREDICTION ============================
# ==============================================================================
if selection == "Peritonitis Prediction":
    st.markdown("<h1 style='color: #1E3A8A; font-family: sans-serif; margin-bottom: 2px;'>Prediksi Risiko Peritonitis pada Pasien Pediatri Peritoneal Dialysis</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size: 1.05rem; margin-top: 0px;'>Isi parameter klinis di bawah ini, lalu biarkan sistem menganalisis tingkat risiko peritonitis pasien!</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    variables_data = [
        {"label": "Age", "peritonitis": "<2 yo", "non-peritonitis": ">2 yo", "p_val": 0.002, "weight": 2, "mean": 1.4, "std_dev": (1.73 - 1.14)/4, "mrf": False},
        {"label": "Gender", "peritonitis": "Male", "non-peritonitis": "Female", "p_val": 0.090, "weight": 0, "mean": 1.08, "std_dev": (1.18 - 0.99)/4, "mrf": False},
        {"label": "Duration of PD", "peritonitis": ">12 mo", "non-peritonitis": "<12 mo", "p_val": 0.001, "weight": 2, "mean": 2.29, "std_dev": (3.07 - 1.70)/4, "mrf": False},
        {"label": "Place of Residence", "peritonitis": "Urban", "non-peritonitis": "Rural", "p_val": 0.080, "weight": 0, "mean": 1.22, "std_dev": (1.51 - 0.98)/4, "mrf": False},
        {"label": "Housing", "peritonitis": "Fair/poor service", "non-peritonitis": "Good service", "p_val": 0.770, "weight": 1, "mean": 1.086956522, "std_dev": (1.63 - 0.52)/4, "mrf": True}, 
        {"label": "Socioeconomic", "peritonitis": "Poor/fair", "non-peritonitis": "Good", "p_val": 0.090, "weight": 1, "mean": 1.19047619, "std_dev": (1.03 - 0.68)/4, "mrf": True},     
        {"label": "Education", "peritonitis": "Illiterate", "non-peritonitis": "Studies", "p_val": 0.480, "weight": 1, "mean": 1.21, "std_dev": (2.08 - 0.71)/4, "mrf": False},
        {"label": "Peritonitis in ESI", "peritonitis": "ESI", "non-peritonitis": "No ESI", "p_val": 0.0001, "weight": 2, "mean": 1.35, "std_dev": (1.58 - 1.16)/4, "mrf": True},
        {"label": "Nutrition", "peritonitis": "Poor nutrition", "non-peritonitis": "Normal Nutrition", "p_val": 0.190, "weight": 1, "mean": 1.123595506, "std_dev": (1.06 - 0.76)/4, "mrf": True}, 
        {"label": "Cause of ESRD", "peritonitis": "Non-glomerular", "non-peritonitis": "Glomerular", "p_val": 0.040, "weight": 2, "mean": 1.13, "std_dev": (1.27 - 1.00)/4, "mrf": False},
        {"label": "Type of Catheter (Shape)", "peritonitis": "Straight", "non-peritonitis": "Coiled/swan neck", "p_val": 0.480, "weight": 0, "mean": 1.15, "std_dev": (1.72 - 0.77)/4, "mrf": True},
        {"label": "Type of Catheter (Cuff)", "peritonitis": "Single cuff", "non-peritonitis": "Double", "p_val": 0.320, "weight": 2, "mean": 1.33, "std_dev": (2.32 - 0.76)/4, "mrf": True},
        {"label": "Catheter Placement", "peritonitis": "Laparoscopic", "non-peritonitis": "Open", "p_val": 0.850, "weight": 0, "mean": 1.03, "std_dev": (1.45 - 0.74)/4, "mrf": True},
        {"label": "Gastrostomy/Intraperitoneal Device", "peritonitis": "Yes", "non-peritonitis": "No", "p_val": 0.230, "weight": 2, "mean": 1.282051282, "std_dev": (1.16 - 0.52)/4, "mrf": True}, 
        {"label": "Performed CAPD", "peritonitis": "Parents/others", "non-peritonitis": "Patients", "p_val": 0.270, "weight": 0, "mean": 1.234567901, "std_dev": (1.17 - 0.56)/4, "mrf": True},    
        {"label": "Starting PD <2 weeks after PD catheter placement", "peritonitis": "Yes", "non-peritonitis": "No", "p_val": 0.230, "weight": 1, "mean": 1.37, "std_dev": (2.27 - 0.82)/4, "mrf": True},
        {"label": "Catheter Orientation", "peritonitis": "upward", "non-peritonitis": "Lateral/downward", "p_val": 0.120, "weight": 2, "mean": 1.515151515, "std_dev": (1.11 - 0.39)/4, "mrf": True}, 
        {"label": "Stunting", "peritonitis": "Stunting", "non-peritonitis": "No stunting", "p_val": 0.320, "weight": 1, "mean": 1.388888889, "std_dev": (1.38 - 0.37)/4, "mrf": True} 
    ]

    mrf_explanations = {
        "Housing": "Lingkungan rumah harus diadaptasi untuk memenuhi standar prosedur medis. Ruangan yang digunakan untuk pertukaran cairan harus bersih dan bebas debu untuk meminimalkan risiko infeksi, sebab partikel debu dapat menjadi vektor bagi patogen udara yang dapat mengontaminasi set transfer saat prosedur koneksi atau diskoneksi. Penyediaan wastafel di dalam atau dekat ruangan dialisis diperlukan untuk memastikan kepatuhan protokol antiseptic tangan sehingga menurunkan insiden peritonitis akibat touch contamination. Pencahayaan yang optimal di dalam ruangan diperlukan agar caregiver dapat memantau kejernihan cairan efluen serta memeriksa kondisi tempat keluar kateter dengan teliti. Hewan peliharaan tidak boleh berada di area perawatan saat proses koneksi atau diskoneksi berlangsung karena risiko paparan bakteri seperti Pasteurella multocida atau kerusakan fisik pada selang dialisis akibat gigitan atau cakaran. Selain itu, caregiverharus ditekankan untuk selalu mencuci tangan setelah berinteraksi dengan hewan dan sebelum memulai prosedur dialisis. [Sumber 1](https://www.freseniuskidneycare.com/treatment/home-dialysis/getting-prepared) [Sumber 2](https://www.ouh.nhs.uk/media/agxhnni2/85713pdialysis.pdf) [Sumber 3](https://www.kidney.org/kidney-topics/preparing-home-dialysis) [Sumber 4](https://spnp-spp.pt/media/rqdpbrom/catheter-related-infections-and-peritonitis-in-pediatric-patients-receiving-peritoneal-dialysis-guideline-for-prevention-and-treatment-2012-1-_compressed-1.pdf) [Sumber 5](https://freseniusmedicalcare.com/content/dam/home-products-education/steps2home-pd/Preventing_Peritonitis.pdf) [Sumber 6](https://www.satellitehealthcare.com/blog/pets-and-peritoneal-dialysis-absolutely/)",
        "Nutrition": "Malnutrisi protein-kalori (cachexia) adalah masalah umum pada anak yang menjalani PD. Manajemen nutrisi bertujuan untuk mengejar pertumbuhan dan mengganti hilangnya protein serta asam amino ke dalam cairan dialysis.Penilaian status nutrisi harus dilakukan secara berkala, minimal setiap bulan pada bayi dan 3-4 bulan pada anak yang lebih tua, menggunakan parameter antropometri (berat badan, tinggi badan, lingkar kepala), biokimia (albumin urea), and analisis bioimpedansi jika tersedia. Penanganannya juga harus multidisiplin dan mencakup memastikan asupan energi dan protein yang adekuat; kontrol metabolik yang optimal, dengan koreksi asidosis, anemia, dan hiperparatiroidisme; dosis dialisis yang optimal (atau setidaknya adekuat); dan, jika perlu, pemberian obat-obatan tertentu seperti hormon pertumbuhan manusia rekombinan. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/)",
        "Socioeconomic": "Deprivasi sosioekonomi berdampak pada hasil treatment yang lebih buruk. Hal ini kemungkinan disebabkan oleh keterbatasan akses terhadap fasilitas sanitasi yang memadai, tekanan psikologis pada pengasuh, serta keterbatasan informasi medis. Strategi bisa dilakukan melalui program pelatihan bagi keluarga (caregiver) dari perawat dialisis yang berpengalaman. Bagi keluarga dengan keterbatasan pendidikan atau ekonomi, dukungan teknis telepon 24 jam dan kunjungan rumah secara berkala oleh tim medis sosial sangat efektif dalam memastikan kepatuhan terhadap prosedur aseptik. Pelatihan ulang sangat dianjurkan, terutama setelah terjadinya peritonitis, untuk mengidentifikasi adanya penyimpangan dalam teknik pertukaran cairan. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC11835194/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC4934433/) [Sumber 3](https://pubmed.ncbi.nlm.nih.gov/23226378/) [Sumber 4](https://pubmed.ncbi.nlm.nih.gov/16091376/) [Sumber 6](https://spnp-spp.pt/media/rqdpbrom/catheter-related-infections-and-peritonitis-in-pediatric-patients-receiving-peritoneal-dialysis-guideline-for-prevention-and-treatment-2012-1-_compressed-1.pdf) [Sumber 7](https://pmc.ncbi.nlm.nih.gov/articles/PMC5691857/) [Sumber 8](https://pmc.ncbi.nlm.nih.gov/articles/PMC4335934/) [Sumber 9](https://www.kidney.org/kidney-topics/preparing-home-dialysis)",
        "Performed CAPD": "Tidak ada perbedaan yang signifikan dalam tingkat kelangsungan hidup teknik, kematian, maupun episode peritonitis antara dialisis yang dilakukan sendiri oleh pasien (self-care) dengan dialisis yang dibantu oleh keluarga atau pengasuh (assisted/home-care). Namun, pada populasi anak (khususnya balita atau anak dengan keterbatasan fisik/kognitif), peran orang tua (Parent/Others) sangat mutlak diperlukan. Bagi orang tua yang memiliki tingkat pendidikan rendah atau keterbatasan ekonomi, dialisis tetap dapat berhasil dengan baik tanpa komplikasi besar asalkan diberikan pelatihan intensif secara 1:1, dukungan telepon 24 jam, dan kunjungan rumah berkala oleh perawat dialisis berpengalaman. Di sisi lain, bagi pasien remaja yang melakukan dialisis secara mandiri (Patient), tantangan psikososial seperti kejenuhan (burnout), perasaan terkekang (slavery feeling), dan depresi sering kali muncul, sehingga membutuhkan pengawasan ketat dari tim medis agar kepatuhan terhadap prosedur aseptik tetap terjaga. [Sumber 1](https://pubmed.ncbi.nlm.nih.gov/29456210/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC4335934/) [Sumber 3](https://www.ispd.org/wp-content/uploads/2025/12/Assisted-PD-PP-2024-with-VA_formatted.pdf)",
        "Gastronomy Device": "Keberadaan perangkat gastrostomi secara signifikan meningkatkan risiko infeksi, terutama peritonitis fungal dan peritonitis bakteri akibat translokasi kuman serta kontaminasi silang. Bagi anak yang memerlukan gastrostomi, sangat disarankan agar pemasangannya direncanakan secara matang dan dilakukan sebelum atau bersamaan dengan pemasangan kateter dialisis peritoneal ('PEG before PD'). Apabila gastrostomi (seperti PEG) terpaksa dipasang setelah dialisis peritoneal berjalan, beberapa protokol pencegahan infeksi wajib diterapkan, seperti memberikan profilaksis antibiotik dan antijamur, menghentikan sementara prosedur dialisis peritoneal selama 2–3 hari pasca-operasi (pasien dialihkan sementara ke hemodialisis jika diperlukan), serta memastikan lokasi keluar kateter dialisis diletakkan sejauh mungkin dari area gastrostomi untuk menghindari kontaminasi silang. [Sumber 1](https://www.researchgate.net/publication/7239515_Percutaneous_Endoscopic_Gastrostomy_in_Children_on_Peritoneal_Dialysis) [Sumber 2](https://ajkdblog.org/2014/08/11/pd-in-patients-with-gastrostomy-tubes-vice-versa-challenging-but-doable/) [Sumber 3](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Catheter Orientation": "Posisi atau arah lubang keluar kateter (exit site) sangat memengaruhi risiko terjadinya infeksi. Data multisentrik dari SCOPE Collaborative menunjukkan bahwa orientasi kateter yang menghadap ke atas (Upward) dikaitkan dengan peningkatan risiko peritonitis hingga 4.2 kali lipat (Rate Ratio: 4.2; 95% CI: 1.49–11.89) dibandingkan orientasi lainnya. Secara anatomis, lubang keluar yang menghadap ke atas menciptakan bentuk cekungan yang dapat menampung keringat, air mandi, dan kotoran. Akibat gaya gravitasi, bakteri yang terkumpul di area ini akan mengendap dan bermigrasi ke dalam terowongan kateter. Oleh karena itu, lubang keluar kateter harus selalu diarahkan ke bawah (Downward) atau ke samping (Lateral) untuk mencegah penumpukan bakteri secara alami. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5012476/) [Sumber 2](https://openurologyandnephrologyjournal.com/VOLUME/5/PAGE/4/) [Sumber 3](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Stunting": "Stunting pada anak dialisis bukan hanya disebabkan oleh asupan kalori yang rendah, tetapi juga oleh asidosis metabolik, anemia, osteodistrofi ginjal, dan resistensi terhadap hormon pertumbuhan. Intervensi pertama adalah memastikan kecukupan dialisis dan koreksi parameter metabolik seperti asidosis dan hiperparatiroidisme.Jika pertumbuhan masih belum optimal meskipun parameter metabolik telah terkendali dan asupan nutrisi sudah mencapai target, terapi dengan hormon pertumbuhan manusia rekombinan (rhGH) dapat dipertimbangkan. Selain itu, dukungan nutrisi intensif dan klirens dialisis yang adekuat pada pasien prepubertal dapat mempromosikan pertumbuhan normal tanpa selalu memerlukan rhGH. Pada anak yang mengalami stunting (tinggi badan < persentil ke-2), perhitungan kebutuhan energi dan mikronutrien harus didasarkan pada height-age pasien, bukan chronological age-nya, untuk memberikan dukungan yang sesuai dengan ukuran tubuh aktualnya. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/)",
        "Starting PD <2 weeks after PD catheter placement": "Waktu antara pemasangan kateter dan dimulainya dialisis (break-in-period) merupakan faktor penting untuk mencegah komplikasi. Masa penyembuhan minimal 2 minggu sebelum dialysis dimulai. Namun, dalam kondisi klinis tertentu di mana pasien membutuhkan dialisis segera, urgent-start PD (dimulai dalam <14 hari atau bahkan <48 jam) menjadi alternatif yang baik untuk menghindari penggunakan kateter hemodialysis sementara. Pasien dengan break-in-period < 7 hari memiliki risiko yang lebih tinggi terhadap komplikasi awal seperti kebocoran dialisat dan malposisi kateter. Namun, risiko tersebut tidak berkorelasi dengan penurunan kelangsungan hidup atau peningkatan risiko peritonitis jika dilakukan dengan protokol yang tepat. Pada kondisi urgent-start, risiko kebocoran dimitigasi dengan menggunakan volume pengisian rendah (10-20 ml/kg) dan posisi pasien supine untuk mengurangi tekanan intra-abdominal.[Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC3923692/) [Sumber 2](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206426) [Sumber 3](https://www.sages.org/publications/guidelines/peritoneal-dialysis-access-guideline-update-2023/) [Sumber 4](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2022.936573/full) [Sumber 5](https://scholarlyexchange.childrensmercy.org/cgi/viewcontent.cgi?article=7522&context=papers) [Sumber 6](https://pubmed.ncbi.nlm.nih.gov/33523772/) [Sumber 7](https://www.bcrenal.ca/resource-gallery/Documents/PD_Procedures-Exit_Site_Care-Post-Operative_PD_Catheter_Insertion.pdf)",
        "Peritonitis in ESI": "Penggunaan antibiotik topikal secara rutin pada tempat keluar kateter telat terbukti menurunkan angka infeksi. Aplikasi harian salep mupirocin atau gentamicin pada exit-site direkomendasikan untuk menekan kolonisasi Staphylococcus aureus dan Pseudomonas aeruginosa.Pembersihan area secara rutin dengan larutan antiseptik non-iritan (seperti chlorhexidine 0,05% atau sabun antibakteri ringan) juga merupakan bagian standar dari perawatan. Penilaian kondisi exit-site secara objektif menggunakan sistem skor (seperti Skor ISPD yang mencakup pembengkakan, kerak, kemerahan, nyeri, dan sekret) sangat membantu caregiver dalam mendeteksi infeksi secara dini. Immobilisasi kateter dengan menggunakan plester atau perangkat fiksasi sangat krusial karena trauma mekanis pada tempat keluar sering kali menjadi pintu masuk bagi bakteri. Jika ESI terjadi, terapi antibiotik oral atau intraperitoneal harus dimulai segera dan dilanjutkan selama minimal 2 minggu, atau 3 minggu jika disebabkan oleh Pseudomonas. Pengangkatan kateter mungkin diperlukan jika infeksi bersifat refrakter (tidak merespons pengobatan setelah 2 minggu) atau jika infeksi telah menyebar ke terowongan kateter (tunnel infection) yang menyebabkan peritonitis berulang. [Sumber 1](https://ispd.org/wp-content/uploads/2025/09/LI-ET-1.pdf) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC12640025/) [Sumber 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5033625/) [Sumber 4](https://www.chikd.org/journal/view.php?number=726) [Sumber 5](https://ispd.org/wp-content/uploads/ISPD-Catheter-related-Infection-Recommendations-2023-Update.pdf) [Sumber 6](https://www.bcrenal.ca/resource-gallery/Documents/PD_Procedures-Exit_Site_Care-Post-Operative_PD_Catheter_Insertion.pdf) [Sumber 7](https://davita.com/treatment-options/articles/preventing-catheter-infections-on-peritoneal-dialysis/) [Sumber 8](https://edren.org/ren/handbook/pd-handbook/protocol-for-the-management-of-pd-peritonitis-long-version/)",
        "Type of Catheter (Cuff)": "Penggunaan kateter dengan double-cuff lebih disarankan daripada single-cuff)untuk populasi anak secara umum. Deep cuff berfungsi untuk menjangkar kateter di otot rektus dan mencegah kebocoran, sementara superficial cuff bertindak sebagai penghalang fisik terhadap migrasi bakteri ke arah rongga peritoneum. Namun, pada neonatus atau bayi dengan dinding perut yang sangat tipis, kateter single-cuff sering kali lebih dipilih untuk mencegah ekstrusi manset ke permukaan kulit. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10223083/) [Sumber 2](http://ispd.org/wp-content/uploads/7.-Dagmara-Borzych-Duzalka-Peritoneal-Dialysis-Catheters-Outcome-in-Children.-The-IPPN-Data.pdf) [Sumber 3](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Type of Catheter (Shape)": "Perdebatan mengenai efektivitas kateter straight dibandingkan dengan kateter coiled/curled masih berlangsung. Kateter coiled secara teoretis mengurangi nyeri saat pengisian cairan dan meminimalkan trauma pada organ visceral, tetapi beberapa data menunjukkan risiko malposisi yang lebih tinggi dibandingkan tipe lurus pada beberapa kelompok pasien. Di sisi lain, kateter straight lebih mudah ditempatkan pada bayi kecil yang memiliki ruang intra-abdominal terbatas. Secara keseluruhan, pedoman tidak menyatakan superioritas mutlak salah satu bentuk, dan pemilihan sering kali bergantung pada preferensi pusat dialisis dan anatomi pasien. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC9365012/) [Sumber 2](http://ispd.org/wp-content/uploads/7.-Dagmara-Borzych-Duzalka-Peritoneal-Dialysis-Catheters-Outcome-in-Children.-The-IPPN-Data.pdf) [Sumber 3](https://scholarlyexchange.childrensmercy.org/cgi/viewcontent.blogspot.com/?article=7522&context=papers) [Sumber 4](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Catheter Placement": "Pedoman klinis terbaru dari Society of American Gastrointestinal and Endoscopic Surgeons (SAGES) menyarankan penggunaan teknik laparoskopi tingkat lanjut (Laparoscopic) dibandingkan teknik bedah terbuka (Open) untuk pemasangan kateter pada populasi pediatrik. Laparoscopic menawarkan akurasi catheter placement yang jauh lebih tinggi di dalam rongga abdomen karena visualisasi langsung, serta meminimalkan trauma mekanis pada jaringan perut. Lebih lanjut, Laparoscopic memungkinkan dokter untuk melakukan prosedur profilaksis penting seperti omentektomi atau omentopeksi untuk meminimalkan risiko omental wrapping (penyumbatan kateter oleh omentum), yang merupakan salah satu penyebab utama kegagalan mekanis kateter pada anak-anak. Laparoscopic juga terbukti mempermudah penyelamatan (salvage) jika terjadi malposisi atau disfungsi kateter tanpa harus melakukan pembedahan ulang yang invasif. [Sumber 1](https://www.sages.org/publications/guidelines/peritoneal-dialysis-access-guideline-update-2023/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC10223083/) [[3]](https://kidney.wiki/peritoneal-dialysis/pd-access/)"
    }

    significant_vars = ["Duration of PD", "Age", "Peritonitis in ESI", "Cause of ESRD"]

    patient_name = st.text_input("👤 Nama Pasien", placeholder="Masukkan nama pasien ...")
    st.space()
    st.markdown("#### Pilih Sesuai dengan Kondisi Pasien")

    if "peritonitis_active_tab" not in st.session_state:
        st.session_state["peritonitis_active_tab"] = 0

    user_selections = {}
    raw_choices_for_log = {}
    demografi_labels = ["Age", "Gender", "Place of Residence", "Housing", "Socioeconomic", "Education"]

    valid_demo_count = 0
    valid_medis_count = 0

    for i, var in enumerate(variables_data):
        if var['label'] in demografi_labels:
            key_demo = f"peritonitis_demo_select_{var['label']}_{i}"
            if key_demo in st.session_state and st.session_state[key_demo] != "Tidak Diketahui":
                valid_demo_count += 1
        else:
            key_med = f"peritonitis_med_select_{var['label']}_{i}"
            if key_med in st.session_state and st.session_state[key_med] != "Tidak Diketahui":
                valid_medis_count += 1

    status_demo = "🟢 Lengkap" if valid_demo_count == 6 else "🔴 Belum Lengkap"
    status_medis = "🟢 Lengkap" if valid_medis_count == 12 else "🔴 Belum Lengkap"

    tab_list = st.tabs(
        [f"Demografi ({status_demo})", f"Kondisi Medis ({status_medis})"]
    )

    with tab_list[0]:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        demo_col1, demo_col2 = st.columns(2)
        
        demo_counter = 0
        for i, var in enumerate(variables_data):
            if var['label'] in demografi_labels:
                target_col = demo_col1 if demo_counter < 3 else demo_col2
                
                is_significant = "*" if var['label'] in significant_vars else ""
                label = f"{demo_counter+1}. {var['label']}{is_significant}"
                options = ["Tidak Diketahui", var['peritonitis'], var['non-peritonitis']]
                
                choice = target_col.selectbox(label, options, index=0, key=f"peritonitis_demo_select_{var['label']}_{i}")
                raw_choices_for_log[var['label']] = choice
                user_selections[var['label']] = choice
                demo_counter += 1
            else:
                user_selections[var['label']] = "Tidak Diketahui"

        st.markdown("<br>", unsafe_allow_html=True)
        col_space, col_btn = st.columns([3.8, 0.4])
        with col_btn:
            if st.button("Lanjut ➜", use_container_width=True):
                st.components.v1.html("""
                    <script>
                        window.parent.document.querySelectorAll('.stTabs [role="tab"]')[1].click();
                    </script>
                """, height=0, width=0)

    with tab_list[1]:
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        med_col1, med_col2 = st.columns(2)
        
        medis_counter = 0
        for i, var in enumerate(variables_data):
            if var['label'] not in demografi_labels:
                target_col = med_col1 if medis_counter < 6 else med_col2
                
                is_significant = "*" if var['label'] in significant_vars else ""
                label = f"{medis_counter+1}. {var['label']}{is_significant}"
                options = ["Tidak Diketahui", var['peritonitis'], var['non-peritonitis']]
                
                choice = target_col.selectbox(label, options, index=0, key=f"peritonitis_med_select_{var['label']}_{i}")
                raw_choices_for_log[var['label']] = choice
                user_selections[var['label']] = choice
                medis_counter += 1

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("ℹ️ Variabel dengan tanda bintang (*) berpengaruh **signifikan** terhadap peritonitis (berdasarkan hasil meta-analisis).")
        st.info("💡 Pastikan semua indikator tab di atas berwarna hijau 🟢 atau Anda telah meninjau sebelum memulai hitung")

        st.markdown(" ")
        eksekusi_hitung = st.button("Hitung Tingkat Risiko", type="primary")

    if eksekusi_hitung:
            if not patient_name:
                st.warning("⚠️ Mohon isi nama atau inisial pasien terlebih dahulu.")
            else:
                user_selections["Nama Pasien"] = patient_name
                raw_choices_for_log["Nama Pasien"] = patient_name
                
                xai_supporting_peritonitis = []
                xai_supporting_non_peritonitis = []
                xai_unknown_data = []
                modifiable_risk_factors = []
                mrf_text_logs = []

                # --------------------------------------------------------------------------
                # SKENARIO A: MAIN - MULTIPLICATIVE FIXED RR
                # --------------------------------------------------------------------------
                mult_fixed_cumulative = 1.0
                for var in variables_data:
                    pilihan_aktif = user_selections[var["label"]]
                    
                    if pilihan_aktif == "Tidak Diketahui":
                        xai_unknown_data.append(var["label"])
                        current_multiplier = 1.0
                    elif pilihan_aktif == var["non-peritonitis"]:
                        xai_supporting_non_peritonitis.append(var["label"])
                        current_multiplier = 1.0
                    else:
                        is_sig = "*" if var["label"] in significant_vars else ""
                        xai_supporting_peritonitis.append(f"{var['label']}{is_sig}")
                        current_multiplier = var["mean"]
                        
                        if var["mrf"]:
                            modifiable_risk_factors.append(var["label"])
                            mrf_text_logs.append(f"[{var['label']}]: {mrf_explanations.get(var['label'], '')}")
                            
                    mult_fixed_cumulative *= current_multiplier
                
                score_mult_fixed = mult_fixed_cumulative

                # --------------------------------------------------------------------------
                # SKENARIO B: PEMBANDING 1 - MULTIPLICATIVE RANDOMIZED RR (GAUSSIAN MODEL)
                # --------------------------------------------------------------------------
                mult_rand_cumulative = 1.0
                for var in variables_data:
                    pilihan_aktif = user_selections[var["label"]]
                    
                    random_rr = np.random.normal(loc=var["mean"], scale=var["std_dev"])
                    if random_rr <= 0: 
                        random_rr = 0.01
                        
                    if pilihan_aktif == "Tidak Diketahui" or pilihan_aktif == var["non-peritonitis"]:
                        current_multiplier = 1.0
                    else:
                        current_multiplier = random_rr
                        
                    mult_rand_cumulative *= current_multiplier
                
                score_mult_rand = mult_rand_cumulative
                score_mult_rand = min(score_mult_rand, 100.0)
                
                # --------------------------------------------------------------------------
                # SKENARIO C: PEMBANDING 2 - WEIGHTED AVERAGE BASELINE (18 VARIABEL)
                # --------------------------------------------------------------------------
                wa_base_wi_xi = 0
                wa_base_wi = 0
                for var in variables_data:
                    wi = 2 if var["p_val"] < 0.05 else 1
                    xi = 1 if user_selections[var["label"]] == var["peritonitis"] else 0
                    wa_base_wi_xi += (wi * xi)
                    wa_base_wi += wi
                score_wa_base = (wa_base_wi_xi / wa_base_wi) * 100

                # --------------------------------------------------------------------------
                # SKENARIO D: PEMBANDING 3 - WEIGHTED AVERAGE TEROPTIMASI (14 VARIABEL)
                # --------------------------------------------------------------------------
                wa_opt_wi_xi = 0
                wa_opt_wi = 0
                for var in variables_data:
                    wi = var["weight"]
                    xi = 1 if user_selections[var["label"]] == var["peritonitis"] else 0
                    if wi > 0:
                        wa_opt_wi_xi += (wi * xi)
                        wa_opt_wi += wi
                score_wa_opt = (wa_opt_wi_xi / wa_opt_wi) * 100 if wa_opt_wi > 0 else 0.0

                # ==============================================================================
                # HASIL PREDIKSI
                # ==============================================================================
                st.markdown("---")
                st.markdown("### Hasil Prediksi")
                
                if score_mult_fixed >= 50.0:
                    status_color = "#DC2626"  
                    status = "BERISIKO TINGGI PERITONITIS"
                    status_desc = "karena tingkat risiko ≥ 50.00%. Pasien memerlukan pengawasan dan evaluasi."
                else:
                    status_color = "#16A34A"  
                    status = "BERISIKO RENDAH PERITONITIS"
                    status_desc = "karena tingkat risiko < 50.00%. Pasien terpantau aman terkendali."

                st.markdown(f"""
                <div style='background-color: #FFFFFF; padding: 24px; border-radius: 16px; box-shadow: 0 10px 25px -3px rgba(0,0,0,0.04), 0 4px 6px -2px rgba(0,0,0,0.02); border: 1px solid #CBD5E1; border-left: 8px solid {status_color}; margin-bottom: 25px;'>
                    <p style='margin: 0; font-size: 13px; color: #94A3B8; font-weight: 400; font-family: \"Inter\", sans-serif;'>Multiplicative Fixed RR</p>
                    <h1 style='margin: 2px 0 8px 0; color: #0F172A; font-size: 3rem; font-weight: 700;'>{score_mult_fixed:.2f}%</h1>
                    <p style='margin: 0; font-size: 14.5px; color: #334155; line-height: 1.5;'>
                        Pasien termasuk kategori <strong style='color: {status_color}; font-weight: 700;'>{status}</strong> {status_desc}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("🔍 Lihat Perbandingan dengan Metode Lain"):
                    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                    comp_col1, comp_col2, comp_col3 = st.columns(3)
                    
                    with comp_col1:
                        st.metric(label="Multiplicative Randomized RR", value=f"{score_mult_rand:.2f}%", delta=f"{score_mult_rand - score_mult_fixed:.2f}% vs Utama", delta_color="off")
                    with comp_col2:
                        st.metric(label="Weighted Average (18 Variabel)", value=f"{score_wa_base:.2f}%", delta=f"{score_wa_base - score_mult_fixed:.2f}% vs Utama", delta_color="off")
                    with comp_col3:
                        st.metric(label="Weighted Average (Teroptimasi 14 Variabel)", value=f"{score_wa_opt:.2f}%", delta=f"{score_wa_opt - score_mult_fixed:.2f}% vs Utama", delta_color="off")
                
                # ==============================================================================
                # XAI
                # ==============================================================================
                st.markdown(" ")
                st.markdown("#### 💡 Explainable AI")
                expl_col1, expl_col2 = st.columns(2)

                with expl_col1:
                    html_protektif = """<div style="background-color: #F0FDF4; padding: 24px; border-radius: 16px; border: 1px solid #BBF7D0; box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.08), 0 4px 6px -2px rgba(16, 185, 129, 0.04); font-family: 'Inter', sans-serif;"><span style="color: #14532D; font-size: 0.95rem; font-weight: 700; display: block; margin-bottom: 4px;">🛡️ Faktor Protektif Peritonitis</span><p style="color: #166534; font-size: 0.75rem; margin-bottom: 12px; line-height: 1.4;">Variabel yang menurunkan risiko peritonitis (RR &lt; 1)</p>"""
                    if xai_supporting_non_peritonitis:
                        html_protektif += """<ul style="color: #1F2937; font-size: 0.875rem; padding-left: 16px; margin: 0; line-height: 1.8; list-style-type: disc;">"""
                        for item in xai_supporting_non_peritonitis: html_protektif += f"<li style='margin-bottom: 6px;'>{item}</li>"
                        html_protektif += "</ul>"
                    else: 
                        html_protektif += "<p style='color: #94A3B8; font-size: 0.875rem; margin: 0; padding-left: 0;'>Tidak ada protective factors spesifik.</p>"
                    st.markdown(html_protektif + "</div>", unsafe_allow_html=True)

                with expl_col2:
                    html_pemicu = """<div style="background-color: #FEF2F2; padding: 24px; border-radius: 16px; border: 1px solid #FCA5A5; box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.08), 0 4px 6px -2px rgba(239, 68, 68, 0.04); font-family: 'Inter', sans-serif;"><span style="color: #7A1B1B; font-size: 0.95rem; font-weight: 700; display: block; margin-bottom: 4px;">⚠️ Faktor Risiko Peritonitis</span><p style="color: #991B1B; font-size: 0.75rem; margin-bottom: 12px; line-height: 1.4;">Variabel yang memicu risiko peritonitis (RR &gt; 1)</p>"""
                    if xai_supporting_peritonitis:
                        html_pemicu += """<ul style="color: #1F2937; font-size: 0.875rem; padding-left: 16px; margin: 0; line-height: 1.8; list-style-type: disc;">"""
                        for item in xai_supporting_peritonitis: html_pemicu += f"<li style='margin-bottom: 6px;'>{item}</li>"
                        html_pemicu += "</ul>"
                    else: 
                        html_pemicu += "<p style='color: #94A3B8; font-size: 0.875rem; margin: 0; padding-left: 0;'>Tidak ada risk factors spesifik.</p>"
                    st.markdown(html_pemicu + "</div>", unsafe_allow_html=True)
                
                st.space()
                st.caption("ℹ️ Variabel dengan tanda bintang (*) berpengaruh **signifikan** terhadap peritonitis (berdasarkan hasil meta-analisis).")
                    
                if xai_unknown_data:
                    xai_unknown_with_stars = [
                        f"{item}*" if item in significant_vars else item 
                        for item in xai_unknown_data
                    ]
                    
                    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
                    
                    html_unknown = f"""
                    <div style="background-color: #FFFFFF; padding: 24px; border-radius: 16px; border: 1px solid #CBD5E1; box-shadow: 0 10px 25px -3px rgba(0,0,0,0.04), 0 4px 6px -2px rgba(0,0,0,0.02); font-family: 'Inter', sans-serif;">
                        <span style="color: #334155; font-size: 0.95rem; font-weight: 700; display: block; margin-bottom: 4px;">Komponen Klinis Belum Lengkap / Tidak Diketahui ({len(xai_unknown_data)} Fitur)</span>
                        <p style="color: #64748B; font-size: 0.75rem; margin-bottom: 12px; line-height: 1.4;">Variabel berikut diisi dengan nilai 'Tidak Diketahui'. Sistem mengunci nilainya pada multiplier netral (1.00) demi keadilan evaluasi. Tanda (*) menunjukkan fitur signifikan.</p>
                        <p style="color: #1F2937; font-size: 0.875rem; font-weight: 350; font-family: monospace; margin: 0;">
                            {", ".join(xai_unknown_with_stars)}
                        </p>
                    </div>
                    """
                    st.markdown(html_unknown, unsafe_allow_html=True)
                
                st.space()
                if modifiable_risk_factors:
                    st.markdown(" ")
                    st.markdown("#### 📋 Rekomendasi Intervensi Modifiable Risk Factors")
                    st.markdown("<p style='color: #6B7280;'>Berikut adalah rekomendasi intervensi yang dapat diambil untuk meminimalkan pemicu risiko peritonitis.</p>", unsafe_allow_html=True)
                    for mrf in modifiable_risk_factors:
                        penjelasan = mrf_explanations.get(mrf, "Perlu konsultasi lebih lanjut dengan Dokter Spesialis Anak.")
                        with st.expander(f"**{mrf}**"): st.markdown(penjelasan)

                # ==============================================================================
                # SINKRONISASI DATABASE & ME-RECORD FILE DONWLOAD
                # ==============================================================================
                id_anonim = save_prediction(
                    raw_choices_for_log, 
                    score_mult_fixed, 
                    score_mult_rand, 
                    score_wa_base, 
                    score_wa_opt, 
                    status, 
                    "Peritonitis", 
                    xai_supporting_non_peritonitis, 
                    xai_supporting_peritonitis, 
                    modifiable_risk_factors, 
                    mrf_explanations
                )
                
                mrf_advice_text = " | ".join(mrf_text_logs) if mrf_text_logs else "Tidak ada intervensi MRF aktif."
                
                data_download = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Patient_ID": id_anonim,
                    "Age": raw_choices_for_log.get("Age", "Tidak Diketahui"),
                    "Gender": raw_choices_for_log.get("Gender", "Tidak Diketahui"),
                    "Duration of PD": raw_choices_for_log.get("Duration of PD", "Tidak Diketahui"),
                    "Place of Residence": raw_choices_for_log.get("Place of Residence", "Tidak Diketahui"),
                    "Housing": raw_choices_for_log.get("Housing", "Tidak Diketahui"),
                    "Socioeconomic": raw_choices_for_log.get("Socioeconomic", "Tidak Diketahui"),
                    "Education": raw_choices_for_log.get("Education", "Tidak Diketahui"),
                    "Peritonitis in ESI": raw_choices_for_log.get("Peritonitis in ESI", "Tidak Diketahui"),
                    "Nutrition": raw_choices_for_log.get("Nutrition", "Tidak Diketahui"),
                    "Cause of ESRD": raw_choices_for_log.get("Cause of ESRD", "Tidak Diketahui"),
                    "Type of Catheter (Shape)": raw_choices_for_log.get("Type of Catheter (Shape)", "Tidak Diketahui"),
                    "Type of Catheter (Cuff)": raw_choices_for_log.get("Type of Catheter (Cuff)", "Tidak Diketahui"),
                    "Catheter Placement": raw_choices_for_log.get("Catheter Placement", "Tidak Diketahui"),
                    "Gastrostomy/Intraperitoneal Device": raw_choices_for_log.get("Gastrostomy/Intraperitoneal Device", "Tidak Diketahui"),
                    "Performed CAPD": raw_choices_for_log.get("Performed CAPD", "Tidak Diketahui"),
                    "Starting PD <2 weeks after PD catheter placement": raw_choices_for_log.get("Starting PD <2 weeks after PD catheter placement", "Tidak Diketahui"),
                    "Catheter Orientation": raw_choices_for_log.get("Catheter Orientation", "Tidak Diketahui"),
                    "Stunting": raw_choices_for_log.get("Stunting", "Tidak Diketahui"),
                    "Outcome_Category": status,
                    "Peritonitis_Risk_Rate_Fixed_RR": f"{score_mult_fixed:.2f}%",
                    "Peritonitis_Risk_Rate_Randomized_RR": f"{score_mult_rand:.2f}%",
                    "Peritonitis_Risk_Rate_Weighted_Average": f"{score_wa_base:.2f}%",
                    "Peritonitis_Risk_Rate_Weighted_Average_Opt": f"{score_wa_opt:.2f}%",
                    "protective_factors": ", ".join(xai_supporting_non_peritonitis) if xai_supporting_non_peritonitis else "",
                    "risk_factors": ", ".join(xai_supporting_peritonitis) if xai_supporting_peritonitis else "",
                    "Modifiable_Risk_Factors_Advice": mrf_advice_text
                }
                
                st.markdown("---")
                st.download_button(
                    label=f"**💾 Download Hasil Prediksi** (ID Pasien: {id_anonim})", 
                    data=pd.DataFrame([data_download]).to_csv(index=False).encode('utf-8'), 
                    file_name=f"Hasil_Peritonitis_{id_anonim}.csv", 
                    mime="text/csv", 
                    use_container_width=True, 
                    type="primary"
                )

# ==============================================================================
# ============================= CRRT PREDICTION ================================
# ==============================================================================
elif selection == "CRRT Prediction":
    st.title("Survival Prediction Calculator for Pediatric CRRT")
    patient_name = st.text_input("Patient Name", placeholder="Enter patient name")
    date = datetime.now().strftime("%d-%m-%Y")

    variables = {
        "sex": {"label": "Sex", "default": "Male", "tag": "Sex"},
        "age": {"label": "Age (years)", "default": 5.7, "tag": "Age (Significant)"},
        "weight": {"label": "Weight (kg)", "default": 16.08, "tag": "Weight (Significant)"},
        "prism_score": {"label": "PRISM III Score *", "default": 14.02, "tag": "PRISM III Score (Significant)"},
        "vis": {"label": "Vasoactive-Inotropic Score *", "default": 9.36, "tag": "Vasoactive-Inotropic Score (Significant)"},
        "picu_stay": {"label": "PICU Stay (days)", "default": 13.5, "tag": "PICU Stay"},
        "ventilator": {"label": "Ventilator Usage *", "default": "No", "tag": "Ventilator Usage (Significant)"},
        "admss": {"label": "Interval from Admission (hours)", "default": 18.17, "tag": "Interval from Admission"},
        "crrt": {"label": "Duration of CRRT (days)", "default": 4.23, "tag": "Duration of CRRT (Significant)"},
        "fo": {"label": "Fluid Overload *", "default": "No", "tag": "Fluid Overload (Significant)"},
        "fo_at_crrt": {"label": "% FO at CRRT Initiation *", "default": 8.12, "tag": "% FO at CRRT Initiation (Significant)"},
        "ph": {"label": "pH Level *", "default": 7.33, "tag": "pH Level (Significant)"},
        "lactic": {"label": "Lactic Acid (mmol/L) *", "default": 2.24, "tag": "Lactic Acid"},
        "hb": {"label": "Hemoglobin (g/dL)", "default": 9.45, "tag": "Hemoglobin"},
        "platelet": {"label": "Platelet (103/µL)", "default": 109.54, "tag": "Platelet"},
        "urine_v": {"label": "Urine Volume (mL/Kg/h) *", "default": 0.9, "tag": "Urine Volume"},
        "sepsis": {"label": "Sepsis", "default": "No", "tag": "Sepsis (Significant)"},
        "alf": {"label": "Acute Liver Failure", "default": "No", "tag": "Acute Liver Failure (Significant)"},
        "rsd": {"label": "Respiratory System Disease *", "default": "No", "tag": "Respiratory System Disease (Significant)"},
        "albumin": {"label": "Albumin (g/dL) *", "default": 3.05, "tag": "Albumin (Significant)"},
        "kreatinin": {"label": "Creatinine (mg/dL)", "default": 1.5, "tag": "Creatinine (Significant)"},
        "pelod": {"label": "PELOD Score *", "default": 12.22, "tag": "PELOD Score (Significant)"},
        "psofa": {"label": "pSOFA Score *", "default": 9.56, "tag": "pSOFA Score (Significant)"},
        "bicarbonate": {"label": "Bicarbonate (mmEq/L)", "default": 21.7, "tag": "Bicarbonate"},
        "sodium": {"label": "Sodium (mmol/L)", "default": 138.72, "tag": "Sodium (Significant)"},
        "potassium": {"label": "Potassium (mmol/L)", "default": 3.61, "tag": "Potassium"},
        "tls": {"label": "Tumor Lysis Syndrome", "default": "Yes", "tag": "Tumor Lysis Syndrome"},
        "hyperammonemia": {"label": "Hyperammonemia", "default": "Yes", "tag": "Hyperammonemia"}
    }

    categorical_options = {"sex": ["Male", "Female"], "ventilator": ["Yes", "No"], "fo": ["Yes", "No"], "sepsis": ["Yes", "No"], "alf": ["Yes", "No"], "rsd": ["Yes", "No"], "tls": ["Yes", "No"], "hyperammonemia": ["Yes", "No"]}
    significant_variables = ["age", "weight", "prism_score", "vis", "ventilator", "crrt", "fo", "fo_at_crrt", "ph", "sepsis", "alf", "rsd", "albumin", "kreatinin", "pelod", "psofa", "sodium"]
    higher_or_equal_variables = ["ph", "platelet", "urine_v", "albumin", "bicarbonate", "potassium"]

    with st.container():
        col1, col2 = st.columns(2)
        user_data = {}
        with col1:
            for i, (var, props) in enumerate(variables.items()):
                if i % 2 == 0:
                    if var in categorical_options: user_data[var] = st.selectbox(f"{props['label']}", ["Tidak Diketahui"] + list(categorical_options[var]), index=0, key=f"crrt_select_{var}_{i}")
                    else: user_data[var] = st.number_input(f"{props['label']}", step=0.1, value=None, format="%.2f")
        with col2:
            for i, (var, props) in enumerate(variables.items()):
                if i % 2 != 0:
                    if var in categorical_options: user_data[var] = st.selectbox(f"{props['label']}", ["Tidak Diketahui"] + list(categorical_options[var]), index=0, key=f"crrt_select_{var}_{i}")
                    else: user_data[var] = st.number_input(f"{props['label']}", step=0.1, value=None, format="%.2f")

    st.markdown(" ")
    if st.button("Calculate CRRT Survival", type="primary"):
        total_variables = 0
        within_limit = 0
        within_limit_vars = []

        for var, props in variables.items():
            value = user_data[var]
            upper_limit = props['default']
            if value is not None and value != "Tidak Diketahui":
                if var in categorical_options:
                    total_variables += 1
                    if var in significant_variables: total_variables += 1
                    if value == upper_limit:
                        within_limit += 1
                        within_limit_vars.append(props['tag'])
                        if var in significant_variables: within_limit += 1
                else:
                    total_variables += 1
                    if var in significant_variables: total_variables += 1  
                    if var in higher_or_equal_variables:
                        if value >= upper_limit:
                            within_limit += 1
                            within_limit_vars.append(props['tag'])
                            if var in significant_variables: within_limit += 1
                    else:
                        if value <= upper_limit:
                            within_limit += 1
                            within_limit_vars.append(props['tag'])
                            if var in significant_variables: within_limit += 1

        if total_variables > 0:
            final_score = (within_limit / total_variables) * 100
            outcome = "Survivor" if final_score >= 50 else "Non-Survivor"
            user_data["Nama Pasien"] = patient_name 

            if final_score >= 50: st.success(f"The survival probability score is: {final_score:.2f}%")
            else: st.error(f"The survival probability score is: {final_score:.2f}%")
            
            st.info(f"Variables within the survivor criteria: ({', '.join(within_limit_vars)})")
            id_anonim = save_prediction(
                user_data,
                final_score,
                0.0,
                0.0,
                0.0,
                outcome,
                "CRRT"
            )

            data_download = {"Date": date, "Patient_ID": id_anonim, "Survival_Probability": f"{final_score:.2f}%", "Outcome": outcome, **{k: v for k, v in user_data.items() if k != "Nama Pasien"}}
            st.download_button(label=f"💾 Download Hasil Prediksi CRRT ({id_anonim})", data=pd.DataFrame([data_download]).to_csv(index=False).encode('utf-8'), file_name=f"Hasil_CRRT_{id_anonim}.csv", mime="text/csv", use_container_width=True)
        else:
            st.warning("No variables included in the calculation.")