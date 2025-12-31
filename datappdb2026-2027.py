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

# --- KONFIGURASI ALAMAT & PETA SEKOLAH ---
ALAMAT_SEKOLAH = {
    "Nama": "KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI",
    "Jalan": "Jl. Letjend Suprapto No.21, Kel. Pakelan, Kec. Kota",
    "Kota": "Kota Kediri, Jawa Timur",
    "Kodepos": "64129",
    "Telepon": "(0354) 682524",
    # Link Embed Google Maps (Pastikan menggunakan link embed/iframe)
    "Maps_Embed": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m12!1m12!1m3!1d3952.66585141203!2d112.012526!3d-7.825217!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e78570420000001%3A0x6b80170a4a58b27!2sKB-RA%20AL%20IRSYAD%20AL%20ISLAMIIYAH!5e0!3m2!1sid!2sid!4v1700000000000"
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

# Tambahkan link foto kegiatan Anda di sini (Pastikan sharing "Anyone with the link can view")
LIST_FOTO_KEGIATAN = [
    "https://drive.google.com/file/d/LINK_FOTO_1/view",
    "https://drive.google.com/file/d/LINK_FOTO_2/view"
]

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

# --- 4. TAMPILAN ---
st.set_page_config(page_title="PPDB AL IRSYAD KEDIRI", page_icon="🏫", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f4f7f6; }}
    .main-header {{ text-align: center; background-color: #1E5128; padding: 25px; border-radius: 15px; color: white; margin-bottom: 25px; }}
    .section-header {{ background-color: #ffffff; padding: 12px; border-radius: 8px; margin-top: 20px; margin-bottom: 10px; border-left: 8px solid #1E5128; font-weight: bold; }}
    .contact-box {{ background-color: #e8f5e9; padding: 15px; border-radius: 10px; border: 1px solid #1E5128; margin-top: 20px; font-size: 14px; line-height: 1.6; }}
    </style>
""", unsafe_allow_html=True)

# Header Utama
if LOGO_BASE64:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="120"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-header"><h1>SISTEM INFORMASI PPDB ONLINE</h1><h3>{ALAMAT_SEKOLAH["Nama"]}</h3><p>Tahun Ajaran 2026-2027</p></div>', unsafe_allow_html=True)

# --- SIDEBAR (Perbaikan Navigasi, Alamat & Peta) ---
with st.sidebar:
    if LOGO_BASE64:
        st.image(f"data:image/png;base64,{LOGO_BASE64}", use_container_width=True)
    st.markdown("---")
    menu = st.radio("MENU UTAMA", ["📝 Pendaftaran Murid", "🖼️ Galeri Sekolah", "📊 Dashboard Admin"])
    
    st.markdown(f"""
        <div class="contact-box">
            <b>📍 Lokasi & Kontak Sekolah:</b><br>
            {ALAMAT_SEKOLAH["Jalan"]}<br>
            {ALAMAT_SEKOLAH["Kota"]}, {ALAMAT_SEKOLAH["Kodepos"]}<br>
            <b>Telepon:</b> {ALAMAT_SEKOLAH["Telepon"]}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<b>🗺️ Peta Lokasi:</b>", unsafe_allow_html=True)
    # PERBAIKAN DI SINI: Pemanggilan iframe yang benar
    st.components.v1.iframe(ALAMAT_SEKOLAH["Maps_Embed"], height=250)

client = init_google_sheets()
if not client: st.stop()

# --- MODUL 1: PENDAFTARAN ---
if menu == "📝 Pendaftaran Murid":
    with st.form("ppdb_form", clear_on_submit=True):
        st.markdown('<div class="section-header">📑 HALAMAN 1: DATA SISWA (Rentang 1945-2100)</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap Siswa*")
        nisn = c2.text_input("NISN")
        nis_lokal = c1.text_input("NIS Lokal")
        kwn = c2.text_input("Kewarganegaraan", value="WNI")
        nik_s = c1.text_input("NIK Siswa (16 Digit)*")
        tgl_s = c2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
        tmp_s = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = c1.number_input("Jumlah Saudara", min_value=0, step=1)
        anak_ke = c2.number_input("Anak Ke", min_value=1, step=1)
        agama = c1.selectbox("Agama", ["Islam"])
        no_kk = c2.text_input("No. Kartu Keluarga (KK)")
        kepala_kk = c1.text_input("Nama Kepala Keluarga")
        no_wa = c2.text_input("Nomor WhatsApp Wali (Mulai 08...)*")

        st.markdown('<div class="section-header">👨‍👩‍👧‍👦 HALAMAN 2: DATA KELUARGA</div>', unsafe_allow_html=True)
        t_ay, t_ib = st.tabs(["Data Ayah", "Data Ibu"])
        with t_ay:
            ay1, ay2 = st.columns(2)
            n_ayah, nik_a = ay1.text_input("Nama Ayah"), ay2.text_input("NIK Ayah")
            tmp_a = ay1.text_input("Tempat Lahir Ayah")
            tgl_a = ay2.date_input("Tgl Lahir Ayah", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31), key="a_1")
            pend_a, pek_a = ay1.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA/K", "S1", "S2"]), ay2.text_input("Pekerjaan Ayah")
            gaji_a = st.number_input("Gaji Ayah", min_value=0)
        with t_ib:
            ib1, ib2 = st.columns(2)
            n_ibu, nik_i = ib1.text_input("Nama Ibu"), ib2.text_input("NIK Ibu")
            tmp_i = ib1.text_input("Tempat Lahir Ibu")
            tgl_i = ib2.date_input("Tgl Lahir Ibu", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31), key="i_1")
            pend_i, pek_i = ib1.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA/K", "S1", "S2"]), ib2.text_input("Pekerjaan Ibu")
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
                    
                    # Data final (37 Kolom)
                    data_final = [
                        reg_id, nama, nisn, nis_lokal, kwn, f"'{nik_s}", str(tgl_s), tmp_s, jk, saudara, anak_ke, 
                        agama, f"'{no_kk}", kepala_kk, wa_fix, n_ayah, f"'{nik_a}", tmp_a, str(tgl_a), pend_a, 
                        pek_a, gaji_a, n_ibu, f"'{nik_i}", tmp_i, str(tgl_i), pend_i, pek_i, gaji_i,
                        status_rmh, prov, kota, "", "", alamat, pos, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"
                    ]
                    sheet.append_row(data_final)
                    st.success(f"Berhasil! No Reg: {reg_id}")
                    # Konfirmasi WA
                    pesan = urllib.parse.quote(f"Pendaftaran Ananda {nama} berhasil.\nNo Reg: {reg_id}")
                    st.markdown(f'<a href="https://wa.me/{wa_fix}?text={pesan}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; padding:15px; border-radius:8px; border:none; font-weight:bold; cursor:pointer;">📲 KIRIM KONFIRMASI WA</button></a>', unsafe_allow_html=True)
                    st.balloons()
                except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Nama, NIK, dan WA wajib diisi!")

# --- MODUL 2: GALERI ---
elif menu == "🖼️ Galeri Sekolah":
    st.markdown('<div class="section-header">📸 DOKUMENTASI KEGIATAN SEKOLAH</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, link in enumerate(LIST_FOTO_KEGIATAN):
        img = get_image_base64(link)
        if img: cols[idx % 3].image(f"data:image/png;base64,{img}", use_container_width=True)

# --- MODUL 3: ADMIN ---
elif menu == "📊 Dashboard Admin":
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pw = st.text_input("Sandi Admin", type="password")
        if st.button("Masuk"):
            if pw == ADMIN_PASSWORD: st.session_state.auth = True; st.rerun()
            else: st.error("Salah!")
        st.stop()
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(sheet.get_all_records()).astype(str).replace('nan', '')
        tab1, tab2 = st.tabs(["🔍 Monitoring Data", "📥 Import & Template Excel"])
        with tab1:
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Ekspor CSV", df.to_csv(index=False).encode('utf-8'), "Data_PPDB.csv", "text/csv")
        with tab2:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
                pd.DataFrame(columns=KOLOM_DATABASE).to_excel(wr, index=False)
            st.download_button("📥 Unduh Template", buf.getvalue(), "Template_PPDB.xlsx")
            up = st.file_uploader("Upload Excel", type=['xlsx'])
            if up and st.button("Proses Import"):
                sheet.append_rows(pd.read_excel(up).astype(str).replace('nan', '').values.tolist())
                st.success("Import Berhasil!"); st.rerun()
    except Exception as e: st.error(f"Error: {e}")
