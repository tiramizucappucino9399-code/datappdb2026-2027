import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64
import requests
import urllib.parse

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 

# Inisialisasi Session State
if 'role' not in st.session_state: st.session_state['role'] = None 
if 'staff_data' not in st.session_state: st.session_state['staff_data'] = []
if 'PENGUMUMAN' not in st.session_state: 
    st.session_state['PENGUMUMAN'] = "Selamat Datang di PPDB Online RA AL IRSYAD AL ISLAMIYYAH KEDIRI."

if 'INFO_LEMBAGA' not in st.session_state:
    st.session_state['INFO_LEMBAGA'] = {
        "Nama": "RA AL IRSYAD AL ISLAMIYYAH", "NSM": "101235710017", "NPSN": "69749712",
        "Status": "Swasta", "Bentuk SP": "RA", "Kepala": "IMROATUS SOLIKHAH",
        "Nama Penyelenggara": "AL IRSYAD AL ISLAMIYYAH KOTA KEDIRI", "Afiliasi": "Nahdlatul Ulama",
        "Waktu Belajar": "Pagi", "Status KKM": "Anggota", "Komite": "Sudah Terbentuk",
        "Alamat": "Jl. Tembus Kaliombo No. 3-5", "RT/RW": "29/10", "Desa": "TOSAREN",
        "Kecamatan": "PESANTREN", "Kota": "KOTA KEDIRI", "Provinsi": "JAWA TIMUR",
        "Pos": "64133", "Koordinat": "-7.8301756, 112.0168655", "Telepon": "(0354) 682524",
        "Email": "ra.alirsyad.kediri@gmail.com"
    }

# --- 2. FUNGSI DATABASE & MEDIA (PERBAIKAN NOTIFIKASI) ---
@st.cache_resource
def init_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        if "gcp_service_account" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        return gspread.authorize(creds)
    except: return None

client = init_sheets()

def save_media(tipe, b64, desc=""):
    """Menyimpan media dengan return status True/False untuk notifikasi"""
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        db.append_row([tipe, b64, desc, datetime.now().strftime("%Y-%m-%d %H:%M")])
        return True
    except Exception as e:
        st.error(f"Gagal Simpan ke Database: {e}")
        return False

def load_media(tipe):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        all_data = db.get_all_records()
        return [d for d in all_data if d['Tipe_Data'] == tipe]
    except: return []

def hitung_umur(born_str):
    try:
        born = datetime.strptime(born_str, "%Y-%m-%d")
        today = datetime.today()
        return f"{today.year - born.year - ((today.month, today.day) < (born.month, born.day))} Thn"
    except: return "-"

# --- 3. UI STYLING ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", layout="wide")

def set_dynamic_bg(menu_name):
    data = load_media(f"BG_{menu_name}")
    b64 = data[-1]['Konten_Base64'] if data else ""
    overlay = "rgba(2, 132, 199, 0.75)" if st.session_state['role'] is None else "rgba(255, 255, 255, 0.93)"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient({overlay}, {overlay}), url("data:image/png;base64,{b64}");
            background-size: cover; background-attachment: fixed;
        }}
        .header-box {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; align-items: center; margin-bottom: 20px; border: 1px solid #E2E8F0; }}
        .announcement-box {{ background-color: #E0F2FE; border-left: 5px solid #0284C7; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #0369A1; font-weight: 500; }}
        .emis-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .emis-table td {{ padding: 10px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
        .label-emis {{ font-weight: bold; color: #64748B; width: 220px; text-transform: uppercase; }}
        .staff-card {{ background: white; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #E2E8F0; transition: 0.3s; }}
        .section-title {{ background: #0284C7; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. GERBANG LOGIN ---
if st.session_state['role'] is None:
    set_dynamic_bg("LOGIN")
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background:white; padding:50px; border-radius:20px; text-align:center; max-width:550px; margin:auto; box-shadow:0 20px 25px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        st.markdown("<h1 style='color:#0284C7; margin-bottom:0;'>PORTAL PPDB</h1><h4 style='color:#64748B;'>RA AL IRSYAD AL ISLAMIYYAH</h4><hr>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 WALI MURID", use_container_width=True): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMIN", use_container_width=True): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    st.markdown('<div style="max-width:400px; margin:auto; background:white; padding:30px; border-radius:10px;">', unsafe_allow_html=True)
    pw = st.text_input("Password Admin", type="password")
    if st.button("Masuk"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.rerun()
        else: st.error("Sandi Salah")
    if st.button("Kembali"): st.session_state['role'] = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- 5. SIDEBAR NAVIGASI ---
with st.sidebar:
    st.markdown(f"### LOGIN: {st.session_state['role'].upper()}")
    menu = st.selectbox("MENU NAVIGASI", ["🏠 Profil Sekolah", "📝 Pendaftaran Siswa Baru", "📋 Daftar Siswa Terdaftar", "📸 Galeri Sekolah", "👨‍🏫 Profil Guru & Staf", "⚙️ Pengaturan BG"])
    if st.button("Log Out 🚪"): st.session_state['role'] = None; st.rerun()

set_dynamic_bg(menu.replace(" ", "_"))

# --- 6. LOGIKA HALAMAN ---

# MENU 1: PROFIL
if menu == "🏠 Profil Sekolah":
    st.markdown(f'<div class="header-box"><div><h2 style="margin:0; color:#1E293B;">{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2><p style="margin:0; color:#64748B;">NSM: {st.session_state["INFO_LEMBAGA"]["NSM"]} | NPSN: {st.session_state["INFO_LEMBAGA"]["NPSN"]}</p></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="announcement-box">📢 <b>PENGUMUMAN:</b> {st.session_state["PENGUMUMAN"]}</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("✏️ Edit Pengumuman"):
            st.session_state['PENGUMUMAN'] = st.text_area("Isi Baru", st.session_state['PENGUMUMAN'])
            if st.button("Update"): st.rerun()

    st.markdown('<div style="background:white; padding:25px; border-radius:12px; border:1px solid #E2E8F0;">', unsafe_allow_html=True)
    colL, colR = st.columns(2)
    with colL:
        st.markdown('<div class="section-title">INFORMASI UMUM</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">KEPALA MADRASAH</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
            <tr><td class="label-emis">PENYELENGGARA</td><td>: {st.session_state['INFO_LEMBAGA']['Nama Penyelenggara']}</td></tr>
            <tr><td class="label-emis">AFILIASI</td><td>: {st.session_state['INFO_LEMBAGA']['Afiliasi']}</td></tr>
            <tr><td class="label-emis">WAKTU BELAJAR</td><td>: {st.session_state['INFO_LEMBAGA']['Waktu Belajar']}</td></tr>
        </table>""", unsafe_allow_html=True)
    with colR:
        st.markdown('<div class="section-title">DOMISILI</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
            <tr><td class="label-emis">KECAMATAN / KOTA</td><td>: {st.session_state['INFO_LEMBAGA']['Kecamatan']} / {st.session_state['INFO_LEMBAGA']['Kota']}</td></tr>
            <tr><td class="label-emis">KOORDINAT</td><td>: {st.session_state['INFO_LEMBAGA']['Koordinat']}</td></tr>
        </table>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# MENU 2: PENDAFTARAN (3 TABS LENGKAP)
elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<div class="section-title">FORMULIR PENDAFTARAN</div>', unsafe_allow_html=True)
    with st.form("ppdb_full_form", clear_on_submit=True):
        t1, t2, t3 = st.tabs(["1. Data Siswa", "2. Data Keluarga", "3. Data Alamat"])
        with t1:
            c1, c2 = st.columns(2)
            nm = c1.text_input("Nama Lengkap*")
            nsn = c2.text_input("NISN")
            nk = c1.text_input("NIK*")
            tl = c2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            jk = c1.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            u_kk = st.file_uploader("Upload KK (PDF/JPG/PNG - Max 2MB)", type=['pdf','jpg','png'])
        with t2:
            ay_n = st.text_input("Nama Ayah Kandung")
            ay_p = st.selectbox("Pendidikan Ayah", ["SD","SMP","SMA","S1","S2","S3"])
            ay_g = st.text_input("Penghasilan Ayah")
            st.markdown("---")
            ib_n = st.text_input("Nama Ibu Kandung")
            ib_p = st.selectbox("Pendidikan Ibu", ["SD","SMP","SMA","S1","S2","S3"])
            ib_g = st.text_input("Penghasilan Ibu")
        with t3:
            sh = st.selectbox("Status Rumah", ["Milik Sendiri", "Sewa", "Lainnya"])
            al = st.text_area("Alamat Lengkap")
        
        if st.form_submit_button("✅ KIRIM DATA"):
            if nm and nk:
                try:
                    db = client.open(SHEET_NAME).sheet1
                    db.append_row([datetime.now().strftime("%Y-%m-%d"), nm, nsn, nk, str(tl), jk, ay_n, ay_p, ay_g, ib_n, ib_p, ib_g, sh, al])
                    st.success("Berhasil Terdaftar!"); st.balloons()
                except: st.error("Gagal Koneksi")

# MENU 4: GALERI (PERBAIKAN DISPLAY & PREVIEW)
elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">📸 GALERI DOKUMENTASI</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Upload Foto Baru"):
            with st.form("form_gal", clear_on_submit=True):
                f = st.file_uploader("Pilih Gambar", type=['jpg','png','jpeg'])
                d = st.text_input("Deskripsi")
                if st.form_submit_button("Upload"):
                    if f:
                        b64 = base64.b64encode(f.getvalue()).decode()
                        if save_media("Galeri", b64, d):
                            st.success("✅ Berhasil diunggah!")
                            st.rerun()
                    else: st.error("Pilih file dulu!")

    items = load_media("Galeri")
    if items:
        cols = st.columns(3)
        for i, itm in enumerate(items):
            with cols[i % 3]:
                st.image(f"data:image/png;base64,{itm['Konten_Base64']}", use_container_width=True)
                with st.expander("🔍 Zoom / Preview"):
                    st.image(f"data:image/png;base64,{itm['Konten_Base64']}", caption=itm['Deskripsi'])
    else: st.info("Galeri Kosong.")

# MENU 6: PENGATURAN BG
elif menu == "⚙️ Pengaturan BG":
    if st.session_state['role'] == 'admin':
        st.subheader("Atur Background Per Menu")
        target = st.selectbox("Pilih Menu", ["LOGIN", "🏠_Profil_Sekolah", "📝_Pendaftaran_Siswa_Baru", "📸_Galeri_Sekolah"])
        with st.form("form_bg"):
            f_bg = st.file_uploader("Upload BG", type=['jpg','png'])
            if st.form_submit_button("Simpan"):
                if f_bg:
                    b64 = base64.b64encode(f_bg.getvalue()).decode()
                    if save_media(f"BG_{target}", b64):
                        st.success("✅ Background Diperbarui!")
                        st.rerun()
    else: st.warning("Khusus Admin")

# MENU LAINNYA (DAFTAR SISWA & GURU)
elif menu == "📋 Daftar Siswa Terdaftar":
    try:
        db = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(db.get_all_records())
        if not df.empty:
            df['UMUR'] = df['Tanggal Lahir'].apply(lambda x: hitung_umur(str(x)))
            st.table(df[['Nama Lengkap', 'NIK', 'Jenis Kelamin', 'UMUR']])
    except: st.info("Belum ada data.")

elif menu == "👨‍🏫 Profil Guru & Staf":
    st.info("Fitur Profil Guru tampil di sini.")
