import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import requests
import urllib.parse
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 
# MASUKKAN ID FOLDER GOOGLE DRIVE ANDA DI SINI
PARENT_FOLDER_ID = "1VKgQOAlc1WeZlTRIc4AlotswD0EQjCuI"

# Inisialisasi Session State
if 'role' not in st.session_state: st.session_state['role'] = None 
if 'staff_data' not in st.session_state: st.session_state['staff_data'] = []
if 'PENGUMUMAN' not in st.session_state: 
    st.session_state['PENGUMUMAN'] = "Selamat Datang di PPDB Online RA AL IRSYAD AL ISLAMIYYAH KEDIRI."

# Data Lembaga Lengkap
if 'INFO_LEMBAGA' not in st.session_state:
    st.session_state['INFO_LEMBAGA'] = {
        "Nama": "RA AL IRSYAD AL ISLAMIYYAH", "NSM": "101235710017", "NPSN": "69749712",
        "Status": "Swasta", "Bentuk SP": "RA", "Kepala": "IMROATUS SOLIKHAH",
        "Penyelenggara": "AL IRSYAD AL ISLAMIYYAH KOTA KEDIRI", "Afiliasi": "Nahdlatul Ulama",
        "Waktu Belajar": "Pagi", "Status KKM": "Anggota", "Komite": "Sudah Terbentuk",
        "Alamat": "Jl. Tembus Kaliombo No. 3-5", "RT/RW": "29/10", "Desa": "TOSAREN",
        "Kecamatan": "PESANTREN", "Kota": "KOTA KEDIRI", "Provinsi": "JAWA TIMUR",
        "Pos": "64133", "Koordinat": "-7.8301756, 112.0168655", "Telepon": "(0354) 682524",
        "Email": "ra.alirsyad.kediri@gmail.com"
    }

# --- 2. KONEKSI GOOGLE SERVICES ---
@st.cache_resource
def get_creds():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 
             'https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/drive.file']
    if "gcp_service_account" in st.secrets:
        return ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    else:
        return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

creds = get_creds()
client = gspread.authorize(creds)
drive_service = build('drive', 'v3', credentials=creds)

# --- 3. FUNGSI UNGGAH KE DRIVE ---
def upload_to_drive(file, filename):
    try:
        file_metadata = {'name': filename, 'parents': [PARENT_FOLDER_ID]}
        media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype='image/jpeg', resumable=True)
        uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = uploaded_file.get('id')
        
        # Memberikan izin publik agar bisa dilihat di App
        drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        
        # URL Langsung untuk Display
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except Exception as e:
        st.error(f"Gagal Upload Drive: {e}")
        return None

def save_media_link(tipe, link, desc=""):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        db.append_row([tipe, link, desc, datetime.now().strftime("%Y-%m-%d %H:%M")])
        return True
    except: return False

def load_media_links(tipe):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        data = db.get_all_records()
        return [d for d in data if d['Tipe_Data'] == tipe]
    except: return []

# --- 4. UI STYLING ---
st.set_page_config(page_title="PPDB DRIVE SYSTEM", layout="wide")

def set_bg(menu):
    bgs = load_media_links(f"BG_{menu}")
    bg_url = bgs[-1]['Link_Drive'] if bgs else ""
    overlay = "rgba(2, 132, 199, 0.7)" if st.session_state['role'] is None else "rgba(255, 255, 255, 0.95)"
    st.markdown(f"""
        <style>
        .stApp {{ background-image: linear-gradient({overlay}, {overlay}), url("{bg_url}"); background-size: cover; background-attachment: fixed; }}
        .header-box {{ background: white; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; display: flex; align-items: center; margin-bottom: 20px; }}
        .section-title {{ background: #0284C7; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; }}
        .emis-table {{ width: 100%; font-size: 13px; border-collapse: collapse; }}
        .emis-table td {{ padding: 10px; border-bottom: 1px solid #F1F5F9; }}
        .label-emis {{ font-weight: bold; color: #64748B; width: 200px; text-transform: uppercase; }}
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
    pw = st.text_input("Password Admin", type="password")
    if st.button("Login"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.rerun()
        else: st.error("Sandi Salah")
    st.stop()

# --- 6. SIDEBAR & MENU ---
with st.sidebar:
    st.markdown(f"### USER: {st.session_state['role'].upper()}")
    menu = st.selectbox("MENU", ["🏠 Profil", "📝 Pendaftaran", "📋 Daftar Siswa", "📸 Galeri", "👨‍🏫 Guru", "⚙️ Pengaturan BG"])
    if st.button("Log Out"): st.session_state['role'] = None; st.rerun()

set_bg(menu.replace(" ", "_"))

# --- 7. LOGIKA PER HALAMAN ---

# HALAMAN PROFIL
if menu == "🏠 Profil":
    st.markdown(f'<div class="header-box"><div><h2 style="margin:0;">{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2><p>NSM: {st.session_state["INFO_LEMBAGA"]["NSM"]}</p></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background: #E0F2FE; padding: 15px; border-radius: 10px; margin-bottom: 20px;">📢 <b>PENGUMUMAN:</b> {st.session_state["PENGUMUMAN"]}</div>', unsafe_allow_html=True)
    
    colL, colR = st.columns(2)
    with colL:
        st.markdown('<div class="section-title">INFO LEMBAGA</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">KEPALA</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
            <tr><td class="label-emis">PENYELENGGARA</td><td>: {st.session_state['INFO_LEMBAGA']['Nama Penyelenggara']}</td></tr>
            <tr><td class="label-emis">AFILIASI</td><td>: {st.session_state['INFO_LEMBAGA']['Afiliasi']}</td></tr>
        </table>""", unsafe_allow_html=True)
    with colR:
        st.markdown('<div class="section-title">ALAMAT</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
            <tr><td class="label-emis">KECAMATAN</td><td>: {st.session_state['INFO_LEMBAGA']['Kecamatan']}</td></tr>
            <tr><td class="label-emis">KOORDINAT</td><td>: {st.session_state['INFO_LEMBAGA']['Koordinat']}</td></tr>
        </table>""", unsafe_allow_html=True)

# HALAMAN PENDAFTARAN (3 TABS LENGKAP)
elif menu == "📝 Pendaftaran":
    st.markdown('<div class="section-title">PENDAFTARAN SISWA BARU</div>', unsafe_allow_html=True)
    with st.form("ppdb_drive", clear_on_submit=True):
        t1, t2, t3 = st.tabs(["📄 Siswa", "👨‍👩‍👧 Keluarga", "🏠 Alamat"])
        with t1:
            nm = st.text_input("Nama Lengkap*")
            ns = st.text_input("NISN")
            nk = st.text_input("NIK*")
            tl = st.date_input("Tanggal Lahir", min_value=datetime(1945,1,1))
            jk = st.selectbox("Kelamin", ["Laki-laki", "Perempuan"])
            st.info("Upload KK akan otomatis dikirim ke Google Drive")
            f_kk = st.file_uploader("Pilih File KK (PDF/JPG)", type=['pdf','jpg','png'])
        with t2:
            ay_n = st.text_input("Nama Ayah")
            ay_p = st.text_input("Pendidikan Ayah")
            ay_g = st.text_input("Penghasilan Ayah")
            st.markdown("---")
            ib_n = st.text_input("Nama Ibu")
            ib_p = st.text_input("Pendidikan Ibu")
            ib_g = st.text_input("Penghasilan Ibu")
        with t3:
            st_h = st.selectbox("Status Rumah", ["Milik Sendiri", "Sewa", "Lainnya"])
            alm = st.text_area("Alamat Lengkap")
        
        if st.form_submit_button("✅ KIRIM DATA"):
            if nm and nk:
                url_kk = upload_to_drive(f_kk, f"KK_{nm}_{nk}") if f_kk else "No File"
                try:
                    db = client.open(SHEET_NAME).sheet1
                    db.append_row([datetime.now().strftime("%Y-%m-%d"), nm, ns, nk, str(tl), jk, ay_n, ay_p, ay_g, ib_n, ib_p, ib_g, st_h, alm, url_kk])
                    st.success("Berhasil! Foto tersimpan di Drive dan Data di Sheets."); st.balloons()
                except: st.error("Gagal koneksi.")

# HALAMAN GALERI (DIRECT DRIVE DISPLAY)
elif menu == "📸 Galeri":
    st.markdown('<div class="section-title">📸 GALERI SEKOLAH</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Tambah Foto (Langsung ke Drive)"):
            f_gal = st.file_uploader("Pilih Gambar")
            d_gal = st.text_input("Deskripsi")
            if st.button("Proses Simpan"):
                if f_gal:
                    link = upload_to_drive(f_gal, f"GALERI_{datetime.now().timestamp()}")
                    if link:
                        save_media_link("Galeri", link, d_gal)
                        st.success("Berhasil diunggah ke Drive!"); st.rerun()

    items = load_media_links("Galeri")
    if items:
        cols = st.columns(3)
        for i, itm in enumerate(items):
            with cols[i % 3]:
                st.image(itm['Link_Drive'], use_container_width=True)
                with st.expander("🔍 Preview / Perbesar"):
                    st.image(itm['Link_Drive'], caption=itm['Deskripsi'])
    else: st.info("Galeri Kosong.")

# HALAMAN PENGATURAN BG
elif menu == "⚙️ Pengaturan BG":
    if st.session_state['role'] == 'admin':
        st.subheader("Atur Background Per Menu")
        target = st.selectbox("Pilih Menu", ["LOGIN", "🏠_Profil", "📝_Pendaftaran", "📸_Galeri"])
        f_bg = st.file_uploader(f"Upload Gambar untuk {target}")
        if st.button("Simpan Permanen"):
            if f_bg:
                link = upload_to_drive(f_bg, f"BG_{target}_{datetime.now().timestamp()}")
                if link:
                    save_media_link(f"BG_{target}", link)
                    st.success("Background tersimpan!"); st.rerun()
    else: st.warning("Khusus Admin")
