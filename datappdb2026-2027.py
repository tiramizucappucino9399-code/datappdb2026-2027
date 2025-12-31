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

# --- KLASTER LINK GAMBAR (LOGO & FOLDER GALERI) ---
# Pastikan semua file di folder Drive Anda sudah diatur: "Anyone with the link can view"
@st.cache_data
def get_image_base64(url):
    try:
        if "drive.google.com" in url:
            # Ekstrak ID File dari Link Drive
            if "id=" in url:
                id_file = url.split("id=")[-1].split("&")[0]
            else:
                id_file = url.split('/')[-2]
            url = f"https://drive.google.com/uc?export=download&id={id_file}"
        
        response = requests.get(url, timeout=10)
        return base64.b64encode(response.content).decode()
    except:
        return None

# Ambil link satu per satu dari folder Drive Anda dan masukkan ke sini:
LOGO_LINK = "https://drive.google.com/file/d/1DOuK4dzVSLdzb8QewaFIzOL85IDWNP9P/view?usp=drive_link"

# Daftar Link Foto Kegiatan dari Folder yang sama (Tambahkan sebanyak yang Anda mau)
LIST_FOTO_KEGIATAN = [
    "https://drive.google.com/file/d/LINK_FOTO_1/view",
    "https://drive.google.com/file/d/LINK_FOTO_2/view",
    "https://drive.google.com/file/d/LINK_FOTO_3/view",
    "https://drive.google.com/file/d/LINK_FOTO_4/view"
]

LOGO_BASE64 = get_image_base64(LOGO_LINK)

# --- 2. FUNGSI KONEKSI GOOGLE SHEETS ---
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
        st.error(f"Koneksi Gagal: {e}")
        return None

# --- 3. STANDARISASI KOLOM (37 KOLOM TETAP UTUH) ---
KOLOM_DATABASE = [
    "No. Registrasi", "Nama Lengkap", "NISN", "NIS Lokal", "Kewarganegaraan", "NIK Siswa", 
    "Tanggal Lahir", "Tempat Lahir", "Jenis Kelamin", "Jumlah Saudara", "Anak Ke", 
    "Agama", "No KK", "Nama Kepala Keluarga", "Nomor WhatsApp",
    "Nama Ayah", "NIK Ayah", "Tempat Lahir Ayah", "Tanggal Lahir Ayah", "Pendidikan Ayah", "Pekerjaan Ayah", "Penghasilan Ayah",
    "Nama Ibu", "NIK Ibu", "Tempat Lahir Ibu", "Tanggal Lahir Ibu", "Pendidikan Ibu", "Pekerjaan Ibu", "Penghasilan Ibu",
    "Status Rumah", "Provinsi", "Kabupaten/Kota", "Kecamatan", "Kelurahan/Desa", "Alamat Lengkap", "Kode Pos",
    "Tanggal Daftar", "Status Verifikasi"
]

# --- 4. TAMPILAN ANTARMUKA ---
st.set_page_config(page_title="PPDB AL IRSYAD KEDIRI", page_icon="🏫", layout="wide")

# CSS Background & Styling
st.markdown(f"""
    <style>
    .stApp {{
        background-color: #f4f7f6;
    }}
    .main-header {{
        text-align: center; background-color: #1E5128; padding: 25px; 
        border-radius: 15px; color: white; margin-bottom: 25px;
    }}
    .section-header {{
        background-color: #ffffff; padding: 12px; border-radius: 8px; 
        margin-top: 20px; margin-bottom: 10px; border-left: 8px solid #1E5128; font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# Header dengan Logo
if LOGO_BASE64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="120"></div>', unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1>SISTEM INFORMASI PPDB & NOTIFIKASI</h1>
        <h3>KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI</h3>
        <p>Tahun Ajaran 2026-2027</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
if LOGO_BASE64:
    st.sidebar.image(f"data:image/png;base64,{LOGO_BASE64}", use_container_width=True)
st.sidebar.markdown("---")

client = init_google_sheets()
if not client: st.stop()

menu = st.sidebar.radio("MENU UTAMA", ["📝 Pendaftaran Murid", "🖼️ Galeri Sekolah", "📊 Dashboard Admin"])

# --- MODUL 1: PENDAFTARAN ---
if menu == "📝 Pendaftaran Murid":
    with st.form("ppdb_form", clear_on_submit=True):
        st.markdown('<div class="section-header">📑 HALAMAN 1: DATA SISWA</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap*")
        nisn = c2.text_input("NISN")
        nis_lokal = c1.text_input("NIS Lokal")
        kwn = c2.text_input("Kewarganegaraan", value="WNI")
        nik_s = c1.text_input("NIK Siswa (16 Digit)*")
        # --- REVISI TAHUN 1945 - 2100 ---
        tgl_s = c2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
        tmp_s = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = c1.number_input("Jumlah Saudara", min_value=0, step=1)
        anak_ke = c2.number_input("Anak Ke", min_value=1, step=1)
        agama = c1.selectbox("Agama", ["Islam", "Lainnya"])
        no_kk = c2.text_input("No. Kartu Keluarga (KK)")
        kepala_kk = c1.text_input("Nama Kepala Keluarga")
        no_wa = c2.text_input("Nomor WhatsApp Aktif (08...)*")

        st.markdown('<div class="section-header">👨‍👩‍👧‍👦 HALAMAN 2: DATA KELUARGA</div>', unsafe_allow_html=True)
        t_ay, t_ib = st.tabs(["Data Ayah", "Data Ibu"])
        with t_ay:
            ay1, ay2 = st.columns(2)
            n_ayah, nik_a = ay1.text_input("Nama Ayah"), ay2.text_input("NIK Ayah")
            tmp_a = ay1.text_input("Tempat Lahir Ayah")
            tgl_a = ay2.date_input("Tgl Lahir Ayah", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31), key="a1")
            pend_a, pek_a = ay1.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA", "S1", "S2"]), ay2.text_input("Pekerjaan Ayah")
            gaji_a = st.number_input("Gaji Ayah", min_value=0)
        with t_ib:
            ib1, ib2 = st.columns(2)
            n_ibu, nik_i = ib1.text_input("Nama Ibu"), ib2.text_input("NIK Ibu")
            tmp_i = ib1.text_input("Tempat Lahir Ibu")
            tgl_i = ib2.date_input("Tgl Lahir Ibu", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31), key="i1")
            pend_i, pek_i = ib1.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA", "S1", "S2"]), ib2.text_input("Pekerjaan Ibu")
            gaji_i = st.number_input("Gaji Ibu", min_value=0)

        st.markdown('<div class="section-header">🏠 HALAMAN 3: DATA ALAMAT</div>', unsafe_allow_html=True)
        status_rmh = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak", "Lainnya"])
        al1, al2 = st.columns(2)
        prov, kota = al1.text_input("Provinsi", value="Jawa Timur"), al2.text_input("Kota", value="Kediri")
        alamat, pos = st.text_area("Alamat Lengkap"), st.text_input("Kode Pos")

        if st.form_submit_button("✅ DAFTAR SEKARANG"):
            if nama and nik_s and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    wa_fix = no_wa.replace("08", "628", 1) if no_wa.startswith("08") else no_wa
                    data_final = [
                        reg_id, nama, nisn, nis_lokal, kwn, f"'{nik_s}", str(tgl_s), tmp_s, jk, saudara, anak_ke, agama, f"'{no_kk}", kepala_kk, wa_fix,
                        n_ayah, f"'{nik_a}", tmp_a, str(tgl_a), pend_a, pek_a, gaji_a, n_ibu, f"'{nik_i}", tmp_i, str(tgl_i), pend_i, pek_i, gaji_i,
                        status_rmh, prov, kota, "", "", alamat, pos, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"
                    ]
                    sheet.append_row(data_final)
                    st.success(f"Pendaftaran Berhasil! No Reg: {reg_id}")
                    # Fitur WA
                    pesan = urllib.parse.quote(f"Alhamdulillah, pendaftaran Ananda {nama} berhasil.\nNo Reg: {reg_id}")
                    st.markdown(f'<a href="https://wa.me/{wa_fix}?text={pesan}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border-radius:8px; border:none; font-weight:bold; cursor:pointer;">📲 KIRIM KONFIRMASI WA</button></a>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Nama, NIK, dan WA wajib diisi!")

# --- MODUL 2: GALERI ---
elif menu == "🖼️ Galeri Sekolah":
    st.markdown('<div class="section-header">📸 DOKUMENTASI KEGIATAN</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, link in enumerate(LIST_FOTO_KEGIATAN):
        img = get_image_base64(link)
        if img:
            cols[idx % 3].image(f"data:image/png;base64,{img}", use_container_width=True)

# --- MODUL 3: ADMIN ---
elif menu == "📊 Dashboard Admin":
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pw = st.text_input("Password Admin", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD: st.session_state.auth = True; st.rerun()
            else: st.error("Salah!")
        st.stop()
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(sheet.get_all_records()).astype(str)
        tab1, tab2 = st.tabs(["🔍 Monitoring Data", "📥 Import & Template"])
        with tab1:
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Download CSV", df.to_csv(index=False).encode('utf-8'), "Data_PPDB.csv", "text/csv")
        with tab2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                pd.DataFrame(columns=KOLOM_DATABASE).to_excel(wr, index=False)
            st.download_button("📥 Download Template Excel", buf.getvalue(), "Template_PPDB.xlsx")
            up = st.file_uploader("Upload Excel", type=['xlsx'])
            if up and st.button("Proses Import"):
                df_up = pd.read_excel(up)
                sheet.append_rows(df_up.astype(str).replace('nan', '').values.tolist())
                st.success("Import Berhasil!"); st.rerun()
    except Exception as e: st.error(f"Error: {e}")
