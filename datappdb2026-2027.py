import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
from datetime import datetime

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 

# --- 2. FUNGSI KONEKSI GOOGLE SHEETS ---
@st.cache_resource
def init_google_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Gagal menyambungkan ke Google Sheets: {e}")
        return None

# --- 3. STANDARISASI KOLOM DATABASE ---
KOLOM_DATABASE = [
    "No. Registrasi", "Nama Lengkap", "NIK Siswa", "Tanggal Lahir", 
    "Jenis Kelamin", "Nama Ayah", "Nama Ibu", "Alamat Lengkap", 
    "Tanggal Daftar", "Status Verifikasi"
]

# --- 4. UI SETUP ---
st.set_page_config(page_title="PPDB AL IRSYAD KEDIRI", page_icon="🏫", layout="wide")

st.markdown("""
    <style>
    .main-header {text-align: center; background-color: #1E5128; padding: 25px; border-radius: 10px; color: white; margin-bottom: 25px;}
    .stButton>button {width: 100%; border-radius: 8px; height: 3.5em; background-color: #1E5128; color: white; font-weight: bold;}
    </style>
    <div class="main-header">
        <h1>SISTEM INFORMASI PPDB ONLINE</h1>
        <h3>KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI</h3>
    </div>
""", unsafe_allow_html=True)

client = init_google_sheets()
if not client: st.stop()

menu = st.sidebar.radio("NAVIGASI UTAMA", ["📝 Form Pendaftaran Siswa", "📊 Dashboard Admin"])

# --- MODUL 1: FORMULIR ---
if menu == "📝 Form Pendaftaran Siswa":
    st.subheader("📑 Formulir Pendaftaran Siswa Baru")
    with st.form("ppdb_form", clear_on_submit=True):
        nama = st.text_input("Nama Lengkap Siswa*")
        nik_s = st.text_input("NIK Siswa (16 Digit)*")
        tgl_s = st.date_input("Tanggal Lahir", min_value=datetime(2015,1,1))
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        n_ayah = st.text_input("Nama Ayah Kandung")
        n_ibu = st.text_input("Nama Ibu Kandung")
        alamat = st.text_area("Alamat Lengkap")
        
        submitted = st.form_submit_button("SIMPAN & DAFTAR SEKARANG")
        if submitted:
            if not nama or len(nik_s) != 16:
                st.error("Cek kembali Nama dan NIK (harus 16 digit)!")
            else:
                sheet = client.open(SHEET_NAME).sheet1
                reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                row_data = [reg_id, nama, f"'{nik_s}", str(tgl_s), jk, n_ayah, n_ibu, alamat, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"]
                sheet.append_row(row_data)
                st.success(f"Berhasil terdaftar! No. Reg: {reg_id}")

# --- MODUL 2: DASHBOARD ADMIN (TEMPAT UPLOAD EXCEL) ---
elif menu == "📊 Dashboard Admin":
    st.subheader("🛠 Pusat Kendali Database PPDB")
    try:
        sheet = client.open(SHEET_NAME).sheet1
        data_all = sheet.get_all_records()
        
        # --- PERHATIKAN BAGIAN TABS INI ---
        tab_view, tab_import = st.tabs(["🔍 Monitoring Data", "📥 Import & Template Excel"])
        
        with tab_view:
            if data_all:
                df = pd.DataFrame(data_all)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Belum ada data pendaftar.")

        # --- DI SINI MENU UPLOAD EXCEL NYA ---
        with tab_import:
            st.markdown("### Import Data Masal via Excel")
            
            # DOWNLOAD TEMPLATE
            df_template = pd.DataFrame(columns=KOLOM_DATABASE)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_template.to_excel(writer, index=False)
            
            st.download_button(
                label="📥 Langkah 1: Download Template Excel", 
                data=buffer.getvalue(), 
                file_name="Template_PPDB_AlIrsyad.xlsx"
            )
            
            st.markdown("---")
            
            # UPLOAD EXCEL
            excel_file = st.file_uploader("Langkah 2: Pilih File Excel (.xlsx) untuk diunggah", type=['xlsx'])
            if excel_file:
                df_to_import = pd.read_excel(excel_file)
                st.write("Pratinjau Data:")
                st.dataframe(df_to_import.head())
                
                if st.button("🚀 Klik untuk Konfirmasi & Simpan ke Google Sheets"):
                    # Pastikan kolom Excel sama dengan kolom Sistem
                    if list(df_to_import.columns) == KOLOM_DATABASE:
                        data_list = df_to_import.astype(str).replace('nan', '').values.tolist()
                        sheet.append_rows(data_list)
                        st.success("Data Berhasil Diimport!")
                        st.rerun()
                    else:
                        st.error("Format Excel Salah! Gunakan Template yang sudah diunduh.")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
