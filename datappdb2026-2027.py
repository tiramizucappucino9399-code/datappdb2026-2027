import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
from datetime import datetime
import urllib.parse

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 

# --- PERBAIKAN LINK GAMBAR (Direct Link Google Drive) ---
# Saya sertakan fungsi otomatis untuk merubah link Drive biasa menjadi link gambar
def get_drive_direct_link(url):
    if "drive.google.com" in url:
        id_file = url.split('/')[-2] if 'view' in url else url.split('id=')[-1]
        return f"https://drive.google.com/uc?export=view&id={id_file}"
    return url

# Link Logo dari Anda
RAW_LOGO_URL = "https://drive.google.com/file/d/1DOuK4dzVSLdzb8QewaFIzOL85IDWNP9P/view?usp=drive_link"
LOGO_URL = get_drive_direct_link(RAW_LOGO_URL)

# Link Background (Silakan masukkan link Drive Background Anda di sini)
# Jika belum ada, sementara saya beri warna dasar hijau tua yang profesional
BG_URL = "https://www.transparenttextures.com/patterns/cubes.png" 

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

# --- 3. STANDARISASI KOLOM (37 KOLOM - TETAP UTUH) ---
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

# CSS untuk Background dan Header
st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)), url("{BG_URL}");
        background-size: cover;
        background-attachment: fixed;
    }}
    .main-header {{
        text-align: center; 
        background-color: #1E5128; 
        padding: 25px; 
        border-radius: 15px; 
        color: white; 
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    .section-header {{
        background-color: #ffffff; 
        padding: 12px; 
        border-radius: 8px; 
        margin-top: 20px; 
        margin-bottom: 10px; 
        border-left: 8px solid #1E5128; 
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# Menampilkan Logo dan Judul di Header
with st.container():
    col_l, col_r, col_c = st.columns([1, 4, 1])
    with col_r:
        st.markdown(f'<div class="main-header">', unsafe_allow_html=True)
        st.image(LOGO_URL, width=120) # Menampilkan logo dengan fungsi asli Streamlit agar lebih stabil
        st.markdown('<h1>SISTEM INFORMASI PPDB & NOTIFIKASI</h1>', unsafe_allow_html=True)
        st.markdown('<h3>KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI</h3>', unsafe_allow_html=True)
        st.markdown('<p>Tahun Ajaran 2026-2027</p></div>', unsafe_allow_html=True)

# Logo di Sidebar
st.sidebar.image(LOGO_URL, use_container_width=True)
st.sidebar.markdown("---")

client = init_google_sheets()
if not client: st.stop()

menu = st.sidebar.radio("NAVIGASI UTAMA", ["📝 Pendaftaran Murid", "📊 Dashboard Admin"])

# --- MODUL 1: PENDAFTARAN ---
if menu == "📝 Pendaftaran Murid":
    with st.form("ppdb_form", clear_on_submit=True):
        st.markdown('<div class="section-header">📑 HALAMAN 1: DATA SISWA & KONTAK</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap*")
        nisn = c2.text_input("NISN")
        nis_lokal = c1.text_input("NIS Lokal")
        kwn = c2.text_input("Kewarganegaraan", value="WNI")
        nik_s = c1.text_input("NIK Siswa (16 Digit)*")
        tgl_s = c2.date_input("Tanggal Lahir", min_value=datetime(2015,1,1))
        tmp_s = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = c1.number_input("Jumlah Saudara", min_value=0, step=1)
        anak_ke = c2.number_input("Anak Ke", min_value=1, step=1)
        agama = c1.selectbox("Agama", ["Islam", "Kristen", "Katolik", "Hindu", "Budha", "Khonghucu"])
        no_kk = c2.text_input("No. Kartu Keluarga (KK)")
        kepala_kk = c1.text_input("Nama Kepala Keluarga")
        no_wa = c2.text_input("Nomor WhatsApp Wali (Contoh: 08123...)*")

        st.markdown('<div class="section-header">👨‍👩‍👧‍👦 HALAMAN 2: DATA KELUARGA</div>', unsafe_allow_html=True)
        t_ayah, t_ibu = st.tabs(["Data Ayah Kandung", "Data Ibu Kandung"])
        with t_ayah:
            ay1, ay2 = st.columns(2)
            n_ayah, nik_a = ay1.text_input("Nama Ayah Kandung"), ay2.text_input("NIK Ayah")
            tmp_a, tgl_a = ay1.text_input("Tempat Lahir Ayah"), ay2.date_input("Tgl Lahir Ayah", key="a_1")
            pend_a, pek_a = ay1.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA", "S1"]), ay2.text_input("Pekerjaan Ayah")
            gaji_a = st.number_input("Gaji Ayah", min_value=0)
        with t_ibu:
            ib1, ib2 = st.columns(2)
            n_ibu, nik_i = ib1.text_input("Nama Ibu Kandung"), ib2.text_input("NIK Ibu")
            tmp_i, tgl_i = ib1.text_input("Tempat Lahir Ibu"), ib2.date_input("Tgl Lahir Ibu", key="i_1")
            pend_i, pek_i = ib1.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA", "S1"]), ib2.text_input("Pekerjaan Ibu")
            gaji_i = st.number_input("Gaji Ibu", min_value=0)

        st.markdown('<div class="section-header">🏠 HALAMAN 3: DATA ALAMAT</div>', unsafe_allow_html=True)
        status_rmh = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak/Sewa", "Lainnya"])
        a1, a2 = st.columns(2)
        prov, kota = a1.text_input("Provinsi", value="Jawa Timur"), a2.text_input("Kab/Kota", value="Kediri")
        kec, desa = a1.text_input("Kecamatan"), a2.text_input("Kelurahan/Desa")
        alamat, pos = st.text_area("Alamat Lengkap"), st.text_input("Kode Pos")

        btn_submit = st.form_submit_button("✅ DAFTAR SEKARANG")
        if btn_submit:
            if nama and nik_s and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    wa_fix = no_wa.replace("08", "628", 1) if no_wa.startswith("08") else no_wa
                    data_final = [
                        reg_id, nama, nisn, nis_lokal, kwn, f"'{nik_s}", str(tgl_s), tmp_s, jk, saudara, anak_ke, agama, f"'{no_kk}", kepala_kk, wa_fix,
                        n_ayah, f"'{nik_a}", tmp_a, str(tgl_a), pend_a, pek_a, gaji_a, n_ibu, f"'{nik_i}", tmp_i, str(tgl_i), pend_i, pek_i, gaji_i,
                        status_rmh, prov, kota, kec, desa, alamat, pos, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"
                    ]
                    sheet.append_row(data_final)
                    st.success(f"Berhasil Terdaftar! No Reg: {reg_id}")
                    # Fitur WA
                    msg = urllib.parse.quote(f"Pendaftaran Ananda {nama} Berhasil. No Reg: {reg_id}")
                    st.markdown(f'<a href="https://wa.me/{wa_fix}?text={msg}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 KIRIM KONFIRMASI WA</button></a>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Error: {e}")

# --- MODUL 2: DASHBOARD ADMIN ---
elif menu == "📊 Dashboard Admin":
    if "admin_ok" not in st.session_state: st.session_state.admin_ok = False
    if not st.session_state.admin_ok:
        pw = st.text_input("Sandi Admin", type="password")
        if st.button("Masuk"):
            if pw == ADMIN_PASSWORD: st.session_state.admin_ok = True; st.rerun()
            else: st.error("Salah!")
        st.stop()
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(sheet.get_all_records()).astype(str).replace('nan', '')
        tab1, tab2 = st.tabs(["🔍 Monitoring", "📥 Import & Template"])
        with tab1:
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Ekspor CSV", df.to_csv(index=False).encode('utf-8'), "Data_PPDB.csv", "text/csv")
        with tab2:
            # Template Excel (Tetap 37 Kolom)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                pd.DataFrame(columns=KOLOM_DATABASE).to_excel(writer, index=False)
            st.download_button("📥 Download Template Excel", output.getvalue(), "Template_PPDB.xlsx")
            st.markdown("---")
            up = st.file_uploader("Upload Excel", type=['xlsx'])
            if up and st.button("Proses Import"):
                df_up = pd.read_excel(up)
                sheet.append_rows(df_up.astype(str).replace('nan', '').values.tolist())
                st.success("Import Berhasil!"); st.rerun()
    except Exception as e: st.error(f"Gagal memuat: {e}")
