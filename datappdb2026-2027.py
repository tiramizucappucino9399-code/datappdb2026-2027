import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime
import io
import base64

# --- 1. KONFIGURASI DATABASE & AKSES ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 
# Ganti dengan ID Folder Google Drive Anda
PARENT_FOLDER_ID = "MASUKKAN_ID_FOLDER_DRIVE_DI_SINI"

# Inisialisasi State agar data tidak hilang saat navigasi
if 'role' not in st.session_state: st.session_state['role'] = None 
if 'PENGUMUMAN' not in st.session_state: 
    st.session_state['PENGUMUMAN'] = "Selamat Datang di PPDB Online RA AL IRSYAD AL ISLAMIYYAH KEDIRI Tahun Pelajaran 2026/2027."

# Data Informasi Umum Lembaga (Lengkap sesuai Gambar)
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

# --- 2. KONEKSI GOOGLE SERVICES (SHEETS & DRIVE) ---
@st.cache_resource
def get_google_services():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    if "gcp_service_account" in st.secrets:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    return gspread.authorize(creds), build('drive', 'v3', credentials=creds)

client, drive_service = get_google_services()

# --- 3. FUNGSI MEDIA (DRIVE STORAGE) ---
def upload_to_drive(file, filename):
    try:
        file_metadata = {'name': filename, 'parents': [PARENT_FOLDER_ID]}
        media = MediaIoBaseUpload(io.BytesIO(file.getvalue()), mimetype='application/octet-stream', resumable=True)
        uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        f_id = uploaded.get('id')
        drive_service.permissions().create(fileId=f_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        return f"https://drive.google.com/uc?export=download&id={f_id}"
    except: return None

def save_media_to_sheet(tipe, link, desc=""):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        db.append_row([tipe, link, desc, datetime.now().strftime("%Y-%m-%d %H:%M")])
    except: st.error("Tab 'Media_Data' tidak ditemukan di Sheets!")

def load_media_from_sheet(tipe):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        data = db.get_all_records()
        return [d for d in data if d['Tipe_Data'] == tipe]
    except: return []

# --- 4. TAMPILAN & BACKGROUND DINAMIS ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", layout="wide")

def apply_custom_style(menu_name):
    # Mengambil BG khusus menu dari Drive
    clean_menu = menu_name.replace(" ", "_")
    bg_links = load_media_from_sheet(f"BG_{clean_menu}")
    bg_url = bg_links[-1]['Link_Drive'] if bg_links else ""
    
    overlay = "rgba(2, 132, 199, 0.75)" if st.session_state['role'] is None else "rgba(255, 255, 255, 0.95)"
    
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient({overlay}, {overlay}), url("{bg_url}");
            background-size: cover; background-attachment: fixed;
        }}
        .header-box {{ background: white; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 20px; }}
        .section-title {{ background: #0284C7; color: white; padding: 12px; border-radius: 8px; font-weight: bold; margin-bottom: 15px; }}
        .emis-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        .emis-table td {{ padding: 10px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
        .label-emis {{ font-weight: bold; color: #64748B; width: 200px; text-transform: uppercase; }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. LOGIKA GERBANG LOGIN ---
if st.session_state['role'] is None:
    apply_custom_style("LOGIN")
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background:white; padding:50px; border-radius:20px; text-align:center; max-width:550px; margin:auto; box-shadow:0 15px 30px rgba(0,0,0,0.3);">', unsafe_allow_html=True)
        st.markdown("<h1 style='color:#0284C7;'>PORTAL PPDB</h1><h4>RA AL IRSYAD AL ISLAMIYYAH KEDIRI</h4><hr>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 WALI MURID", use_container_width=True): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMINISTRATOR", use_container_width=True): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    st.markdown('<div style="max-width:400px; margin:auto; background:white; padding:30px; border-radius:10px;">', unsafe_allow_html=True)
    pw = st.text_input("Sandi Admin", type="password")
    if st.button("Masuk"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.rerun()
        else: st.error("Sandi Salah!")
    if st.button("Kembali"): st.session_state['role'] = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- 6. SIDEBAR NAVIGASI ---
with st.sidebar:
    st.markdown(f"### LOGIN SEBAGAI: {st.session_state['role'].upper()}")
    menu = st.selectbox("PILIH MENU", ["🏠 Profil Sekolah", "📝 Pendaftaran Baru", "📋 Daftar Pendaftar", "📸 Galeri Kegiatan", "⚙️ Pengaturan App"])
    if st.button("Keluar 🚪"): st.session_state['role'] = None; st.rerun()

apply_custom_style(menu)

# --- 7. MODUL HALAMAN ---

# A. PROFIL SEKOLAH
if menu == "🏠 Profil Sekolah":
    st.markdown(f'<div class="header-box"><h2>{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2></div>', unsafe_allow_html=True)
    st.info(f"📢 **PENGUMUMAN:** {st.session_state['PENGUMUMAN']}")
    
    colL, colR = st.columns(2)
    with colL:
        st.markdown('<div class="section-title">INFORMASI UMUM</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">NSM / NPSN</td><td>: {st.session_state['INFO_LEMBAGA']['NSM']} / {st.session_state['INFO_LEMBAGA']['NPSN']}</td></tr>
            <tr><td class="label-emis">KEPALA</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
            <tr><td class="label-emis">PENYELENGGARA</td><td>: {st.session_state['INFO_LEMBAGA']['Nama Penyelenggara']}</td></tr>
        </table>""", unsafe_allow_html=True)
    with colR:
        st.markdown('<div class="section-title">DOMISILI</div>', unsafe_allow_html=True)
        st.markdown(f"""<table class="emis-table">
            <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
            <tr><td class="label-emis">KECAMATAN</td><td>: {st.session_state['INFO_LEMBAGA']['Kecamatan']}</td></tr>
            <tr><td class="label-emis">KOORDINAT</td><td>: {st.session_state['INFO_LEMBAGA']['Koordinat']}</td></tr>
        </table>""", unsafe_allow_html=True)

# B. PENDAFTARAN (37 KOLOM LENGKAP)
elif menu == "📝 Pendaftaran Baru":
    st.markdown('<div class="section-title">FORMULIR PPDB (3 HALAMAN)</div>', unsafe_allow_html=True)
    with st.form("ppdb_main_form", clear_on_submit=True):
        t1, t2, t3 = st.tabs(["📄 DATA SISWA", "👨‍👩‍👧 DATA KELUARGA", "🏠 DATA ALAMAT"])
        
        with t1:
            st.subheader("Identitas Peserta Didik")
            c1, c2 = st.columns(2)
            nm = c1.text_input("Nama Lengkap*")
            nsn = c2.text_input("NISN")
            nsl = c1.text_input("Nis Lokal")
            kwn = c2.selectbox("Kewarganegaraan", ["WNI", "WNA"])
            nik = c1.text_input("NIK Siswa*")
            tgl = c2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1))
            tmp = c1.text_input("Tempat Lahir")
            jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            sau = c1.number_input("Jumlah Saudara", 0)
            ake = c2.number_input("Anak Ke", 1)
            agm = c1.selectbox("Agama", ["Islam", "Kristen", "Katolik", "Hindu", "Budha"])
            nkk = c2.text_input("No Kartu Keluarga")
            f_kk = st.file_uploader("Upload KK (PDF/JPG/PNG)", type=['pdf','jpg','png'])
            nk_kk = st.text_input("Nama Kepala Keluarga")

        with t2:
            st.subheader("Data Ayah & Ibu Kandung")
            ay1, ay2 = st.columns(2)
            ay_n = ay1.text_input("Nama Ayah")
            ay_k = ay2.text_input("NIK Ayah")
            ay_t = ay1.text_input("Tempat Lahir Ayah")
            ay_d = ay2.date_input("Tgl Lahir Ayah", key="ayd", min_value=datetime(1940,1,1))
            ay_p = ay1.selectbox("Pendidikan Ayah", ["SD","SMP","SMA","D3","S1","S2","S3"])
            ay_j = ay2.text_input("Pekerjaan Ayah")
            ay_g = st.text_input("Penghasilan Ayah")
            st.markdown("---")
            ib1, ib2 = st.columns(2)
            ib_n = ib1.text_input("Nama Ibu")
            ib_k = ib2.text_input("NIK Ibu")
            ib_t = ib1.text_input("Tempat Lahir Ibu")
            ib_d = ib2.date_input("Tgl Lahir Ibu", key="ibd", min_value=datetime(1940,1,1))
            ib_p = ib1.selectbox("Pendidikan Ibu", ["SD","SMP","SMA","D3","S1","S2","S3"])
            ib_j = ib2.text_input("Pekerjaan Ibu")
            ib_g = st.text_input("Penghasilan Ibu")

        with t3:
            st.subheader("Data Alamat & Kontak")
            sh = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak/Sewa", "Lainnya"])
            al1, al2 = st.columns(2)
            prov = al1.text_input("Provinsi", "Jawa Timur")
            kab = al2.text_input("Kabupaten/Kota", "Kediri")
            kec = al1.text_input("Kecamatan")
            des = al2.text_input("Kelurahan/Desa")
            alm = st.text_area("Alamat Lengkap")
            kpos = st.text_input("Kode Pos")

        if st.form_submit_button("✅ KIRIM PENDAFTARAN"):
            if nm and nik:
                url_kk = upload_to_drive(f_kk, f"KK_{nm}_{nik}") if f_kk else "Tanpa File"
                try:
                    db = client.open(SHEET_NAME).sheet1
                    # Total 37 Kolom Isian
                    data_final = [
                        datetime.now().strftime("%Y-%m-%d"), nm, nsn, nsl, kwn, f"'{nik}", str(tgl), tmp, jk, sau, ake, agm, f"'{nkk}", nk_kk,
                        ay_n, f"'{ay_k}", ay_t, str(ay_d), ay_p, ay_j, ay_g,
                        ib_n, f"'{ib_k}", ib_t, str(ib_d), ib_p, ib_j, ib_g,
                        sh, prov, kab, kec, des, alm, kpos, url_kk, "Pending"
                    ]
                    db.append_row(data_final)
                    st.success("Data Berhasil Disimpan di Cloud!"); st.balloons()
                except: st.error("Gagal terhubung ke Database!")

# C. GALERI (DENGAN PREVIEW)
elif menu == "📸 Galeri Kegiatan":
    st.markdown('<div class="section-title">DOKUMENTASI SEKOLAH</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Upload Foto ke Drive"):
            f_g = st.file_uploader("Pilih Foto")
            d_g = st.text_input("Deskripsi")
            if st.button("Upload"):
                link = upload_to_drive(f_g, f"GAL_{datetime.now().timestamp()}")
                if link:
                    save_media_to_sheet("Galeri", link, d_g)
                    st.success("Tersimpan!"); st.rerun()

    items = load_media_from_sheet("Galeri")
    cols = st.columns(3)
    for i, itm in enumerate(items):
        with cols[i % 3]:
            st.image(itm['Link_Drive'], use_container_width=True)
            with st.expander("🔍 Zoom"):
                st.image(itm['Link_Drive'], caption=itm['Deskripsi'])

# D. PENGATURAN APP (GANTI BACKGROUND)
elif menu == "⚙️ Pengaturan App":
    if st.session_state['role'] == 'admin':
        st.markdown('<div class="section-title">PENGATURAN BACKGROUND PER MENU</div>', unsafe_allow_html=True)
        target = st.selectbox("Pilih Menu", ["LOGIN", "🏠_Profil_Sekolah", "📝_Pendaftaran_Baru", "📸_Galeri_Kegiatan"])
        f_bg = st.file_uploader(f"Upload Background untuk {target}")
        if st.button("Update Background"):
            link = upload_to_drive(f_bg, f"BG_{target}")
            if link:
                save_media_to_sheet(f"BG_{target}", link)
                st.success("Berhasil diperbarui!"); st.rerun()
    else: st.warning("Khusus Admin!")
