import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
from datetime import date

# --- 1. KONFIGURASI SISTEM ---
# PASTIKAN: Folder ID di bawah ini sudah Anda klik kanan -> Share -> Masukkan email Service Account sebagai Editor
FOLDER_DRIVE_ID = "1VKgQOAlc1WeZlTRIc4AlotswD0EQjCuI" 
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 

# --- 2. FUNGSI KONEKSI CLOUD ---
@st.cache_resource
def init_google_services():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
        'https://spreadsheets.google.com/feeds'
    ]
    
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        
        client = gspread.authorize(creds)
        
        gauth = GoogleAuth()
        gauth.credentials = creds
        drive = GoogleDrive(gauth)
        
        return client, drive
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        return None, None

# --- TAMPILAN ---
st.set_page_config(page_title="PPDB KB-RA AL IRSYAD KEDIRI", page_icon="🏫", layout="wide")

client, drive = init_google_services()

if not client:
    st.stop()

menu = st.sidebar.radio("MENU UTAMA", ["📝 Pendaftaran Murid", "📊 Dashboard Admin"])

if menu == "📝 Pendaftaran Murid":
    with st.form("ppdb_form", clear_on_submit=True):
        # ... (Bagian input form tetap sama seperti kode Anda)
        st.subheader("📑 I. DATA SISWA")
        nama = st.text_input("Nama Lengkap")
        nik_s = st.text_input("NIK Siswa")
        file_kk = st.file_uploader("Upload KK", type=['pdf', 'jpg', 'png'])
        # ... (Input lainnya sesuaikan dengan kebutuhan)
        
        btn_submit = st.form_submit_button("✅ KIRIM DATA PENDAFTARAN")

    if btn_submit:
        if file_kk and nama and nik_s:
            try:
                with st.spinner("Sedang memproses data..."):
                    # 1. Simpan file sementara di server
                    ext = os.path.splitext(file_kk.name)[1]
                    fname = f"KK_{nama}_{nik_s}{ext}".replace(" ", "_")
                    with open(fname, "wb") as f:
                        f.write(file_kk.getbuffer())

                    # 2. Upload ke Drive (PENERAPAN SOLUSI QUOTA)
                    # Kita menambahkan 'supportsAllDrives': True agar bisa masuk ke folder yang di-share
                    file_metadata = {
                        'title': fname, 
                        'parents': [{'id': FOLDER_DRIVE_ID}]
                    }
                    
                    gfile = drive.CreateFile(file_metadata)
                    gfile.SetContentFile(fname)
                    
                    # Tambahkan parameter supportsAllDrives untuk mengatasi limitasi service account
                    gfile.Upload(param={'supportsAllDrives': True})
                    
                    # Beri izin akses link (Opsional)
                    gfile.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
                    link_kk = gfile['alternateLink']
                    
                    # Hapus file lokal
                    if os.path.exists(fname):
                        os.remove(fname)

                    # 3. Simpan ke Google Sheets
                    sheet = client.open(SHEET_NAME).sheet1
                    # (Susun data_final Anda di sini sesuai jumlah kolom)
                    data_final = [nama, nik_s, link_kk, str(date.today())] 
                    sheet.append_row(data_final)
                    
                    st.balloons()
                    st.success(f"Berhasil disimpan!")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat upload: {e}")
                st.info("Tips: Pastikan folder Drive sudah di-Share ke email Service Account Anda sebagai Editor.")

# ... (Sisa kode Dashboard Admin tetap sama)
