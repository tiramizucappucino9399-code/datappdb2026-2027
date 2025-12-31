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
    # Menentukan scope akses
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        if "gcp_service_account" in st.secrets:
            # Jika di Streamlit Cloud
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Jika dijalankan secara lokal
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Gagal menyambungkan ke Google Sheets: {e}")
        return None

# --- 3. STANDARISASI KOLOM DATABASE ---
# Pastikan urutan ini sama dengan di Google Sheets Anda
KOLOM_DATABASE = [
    "No. Registrasi", "Nama Lengkap", "NIK Siswa", "Tanggal Lahir", 
    "Jenis Kelamin", "Nama Ayah", "Nama Ibu", "Alamat Lengkap", 
    "Tanggal Daftar", "Status Verifikasi"
]

# --- 4. PENGATURAN UI ---
st.set_page_config(page_title="PPDB AL IRSYAD KEDIRI", page_icon="🏫", layout="wide")

st.markdown("""
    <style>
    .main-header {text-align: center; background-color: #1E5128; padding: 25px; border-radius: 10px; color: white; margin-bottom: 25px;}
    .stButton>button {width: 100%; border-radius: 8px; height: 3.5em; background-color: #1E5128; color: white; font-weight: bold;}
    .status-badge {padding: 5px 10px; border-radius: 5px; color: white; font-weight: bold;}
    </style>
    <div class="main-header">
        <h1>SISTEM INFORMASI PPDB ONLINE</h1>
        <h3>KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI</h3>
        <p>Kelancaran Data, Ketepatan Administrasi</p>
    </div>
""", unsafe_allow_html=True)

client = init_google_sheets()

if not client:
    st.warning("⚠️ Aplikasi belum terhubung ke Database. Pastikan kredensial sudah benar.")
    st.stop()

menu = st.sidebar.radio("NAVIGASI UTAMA", ["📝 Form Pendaftaran Siswa", "📊 Dashboard Admin"])

# --- MODUL 1: FORMULIR PENDAFTARAN ---
if menu == "📝 Form Pendaftaran Siswa":
    st.subheader("📑 Formulir Pendaftaran Siswa Baru")
    
    with st.form("ppdb_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        
        with c1:
            nama = st.text_input("Nama Lengkap Siswa*")
            nik_s = st.text_input("NIK Siswa (16 Digit)*", help="Masukkan 16 digit nomor induk kependudukan")
            tgl_s = st.date_input("Tanggal Lahir", min_value=datetime(2015,1,1))
        
        with c2:
            jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            n_ayah = st.text_input("Nama Ayah Kandung")
            n_ibu = st.text_input("Nama Ibu Kandung")
            
        alamat = st.text_area("Alamat Lengkap Tempat Tinggal")
        
        st.info("Pastikan seluruh data yang diisi sudah benar sebelum menekan tombol simpan.")
        submitted = st.form_submit_button("SIMPAN & DAFTAR SEKARANG")
        
        if submitted:
            # --- VALIDASI DATA ---
            if not nama or not nik_s:
                st.error("❌ Nama dan NIK Siswa wajib diisi!")
            elif len(nik_s) != 16 or not nik_s.isdigit():
                st.error("❌ NIK harus berjumlah 16 digit angka!")
            else:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    
                    # Membuat No. Registrasi otomatis
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    tgl_daftar = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Menyusun baris data sesuai KOLOM_DATABASE
                    row_data = [
                        reg_id, nama, f"'{nik_s}", str(tgl_s), 
                        jk, n_ayah, n_ibu, alamat, 
                        tgl_daftar, "Belum Diverifikasi"
                    ]
                    
                    sheet.append_row(row_data)
                    st.balloons()
                    st.success(f"✅ Alhamdulillah! Ananda {nama} berhasil didaftarkan. Nomor Registrasi: {reg_id}")
                except Exception as e:
                    st.error(f"Gagal menyimpan ke Google Sheets: {e}")

# --- MODUL 2: DASHBOARD ADMIN ---
elif menu == "📊 Dashboard Admin":
    st.subheader("🛠 Pusat Kendali Database PPDB")
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        data_all = sheet.get_all_records()
        
        tab_view, tab_import = st.tabs(["🔍 Monitoring Data", "📥 Import & Template Excel"])
        
        with tab_view:
            if data_all:
                df = pd.DataFrame(data_all)
                
                # Statistik Ringkas
                col_s1, col_s2, col_s3 = st.columns(3)
                col_s1.metric("Total Pendaftar", len(df))
                col_s2.metric("Belum Diverifikasi", len(df[df['Status Verifikasi'] == 'Belum Diverifikasi']))
                
                st.markdown("---")
                # Pencarian
                search_query = st.text_input("Cari Nama atau No. Registrasi")
                if search_query:
                    df = df[df['Nama Lengkap'].str.contains(search_query, case=False) | 
                            df['No. Registrasi'].str.contains(search_query, case=False)]
                
                st.dataframe(df, use_container_width=True)
                
                # Tombol Download Data
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Ekspor Semua Data ke CSV", csv_data, f"Data_PPDB_{datetime.now().date()}.csv", "text/csv")
            else:
                st.info("Belum ada data pendaftar yang masuk.")

        with tab_import:
            st.markdown("### Import Data Masal via Excel")
            
            # 1. Download Template
            df_template = pd.DataFrame(columns=KOLOM_DATABASE)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_template.to_excel(writer, index=False)
            
            st.write("1. Silakan unduh template agar kolom sesuai dengan sistem.")
            st.download_button("📥 Download Template Excel", data=buffer.getvalue(), file_name="Template_PPDB_AlIrsyad.xlsx")
            
            st.markdown("---")
            
            # 2. Upload Excel
            st.write("2. Unggah file Excel yang sudah diisi.")
            excel_file = st.file_uploader("Pilih File Excel (.xlsx)", type=['xlsx'])
            
            if excel_file:
                df_to_import = pd.read_excel(excel_file)
                st.write("Pratinjau Data:")
                st.dataframe(df_to_import.head())
                
                if st.button("Konfirmasi & Import ke Google Sheets"):
                    # Validasi Header
                    if list(df_to_import.columns) == KOLOM_DATABASE:
                        with st.spinner("Sedang memproses data..."):
                            # Membersihkan data
                            data_list = df_to_import.astype(str).replace('nan', '').values.tolist()
                            sheet.append_rows(data_list)
                            st.success(f"Berhasil mengimport {len(data_list)} data!")
                            st.rerun()
                    else:
                        st.error("❌ Gagal! Judul kolom di file Excel tidak sesuai dengan Template.")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat Dashboard: {e}")
