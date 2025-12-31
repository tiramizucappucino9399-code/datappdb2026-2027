import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64
import requests
import urllib.parse
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 
# MASUKKAN ID FOLDER GOOGLE DRIVE ANDA DI SINI
PARENT_FOLDER_ID = "1XW_CONTOH_ID_FOLDER_DRIVE_ANDA"

# Inisialisasi Session State
if 'role' not in st.session_state: st.session_state['role'] = None 
if 'staff_data' not in st.session_state: st.session_state['staff_data'] = []
if 'PENGUMUMAN' not in st.session_state: 
    st.session_state['PENGUMUMAN'] = "Selamat Datang di PPDB Online RA AL IRSYAD AL ISLAMIYYAH KEDIRI."

# DATA LEMBAGA (Kunci Nama Penyelenggara sudah disesuaikan agar tidak KeyError)
if 'INFO_LEMBAGA' not in st.session_state:
    st.session_state['INFO_LEMBAGA'] = {
        "Nama": "RA AL IRSYAD AL ISLAMIYYAH", 
        "NSM": "101235710017", 
        "NPSN": "69749712",
        "Status": "Swasta", 
        "Bentuk SP": "RA", 
        "Kepala": "IMROATUS SOLIKHAH",
        "Nama Penyelenggara": "AL IRSYAD AL ISLAMIYYAH KOTA KEDIRI", 
        "Afiliasi": "Nahdlatul Ulama",
        "Waktu Belajar": "Pagi", 
        "Status KKM": "Anggota", 
        "Komite": "Sudah Terbentuk",
        "Alamat": "Jl. Tembus Kaliombo No. 3-5", 
        "RT/RW": "29/10", 
        "Desa": "TOSAREN",
        "Kecamatan": "PESANTREN", 
        "Kota": "KOTA KEDIRI", 
        "Provinsi": "JAWA TIMUR",
        "Pos": "64133", 
        "Koordinat": "-7.8301756, 112.0168655", 
        "Telepon": "(0354) 682524",
        "Email": "ra.alirsyad.kediri@gmail.com"
    }

# --- 2. KONEKSI GOOGLE SERVICES ---
@st.cache_resource
def get_creds():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 
             'https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/drive.file']
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

creds = get_creds()
client = gspread.authorize(creds)
drive_service = build('drive', 'v3', credentials=creds)

# --- 3. FUNGSI MEDIA (DRIVE & SHEETS) ---
def upload_to_drive(file, filename):
    try:
        file_metadata = {'name': filename, 'parents': [PARENT_FOLDER_ID]}
        media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype='image/jpeg', resumable=True)
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = uploaded_file.get('id')
        drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except: return None

def save_media_link(tipe, link, desc=""):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        db.append_row([tipe, link, desc, datetime.now().strftime("%Y-%m-%d %H:%M")])
    except: pass

def load_media_links(tipe):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        data = db.get_all_records()
        return [d for d in data if d['Tipe_Data'] == tipe]
    except: return []

def hitung_umur(born_str):
    try:
        born = datetime.strptime(born_str, "%Y-%m-%d")
        today = datetime.today()
        return f"{today.year - born.year - ((today.month, today.day) < (born.month, born.day))} Thn"
    except: return "-"

# --- 4. UI STYLING & DYNAMIC BG ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", layout="wide")

def set_bg(menu_name):
    clean_menu = menu_name.replace(" ", "_")
    bgs = load_media_links(f"BG_{clean_menu}")
    bg_url = bgs[-1]['Link_Drive'] if bgs else ""
    overlay = "rgba(2, 132, 199, 0.75)" if st.session_state['role'] is None else "rgba(255, 255, 255, 0.94)"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: linear-gradient({overlay}, {overlay}), url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
        .header-box {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; align-items: center; margin-bottom: 20px; border: 1px solid #E2E8F0; }}
        .section-title {{ background: #0284C7; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; }}
        .emis-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .emis-table td {{ padding: 10px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
        .label-emis {{ font-weight: bold; color: #64748B; width: 220px; text-transform: uppercase; }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. GERBANG LOGIN ---
if st.session_state['role'] is None:
    set_bg("LOGIN")
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background:white; padding:50px; border-radius:20px; text-align:center; max-width:550px; margin:auto; box-shadow:0 20px 25px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        st.markdown("<h1 style='color:#0284C7; margin-bottom:0;'>PORTAL PPDB</h1><h4>RA AL IRSYAD AL ISLAMIYYAH</h4><hr>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 WALI MURID", use_container_width=True): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMIN", use_container_width=True): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    st.markdown('<div style="max-width:400px; margin:auto; background:white; padding:30px; border-radius:10px;">', unsafe_allow_html=True)
    pw = st.text_input("Sandi Admin", type="password")
    if st.button("Masuk"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.rerun()
        else: st.error("Sandi Salah")
    if st.button("Kembali"): st.session_state['role'] = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"### LOGIN: {st.session_state['role'].upper()}")
    menu = st.selectbox("Pilih Halaman", ["🏠 Profil Sekolah", "📝 Pendaftaran Siswa Baru", "📋 Daftar Siswa Terdaftar", "📸 Galeri Sekolah", "👨‍🏫 Profil Guru & Staf", "⚙️ Pengaturan BG"])
    if st.button("Log Out 🚪"): st.session_state['role'] = None; st.rerun()

set_bg(menu)

# --- 7. LOGIKA HALAMAN ---

if menu == "🏠 Profil Sekolah":
    st.markdown(f'<div class="header-box"><div><h2 style="margin:0; color:#1E293B;">{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2><p>NSM: {st.session_state["INFO_LEMBAGA"]["NSM"]} | NPSN: {st.session_state["INFO_LEMBAGA"]["NPSN"]}</p></div></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div style="background:#E0F2FE; padding:15px; border-radius:10px; margin-bottom:20px; color:#0369A1;">📢 <b>PENGUMUMAN:</b> {st.session_state["PENGUMUMAN"]}</div>', unsafe_allow_html=True)
    
    colL, colR = st.columns(2)
    with colL:
        st.markdown('<div class="section-title">Informasi Umum</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">KEPALA</td><td>: {st.session_state['INFO_LEMBAGA'].get('Kepala', '-')}</td></tr>
            <tr><td class="label-emis">PENYELENGGARA</td><td>: {st.session_state['INFO_LEMBAGA'].get('Nama Penyelenggara', '-')}</td></tr>
            <tr><td class="label-emis">AFILIASI</td><td>: {st.session_state['INFO_LEMBAGA'].get('Afiliasi', '-')}</td></tr>
            <tr><td class="label-emis">WAKTU BELAJAR</td><td>: {st.session_state['INFO_LEMBAGA'].get('Waktu Belajar', '-')}</td></tr>
        </table>""", unsafe_allow_html=True)
    with colR:
        st.markdown('<div class="section-title">Domisili</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA'].get('Alamat', '-')}</td></tr>
            <tr><td class="label-emis">KECAMATAN</td><td>: {st.session_state['INFO_LEMBAGA'].get('Kecamatan', '-')}</td></tr>
            <tr><td class="label-emis">KOORDINAT</td><td>: {st.session_state['INFO_LEMBAGA'].get('Koordinat', '-')}</td></tr>
        </table>""", unsafe_allow_html=True)

elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<div class="section-title">FORMULIR PENDAFTARAN (3 TABS)</div>', unsafe_allow_html=True)
    with st.form("ppdb_drive", clear_on_submit=True):
        t1, t2, t3 = st.tabs(["📄 1. Data Siswa", "👨‍👩‍👧 2. Data Keluarga", "🏠 3. Data Alamat"])
        with t1:
            nm = st.text_input("Nama Lengkap*")
            nk = st.text_input("NIK*")
            tl = st.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            jk = st.selectbox("Kelamin", ["Laki-laki", "Perempuan"])
            f_kk = st.file_uploader("Upload KK (PDF/JPG)", type=['pdf','jpg','png'])
        with t2:
            ay_n = st.text_input("Nama Ayah")
            ay_p = st.selectbox("Pendidikan Ayah", ["SD","SMP","SMA","S1","S2","S3"])
            ay_g = st.text_input("Penghasilan Ayah")
            st.markdown("---")
            ib_n = st.text_input("Nama Ibu")
            ib_p = st.selectbox("Pendidikan Ibu", ["SD","SMP","SMA","S1","S2","S3"])
            ib_g = st.text_input("Penghasilan Ibu")
        with t3:
            sh = st.selectbox("Status Rumah", ["Milik Sendiri", "Sewa", "Lainnya"])
            al = st.text_area("Alamat Lengkap")
        
        if st.form_submit_button("✅ KIRIM DATA"):
            if nm and nk:
                url_kk = upload_to_drive(f_kk, f"KK_{nm}_{nk}") if f_kk else "No File"
                try:
                    db = client.open(SHEET_NAME).sheet1
                    db.append_row([datetime.now().strftime("%Y-%m-%d"), nm, nk, str(tl), jk, ay_n, ay_p, ay_g, ib_n, ib_p, ib_g, sh, al, url_kk])
                    st.success("Pendaftaran Berhasil!")
                except: st.error("Gagal koneksi database")

elif menu == "📋 Daftar Siswa Terdaftar":
    try:
        db = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(db.get_all_records())
        if not df.empty:
            df['UMUR'] = df['Tanggal Lahir'].apply(lambda x: hitung_umur(str(x)))
            st.table(df[['Nama Lengkap', 'NIK', 'UMUR']])
    except: st.info("Belum ada data.")

elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">📸 GALERI DOKUMENTASI (DRIVE)</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Tambah Foto"):
            f_gal = st.file_uploader("Pilih Gambar")
            d_gal = st.text_input("Deskripsi")
            if st.button("Proses Upload"):
                link = upload_to_drive(f_gal, f"GALERI_{datetime.now().timestamp()}")
                if link:
                    save_media_link("Galeri", link, d_gal)
                    st.success("Foto Berhasil Masuk Drive!"); st.rerun()

    items = load_media_links("Galeri")
    cols = st.columns(3)
    for i, itm in enumerate(items):
        with cols[i % 3]:
            st.image(itm['Link_Drive'], use_container_width=True)
            with st.expander("🔍 Zoom"):
                st.image(itm['Link_Drive'], caption=itm['Deskripsi'])

elif menu == "⚙️ Pengaturan BG":
    if st.session_state['role'] == 'admin':
        st.subheader("Atur Background Per Menu")
        target = st.selectbox("Pilih Menu", ["LOGIN", "🏠_Profil_Sekolah", "📝_Pendaftaran_Siswa_Baru", "📸_Galeri_Sekolah", "👨‍🏫_Profil_Guru_&_Staf"])
        f_bg = st.file_uploader(f"Upload Gambar untuk {target}")
        if st.button("Simpan Permanen"):
            link = upload_to_drive(f_bg, f"BG_{target}")
            if link:
                save_media_link(f"BG_{target}", link)
                st.success("Background diperbarui!"); st.rerun()
