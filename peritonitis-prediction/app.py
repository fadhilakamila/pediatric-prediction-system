"""
TA | Peritonitis Prediction Calculator
"""
import streamlit as st
import pandas as pd
import hmac
import hashlib
from datetime import datetime
import os
import streamlit_shadcn_ui as ui
from streamlit_option_menu import option_menu
from streamlit_gsheets import GSheetsConnection
import pytz

# === CACHE (data loading) ===
@st.cache_data
def load_data(module):

    file_path = 'PeritonitisPrediction_Database.xlsx' if module == "Peritonitis" else 'PredictCRRTforKids_Database.xlsx'

    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca data: {e}")
        return pd.DataFrame()

# === simpan ke excel (database lokal)  GSheets (database utama/cloud) ===
def save_prediction(user_selections, survival_rate, outcome, module_name, supporting_factors=None, risk_factors=None, mrf_list=None, mrf_dict=None):
    
    file_path = 'PeritonitisPrediction_Database.xlsx' if module_name == "Peritonitis" else 'PredictCRRTforKids_Database.xlsx'
    tz_jkt = pytz.timezone('Asia/Jakarta')
    timestamp = datetime.now(tz_jkt).strftime("%Y-%m-%d %H:%M:%S")
    raw_name = user_selections.get("Nama Pasien", "Unknown")
    patient_id = hashlib.sha256(raw_name.encode()).hexdigest()[:8].upper() # ID unik = hash nama + waktu
    
    new_data = {
        "Module": module_name,
        "Timestamp": timestamp,
        "Patient_ID": patient_id
    }

    for label, value in user_selections.items():
        if label != "Nama Pasien":
            new_data[label] = value 

    if module_name == "Peritonitis":
        mrf_full_text = ""
        if mrf_list and mrf_dict:
            mrf_full_text = " | ".join([f"{mrf}: {mrf_dict.get(mrf, '')}" for mrf in mrf_list])
        
        new_data["Survival Rate"] = f"{survival_rate:.2f}%"    
        new_data["Outcome"] = outcome
        new_data["Supporting_Factors"] = ", ".join(supporting_factors) if supporting_factors else ""
        new_data["Risk_Factors"] = ", ".join(risk_factors) if risk_factors else ""
        new_data["Modifiable_Risk_Factors_Advice"] = mrf_full_text
    else:
        new_data["survival probability"] = f"{survival_rate:.2f}%"
        new_data["Outcome"] = outcome
    
    new_df = pd.DataFrame([new_data])
    
    # 1. simpan ke excel (database lokal)
    try:
        if os.path.exists(file_path):
            existing_df = pd.read_excel(file_path)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            updated_df = new_df
        updated_df.to_excel(file_path, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan backup lokal: {e}")

    # 2. simpan ke google sheets (database cloud)
    try:
        # Inisialisasi koneksi (Membuka koneksi menggunakan secrets yang tadi dibuat)
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Baca data yang sudah ada di cloud (worksheet sesuai nama modul, yaitu sheets bernama "Peritonitis" dan "CRRT"
        existing_gsheet = conn.read(worksheet=module_name)
        
        # Jika sheet kosong, langsung gunakan data baru. Jika sheets sudah ada isinya, gabungkan.
        if existing_gsheet is not None and not existing_gsheet.empty:
            updated_gsheet = pd.concat([existing_gsheet, new_df], ignore_index=True)
        else:
            updated_gsheet = new_df
        
        # Update lagi data yang sudah di-update ke GSheets
        conn.update(worksheet=module_name, data=updated_gsheet)

    except Exception as e:
        # Jika internet mati, program tidak crash tapi memberi info
        st.warning(f"Gagal sinkronisasi ke Google Sheets (Mode Offline): {e}")

    return patient_id

# === PASSWORD ===
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

    st.markdown("<h1 style='text-align: center;'>Pediatric Prediction System</h1>", unsafe_allow_html=True)
    left_co, cent_co, last_co = st.columns([1, 2, 1])
    
    with cent_co:
        st.subheader("Login")
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Login", on_click=password_entered, use_container_width=True)

        if "password_correct" in st.session_state:
            st.error("Username atau password salah.")
            
    return False

# Konfigurasi Halaman
st.set_page_config(
    page_title="Pediatric Prediction System",
    page_icon="🔬",
    layout="wide"
)

if not check_password():
    st.stop()

# === SIDEBAR NAVIGATION ===
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
        <div style="line-height: 1.2; font-size: 0.9rem;">
            <p style="margin-bottom: 0px;">Developed by</p>
            <p style="margin-top: 0px; margin-bottom: 12px;"><b>{developer}</b></p>        
            <p style="margin-bottom: 0px;">Supervised by</p>
            <p style="margin-top: 0px; margin-bottom: 12px;"><b>Retno Aulia Vinarti, M.Kom., Ph.D.</b></p>
            <p style="margin-bottom: 0px;">Expert</p>
            <p style="margin-top: 0px; margin-bottom: 0px;"><b>dr. Reza Fahlevi, Sp.A(K)</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    st.space()

    # === LOGOUT ===
    if st.button("Log out", use_container_width=True, type="secondary"):
        st.session_state["password_correct"] = False
        st.rerun()
        st.success("Anda berhasil logout")

# === PERITONITIS PREDICTION ===
if selection == "Peritonitis Prediction":
    # --- KNOWLEDGE BASE (sesuai decision table) ---
    # x=1 jika mendukung Non-Survivor (Peritonitis), x=0 jika mendukung Survivor.
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
        {"label": "Starting PD <2 weeks after placement", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "rr": 1.37, "mrf": True},
        {"label": "Catheter Orientation", "non-peritonitis": "Lateral/downward", "peritonitis": "upward", "p_val": 0.12, "rr": 0.66, "mrf": True},
        {"label": "Stunting", "non-peritonitis": "No stunting", "peritonitis": "Stunting", "p_val": 0.32, "rr": 0.72, "mrf": True},
    ]

    mrf_explanations = {
        "Housing": "Perlu perbaikan sanitasi dan fasilitas lingkungan tempat tinggal untuk mengurangi risiko kontaminasi kuman dari lingkungan.",
        "Nutrition": "Perlu peningkatan asupan nutrisi dan pemantauan status gizi secara berkala oleh ahli gizi anak untuk mencapai status gizi normal.",
        "Socioeconomic": "Perlu dukungan biaya kesehatan atau bantuan pekerja sosial untuk memastikan kepatuhan terapi dan ketersediaan logistik dialisis.",
        "Performed CAPD": "Perlu pelatihan ulang yang intensif bagi orang yang melakukan dialisis (pasien/keluarga) mengenai prosedur aseptik yang benar.",
        "Gastronomy Device": "Perlu perawatan ekstra dan pembersihan ketat pada area lubang alat tambahan di perut untuk mencegah infeksi silang ke area kateter.",
        "Stunting": "Perlu optimalisasi pertumbuhan melalui dukungan nutrisi agresif atau terapi hormon pertumbuhan sesuai saran dokter.",
        "Starting PD <2 weeks after placement": "Sebaiknya menunda dimulainya dialisis (jika kondisi klinis memungkinkan) minimal 2 minggu setelah operasi agar luka kateter sembuh sempurna.",
        "Peritonitis in ESI": "Perlu penanganan agresif dan segera terhadap infeksi area keluar kateter (Exit Site Infection) agar kuman tidak masuk ke rongga perut.",
        "Type of Catheter (Cuff)": "Disarankan menggunakan kateter dengan 'Double Cuff' karena memberikan perlindungan ganda (barier bakteri) yang lebih baik.",
        "Type of Catheter (Shape)": "Penggunaan kateter berbentuk 'Coiled' atau 'Swan-neck' lebih disarankan untuk mengurangi risiko kateter berpindah posisi (displacement).",
        "Catheter Placement": "Berdasarkan hasil meta-analisis, metode 'Open' pada populasi ini menunjukkan kecenderungan risiko peritonitis yang lebih rendah dibandingkan 'Laparoscopic'. Konsultasikan untuk teknik yang paling sesuai."
    }

    def main():
        st.title("Prediksi Survival Rate Pasien Pediatri Peritoneal Dialysis")
        st.markdown("---")
        st.markdown("#### Masukkan Kondisi Klinis Pasien!")
        patient_name = st.text_input("Nama Pasien", placeholder="Masukkan nama...")
        
        col1, col2 = st.columns(2)
        user_selections = {}

        for i, var in enumerate(variables_data):
            target_col = col1 if i < 9 else col2
            label = f"{i+1}. {var['label']}"
            options = [var['non-peritonitis'], var['peritonitis']]
            
            choice = target_col.selectbox(label, options, index=0)
            user_selections[var['label']] = choice

        if st.button("Hitung Survival Rate"):
            if not patient_name:
                st.warning("Silakan masukkan nama pasien terlebih dahulu.")
                return

            user_selections["Nama Pasien"] = patient_name

            # === PERHITUNGAN WEIGHTED AVERAGE ===
            total_wi_xi = 0
            total_wi = 0
            
            xai_supporting_non_peritonitis = []
            xai_supporting_peritonitis = []
            modifiable_risk_factors = []

            for var in variables_data:
                # Bobot (wi)
                weight = 2 if var['p_val'] < 0.05 else 1
                
                # Nilai (xi)
                # x=1 jika pilihan user adalah peritonitis, x=0 jika non-peritonitis
                x_val = 1 if user_selections[var['label']] == var['peritonitis'] else 0
                
                total_wi_xi += (weight * x_val)
                total_wi += weight

                # === PERSIAPAN DATA XAI === 
                if x_val == 0:
                    xai_supporting_non_peritonitis.append(var['label'])
                else:
                    xai_supporting_peritonitis.append(var['label'])

                if var['mrf'] and x_val == 1:
                    modifiable_risk_factors.append(var['label'])

            # Rumus Kejadian Peritonitis
            kejadian_peritonitis = total_wi_xi / total_wi
            # Rumus Survival Rate (SR)
            survival_rate = (1 - kejadian_peritonitis) * 100
            
            st.markdown("---")

            # === Hasil Prediksi ===
            if survival_rate >= 50:
                color_code = "#22c55e"
                status_label = "🟢SURVIVOR"
                status_text = "≥ 50%"
                outcome = "Survivor"
            else:
                color_code = "#f97316"
                status_label = "🟠NON-SURVIVOR"
                status_text = "< 50%"
                outcome = "Non-Survivor"
            
            st.markdown(f"""
                <div style="line-height: 1.0;">
                    <h3 style="margin-bottom: 4px; padding-bottom: 0px;">Hasil Prediksi <i>{patient_name}</i></h3>
                    <h1 style="color: {color_code}; margin-top: 0px; margin-bottom: 4px; padding: 0px; font-weight: bold;">{survival_rate:.2f}%</h1>
                    <p style="margin-top: 0px; font-size: 0.85rem; color: gray; font-style: italic;">
                        Pasien dikategorikan sebagai <b>{status_label}</b> karena Survival Rate {status_text}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            expl_col1, expl_col2 = st.columns(2)

            with expl_col1:
                with ui.card(key="card_survival"):
                    ui.element("span", children=["Faktor Pendukung Survival"], className="text-black text-sm font-bold m-1", key="label_surv")
                    ui.element("p", children=["Variabel dengan Risk Ratio (RR) < 1"], className="text-gray-400 text-xs m-1", key="desc_surv")
                    
                    if xai_supporting_non_peritonitis:
                        for idx, item in enumerate(xai_supporting_non_peritonitis):
                            ui.element("p", children=[f"• {item}"], className="text-sm text-gray-700 m-1", key=f"list_surv{idx}")
                    else:
                        ui.element("p", children=["Tidak ada faktor spesifik."], className="text-sm text-gray-400 m-1", key="none_surv")

            with expl_col2:
                with ui.card(key="card_risk"):
                    ui.element("span", children=["Faktor Penyebab Peritonitis"], className="text-black text-sm font-bold m-1", key="label_risk")
                    ui.element("p", children=["Variabel dengan Risk Ratio (RR) > 1"], className="text-gray-400 text-xs m-1", key="desc_risk")
                    
                    if xai_supporting_peritonitis:
                        for idx, item in enumerate(xai_supporting_peritonitis):
                            ui.element("p", children=[f"• {item}"], className="text-sm text-gray-700 m-1", key=f"list_risk{idx}")
                    else:
                        ui.element("p", children=["Risiko terpantau rendah."], className="text-sm text-gray-400 m-1", key="none_risk")

            if modifiable_risk_factors:
                st.markdown("##### Modifiable Risk Factors (MRF)")
                st.write("Berikut adalah rekomendasi intervensi yang dapat diambil untuk meningkatkan peluang survival")
                
                mrf_full_text = " | ".join([f"{mrf}: {mrf_explanations.get(mrf, '')}" for mrf in modifiable_risk_factors])

                accordion_data = []
                for mrf in modifiable_risk_factors:
                    penjelasan = mrf_explanations.get(mrf, "Perlu konsultasi lebih lanjut dengan dokter spesialis.")
                    accordion_data.append({
                        "trigger": f"{mrf}", 
                        "content": penjelasan
                    })
                
                if accordion_data:
                    ui.accordion(data=accordion_data, key="mrf_accordion")
            else:
                mrf_full_text = ""

            # === simpan log ke excel ===
            id_anonim = save_prediction(
                user_selections,
                survival_rate,
                outcome,
                "Peritonitis",
                supporting_factors=xai_supporting_non_peritonitis,
                risk_factors=xai_supporting_peritonitis,
                mrf_list=modifiable_risk_factors,
                mrf_dict=mrf_explanations
            )
            
            st.cache_data.clear()

            # === Download Data ===
            data_single_patient = {
                "Module": "Peritonitis",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Patient_ID": id_anonim,
                **{k: v for k, v in user_selections.items() if k != "Nama Pasien"},
                "Survival_Rate": f"{survival_rate:.2f}%",
                "Outcome": outcome,
                "Supporting_Factors": ", ".join(xai_supporting_non_peritonitis) if xai_supporting_non_peritonitis else "",
                "Risk_Factors": ", ".join(xai_supporting_peritonitis) if xai_supporting_peritonitis else "",
                "Modifiable_Risk_Factors_Advice": mrf_full_text
            }
            
            if "Nama Pasien" in data_single_patient:
                del data_single_patient["Nama Pasien"]
            
            df_single_patient = pd.DataFrame([data_single_patient])
                
            st.download_button(
                label=f"**Download Hasil Prediksi** (ID Pasien: **{id_anonim}**)",
                data=df_single_patient.to_csv(index=False).encode('utf-8'),
                file_name=f"Hasil_Prediksi_Peritonitis_{id_anonim}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_button"
            )

            st.caption("⚠️*Sesuai protokol etik, nama pasien telah dianonimkan dalam database.*")

    if __name__ == "__main__":
        main()

elif selection == "CRRT Prediction":
    
    st.title("Survival Prediction Calculator for Pediatric CRRT")

    patient_name = st.text_input("Patient Name")
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

    categorical_options = {
        "sex": ["Male", "Female"],
        "ventilator": ["Yes", "No"],
        "fo": ["Yes", "No"],
        "sepsis": ["Yes", "No"],
        "alf": ["Yes", "No"],
        "rsd": ["Yes", "No"],
        "tls": ["Yes", "No"],
        "hyperammonemia": ["Yes", "No"]
    }

    significant_variables = ["age", "weight", "prism_score", "vis", "ventilator", "crrt", "fo", "fo_at_crrt", "ph", "sepsis", "alf", "rsd", "albumin", "kreatinin", "pelod", "psofa", "sodium"]

    higher_or_equal_variables = ["ph", "platelet", "urine_v", "albumin", "bicarbonate", "potassium"]

    col1, col2 = st.columns(2)

    user_data = {}
    with col1:
        for i, (var, props) in enumerate(variables.items()):
            if i % 2 == 0: 
                if var in categorical_options:
                    user_data[var] = st.selectbox(f"{props['label']}", categorical_options[var], index=None)
                else:
                    user_data[var] = st.number_input(f"{props['label']}",step=0.1, value=None, format="%.2f")
    with col2:
        for i, (var, props) in enumerate(variables.items()):
            if i % 2 != 0: 
                if var in categorical_options:
                    user_data[var] = st.selectbox(f"{props['label']}", categorical_options[var], index=None)
                else:
                    user_data[var] = st.number_input(f"{props['label']}",step=0.1, value=None, format="%.2f")

    if st.button("Calculate"):
        total_variables = 0
        within_limit = 0
        within_limit_vars = []

        for var, props in variables.items():
            value = user_data[var]
            upper_limit = props['default']
            if value is not None:
                if var in categorical_options:
                    total_variables += 1
                    if var in significant_variables:
                        total_variables += 1
                    if value == upper_limit:
                        within_limit += 1
                        within_limit_vars.append(props['tag'])
                        if var in significant_variables:
                            within_limit += 1 
                else:
                    total_variables += 1
                    if var in significant_variables:
                        total_variables += 1  
                    if var in higher_or_equal_variables:
                        if value >= upper_limit:
                            within_limit += 1
                            within_limit_vars.append(props['tag'])
                            if var in significant_variables:
                                within_limit += 1
                    else:
                        if value <= upper_limit:
                            within_limit += 1
                            within_limit_vars.append(props['tag'])
                            if var in significant_variables:
                                within_limit += 1

        if total_variables > 0:
            final_score = (within_limit / total_variables) * 100
            outcome = "Survivor" if final_score >= 50 else "Non-Survivor"
            
            user_data["Nama Pasien"] = patient_name 

            if final_score >= 50:
                st.success(f"The survival probability score is: {final_score:.2f}%")
            else:
                st.error(f"The survival probability score is: {final_score:.2f}%")
            
            st.info(f"Variables within the survivor criteria: ({', '.join(within_limit_vars)})")

            id_anonim = save_prediction(user_data, final_score, outcome, "CRRT")
        
            data_download = {
                "Date": date,
                "Patient_ID": id_anonim,
                "Survival_Probability": f"{final_score:.2f}%",
                "Outcome": outcome,
                **{k: v for k, v in user_data.items() if k != "Nama Pasien"}
            }
            
            st.download_button(
                label=f"**Download Hasil Prediksi** (Patient_ID: **{id_anonim}**)",
                data=pd.DataFrame([data_download]).to_csv(index=False).encode('utf-8'),
                file_name=f"Hasil_Prediksi_CRRT_{id_anonim}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"crrt_prediction_{id_anonim}"
            )
            
            st.cache_data.clear()
        else:
            st.warning("No variables included in the calculation.")