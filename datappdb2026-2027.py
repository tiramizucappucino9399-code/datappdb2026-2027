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

# Inisialisasi Session State
if 'role' not in st.session_state: st.session_state['role'] = None 
if 'auth' not in st.session_state: st.session_state['auth'] = False

# --- 2. FUNGSI KONEKSI & DATABASE MEDIA ---
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
    except: return None

client = init_google_sheets()

def save_media_to_db(tipe, b64_data, desc=""):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        db.append_row([tipe, b64_data, desc, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        return True
    except: return False

def load_media_from_db(tipe):
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

# --- 3. DATA LEMBAGA & STYLING ---
if 'INFO_LEMBAGA' not in st.session_state:
    st.session_state['INFO_LEMBAGA'] = {
        "Nama": "RA AL IRSYAD AL ISLAMIYYAH", "NSM": "101235710017", "NPSN": "69749712",
        "Status": "Swasta", "Bentuk SP": "RA", "Kepala": "IMROATUS SOLIKHAH",
        "Alamat": "Jl. Tembus Kaliombo No. 3-5", "RT/RW": "29/10", "Desa": "TOSAREN",
        "Kecamatan": "PESANTREN", "Kota": "KOTA KEDIRI", "Provinsi": "JAWA TIMUR",
        "Pos": "64133", "Koordinat": "-7.8301756, 112.0168655", "Telepon": "(0354) 682524",
        "Email": "ra.alirsyad.kediri@gmail.com", "Afiliasi": "Nahdlatul Ulama",
        "Status KKM": "Anggota", "Komite": "Sudah Terbentuk", "Waktu Belajar": "Pagi"
    }

st.set_page_config(page_title="EMIS PPDB AL IRSYAD", page_icon="🏫", layout="wide")

# Load Background dari DB
bg_db = load_media_from_db("Background")
BG_BASE64 = bg_db[-1]['Konten_Base64'] if bg_db else ""

st.markdown(f"""
<style>
    .stApp {{ background-color: #F8FAFC; }}
    {f'.login-bg {{ background-image: linear-gradient(rgba(2, 132, 199, 0.75), rgba(2, 132, 199, 0.75)), url("data:image/png;base64,{BG_BASE64}"); background-size: cover; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }}' if BG_BASE64 else ''}
    .header-box {{ background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; display: flex; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .section-title {{ background-color: #F8FAFC; padding: 12px; font-weight: bold; border-bottom: 2px solid #E2E8F0; margin-bottom: 15px; color: #0284C7; }}
    .emis-table {{ width: 100%; font-size: 13px; color: #334155; border-collapse: collapse; }}
    .emis-table td {{ padding: 10px 8px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
    .label-emis {{ color: #64748B; font-weight: 600; width: 180px; text-transform: uppercase; }}
    .login-card {{ background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px rgba(0,0,0,0.1); max-width: 500px; margin: auto; text-align: center; }}
</style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA LOGIN ---
if st.session_state['role'] is None:
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("<h2>SISTEM PPDB ONLINE</h2><h4>RA AL IRSYAD AL ISLAMIYYAH</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 USER"): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMIN"): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    pw = st.text_input("Sandi Admin", type="password")
    if st.button("Masuk"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.session_state['auth'] = True; st.rerun()
        else: st.error("Salah!")
    if st.button("Kembali"): st.session_state['role'] = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"### AKSES: {st.session_state['role'].upper()}")
    nav = ["🏠 Profil", "📝 Pendaftaran", "📋 Daftar Siswa", "📸 Galeri", "👨‍🏫 Guru & Staf", "⚙️ Pengaturan"]
    if st.session_state['role'] == 'admin': nav.append("🔐 Database")
    menu = st.selectbox("MENU", nav)
    if st.button("🚪 Keluar"): st.session_state['role'] = None; st.rerun()

# --- 6. MODUL MENU ---

if menu == "⚙️ Pengaturan":
    if st.session_state['role'] == 'admin':
        st.subheader("Ganti Background Aplikasi")
        f = st.file_uploader("Upload Foto", type=['jpg','png','jpeg'])
        if st.button("Simpan Permanen"):
            if f: save_media_to_db("Background", base64.b64encode(f.getvalue()).decode()); st.success("Berhasil!"); st.rerun()
    else: st.warning("Khusus Admin.")

elif menu == "🏠 Profil":
    st.markdown(f'<div class="header-box"><h2 style="margin:0;">{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">NSM / NPSN</td><td>: {st.session_state['INFO_LEMBAGA']['NSM']} / {st.session_state['INFO_LEMBAGA']['NPSN']}</td></tr>
            <tr><td class="label-emis">KEPALA</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
            <tr><td class="label-emis">AFILIASI</td><td>: {st.session_state['INFO_LEMBAGA']['Afiliasi']}</td></tr>
        </table>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
            <tr><td class="label-emis">KOTA</td><td>: {st.session_state['INFO_LEMBAGA']['Kota']}</td></tr>
            <tr><td class="label-emis">KOORDINAT</td><td>: {st.session_state['INFO_LEMBAGA']['Koordinat']}</td></tr>
        </table>""", unsafe_allow_html=True)

elif menu == "📝 Pendaftaran":
    st.markdown('<div class="section-title">FORMULIR PENDAFTARAN (LENGKAP 37 KOLOM)</div>', unsafe_allow_html=True)
    with st.form("ppdb_full", clear_on_submit=True):
        st.markdown("##### I. IDENTITAS SISWA")
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap*")
        nik_s = c2.text_input("NIK Siswa*")
        tgl_s = c1.date_input("Tgl Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
        rombel = c2.selectbox("Rombel", ["RA-A", "RA-B", "KB"])
        
        st.markdown("##### II. DATA ORANG TUA")
        tab1, tab2 = st.tabs(["Data Ayah", "Data Ibu"])
        with tab1:
            a1, a2 = st.columns(2)
            n_ay = a1.text_input("Nama Ayah")
            nik_ay = a2.text_input("NIK Ayah")
            pend_ay = a1.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA", "D3", "S1", "S2", "S3"])
            pek_ay = a2.text_input("Pekerjaan Ayah")
        with tab2:
            i1, i2 = st.columns(2)
            n_ib = i1.text_input("Nama Ibu")
            nik_ib = i2.text_input("NIK Ibu")
            pend_ib = i1.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA", "D3", "S1", "S2", "S3"])
            pek_ib = i2.text_input("Pekerjaan Ibu")

        wa = st.text_input("WA Wali*")
        alamat = st.text_area("Alamat Lengkap")

        if st.form_submit_button("Kirim"):
            if nama and wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    # Simpan data sesuai struktur 37 kolom Anda
                    row = [reg_id, nama, "", rombel, "WNI", f"'{nik_s}", str(tgl_s), "", "", 0, 1, "Islam", "", "", wa, n_ay, f"'{nik_ay}", "", "", pend_ay, pek_ay, "", n_ib, f"'{nik_ib}", "", "", pend_ib, pek_ib, "", "", "", "", "", "", alamat, "", datetime.now().strftime("%Y-%m-%d")]
                    sheet.append_row(row)
                    st.success("Tersimpan!")
                except: st.error("Error Database.")

elif menu == "📸 Galeri":
    st.markdown('<div class="section-title">📸 GALERI & PREVIEW</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("Upload Foto"):
            g_f = st.file_uploader("Pilih")
            g_d = st.text_input("Deskripsi")
            if st.button("Simpan"):
                save_media_to_db("Galeri", base64.b64encode(g_f.getvalue()).decode(), g_d); st.rerun()
    
    items = load_media_from_db("Galeri")
    cols = st.columns(3)
    for i, itm in enumerate(items):
        with cols[i % 3]:
            st.image(f"data:image/png;base64,{itm['Konten_Base64']}", use_container_width=True)
            with st.expander("🔍 Klik untuk Perbesar"):
                st.image(f"data:image/png;base64,{itm['Konten_Base64']}", caption=itm['Deskripsi'])

elif menu == "📋 Daftar Siswa":
    try:
        sheet = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(sheet.get_all_records())
        disp = pd.DataFrame()
        disp['NAMA'] = df['Nama Lengkap']
        disp['ROMBEL'] = df['NISN']
        disp['UMUR'] = df['Tanggal Lahir'].apply(lambda x: hitung_umur(str(x)))
        st.table(disp)
    except: st.info("Data Kosong.")
