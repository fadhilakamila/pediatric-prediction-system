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
@st.cache_data(ttl=600)
def load_data(module_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=module_name)
        
        if df is not None:
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
        return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari database: {e}")
        return pd.DataFrame()

# === simpan ke excel (database lokal)  GSheets (database utama/cloud) ===
def save_prediction(user_selections, survival_rate, outcome, module_name, supporting_factors=None, risk_factors=None, mrf_list=None, mrf_dict=None):
    
    file_path = 'PeritonitisPrediction_Database.xlsx' if module_name == "Peritonitis" else 'PredictCRRTforKids_Database.xlsx'
    tz_jkt = pytz.timezone('Asia/Jakarta')
    timestamp = datetime.now(pytz.utc).astimezone(tz_jkt).strftime("%Y-%m-%d %H:%M:%S")
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

        if st.session_state.get("password_correct") == False:
            st.error("Username atau password salah.")

        if st.session_state.get("logout_success"):
            st.success("Anda berhasil logout.")
            del st.session_state["logout_success"]
            
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
    
    st.markdown("<br>", unsafe_allow_html=True)

    # === LOGOUT ===
    if st.button("Log out", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        if "password_correct" in st.session_state:
            del st.session_state["password_correct"]
        st.session_state["logout_success"] = True
        st.toast("Anda berhasil logout!")
        import time
        time.sleep(2.5)
        st.rerun()

    st.sidebar.markdown(f"""
    <div style="
        background-color: #e8f0fe; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #1a73e8;
        color: #1a73e8;
        font-size: 0.9rem;
        line-height: 1.3;
    ">
        <strong>⚠️ Peringatan</strong><br>
        Sistem ini dikembangkan menggunakan pengetahuan dari meta-analisis studi peritonitis pediatri.<br>
        Aplikasi ini berfungsi sebagai alat bantu dan bukan pengganti keputusan akhir dari Dokter Spesialis Anak Konsultan Nefrologi.
    </div>
    """, unsafe_allow_html=True) 
    
    st.markdown("<br>", unsafe_allow_html=True)

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
        {"label": "Starting PD <2 weeks after catheter placement", "non-peritonitis": "No", "peritonitis": "Yes", "p_val": 0.23, "rr": 1.37, "mrf": True},
        {"label": "Catheter Orientation", "non-peritonitis": "Lateral/downward", "peritonitis": "upward", "p_val": 0.12, "rr": 0.66, "mrf": True},
        {"label": "Stunting", "non-peritonitis": "No stunting", "peritonitis": "Stunting", "p_val": 0.32, "rr": 0.72, "mrf": True},
    ]

    # 🔗
    mrf_explanations = {
        "Housing": "Lingkungan rumah harus diadaptasi untuk memenuhi standar prosedur medis. Ruangan yang digunakan untuk pertukaran cairan harus bersih dan bebas debu untuk meminimalkan risiko infeksi, sebab partikel debu dapat menjadi vektor bagi patogen udara yang dapat mengontaminasi set transfer saat prosedur koneksi atau diskoneksi. Penyediaan wastafel di dalam atau dekat ruangan dialisis diperlukan untuk memastikan kepatuhan protokol antiseptic tangan sehingga menurunkan insiden peritonitis akibat touch contamination. Pencahayaan yang optimal di dalam ruangan diperlukan agar caregiver dapat memantau kejernihan cairan efluen serta memeriksa kondisi tempat keluar kateter dengan teliti. Hewan peliharaan tidak boleh berada di area perawatan saat proses koneksi atau diskoneksi berlangsung karena risiko paparan bakteri seperti Pasteurella multocida atau kerusakan fisik pada selang dialisis akibat gigitan atau cakaran. Selain itu, caregiverharus ditekankan untuk selalu mencuci tangan setelah berinteraksi dengan hewan dan sebelum memulai prosedur dialisis. [Sumber 1](https://www.freseniuskidneycare.com/treatment/home-dialysis/getting-prepared) [Sumber 2](https://www.ouh.nhs.uk/media/agxhnni2/85713pdialysis.pdf) [Sumber 3](https://www.kidney.org/kidney-topics/preparing-home-dialysis) [Sumber 4](https://spnp-spp.pt/media/rqdpbrom/catheter-related-infections-and-peritonitis-in-pediatric-patients-receiving-peritoneal-dialysis-guideline-for-prevention-and-treatment-2012-1-_compressed-1.pdf) [Sumber 5](https://freseniusmedicalcare.com/content/dam/home-products-education/steps2home-pd/Preventing_Peritonitis.pdf) [Sumber 6](https://www.satellitehealthcare.com/blog/pets-and-peritoneal-dialysis-absolutely/)",
        "Nutrition": "Malnutrisi protein-kalori (cachexia) adalah masalah umum pada anak yang menjalani PD. Manajemen nutrisi bertujuan untuk mengejar pertumbuhan dan mengganti hilangnya protein serta asam amino ke dalam cairan dialysis.Penilaian status nutrisi harus dilakukan secara berkala, minimal setiap bulan pada bayi dan 3-4 bulan pada anak yang lebih tua, menggunakan parameter antropometri (berat badan, tinggi badan, lingkar kepala), biokimia (albumin urea), dan analisis bioimpedansi jika tersedia. Penanganannya juga harus multidisiplin dan mencakup memastikan asupan energi dan protein yang adekuat; kontrol metabolik yang optimal, dengan koreksi asidosis, anemia, dan hiperparatiroidisme; dosis dialisis yang optimal (atau setidaknya adekuat); dan, jika perlu, pemberian obat-obatan tertentu seperti hormon pertumbuhan manusia rekombinan. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/)",
        "Socioeconomic": "Deprivasi sosioekonomi berdampak pada hasil treatment yang lebih buruk. Hal ini kemungkinan disebabkan oleh keterbatasan akses terhadap fasilitas sanitasi yang memadai, tekanan psikologis pada pengasuh, serta keterbatasan informasi medis. Strategi bisa dilakukan melalui program pelatihan bagi keluarga (caregiver) dari perawat dialisis yang berpengalaman. Bagi keluarga dengan keterbatasan pendidikan atau ekonomi, dukungan teknis telepon 24 jam dan kunjungan rumah secara berkala oleh tim medis sosial sangat efektif dalam memastikan kepatuhan terhadap prosedur aseptik. Pelatihan ulang sangat dianjurkan, terutama setelah terjadinya peritonitis, untuk mengidentifikasi adanya penyimpangan dalam teknik pertukaran cairan. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC11835194/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC4934433/) [Sumber 3](https://pubmed.ncbi.nlm.nih.gov/23226378/) [Sumber 4](https://pubmed.ncbi.nlm.nih.gov/16091376/) [Sumber 6](https://spnp-spp.pt/media/rqdpbrom/catheter-related-infections-and-peritonitis-in-pediatric-patients-receiving-peritoneal-dialysis-guideline-for-prevention-and-treatment-2012-1-_compressed-1.pdf) [Sumber 7](https://pmc.ncbi.nlm.nih.gov/articles/PMC5691857/) [Sumber 8](https://pmc.ncbi.nlm.nih.gov/articles/PMC4335934/) [Sumber 9](https://www.kidney.org/kidney-topics/preparing-home-dialysis)",
        "Performed CAPD": "Tidak ada perbedaan yang signifikan dalam tingkat kelangsungan hidup teknik, kematian, maupun episode peritonitis antara dialisis yang dilakukan sendiri oleh pasien (self-care) dengan dialisis yang dibantu oleh keluarga atau pengasuh (assisted/home-care). Namun, pada populasi anak (khususnya balita atau anak dengan keterbatasan fisik/kognitif), peran orang tua (Parent/Others) sangat mutlak diperlukan. Bagi orang tua yang memiliki tingkat pendidikan rendah atau keterbatasan ekonomi, dialisis tetap dapat berhasil dengan baik tanpa komplikasi besar asalkan diberikan pelatihan intensif secara 1:1, dukungan telepon 24 jam, dan kunjungan rumah berkala oleh perawat dialisis berpengalaman. Di sisi lain, bagi pasien remaja yang melakukan dialisis secara mandiri (Patient), tantangan psikososial seperti kejenuhan (burnout), perasaan terkekang (slavery feeling), dan depresi sering kali muncul, sehingga membutuhkan pengawasan ketat dari tim medis agar kepatuhan terhadap prosedur aseptik tetap terjaga. [Sumber 1](https://pubmed.ncbi.nlm.nih.gov/29456210/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC4335934/) [Sumber 3](https://www.ispd.org/wp-content/uploads/2025/12/Assisted-PD-PP-2024-with-VA_formatted.pdf)",
        "Gastronomy Device": "Keberadaan perangkat gastrostomi secara signifikan meningkatkan risiko infeksi, terutama peritonitis fungal dan peritonitis bakteri akibat translokasi kuman serta kontaminasi silang. Bagi anak yang memerlukan gastrostomi, sangat disarankan agar pemasangannya direncanakan secara matang dan dilakukan sebelum atau bersamaan dengan pemasangan kateter dialisis peritoneal ('PEG before PD'). Apabila gastrostomi (seperti PEG) terpaksa dipasang setelah dialisis peritoneal berjalan, beberapa protokol pencegahan infeksi wajib diterapkan, seperti memberikan profilaksis antibiotik dan antijamur, menghentikan sementara prosedur dialisis peritoneal selama 2–3 hari pasca-operasi (pasien dialihkan sementara ke hemodialisis jika diperlukan), serta memastikan lokasi keluar kateter dialisis diletakkan sejauh mungkin dari area gastrostomi untuk menghindari kontaminasi silang. [Sumber 1](https://www.researchgate.net/publication/7239515_Percutaneous_Endoscopic_Gastrostomy_in_Children_on_Peritoneal_Dialysis) [Sumber 2](https://ajkdblog.org/2014/08/11/pd-in-patients-with-gastrostomy-tubes-vice-versa-challenging-but-doable/) [Sumber 3](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Catheter Orientation": "Posisi atau arah lubang keluar kateter (exit site) sangat memengaruhi risiko terjadinya infeksi. Data multisentrik dari SCOPE Collaborative menunjukkan bahwa orientasi kateter yang menghadap ke atas (Upward) dikaitkan dengan peningkatan risiko peritonitis hingga 4.2 kali lipat (Rate Ratio: 4.2; 95% CI: 1.49–11.89) dibandingkan orientasi lainnya. Secara anatomis, lubang keluar yang menghadap ke atas menciptakan bentuk cekungan yang dapat menampung keringat, air mandi, dan kotoran. Akibat gaya gravitasi, bakteri yang terkumpul di area ini akan mengendap dan bermigrasi ke dalam terowongan kateter. Oleh karena itu, lubang keluar kateter harus selalu diarahkan ke bawah (Downward) atau ke samping (Lateral) untuk mencegah penumpukan bakteri secara alami. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC5012476/) [Sumber 2](https://openurologyandnephrologyjournal.com/VOLUME/5/PAGE/4/) [Sumber 3](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Stunting": "Stunting pada anak dialisis bukan hanya disebabkan oleh asupan kalori yang rendah, tetapi juga oleh asidosis metabolik, anemia, osteodistrofi ginjal, dan resistensi terhadap hormon pertumbuhan. Intervensi pertama adalah memastikan kecukupan dialisis dan koreksi parameter metabolik seperti asidosis dan hiperparatiroidisme.Jika pertumbuhan masih belum optimal meskipun parameter metabolik telah terkendali dan asupan nutrisi sudah mencapai target, terapi dengan hormon pertumbuhan manusia rekombinan (rhGH) dapat dipertimbangkan. Selain itu, dukungan nutrisi intensif dan klirens dialisis yang adekuat pada pasien prepubertal dapat mempromosikan pertumbuhan normal tanpa selalu memerlukan rhGH. Pada anak yang mengalami stunting (tinggi badan < persentil ke-2), perhitungan kebutuhan energi dan mikronutrien harus didasarkan pada height-age pasien, bukan chronological age-nya, untuk memberikan dukungan yang sesuai dengan ukuran tubuh aktualnya. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC6904418/)",
        "Starting PD <2 weeks after catheter placement": "Waktu antara pemasangan kateter dan dimulainya dialisis (break-in-period) merupakan faktor penting untuk mencegah komplikasi. Masa penyembuhan minimal 2 minggu sebelum dialysis dimulai. Namun, dalam kondisi klinis tertentu di mana pasien membutuhkan dialisis segera, urgent-start PD (dimulai dalam <14 hari atau bahkan <48 jam) menjadi alternatif yang baik untuk menghindari penggunakan kateter hemodialysis sementara. Pasien dengan break-in-period < 7 hari memiliki risiko yang lebih tinggi terhadap komplikasi awal seperti kebocoran dialisat dan malposisi kateter. Namun, risiko tersebut tidak berkorelasi dengan penurunan kelangsungan hidup atau peningkatan risiko peritonitis jika dilakukan dengan protokol yang tepat. Pada kondisi urgent-start, risiko kebocoran dimitigasi dengan menggunakan volume pengisian rendah (10-20 ml/kg) dan posisi pasien supine untuk mengurangi tekanan intra-abdominal.[Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC3923692/) [Sumber 2](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206426) [Sumber 3](https://www.sages.org/publications/guidelines/peritoneal-dialysis-access-guideline-update-2023/) [Sumber 4](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2022.936573/full) [Sumber 5](https://scholarlyexchange.childrensmercy.org/cgi/viewcontent.cgi?article=7522&context=papers) [Sumber 6](https://pubmed.ncbi.nlm.nih.gov/33523772/) [Sumber 7](https://www.bcrenal.ca/resource-gallery/Documents/PD_Procedures-Exit_Site_Care-Post-Operative_PD_Catheter_Insertion.pdf)",
        "Peritonitis in ESI": "Penggunaan antibiotik topikal secara rutin pada tempat keluar kateter telat terbukti menurunkan angka infeksi. Aplikasi harian salep mupirocin atau gentamicin pada exit-site direkomendasikan untuk menekan kolonisasi Staphylococcus aureus dan Pseudomonas aeruginosa.Pembersihan area secara rutin dengan larutan antiseptik non-iritan (seperti chlorhexidine 0,05% atau sabun antibakteri ringan) juga merupakan bagian standar dari perawatan. Penilaian kondisi exit-site secara objektif menggunakan sistem skor (seperti Skor ISPD yang mencakup pembengkakan, kerak, kemerahan, nyeri, dan sekret) sangat membantu caregiver dalam mendeteksi infeksi secara dini. Immobilisasi kateter dengan menggunakan plester atau perangkat fiksasi sangat krusial karena trauma mekanis pada tempat keluar sering kali menjadi pintu masuk bagi bakteri. Jika ESI terjadi, terapi antibiotik oral atau intraperitoneal harus dimulai segera dan dilanjutkan selama minimal 2 minggu, atau 3 minggu jika disebabkan oleh Pseudomonas. Pengangkatan kateter mungkin diperlukan jika infeksi bersifat refrakter (tidak merespons pengobatan setelah 2 minggu) atau jika infeksi telah menyebar ke terowongan kateter (tunnel infection) yang menyebabkan peritonitis berulang. [Sumber 1](https://ispd.org/wp-content/uploads/2025/09/LI-ET-1.pdf) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC12640025/) [Sumber 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC5033625/) [Sumber 4](https://www.chikd.org/journal/view.php?number=726) [Sumber 5](https://ispd.org/wp-content/uploads/ISPD-Catheter-related-Infection-Recommendations-2023-Update.pdf) [Sumber 6](https://www.bcrenal.ca/resource-gallery/Documents/PD_Procedures-Exit_Site_Care-Post-Operative_PD_Catheter_Insertion.pdf) [Sumber 7](https://davita.com/treatment-options/articles/preventing-catheter-infections-on-peritoneal-dialysis/) [Sumber 8](https://edren.org/ren/handbook/pd-handbook/protocol-for-the-management-of-pd-peritonitis-long-version/)",
        "Type of Catheter (Cuff)": "Penggunaan kateter dengan double-cuff lebih disarankan daripada single-cuff)untuk populasi anak secara umum. Deep cuff berfungsi untuk menjangkar kateter di otot rektus dan mencegah kebocoran, sementara superficial cuff bertindak sebagai penghalang fisik terhadap migrasi bakteri ke arah rongga peritoneum. Namun, pada neonatus atau bayi dengan dinding perut yang sangat tipis, kateter single-cuff sering kali lebih dipilih untuk mencegah ekstrusi manset ke permukaan kulit. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC10223083/) [Sumber 2](http://ispd.org/wp-content/uploads/7.-Dagmara-Borzych-Duzalka-Peritoneal-Dialysis-Catheters-Outcome-in-Children.-The-IPPN-Data.pdf) [Sumber 3](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Type of Catheter (Shape)": "Perdebatan mengenai efektivitas kateter straight dibandingkan dengan kateter coiled/curled masih berlangsung. Kateter coiled secara teoretis mengurangi nyeri saat pengisian cairan dan meminimalkan trauma pada organ visceral, tetapi beberapa data menunjukkan risiko malposisi yang lebih tinggi dibandingkan tipe lurus pada beberapa kelompok pasien. Di sisi lain, kateter straight lebih mudah ditempatkan pada bayi kecil yang memiliki ruang intra-abdominal terbatas. Secara keseluruhan, pedoman tidak menyatakan superioritas mutlak salah satu bentuk, dan pemilihan sering kali bergantung pada preferensi pusat dialisis dan anatomi pasien. [Sumber 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC9365012/) [Sumber 2](http://ispd.org/wp-content/uploads/7.-Dagmara-Borzych-Duzalka-Peritoneal-Dialysis-Catheters-Outcome-in-Children.-The-IPPN-Data.pdf) [Sumber 3](https://scholarlyexchange.childrensmercy.org/cgi/viewcontent.cgi?article=7522&context=papers) [Sumber 4](https://kidney.wiki/peritoneal-dialysis/pd-access/)",
        "Catheter Placement": "Pedoman klinis terbaru dari Society of American Gastrointestinal and Endoscopic Surgeons (SAGES) menyarankan penggunaan teknik laparoskopi tingkat lanjut (Laparoscopic) dibandingkan teknik bedah terbuka (Open) untuk pemasangan kateter pada populasi pediatrik. Laparoscopic menawarkan akurasi catheter placement yang jauh lebih tinggi di dalam rongga abdomen karena visualisasi langsung, serta meminimalkan trauma mekanis pada jaringan perut. Lebih lanjut, Laparoscopic memungkinkan dokter untuk melakukan prosedur profilaksis penting seperti omentektomi atau omentopeksi untuk meminimalkan risiko omental wrapping (penyumbatan kateter oleh omentum), yang merupakan salah satu penyebab utama kegagalan mekanis kateter pada anak-anak. Laparoscopic juga terbukti mempermudah penyelamatan (salvage) jika terjadi malposisi atau disfungsi kateter tanpa harus melakukan pembedahan ulang yang invasif. [Sumber 1](https://www.sages.org/publications/guidelines/peritoneal-dialysis-access-guideline-update-2023/) [Sumber 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC10223083/) [[3]](https://kidney.wiki/peritoneal-dialysis/pd-access/)"
    }

    def main():
        st.title("Prediksi Survival Rate Peritoneal Dialysis pada Pasien Anak")
        patient_name = st.text_input("Nama Pasien", placeholder="Masukkan nama...")
        
        # st.caption("ℹ️ Variabel dengan tanda bintang (*) memiliki pengaruh **signifikan** berdasarkan hasil meta-analisis.")
        st.markdown("#### Pilih Sesuai dengan Kondisi Pasien")

        significant_vars = ["Age", "Duration of PD", "Peritonitis in ESI", "Cause of ESRD"]
        
        survival_rate = None
        outcome = None
        xai_supporting_peritonitis = []
        xai_supporting_non_peritonitis = []
        modifiable_risk_factors = []
        mrf_full_text=""

        col1, col2 = st.columns(2)
        user_selections = {}

        for i, var in enumerate(variables_data):
            target_col = col1 if i < 9 else col2

            is_significant = "*" if var['label'] in significant_vars else ""
            label = f"{i+1}. {var['label']}{is_significant}"

            options = [var['non-peritonitis'], var['peritonitis']]
            choice = target_col.selectbox(label, options, index=0)
            user_selections[var['label']] = choice

        st.write("ℹ️ Variabel dengan tanda bintang (*) memiliki pengaruh **signifikan** berdasarkan hasil meta-analisis.")
        
        if st.button("Hitung Survival Rate"):
            if not patient_name:
                st.warning("Silakan masukkan nama pasien terlebih dahulu.")
                return

            user_selections["Nama Pasien"] = patient_name

            # === PERHITUNGAN WEIGHTED AVERAGE ===
            total_wi_xi = 0
            total_wi = 0

            for var in variables_data:
                # Bobot (wi)
                weight = 2 if var['p_val'] < 0.05 else 1
                
                # Nilai (xi)
                # x=1 jika pilihan user adalah peritonitis, x=0 jika non-peritonitis
                x_val = 1 if user_selections[var['label']] == var['peritonitis'] else 0
                
                total_wi_xi += (weight * x_val)
                total_wi += weight

                # === PERSIAPAN DATA XAI === 
                is_sig = "*" if var['label'] in significant_vars else ""
                display_label = f"{var['label']}{is_sig}"

                if x_val == 0:
                    xai_supporting_non_peritonitis.append(display_label)
                else:
                    xai_supporting_peritonitis.append(display_label)

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
    
            st.caption("ℹ️ Variabel dengan tanda bintang (*) memiliki pengaruh signifikan berdasarkan hasil meta-analisis.")

            if modifiable_risk_factors:
                st.markdown("##### Modifiable Risk Factors (MRF)")
                st.write("Berikut adalah rekomendasi intervensi yang dapat diambil untuk meningkatkan peluang survival")

            for mrf in modifiable_risk_factors:
                penjelasan = mrf_explanations.get(mrf, "Perlu konsultasi lebih lanjut dengan Dokter Spesialis Anak Konsultan Nefrologi.")
                
                with st.expander(f"**{mrf}**"):
                    st.markdown(penjelasan) 

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
                
            st.space()

            st.download_button(
                label=f"**Download Hasil Prediksi** (ID Pasien: **{id_anonim}**)",
                data=df_single_patient.to_csv(index=False).encode('utf-8'),
                file_name=f"Hasil_Prediksi_Peritonitis_{id_anonim}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_button",
                icon=":material/download:"
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
                key=f"crrt_prediction_{id_anonim}",
                icon=":material/download:"
            )
            
            st.cache_data.clear()
        else:
            st.warning("No variables included in the calculation.")