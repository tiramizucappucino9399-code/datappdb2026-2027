import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import io
from datetime import datetime
import urllib.parse

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" # Silakan ganti sesuai keinginan

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

# --- 3. STANDARISASI KOLOM (TOTAL 37 KOLOM) ---
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

st.markdown("""
    <style>
    .main-header {text-align: center; background-color: #1E5128; padding: 25px; border-radius: 10px; color: white; margin-bottom: 25px;}
    .stButton>button {width: 100%; border-radius: 8px; height: 3.5em; background-color: #1E5128; color: white; font-weight: bold;}
    .section-header {background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #1E5128; font-weight: bold;}
    </style>
    <div class="main-header">
        <h1>SISTEM INFORMASI PPDB & NOTIFIKASI</h1>
        <h3>KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI</h3>
        <p>Tahun Ajaran 2026-2027</p>
    </div>
""", unsafe_allow_html=True)

client = init_google_sheets()
if not client: st.stop()

menu = st.sidebar.radio("MENU UTAMA", ["📝 Pendaftaran Murid", "📊 Dashboard Admin"])

# --- MODUL 1: PENDAFTARAN ---
if menu == "📝 Pendaftaran Murid":
    with st.form("ppdb_form", clear_on_submit=True):
        
        # HALAMAN 1: DATA SISWA
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
        no_wa = c2.text_input("Nomor WhatsApp Aktif (Contoh: 08123...)*")

        # HALAMAN 2: DATA KELUARGA
        st.markdown('<div class="section-header">👨‍👩‍👧‍👦 HALAMAN 2: DATA KELUARGA</div>', unsafe_allow_html=True)
        t_ayah, t_ibu = st.tabs(["Data Ayah Kandung", "Data Ibu Kandung"])
        
        with t_ayah:
            ay1, ay2 = st.columns(2)
            n_ayah = ay1.text_input("Nama Ayah Kandung")
            nik_a = ay2.text_input("NIK Ayah Kandung")
            tmp_a = ay1.text_input("Tempat Lahir Ayah")
            tgl_a = ay2.date_input("Tanggal Lahir Ayah", key="t_ay")
            pend_a = ay1.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA/K", "D3", "S1", "S2", "S3"])
            pek_a = ay2.text_input("Pekerjaan Utama Ayah")
            gaji_a = st.number_input("Penghasilan Ayah (Rp)", min_value=0, step=100000)

        with t_ibu:
            ib1, ib2 = st.columns(2)
            n_ibu = ib1.text_input("Nama Ibu Kandung")
            nik_i = ib2.text_input("NIK Ibu Kandung")
            tmp_i = ib1.text_input("Tempat Lahir Ibu")
            tgl_i = ib2.date_input("Tanggal Lahir Ibu", key="t_ib")
            pend_i = ib1.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA/K", "D3", "S1", "S2", "S3"])
            pek_i = ib2.text_input("Pekerjaan Utama Ibu")
            gaji_i = st.number_input("Penghasilan Ibu (Rp)", min_value=0, step=100000)

        # HALAMAN 3: DATA ALAMAT
        st.markdown('<div class="section-header">🏠 HALAMAN 3: DATA ALAMAT</div>', unsafe_allow_html=True)
        status_rmh = st.selectbox("Status Kepemilikan Rumah", ["Milik Sendiri", "Kontrak/Sewa", "Lainnya"])
        a1, a2 = st.columns(2)
        prov = a1.text_input("Provinsi", value="Jawa Timur")
        kota = a2.text_input("Kabupaten/Kota", value="Kediri")
        kec = a1.text_input("Kecamatan")
        desa = a2.text_input("Kelurahan/Desa")
        alamat = st.text_area("Alamat Lengkap")
        pos = st.text_input("Kode Pos")

        btn_submit = st.form_submit_button("✅ DAFTAR SEKARANG")

    if btn_submit:
        if nama and nik_s and no_wa:
            try:
                sheet = client.open(SHEET_NAME).sheet1
                reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                wa_fix = no_wa.replace("08", "628", 1) if no_wa.startswith("08") else no_wa
                
                data_final = [
                    reg_id, nama, nisn, nis_lokal, kwn, f"'{nik_s}", 
                    str(tgl_s), tmp_s, jk, saudara, anak_ke, agama, f"'{no_kk}", kepala_kk, wa_fix,
                    n_ayah, f"'{nik_a}", tmp_a, str(tgl_a), pend_a, pek_a, gaji_a,
                    n_ibu, f"'{nik_i}", tmp_i, str(tgl_i), pend_i, pek_i, gaji_i,
                    status_rmh, prov, kota, kec, desa, alamat, pos,
                    datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"
                ]
                sheet.append_row(data_final)
                
                st.success(f"Berhasil Terdaftar! No. Registrasi: {reg_id}")
                
                # Link WhatsApp Otomatis
                pesan = f"Konfirmasi PPDB KB-RA AL IRSYAD KEDIRI\n\nAlhamdulillah, data Ananda *{nama}* telah masuk ke sistem.\nNo. Registrasi: *{reg_id}*\n\nMohon simpan pesan ini."
                wa_url = f"https://wa.me/{wa_fix}?text={urllib.parse.quote(pesan)}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 KIRIM KONFIRMASI KE WHATSAPP SAYA</button></a>', unsafe_allow_html=True)
                st.balloons()
            except Exception as e: st.error(f"Gagal simpan: {e}")
        else: st.warning("Mohon lengkapi Nama, NIK, dan Nomor WhatsApp!")

# --- MODUL 2: DASHBOARD ADMIN ---
elif menu == "📊 Dashboard Admin":
    if "logged_in" not in st.session_state: st.session_state.logged_in = False

    if not st.session_state.logged_in:
        pw = st.text_input("Password Admin", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Salah!")
        st.stop()
    
    if st.sidebar.button("Logout Admin"):
        st.session_state.logged_in = False
        st.rerun()

    try:
        sheet = client.open(SHEET_NAME).sheet1
        data = pd.DataFrame(sheet.get_all_records()).astype(str).replace('nan', '')
        
        tab1, tab2 = st.tabs(["🔍 Monitoring Data", "📥 Import & Template Excel"])
        
        with tab1:
            st.metric("Total Pendaftar", len(data))
            search = st.text_input("Cari Nama...")
            if search: data = data[data['Nama Lengkap'].str.contains(search, case=False)]
            st.dataframe(data, use_container_width=True)
            st.download_button("📥 Download CSV", data.to_csv(index=False).encode('utf-8'), "Data_PPDB.csv", "text/csv")

        with tab2:
            # Download Template
            df_temp = pd.DataFrame(columns=KOLOM_DATABASE)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_temp.to_excel(writer, index=False)
            st.download_button("📥 1. Download Template Excel", buffer.getvalue(), "Template_PPDB.xlsx")
            
            st.markdown("---")
            # Upload Excel
            file_ex = st.file_uploader("📥 2. Upload Data Excel", type=['xlsx'])
            if file_ex:
                df_up = pd.read_excel(file_ex)
                if st.button("Konfirmasi Import"):
                    if list(df_up.columns) == KOLOM_DATABASE:
                        sheet.append_rows(df_up.astype(str).replace('nan', '').values.tolist())
                        st.success("Berhasil Import!"); st.rerun()
                    else: st.error("Judul Kolom Excel Tidak Sesuai Template!")
                    
    except Exception as e: st.error(f"Gagal muat data: {e}")
