import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64
import requests

# --- 1. KONFIGURASI & SESSION STATE ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 

if 'role' not in st.session_state: st.session_state['role'] = None 
if 'staff_data' not in st.session_state: st.session_state['staff_data'] = []

# Data Lembaga Lengkap (Bisa diedit Admin)
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

# --- 2. FUNGSI MEDIA & DATABASE ---
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
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        db.append_row([tipe, b64, desc, datetime.now().strftime("%Y-%m-%d %H:%M")])
    except: pass

def load_media(tipe):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        all_data = db.get_all_records()
        return [d for d in all_data if d['Tipe_Data'] == tipe]
    except: return []

@st.cache_data
def get_img_as_base64(url):
    try:
        res = requests.get(url)
        return base64.b64encode(res.content).decode()
    except: return None

# --- 3. LOGO & TAMPILAN ---
LOGO_URL = "https://drive.google.com/file/d/1DOuK4dzVSLdzb8QewaFIzOL85IDWNP9P/view?usp=sharing" # Contoh link
LOGO_BASE64 = get_img_as_base64(LOGO_URL.replace("file/d/", "uc?export=download&id=").split("/view")[0])

st.set_page_config(page_title="EMIS PPDB AL IRSYAD", layout="wide")

# Fungsi untuk Set Background Berbeda per Menu
def set_bg(tipe_menu):
    data = load_media(f"BG_{tipe_menu}")
    b64 = data[-1]['Konten_Base64'] if data else ""
    overlay = "rgba(2, 132, 199, 0.8)" if st.session_state['role'] is None else "rgba(255, 255, 255, 0.9)"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient({overlay}, {overlay}), url("data:image/png;base64,{b64}");
            background-size: cover; background-attachment: fixed;
        }}
        .header-box {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; align-items: center; margin-bottom: 20px; }}
        .section-title {{ background: #0284C7; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; }}
        .emis-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        .emis-table td {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .label-emis {{ font-weight: bold; color: #64748B; width: 200px; }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. GERBANG LOGIN ---
if st.session_state['role'] is None:
    set_bg("LOGIN")
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background:white; padding:40px; border-radius:20px; text-align:center; max-width:550px; margin:auto; box-shadow:0 10px 25px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        if LOGO_BASE64: st.markdown(f'<img src="data:image/png;base64,{LOGO_BASE64}" width="120">', unsafe_allow_html=True)
        st.markdown("<h1 style='color:#0284C7;'>PPDB ONLINE</h1><h4>RA AL IRSYAD AL ISLAMIYYAH KEDIRI</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 WALI MURID", use_container_width=True): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMIN", use_container_width=True): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    pw = st.text_input("Password Admin", type="password")
    if st.button("Masuk"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.rerun()
        else: st.error("Akses Ditolak")
    st.stop()

# --- 5. SIDEBAR NAVIGASI ---
with st.sidebar:
    if LOGO_BASE64: st.image(f"data:image/png;base64,{LOGO_BASE64}", width=100)
    st.title("NAVIGASI")
    menu = st.selectbox("Pilih Menu", ["🏠 Profil Sekolah", "📝 Pendaftaran Siswa", "📋 Daftar Siswa Terdaftar", "📸 Galeri", "👨‍🏫 Guru & Staf", "⚙️ Pengaturan BG"])
    if st.button("Keluar 🚪"): st.session_state['role'] = None; st.rerun()

# --- 6. LOGIKA MENU ---
set_bg(menu.replace(" ", "_"))

# MENU 1: PROFIL EMIS (LENGKAP SESUAI GAMBAR)
if menu == "🏠 Profil Sekolah":
    st.markdown(f'<div class="header-box"><h2 style="margin:0;">{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2></div>', unsafe_allow_html=True)
    
    colL, colR = st.columns(2)
    with colL:
        st.markdown('<div class="section-title">Informasi Umum</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">NSM / NPSN</td><td>: {st.session_state['INFO_LEMBAGA']['NSM']} / {st.session_state['INFO_LEMBAGA']['NPSN']}</td></tr>
            <tr><td class="label-emis">KEPALA</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
            <tr><td class="label-emis">STATUS</td><td>: {st.session_state['INFO_LEMBAGA']['Status']}</td></tr>
            <tr><td class="label-emis">PENYELENGGARA</td><td>: {st.session_state['INFO_LEMBAGA']['Penyelenggara']}</td></tr>
            <tr><td class="label-emis">AFILIASI</td><td>: {st.session_state['INFO_LEMBAGA']['Afiliasi']}</td></tr>
        </table>""", unsafe_allow_html=True)
    with colR:
        st.markdown('<div class="section-title">Kontak & Alamat</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
            <tr><td class="label-emis">DESA/KECAMATAN</td><td>: {st.session_state['INFO_LEMBAGA']['Desa']} / {st.session_state['INFO_LEMBAGA']['Kecamatan']}</td></tr>
            <tr><td class="label-emis">KOTA/PROVINSI</td><td>: {st.session_state['INFO_LEMBAGA']['Kota']} / {st.session_state['INFO_LEMBAGA']['Provinsi']}</td></tr>
            <tr><td class="label-emis">TELEPON/EMAIL</td><td>: {st.session_state['INFO_LEMBAGA']['Telepon']} / {st.session_state['INFO_LEMBAGA']['Email']}</td></tr>
        </table>""", unsafe_allow_html=True)

# MENU 2: PENDAFTARAN (3 HALAMAN / TABS LENGKAP)
elif menu == "📝 Pendaftaran Siswa":
    st.markdown('<div class="section-title">FORMULIR PENDAFTARAN LENGKAP</div>', unsafe_allow_html=True)
    with st.form("ppdb_form", clear_on_submit=True):
        t1, t2, t3 = st.tabs(["1. Data Siswa", "2. Data Keluarga", "3. Data Alamat"])
        with t1:
            c1, c2 = st.columns(2)
            nm = c1.text_input("Nama Lengkap*")
            ns = c2.text_input("NISN")
            nl = c1.text_input("Nis Lokal")
            kw = c2.selectbox("Kewarganegaraan", ["WNI", "WNA"])
            nk = c1.text_input("NIK*")
            tl = c2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            tp = c1.text_input("Tempat Lahir")
            jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            sd = c1.number_input("Jumlah Saudara", 0)
            ak = c2.number_input("Anak ke", 1)
            ag = c1.selectbox("Agama", ["Islam", "Lainnya"])
            kk = c2.text_input("No Kartu Keluarga")
            fl = st.file_uploader("Upload KK (PDF/JPG/PNG - Max 2MB)", type=['pdf','jpg','png'])
            nk_kk = st.text_input("Nama Kepala Keluarga")
        with t2:
            st.markdown("**Data Ayah**")
            ay_n = st.text_input("Ayah Kandung")
            ay_k = st.text_input("NIK Ayah")
            ay_p = st.selectbox("Pendidikan Ayah", ["SD","SMP","SMA","S1","S2","S3"])
            ay_j = st.text_input("Pekerjaan Ayah")
            ay_g = st.text_input("Penghasilan Ayah")
            st.markdown("**Data Ibu**")
            ib_n = st.text_input("Ibu Kandung")
            ib_k = st.text_input("NIK Ibu")
            ib_p = st.selectbox("Pendidikan Ibu", ["SD","SMP","SMA","S1","S2","S3"])
            ib_j = st.text_input("Pekerjaan Ibu")
            ib_g = st.text_input("Penghasilan Ibu")
        with t3:
            sh = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak/Sewa", "Lainnya"])
            pr = st.text_input("Provinsi", "Jawa Timur")
            kb = st.text_input("Kabupaten", "Kediri")
            kc = st.text_input("Kecamatan")
            ds = st.text_input("Desa")
            al = st.text_area("Alamat Lengkap")
            kp = st.text_input("Kodepos")
        
        if st.form_submit_button("✅ SIMPAN DATA"):
            if nm and nk:
                try:
                    sh_db = client.open(SHEET_NAME).sheet1
                    sh_db.append_row([datetime.now().strftime("%Y-%m-%d"), nm, ns, nl, kw, f"'{nk}", str(tl), tp, jk, sd, ak, ag, f"'{kk}", nk_kk, ay_n, f"'{ay_k}", ay_p, ay_j, ay_g, ib_n, f"'{ib_k}", ib_p, ib_j, ib_g, sh, pr, kb, kc, ds, al, kp])
                    st.success("Data Berhasil Disimpan!"); st.balloons()
                except: st.error("Gagal koneksi ke database")

# MENU 4: GALERI (DENGAN PREVIEW KLIK)
elif menu == "📸 Galeri":
    st.markdown('<div class="section-title">DOKUMENTASI SEKOLAH</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Upload Galeri Baru"):
            f = st.file_uploader("Pilih Gambar")
            d = st.text_input("Deskripsi")
            if st.button("Simpan Permanen"):
                save_media("Galeri", base64.b64encode(f.getvalue()).decode(), d); st.rerun()
    
    imgs = load_media("Galeri")
    cols = st.columns(3)
    for i, item in enumerate(imgs):
        with cols[i % 3]:
            st.image(f"data:image/png;base64,{item['Konten_Base64']}", use_container_width=True)
            with st.expander("🔍 Zoom / Perbesar"):
                st.image(f"data:image/png;base64,{item['Konten_Base64']}", caption=item['Deskripsi'])

# MENU 6: PENGATURAN BACKGROUND PER MENU
elif menu == "⚙️ Pengaturan BG":
    if st.session_state['role'] == 'admin':
        st.subheader("Atur Background Berbeda per Menu")
        target = st.selectbox("Pilih Menu yang Ingin Diatur", ["LOGIN", "🏠_Profil_Sekolah", "📝_Pendaftaran_Siswa", "📸_Galeri", "👨‍🏫_Guru_&_Staf"])
        f_bg = st.file_uploader(f"Upload Background untuk {target}")
        if st.button("Simpan Background"):
            save_media(f"BG_{target}", base64.b64encode(f_bg.getvalue()).decode()); st.success("Background Tersimpan!")
    else: st.warning("Akses Khusus Admin")

# --- MENU LAINNYA ---
elif menu == "📋 Daftar Siswa Terdaftar":
    try:
        sh_db = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(sh_db.get_all_records())
        st.table(df[['Nama Lengkap', 'NIK', 'NISN', 'Alamat Lengkap']])
    except: st.info("Belum ada data pendaftar")

elif menu == "👨‍🏫 Guru & Staf":
    st.info("Profil Guru & Staf Sekolah")
