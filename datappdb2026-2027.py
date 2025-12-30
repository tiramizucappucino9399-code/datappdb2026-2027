import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os
from datetime import date

# --- 1. KONFIGURASI SISTEM ---
FOLDER_DRIVE_ID = "1VKgQOAlc1WeZlTRIc4AlotswD0EQjCuI" 
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 

# --- 2. FUNGSI KONEKSI CLOUD ---
@st.cache_resource
def init_google_services():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
        'https://spreadsheets.google.com/feeds'
    ]
    
    try:
        if "gcp_service_account" in st.secrets:
            # Mode Streamlit Cloud
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            # Mode Lokal
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        
        # Koneksi Sheets
        client = gspread.authorize(creds)
        
        # Koneksi Drive
        gauth = GoogleAuth()
        gauth.credentials = creds
        drive = GoogleDrive(gauth)
        
        return client, drive
    except Exception as e:
        st.error(f"Koneksi Gagal: {e}")
        return None, None

# --- 3. TAMPILAN ANTARMUKA ---
st.set_page_config(page_title="PPDB KB-RA AL IRSYAD KEDIRI", page_icon="🏫", layout="wide")

st.markdown("""
    <style>
    .main-header {text-align: center; background-color: #1E5128; padding: 20px; border-radius: 10px; color: white;}
    </style>
    <div class="main-header">
        <h1>FORMULIR PENDATAAN MURID BARU</h1>
        <h3>KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI</h3>
        <p>Tahun Ajaran 2026-2027</p>
    </div>
    <br>
""", unsafe_allow_html=True)

client, drive = init_google_services()

if client:
    st.sidebar.success("✅ Database Terhubung")
else:
    st.sidebar.error("❌ Database Terputus")
    st.stop()

menu = st.sidebar.radio("MENU UTAMA", ["📝 Pendaftaran Murid", "📊 Dashboard Admin"])

# --- MODUL 1: PENDAFTARAN ---
if menu == "📝 Pendaftaran Murid":
    with st.form("ppdb_form", clear_on_submit=True):
        st.subheader("📑 I. DATA SISWA")
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap")
        nisn = c2.text_input("NISN (Jika Ada)")
        nis_lokal = c1.text_input("NIS Lokal")
        kwn = c2.text_input("Kewarganegaraan", value="WNI")
        nik_s = c1.text_input("NIK Siswa")
        tgl_s = c2.date_input("Tanggal Lahir", min_value=date(2015,1,1))
        tmp_s = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = c1.number_input("Jumlah Saudara", min_value=0, step=1)
        anak_ke = c2.number_input("Anak Ke", min_value=1, step=1)
        agama = c1.selectbox("Agama", ["Islam"])
        no_kk = c1.text_input("No. Kartu Keluarga (KK)")
        kepala_kk = c2.text_input("Nama Kepala Keluarga")
        file_kk = st.file_uploader("Upload KK (PDF, JPG, PNG) - Max 2MB", type=['pdf', 'jpg', 'png'])

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("👨‍👩‍👧‍👦 II. DATA KELUARGA")
        t1, t2 = st.tabs(["Data Ayah Kandung", "Data Ibu Kandung"])
        with t1:
            n_ayah = st.text_input("Nama Ayah")
            nik_a = st.text_input("NIK Ayah")
            tmp_a = st.text_input("Tempat Lahir Ayah")
            tgl_a = st.date_input("Tanggal Lahir Ayah", key="ay1")
            pend_a = st.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA/K", "D3", "S1", "S2", "S3"])
            pek_a = st.text_input("Pekerjaan Utama Ayah")
            gaji_a = st.number_input("Penghasilan Ayah (Rp)", min_value=0, step=100000)
        with t2:
            n_ibu = st.text_input("Nama Ibu")
            nik_i = st.text_input("NIK Ibu")
            tmp_i = st.text_input("Tempat Lahir Ibu")
            tgl_i = st.date_input("Tanggal Lahir Ibu", key="ib1")
            pend_i = st.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA/K", "D3", "S1", "S2", "S3"])
            pek_i = st.text_input("Pekerjaan Utama Ibu")
            gaji_i = st.number_input("Penghasilan Ibu (Rp)", min_value=0, step=100000)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🏠 III. DATA ALAMAT")
        status_rmh = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak/Sewa", "Lainnya"])
        ca1, ca2 = st.columns(2)
        prov = ca1.text_input("Provinsi", value="Jawa Timur")
        kota = ca2.text_input("Kabupaten/Kota", value="Kediri")
        kec = ca1.text_input("Kecamatan")
        desa = ca2.text_input("Kelurahan/Desa")
        alamat = st.text_area("Alamat Lengkap")
        pos = st.text_input("Kode Pos")

        btn_submit = st.form_submit_button("✅ KIRIM DATA PENDAFTARAN")

    if btn_submit:
        if file_kk and nama and nik_s:
            try:
                with st.spinner("Sedang memproses data..."):
                    # 1. Proses File & Upload ke Drive
                    ext = os.path.splitext(file_kk.name)[1]
                    fname = f"KK_{nama}_{nik_s}{ext}".replace(" ", "_")
                    
                    with open(fname, "wb") as f:
                        f.write(file_kk.getbuffer())
                    
                    # PERBAIKAN: Menambahkan supportsAllDrives untuk mengatasi quota 0 service account
                    gfile = drive.CreateFile({'title': fname, 'parents': [{'id': FOLDER_DRIVE_ID}]})
                    gfile.SetContentFile(fname)
                    gfile.Upload(param={'supportsAllDrives': True}) 
                    
                    gfile.InsertPermission({'type': 'anyone', 'value': 'anyone', 'role': 'reader'})
                    link_kk = gfile['alternateLink']
                    
                    # Hapus file lokal setelah upload
                    if os.path.exists(fname):
                        os.remove(fname)

                    # 2. Simpan ke Google Sheets
                    sheet = client.open(SHEET_NAME).sheet1
                    data_final = [
                        nama, nisn, nis_lokal, kwn, nik_s, str(tgl_s), tmp_s, jk, saudara, anak_ke, agama,
                        no_kk, kepala_kk, n_ayah, nik_a, tmp_a, str(tgl_a), pend_a, pek_a, gaji_a,
                        n_ibu, nik_i, tmp_i, str(tgl_i), pend_i, pek_i, gaji_i,
                        status_rmh, prov, kota, kec, desa, alamat, pos, link_kk, str(date.today())
                    ]
                    sheet.append_row(data_final)
                    
                    st.balloons()
                    st.success(f"Alhamdulillah, pendaftaran ananda {nama} berhasil disimpan!")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("⚠️ Mohon lengkapi Nama, NIK, dan Upload file KK!")

# --- MODUL 2: DASHBOARD ADMIN ---
elif menu == "📊 Dashboard Admin":
    st.subheader("📊 Analisis Data Pendaftar")
    try:
        sheet = client.open(SHEET_NAME).sheet1
        records = sheet.get_all_records()
        
        if records:
            data = pd.DataFrame(records)
            
            # Statistik
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Pendaftar", len(data))
            if 'Jenis Kelamin' in data.columns:
                m2.metric("Laki-laki", len(data[data['Jenis Kelamin'] == 'Laki-laki']))
                m3.metric("Perempuan", len(data[data['Jenis Kelamin'] == 'Perempuan']))

            st.markdown("---")
            search = st.text_input("🔍 Cari Nama Murid...")
            if search:
                data = data[data['Nama Lengkap'].astype(str).str.contains(search, case=False)]
            
            st.dataframe(data, use_container_width=True)
            
            csv = data.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Excel (CSV)", data=csv, file_name=f"PPDB_Export_{date.today()}.csv", mime="text/csv")
        else:
            st.info("Belum ada data di database.")
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
