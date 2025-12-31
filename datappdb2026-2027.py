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

# --- DATA LEMBAGA (UNTUK TAMPILAN PROFIL EMIS) ---
INFO_LEMBAGA = {
    "Nama": "RA AL IRSYAD AL ISLAMIYYAH",
    "NSM": "101235710017",
    "NPSN": "69749712",
    "Status": "Swasta",
    "Bentuk SP": "RA",
    "Kepala": "IMROATUS SOLIKHAH",
    "Alamat": "Jl. Letjend Suprapto No.21, Kel. Pakelan",
    "Kecamatan": "Kota",
    "Kabupaten": "Kota Kediri",
    "Provinsi": "Jawa Timur",
    "Kode Pos": "64129",
    "Telepon": "(0354) 682524",
    "Email": "ra.alirsyad.kediri@gmail.com"
}

# --- KLASTER GAMBAR (BASE64) ---
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

# --- 3. UI STYLING ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", page_icon="🏫", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #F8FAFC; }}
    .header-box {{ background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 25px; display: flex; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .emis-table {{ width: 100%; font-size: 14px; color: #334155; border-collapse: collapse; }}
    .emis-table td {{ padding: 10px 5px; border-bottom: 1px solid #F1F5F9; }}
    .label-emis {{ color: #64748B; font-weight: 500; width: 180px; }}
    .section-title {{ background-color: #F8FAFC; padding: 12px; font-weight: bold; border-bottom: 2px solid #E2E8F0; margin-bottom: 15px; color: #0284C7; }}
    .stForm {{ background-color: white; padding: 30px; border-radius: 12px; border: 1px solid #E2E8F0; }}
    </style>
""", unsafe_allow_html=True)

# Inisialisasi session state untuk galeri foto agar bisa diakses antar halaman
if 'temp_gallery' not in st.session_state:
    st.session_state['temp_gallery'] = []

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="110"></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.selectbox(
        "NAVIGASI UTAMA",
        ["🏠 Profil Sekolah", "📝 Pendaftaran Siswa Baru", "📸 Galeri Sekolah", "🔐 Panel Admin"]
    )
    st.markdown("---")
    st.markdown(f"**Lembaga:** {INFO_LEMBAGA['Nama']}")
    st.markdown(f"**Periode:** 2026/2027 Ganjil")

client = init_google_sheets()

# --- LOGIKA HALAMAN ---

if menu == "🏠 Profil Sekolah":
    st.markdown(f"""
    <div class="header-box">
        <img src="data:image/png;base64,{LOGO_BASE64}" width="90" style="margin-right:25px;">
        <div>
            <h2 style="margin:0; color:#1E293B; font-family: sans-serif;">{INFO_LEMBAGA['Nama']}</h2>
            <p style="margin:0; color:#64748B; font-size: 15px;">
                NSM: {INFO_LEMBAGA['NSM']} &nbsp; | &nbsp; STATUS: {INFO_LEMBAGA['Status']} &nbsp; | &nbsp; NPSN: {INFO_LEMBAGA['NPSN']}
            </p>
            <p style="margin-top:8px; font-size:14px; color: #0284C7;">📞 {INFO_LEMBAGA['Telepon']} &nbsp; | &nbsp; ✉️ {INFO_LEMBAGA['Email']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="background-color:white; padding:25px; border-radius:12px; border:1px solid #E2E8F0;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">INFORMASI UMUM LEMBAGA</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <table class="emis-table">
            <tr><td class="label-emis">KEPALA MADRASAH</td><td>: {INFO_LEMBAGA['Kepala']}</td></tr>
            <tr><td class="label-emis">NAMA PENYELENGGARA</td><td>: {INFO_LEMBAGA['Nama']} KOTA KEDIRI</td></tr>
            <tr><td class="label-emis">BENTUK PENDIDIKAN</td><td>: {INFO_LEMBAGA['Bentuk SP']}</td></tr>
            <tr><td class="label-emis">WAKTU BELAJAR</td><td>: Pagi / 6 Hari</td></tr>
        </table>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <table class="emis-table">
            <tr><td class="label-emis">ALAMAT LENGKAP</td><td>: {INFO_LEMBAGA['Alamat']}</td></tr>
            <tr><td class="label-emis">KECAMATAN / KOTA</td><td>: {INFO_LEMBAGA['Kecamatan']} / {INFO_LEMBAGA['Kabupaten']}</td></tr>
            <tr><td class="label-emis">PROVINSI</td><td>: {INFO_LEMBAGA['Provinsi']}</td></tr>
            <tr><td class="label-emis">KODE POS</td><td>: {INFO_LEMBAGA['Kode Pos']}</td></tr>
        </table>
        """, unsafe_allow_html=True)
    
    # --- TAMBAHAN: MENAMPILKAN FOTO DARI GALERI DI HALAMAN PROFIL ---
    if st.session_state['temp_gallery']:
        st.markdown('<br><div class="section-title">DOKUMENTASI KEGIATAN TERBARU</div>', unsafe_allow_html=True)
        cols_profile = st.columns(4) # Tampilan lebih kecil (4 kolom) untuk profil
        for idx, img_b64 in enumerate(st.session_state['temp_gallery']):
            with cols_profile[idx % 4]:
                st.image(f"data:image/png;base64,{img_b64}", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<h3 style="color: #0284C7;">Formulir Pendaftaran Peserta Didik Baru</h3>', unsafe_allow_html=True)
    
    with st.form("ppdb_full_form", clear_on_submit=True):
        st.markdown("##### I. IDENTITAS PESERTA DIDIK")
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap Siswa*")
        nisn = c2.text_input("NISN (Jika ada)")
        nis_lokal = c1.text_input("NIS Lokal")
        kewarganegaraan = c2.selectbox("Kewarganegaraan", ["WNI", "WNA"])
        nik_siswa = c1.text_input("NIK Siswa (16 Digit)*")
        tgl_lahir = c2.date_input("Tanggal Lahir", min_value=datetime(2010,1,1))
        tmp_lahir = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        jml_saudara = c1.number_input("Jumlah Saudara", min_value=0, step=1)
        anak_ke = c2.number_input("Anak Ke", min_value=1, step=1)
        agama = c1.selectbox("Agama", ["Islam"])
        no_kk = c2.text_input("Nomor Kartu Keluarga (KK)")
        nama_kepala_kk = c1.text_input("Nama Kepala Keluarga di KK")
        no_wa = c2.text_input("Nomor WhatsApp Wali (Contoh: 08123...)*")

        st.markdown("<br>##### II. DATA ORANG TUA KANDUNG", unsafe_allow_html=True)
        tab_ayah, tab_ibu = st.tabs(["Data Ayah", "Data Ibu"])
        
        with tab_ayah:
            ay1, ay2 = st.columns(2)
            n_ayah = ay1.text_input("Nama Ayah Kandung")
            nik_ayah = ay2.text_input("NIK Ayah")
            tmp_ayah = ay1.text_input("Tempat Lahir Ayah")
            tgl_ayah = ay2.date_input("Tanggal Lahir Ayah", key="tgl_ay", min_value=datetime(1950,1,1))
            pend_ayah = ay1.selectbox("Pendidikan Terakhir Ayah", ["SD", "SMP", "SMA", "D3", "S1", "S2", "S3"])
            pek_ayah = ay2.text_input("Pekerjaan Ayah")
            gaji_ayah = st.selectbox("Penghasilan Bulanan Ayah", ["< 1 Juta", "1 - 3 Juta", "3 - 5 Juta", "> 5 Juta"])

        with tab_ibu:
            ib1, ib2 = st.columns(2)
            n_ibu = ib1.text_input("Nama Ibu Kandung")
            nik_ibu = ib2.text_input("NIK Ibu")
            tmp_ibu = ib1.text_input("Tempat Lahir Ibu")
            tgl_ibu = ib2.date_input("Tanggal Lahir Ibu", key="tgl_ib", min_value=datetime(1950,1,1))
            pend_ibu = ib1.selectbox("Pendidikan Terakhir Ibu", ["SD", "SMP", "SMA", "D3", "S1", "S2", "S3"])
            pek_ibu = ib2.text_input("Pekerjaan Ibu")
            gaji_ibu = st.selectbox("Penghasilan Bulanan Ibu", ["< 1 Juta", "1 - 3 Juta", "3 - 5 Juta", "> 5 Juta"])

        st.markdown("<br>##### III. DATA DOMISILI / ALAMAT", unsafe_allow_html=True)
        status_rumah = st.selectbox("Status Tempat Tinggal", ["Milik Sendiri", "Rumah Orang Tua", "Sewa/Kontrak", "Lainnya"])
        al1, al2 = st.columns(2)
        provinsi = al1.text_input("Provinsi", value="Jawa Timur")
        kabupaten = al2.text_input("Kabupaten/Kota", value="Kediri")
        kecamatan = al1.text_input("Kecamatan")
        kelurahan = al2.text_input("Kelurahan/Desa")
        alamat_lengkap = st.text_area("Alamat Lengkap (Jalan, RT/RW, No. Rumah)")
        kode_pos = st.text_input("Kode Pos")

        submit = st.form_submit_button("KIRIM DATA PENDAFTARAN")
        
        if submit:
            if nama and nik_siswa and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    wa_fix = no_wa.replace("08", "628", 1) if no_wa.startswith("08") else no_wa
                    row_data = [
                        reg_id, nama, nisn, nis_lokal, kewarganegaraan, f"'{nik_siswa}", 
                        str(tgl_lahir), tmp_lahir, jk, jml_saudara, anak_ke, 
                        agama, f"'{no_kk}", nama_kepala_kk, wa_fix,
                        n_ayah, f"'{nik_ayah}", tmp_ayah, str(tgl_ayah), pend_ayah, pek_ayah, gaji_ayah,
                        n_ibu, f"'{nik_ibu}", tmp_ibu, str(tgl_ibu), pend_ibu, pek_ibu, gaji_ibu,
                        status_rumah, provinsi, kabupaten, kecamatan, kelurahan, alamat_lengkap, kode_pos,
                        datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"
                    ]
                    sheet.append_row(row_data)
                    st.success(f"✅ Data pendaftaran {nama} berhasil dikirim!")
                    pesan_wa = urllib.parse.quote(f"Assalamu'alaikum, Saya wali murid dari {nama}. No Reg: {reg_id}")
                    wa_url = f"https://wa.me/{wa_fix}?text={pesan_wa}"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:8px; cursor:pointer;">📲 Konfirmasi via WhatsApp</button></a>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">📸 GALERI KEGIATAN SISWA & GURU</div>', unsafe_allow_html=True)
    
    st.markdown("##### 📤 Tambah Foto Baru")
    uploaded_files = st.file_uploader("Pilih foto kegiatan (JPG/PNG)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    if st.button("Tampilkan di Galeri"):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.getvalue()
                encoded = base64.b64encode(bytes_data).decode()
                st.session_state['temp_gallery'].append(encoded)
            st.success(f"Berhasil mengunggah {len(uploaded_files)} foto.")
        else:
            st.warning("Silakan pilih file terlebih dahulu.")

    st.markdown("---")
    
    if st.session_state['temp_gallery']:
        cols = st.columns(3)
        for index, img_data in enumerate(st.session_state['temp_gallery']):
            with cols[index % 3]:
                st.image(f"data:image/png;base64,{img_data}", use_container_width=True)
    else:
        st.info("Belum ada foto yang diunggah. Silakan unggah foto di atas.")

elif menu == "🔐 Panel Admin":
    if "auth" not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        pw = st.text_input("Masukkan Password Admin", type="password")
        if st.button("Login"):
            if pw == ADMIN_PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Password Salah!")
        st.stop()
    
    st.markdown('<div class="section-title">DATABASE PENDAFTAR (ADMIN)</div>', unsafe_allow_html=True)
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        all_data = sheet.get_all_values()
        headers = all_data[0]
        rows = all_data[1:]
        df = pd.DataFrame(rows, columns=headers)

        tab_view, tab_edit = st.tabs(["🔍 Lihat Data", "✏️ Edit/Perbarui Data"])

        with tab_view:
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Ekspor CSV", csv, "Data_PPDB.csv", "text/csv")

        with tab_edit:
            st.subheader("Pilih Data yang Akan Diubah")
            search_query = st.text_input("Cari Berdasarkan Nama atau No Registrasi")
            
            if search_query:
                filtered_df = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]
                if not filtered_df.empty:
                    selected_reg = st.selectbox("Pilih No Registrasi untuk Diedit", filtered_df['No. Registrasi'].values)
                    row_index = df.index[df['No. Registrasi'] == selected_reg].tolist()[0] + 2
                    current_values = sheet.row_values(row_index)

                    with st.form("edit_form"):
                        st.info(f"Mengedit Data: {selected_reg}")
                        new_data = []
                        for i, col_name in enumerate(headers):
                            val = st.text_input(f"{col_name}", value=current_values[i] if i < len(current_values) else "")
                            new_data.append(val)
                        
                        btn_update = st.form_submit_button("💾 Simpan Perubahan")
                        if btn_update:
                            sheet.update(f"A{row_index}", [new_data])
                            st.success("✅ Data berhasil diperbarui!")
                            st.rerun()
                else:
                    st.warning("Data tidak ditemukan.")
    except Exception as e:
        st.error(f"Gagal memuat database: {e}")
