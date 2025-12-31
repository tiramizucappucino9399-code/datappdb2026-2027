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
    "Maps_Embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3952.682662243464!2d112.01255557416183!3d-7.823376577695383!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e78570e932338d1%3A0x6334a17088b7764e!2sRA%20Al%20Irsyad!5e0!3m2!1sid!2sid!4v1710000000000!5m2!1sid!2sid"
}

# --- KLASTER GAMBAR (LOGO & GALERI) ---
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

# Placeholder link foto (Silakan ganti dengan link asli Anda)
LIST_FOTO_KEGIATAN = [
    {"judul": "Kegiatan Belajar", "url": "LINK_FOTO_1"},
    {"judul": "Guru & Staf", "url": "LINK_FOTO_2"}
]

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

# --- 3. STANDARISASI KOLOM (37 KOLOM LENGKAP) ---
KOLOM_DATABASE = [
    "No. Registrasi", "Nama Lengkap", "NISN", "NIS Lokal", "Kewarganegaraan", "NIK Siswa", 
    "Tanggal Lahir", "Tempat Lahir", "Jenis Kelamin", "Jumlah Saudara", "Anak Ke", 
    "Agama", "No KK", "Nama Kepala Keluarga", "Nomor WhatsApp",
    "Nama Ayah", "NIK Ayah", "Tempat Lahir Ayah", "Tanggal Lahir Ayah", "Pendidikan Ayah", "Pekerjaan Ayah", "Penghasilan Ayah",
    "Nama Ibu", "NIK Ibu", "Tempat Lahir Ibu", "Tanggal Lahir Ibu", "Pendidikan Ibu", "Pekerjaan Ibu", "Penghasilan Ibu",
    "Status Rumah", "Provinsi", "Kabupaten/Kota", "Kecamatan", "Kelurahan/Desa", "Alamat Lengkap", "Kode Pos",
    "Tanggal Daftar", "Status Verifikasi"
]

# --- 4. UI STYLING EMIS MODERN ---
st.set_page_config(page_title="PPDB EMIS AL IRSYAD", page_icon="🏫", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAFC; }}
    .emis-header {{
        background: linear-gradient(90deg, #0284C7 0%, #38BDF8 100%);
        padding: 25px; border-radius: 0 0 20px 20px; color: white; margin-bottom: 25px;
    }}
    .section-header-emis {{
        background-color: #E0F2FE; color: #0369A1; padding: 12px;
        border-radius: 8px; font-weight: bold; margin-bottom: 15px; border-left: 5px solid #0284C7;
    }}
    .emis-card {{
        background-color: white; padding: 20px; border-radius: 12px;
        border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="110"></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; font-size:12px; color:#64748B; margin-bottom:15px;'><b>{ALAMAT_SEKOLAH['Nama']}</b></div>", unsafe_allow_html=True)
    
    # Menu Navigasi Terpisah
    st.markdown("### 🛠 NAVIGASI")
    menu = st.selectbox("Pilih Menu", ["🏠 Profil & Dashboard", "📝 Pendaftaran Siswa Baru", "📸 Galeri Sekolah", "🔐 Panel Admin"])
    
    st.markdown("---")
    st.markdown(f"📅 **{datetime.now().strftime('%A, %d %b %Y')}**")
    st.components.v1.iframe(ALAMAT_SEKOLAH["Maps_Embed"], height=200)

# --- CONTENT AREA ---
st.markdown(f"""<div class="emis-header">
    <div style="font-size: 26px; font-weight: bold;">SISTEM INFORMASI PPDB & NOTIFIKASI</div>
    <div style="font-size: 14px; opacity: 0.9;">Lembaga: {ALAMAT_SEKOLAH['Nama']} | Tahun Pelajaran 2026/2027</div>
</div>""", unsafe_allow_html=True)

client = init_google_sheets()
if not client: st.stop()

# --- MODUL 0: PROFIL & DASHBOARD ---
if menu == "🏠 Profil & Dashboard":
    st.markdown('<div class="section-header-emis">DASHBOARD UTAMA & PROFIL</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"""<div class="emis-card">
            <h3>Selamat Datang di Portal PPDB</h3>
            <p>Silakan gunakan menu di samping untuk memulai pendaftaran atau melihat informasi sekolah.</p>
            <hr>
            <h4>Visi Sekolah</h4>
            <p><i>"Mewujudkan generasi bertakwa, cerdas, dan berkarakter islami."</i></p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="emis-card" style="background-color: #F0F9FF;">
            <b>📞 Kontak Bantuan:</b><br>{ALAMAT_SEKOLAH['Telepon']}<br>
            <b>📍 Alamat:</b><br>{ALAMAT_SEKOLAH['Jalan']}
        </div>""", unsafe_allow_html=True)

# --- MODUL 1: PENDAFTARAN (37 KOLOM LENGKAP) ---
elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<div class="section-header-emis">FORMULIR PENDAFTARAN (LENGKAP 37 KOLOM)</div>', unsafe_allow_html=True)
    with st.form("form_ppdb", clear_on_submit=True):
        
        # BAGIAN I: DATA SISWA
        st.markdown("##### I. DATA SISWA")
        col1, col2 = st.columns(2)
        nama = col1.text_input("Nama Lengkap*")
        nisn = col2.text_input("NISN")
        nis_lokal = col1.text_input("NIS Lokal")
        kwn = col2.text_input("Kewarganegaraan", value="WNI")
        nik_s = col1.text_input("NIK Siswa (16 Digit)*")
        tgl_s = col2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
        tmp_s = col1.text_input("Tempat Lahir")
        jk = col2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = col1.number_input("Jumlah Saudara", min_value=0, step=1)
        anak_ke = col2.number_input("Anak Ke", min_value=1, step=1)
        agama = col1.selectbox("Agama", ["Islam"])
        no_kk = col2.text_input("No. Kartu Keluarga (KK)")
        kepala_kk = col1.text_input("Nama Kepala Keluarga")
        no_wa = col2.text_input("Nomor WhatsApp Aktif (08...)*")

        # BAGIAN II: DATA KELUARGA
        st.markdown("<br>##### II. DATA KELUARGA", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Data Ayah", "Data Ibu"])
        with t1:
            ay1, ay2 = st.columns(2)
            n_ayah, nik_a = ay1.text_input("Nama Ayah Kandung"), ay2.text_input("NIK Ayah")
            tmp_a, tgl_a = ay1.text_input("Tempat Lahir Ayah"), ay2.date_input("Tgl Lahir Ayah", key="ay", min_value=datetime(1945,1,1))
            pend_a, pek_a = ay1.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA", "S1", "S2"]), ay2.text_input("Pekerjaan Ayah")
            gaji_a = st.number_input("Penghasilan Ayah", min_value=0)
        with t2:
            ib1, ib2 = st.columns(2)
            n_ibu, nik_i = ib1.text_input("Nama Ibu Kandung"), ib2.text_input("NIK Ibu")
            tmp_i, tgl_i = ib1.text_input("Tempat Lahir Ibu"), ib2.date_input("Tgl Lahir Ibu", key="ib", min_value=datetime(1945,1,1))
            pend_i, pek_i = ib1.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA", "S1", "S2"]), ib2.text_input("Pekerjaan Ibu")
            gaji_i = st.number_input("Penghasilan Ibu", min_value=0)

        # BAGIAN III: ALAMAT
        st.markdown("<br>##### III. DATA ALAMAT", unsafe_allow_html=True)
        st_rmh = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak", "Lainnya"])
        prov, kota = col1.text_input("Provinsi", value="Jawa Timur"), col2.text_input("Kota", value="Kediri")
        alamat, pos = st.text_area("Alamat Lengkap"), st.text_input("Kode Pos")

        if st.form_submit_button("SIMPAN PENDAFTARAN"):
            if nama and nik_s and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    wa_fix = no_wa.replace("08", "628", 1) if no_wa.startswith("08") else no_wa
                    
                    # DATA LENGKAP 37 KOLOM
                    row = [
                        reg_id, nama, nisn, nis_lokal, kwn, f"'{nik_s}", str(tgl_s), tmp_s, jk, saudara, anak_ke,
                        agama, f"'{no_kk}", kepala_kk, wa_fix, n_ayah, f"'{nik_a}", tmp_a, str(tgl_a), pend_a, pek_a, gaji_a,
                        n_ibu, f"'{nik_i}", tmp_i, str(tgl_i), pend_i, pek_i, gaji_i,
                        st_rmh, prov, kota, "", "", alamat, pos, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"
                    ]
                    sheet.append_row(row)
                    st.success(f"Berhasil! No Reg: {reg_id}")
                    st.markdown(f'<a href="https://wa.me/{wa_fix}?text=Pendaftaran%20{nama}%20Berhasil" target="_blank">📲 Kirim Konfirmasi WA</a>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")

# --- MODUL 2: GALERI ---
elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-header-emis">GALERI FOTO KEGIATAN & GURU</div>', unsafe_allow_html=True)
    st.info("Fitur Galeri: Menampilkan foto kegiatan anak-anak dan profil guru.")
    cols = st.columns(2)
    with cols[0]:
        st.markdown('<div class="emis-card"><b>🖼️ Kegiatan Anak</b><br>Tampilkan foto aktivitas belajar di sini.</div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="emis-card"><b>👨‍🏫 Profil Guru</b><br>Tampilkan foto tenaga pendidik di sini.</div>', unsafe_allow_html=True)

# --- MODUL 3: ADMIN ---
elif menu == "🔐 Panel Admin":
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pw = st.text_input("Password Admin", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD: st.session_state.auth = True; st.rerun()
            else: st.error("Ditolak!")
        st.stop()
    
    st.markdown('<div class="section-header-emis">DATABASE PENDAFTAR LENGKAP</div>', unsafe_allow_html=True)
    sheet = client.open(SHEET_NAME).sheet1
    df = pd.DataFrame(sheet.get_all_records()).astype(str)
    st.dataframe(df, use_container_width=True)
