import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
from datetime import datetime
import urllib.parse
import requests
import base64

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 

# --- KONFIGURASI ALAMAT ---
ALAMAT_SEKOLAH = {
    "Nama": "KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI",
    "Jalan": "Jl. Letjend Suprapto No.21, Kel. Pakelan, Kec. Kota",
    "Kota": "Kota Kediri, Jawa Timur",
    "Kodepos": "64129",
    "Telepon": "(0354) 682524",
    "Instagram": "https://instagram.com/alirsyad_kediri",
    "Maps_Embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3952.666710486027!2d112.0118331!3d-7.8250266!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e78570f803f290b%3A0xc3f58a364673656c!2sRA%20Al%20Irsyad%20Al%20Islamiyyah!5e0!3m2!1sid!2sid!4v1700000000000"
}

# --- KLASTER GAMBAR ---
@st.cache_data
def get_image_base64(url):
    try:
        if "drive.google.com" in url:
            if "id=" in url:
                id_file = url.split("id=")[-1].split("&")[0]
            else:
                id_file = url.split('/')[-2]
            url = f"https://drive.google.com/uc?export=download&id={id_file}"
        response = requests.get(url, timeout=10)
        return base64.b64encode(response.content).decode()
    except:
        return None

LOGO_LINK = "https://drive.google.com/file/d/1DOuK4dzVSLdzb8QewaFIzOL85IDWNP9P/view?usp=drive_link"
LOGO_BASE64 = get_image_base64(LOGO_LINK)

# --- 2. FUNGSI KONEKSI ---
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
        st.error(f"Koneksi Gagal: {e}"); return None

# --- 3. STANDARISASI KOLOM ---
KOLOM_DATABASE = [
    "No. Registrasi", "Nama Lengkap", "NISN", "NIS Lokal", "Kewarganegaraan", "NIK Siswa", 
    "Tanggal Lahir", "Tempat Lahir", "Jenis Kelamin", "Jumlah Saudara", "Anak Ke", 
    "Agama", "No KK", "Nama Kepala Keluarga", "Nomor WhatsApp",
    "Nama Ayah", "NIK Ayah", "Tempat Lahir Ayah", "Tanggal Lahir Ayah", "Pendidikan Ayah", "Pekerjaan Ayah", "Penghasilan Ayah",
    "Nama Ibu", "NIK Ibu", "Tempat Lahir Ibu", "Tanggal Lahir Ibu", "Pendidikan Ibu", "Pekerjaan Ibu", "Penghasilan Ibu",
    "Status Rumah", "Provinsi", "Kabupaten/Kota", "Kecamatan", "Kelurahan/Desa", "Alamat Lengkap", "Kode Pos",
    "Tanggal Daftar", "Status Verifikasi"
]

# --- 4. UI MODIFIKASI MIRIP EMIS ---
st.set_page_config(page_title="PPDB EMIS AL IRSYAD", page_icon="🏫", layout="wide")

# CSS UNTUK TAMPILAN EMIS (Biru Muda & Bersih)
st.markdown(f"""
    <style>
    /* Background Utama */
    .stApp {{ background-color: #F8FAFC; }}
    
    /* Header Ala EMIS */
    .emis-header {{
        background: linear-gradient(90deg, #0284C7 0%, #38BDF8 100%);
        padding: 20px;
        border-radius: 0px 0px 20px 20px;
        color: white;
        text-align: left;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }}
    
    /* Card/Kotak Isian */
    .emis-card {{
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
        margin-bottom: 20px;
    }}
    
    /* Section Header Biru */
    .section-header-emis {{
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 15px;
        border-left: 5px solid #0284C7;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid #E2E8F0;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGASI MODERN ---
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="100"></div>', unsafe_allow_html=True)
    
    st.markdown(f"<div style='text-align:center; font-size:12px; color:#64748B;'>Staf Lembaga<br><b>{ALAMAT_SEKOLAH['Nama']}</b></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.selectbox(
        "MENU UTAMA",
        ["🏠 Dashboard / Profil", "📝 Pendaftaran Siswa", "🖼️ Galeri Kegiatan", "📊 Panel Admin"]
    )
    
    st.markdown(f"""
        <div style="background-color: #F1F5F9; padding: 10px; border-radius: 8px; font-size: 11px; margin-top: 20px;">
            <b>📍 Info Kontak:</b><br>{ALAMAT_SEKOLAH['Jalan']}<br>Telp: {ALAMAT_SEKOLAH['Telepon']}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<b>🗺️ Lokasi Sekolah:</b>", unsafe_allow_html=True)
    st.components.v1.iframe(ALAMAT_SEKOLAH["Maps_Embed"], height=180)

# --- HEADER TOP BAR ---
st.markdown(f"""
    <div class="emis-header">
        <div style="font-size: 24px; font-weight: bold;">SISTEM INFORMASI PPDB & NOTIFIKASI</div>
        <div style="font-size: 14px; opacity: 0.9;">Tahun Pelajaran 2026/2027 - Ganjil | {ALAMAT_SEKOLAH['Nama']}</div>
    </div>
""", unsafe_allow_html=True)

client = init_google_sheets()

# --- LOGIKA HALAMAN ---

if menu == "🏠 Dashboard / Profil":
    st.markdown('<div class="section-header-emis">Selamat Datang di Portal PPDB Al Irsyad</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
            <div class="emis-card">
                <h3>Informasi Lembaga</h3>
                <p>Selamat datang di sistem pendataan mandiri KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI. 
                Sistem ini dirancang untuk memudahkan wali murid dalam melakukan pendaftaran secara digital dan terintegrasi.</p>
                <br>
                <b>Status Akun:</b> <span style="color:green">Online</span><br>
                <b>Periode:</b> 2026/2027 Ganjil
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="emis-card" style="text-align:center;">
                <h4 style="color:#0284C7;">Alur Pendaftaran</h4>
                <p style="font-size:12px;">1. Isi Formulir<br>2. Verifikasi Data<br>3. Konfirmasi WhatsApp</p>
                <hr>
                <small>Silakan akses menu <b>Pendaftaran Siswa</b> di samping.</small>
            </div>
        """, unsafe_allow_html=True)

elif menu == "📝 Pendaftaran Siswa":
    st.markdown('<div class="section-header-emis">FORMULIR PENDAFTARAN SISWA BARU</div>', unsafe_allow_html=True)
    
    with st.container():
        with st.form("ppdb_form", clear_on_submit=True):
            st.markdown('<div style="font-weight:bold; margin-bottom:10px; color:#0369A1;">I. DATA SISWA & KONTAK</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            nama = c1.text_input("Nama Lengkap Siswa*")
            nik_s = c2.text_input("NIK Siswa (16 Digit)*")
            tgl_s = c1.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            no_wa = c2.text_input("Nomor WhatsApp Wali (08...)*")
            
            # --- MODIFIKASI: MENAMPILKAN TAB DATA KELUARGA DI DALAM FORM ---
            st.markdown('<br><div style="font-weight:bold; margin-bottom:10px; color:#0369A1;">II. DATA KELUARGA (Ayah & Ibu)</div>', unsafe_allow_html=True)
            tab_ay, tab_ib = st.tabs(["Data Ayah", "Data Ibu"])
            with tab_ay:
                ay1, ay2 = st.columns(2)
                n_ayah = ay1.text_input("Nama Ayah Kandung")
                nik_a = ay2.text_input("NIK Ayah Kandung")
            with tab_ib:
                ib1, ib2 = st.columns(2)
                n_ibu = ib1.text_input("Nama Ibu Kandung")
                nik_i = ib2.text_input("NIK Ibu Kandung")
                
            st.markdown('<br><div style="font-weight:bold; margin-bottom:10px; color:#0369A1;">III. DATA ALAMAT</div>', unsafe_allow_html=True)
            alamat = st.text_area("Alamat Lengkap")
            
            # Simpan data pendaftaran
            if st.form_submit_button("SIMPAN DRAFT & DAFTAR"):
                if nama and nik_s and no_wa:
                    try:
                        sheet = client.open(SHEET_NAME).sheet1
                        reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        wa_fix = no_wa.replace("08", "628", 1) if no_wa.startswith("08") else no_wa
                        
                        # Data 37 kolom (dipersingkat untuk contoh, silakan isi lengkap)
                        row = [reg_id, nama, "", "", f"'{nik_s}", str(tgl_s), "", "", "", "", "", "", "", "", wa_fix, n_ayah, f"'{nik_a}", "", "", "", "", "", n_ibu, f"'{nik_i}", "", "", "", "", "", "", "", "", "", "", alamat, "", datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"]
                        sheet.append_row(row)
                        st.success(f"Sukses! No Registrasi: {reg_id}")
                        wa_url = f"https://wa.me/{wa_fix}?text=Pendaftaran%20{nama}%20Berhasil"
                        st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="background-color:#22C55E; color:white; border:none; padding:10px 20px; border-radius:8px;">📲 Kirim Konfirmasi WA</button></a>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"Error: {e}")

elif menu == "📊 Panel Admin":
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pw = st.text_input("Sandi Admin", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD: st.session_state.auth = True; st.rerun()
            else: st.error("Ditolak!")
        st.stop()
    
    st.markdown('<div class="section-header-emis">MONITORING DATA SISWA</div>', unsafe_allow_html=True)
    sheet = client.open(SHEET_NAME).sheet1
    df = pd.DataFrame(sheet.get_all_records()).astype(str)
    st.dataframe(df, use_container_width=True)
