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

# Inisialisasi Session State agar data tetap sinkron antar halaman
if 'role' not in st.session_state:
    st.session_state['role'] = None 
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'temp_gallery' not in st.session_state:
    st.session_state['temp_gallery'] = []
if 'INFO_LEMBAGA' not in st.session_state:
    st.session_state['INFO_LEMBAGA'] = {
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
            id_file = url.split("id=")[-1].split("&")[0] if "id=" in url else url.split('/')[-2]
            url = f"https://drive.google.com/uc?export=download&id={id_file}"
        response = requests.get(url, timeout=10)
        return base64.b64encode(response.content).decode()
    except: return None

LOGO_LINK = "https://drive.google.com/file/d/1DOuK4dzVSLdzb8QewaFIzOL85IDWNP9P/view?usp=drive_link"
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
        st.error(f"Koneksi Gagal: {e}"); return None

# --- 3. UI STYLING ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", page_icon="🏫", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    .header-box { background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 25px; display: flex; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .emis-table { width: 100%; font-size: 14px; color: #334155; border-collapse: collapse; }
    .emis-table td { padding: 10px 5px; border-bottom: 1px solid #F1F5F9; }
    .label-emis { color: #64748B; font-weight: 500; width: 180px; }
    .section-title { background-color: #F8FAFC; padding: 12px; font-weight: bold; border-bottom: 2px solid #E2E8F0; margin-bottom: 15px; color: #0284C7; }
    .stForm { background-color: white; padding: 30px; border-radius: 12px; border: 1px solid #E2E8F0; }
    .gallery-desc { font-size: 13px; color: #475569; margin-top: 5px; text-align: center; font-style: italic; font-weight: bold; }
    .login-card { background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); max-width: 500px; margin: auto; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- HALAMAN LOGIN AWAL (GERBANG AKSES) ---
if st.session_state['role'] is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_BASE64:
            st.markdown(f'<img src="data:image/png;base64,{LOGO_BASE64}" width="120">', unsafe_allow_html=True)
        st.markdown("<h2>SISTEM INFORMASI PPDB</h2><h4>RA AL IRSYAD AL ISLAMIYYAH KEDIRI</h4><p>Silakan Pilih Akses Masuk</p>", unsafe_allow_html=True)
        col_login1, col_login2 = st.columns(2)
        if col_login1.button("👤 WALI MURID / USER"):
            st.session_state['role'] = 'user'
            st.rerun()
        if col_login2.button("🔑 ADMINISTRATOR"):
            st.session_state['role'] = 'admin_auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Validasi Password Khusus Admin
if st.session_state['role'] == 'admin_auth':
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("Login Administrator")
    pw_input = st.text_input("Masukkan Kata Sandi Admin", type="password")
    if st.button("Verifikasi & Masuk"):
        if pw_input == ADMIN_PASSWORD:
            st.session_state['role'] = 'admin'
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Kata Sandi Salah!")
    if st.button("⬅️ Kembali"):
        st.session_state['role'] = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- SIDEBAR NAVIGASI DINAMIS ---
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="110"></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#0284C7; font-weight:bold;'>MODE: {st.session_state['role'].upper()}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    nav_list = ["🏠 Profil Sekolah", "📝 Pendaftaran Siswa Baru", "📸 Galeri Sekolah"]
    if st.session_state['role'] == 'admin':
        nav_list.append("🔐 Panel Admin")
    menu = st.selectbox("NAVIGASI UTAMA", nav_list)
    st.markdown("---")
    if st.button("🚪 Log Out / Keluar"):
        st.session_state['role'] = None
        st.session_state['auth'] = False
        st.rerun()

client = init_google_sheets()

# --- LOGIKA HALAMAN ---

# 1. HALAMAN PROFIL
if menu == "🏠 Profil Sekolah":
    st.markdown(f"""
    <div class="header-box">
        <img src="data:image/png;base64,{LOGO_BASE64}" width="90" style="margin-right:25px;">
        <div>
            <h2 style="margin:0;">{st.session_state['INFO_LEMBAGA']['Nama']}</h2>
            <p style="margin:0; color:#64748B;">NSM: {st.session_state['INFO_LEMBAGA']['NSM']} | NPSN: {st.session_state['INFO_LEMBAGA']['NPSN']} | STATUS: {st.session_state['INFO_LEMBAGA']['Status']}</p>
            <p style="margin-top:5px; font-size:14px; color:#0284C7;">📞 {st.session_state['INFO_LEMBAGA']['Telepon']} | ✉️ {st.session_state['INFO_LEMBAGA']['Email']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="background-color:white; padding:25px; border-radius:12px; border:1px solid #E2E8F0;">', unsafe_allow_html=True)
    c_title, c_edit_btn = st.columns([4, 1])
    c_title.markdown('<div class="section-title">INFORMASI UMUM LEMBAGA</div>', unsafe_allow_html=True)
    
    if st.session_state['role'] == 'admin' and c_edit_btn.button("✏️ Edit Profil"):
        st.session_state['is_editing'] = True

    if st.session_state.get('is_editing', False) and st.session_state['role'] == 'admin':
        with st.form("edit_profil_form"):
            new_info = {}
            for k, v in st.session_state['INFO_LEMBAGA'].items():
                new_info[k] = st.text_input(f"Ubah {k}", value=v)
            if st.form_submit_button("💾 Simpan Perubahan"):
                st.session_state['INFO_LEMBAGA'].update(new_info)
                st.session_state['is_editing'] = False
                st.rerun()
            if st.form_submit_button("❌ Batal"):
                st.session_state['is_editing'] = False
                st.rerun()
    else:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">KEPALA MADRASAH</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
                <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
                <tr><td class="label-emis">KECAMATAN</td><td>: {st.session_state['INFO_LEMBAGA']['Kecamatan']}</td></tr>
            </table>""", unsafe_allow_html=True)
        with col_p2:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">PROVINSI</td><td>: {st.session_state['INFO_LEMBAGA']['Provinsi']}</td></tr>
                <tr><td class="label-emis">KABUPATEN</td><td>: {st.session_state['INFO_LEMBAGA']['Kabupaten']}</td></tr>
                <tr><td class="label-emis">KODE POS</td><td>: {st.session_state['INFO_LEMBAGA']['Kode Pos']}</td></tr>
            </table>""", unsafe_allow_html=True)

    if st.session_state['temp_gallery']:
        st.markdown('<br><div class="section-title">DOKUMENTASI KEGIATAN TERBARU</div>', unsafe_allow_html=True)
        cols_gal = st.columns(4)
        for idx, item in enumerate(st.session_state['temp_gallery']):
            with cols_gal[idx % 4]:
                st.image(f"data:image/png;base64,{item['img']}", use_container_width=True)
                st.markdown(f"<div class='gallery-desc'>{item['desc']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. HALAMAN PENDAFTARAN (LENGKAP 37 KOLOM DENGAN TAHUN 1945-2100)
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
        # RENTANG TAHUN 1945-2100
        tgl_lahir = c2.date_input("Tanggal Lahir*", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
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
            # RENTANG TAHUN 1945-2100
            tgl_ayah = ay2.date_input("Tanggal Lahir Ayah", key="tgl_ay", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            pend_ayah = ay1.selectbox("Pendidikan Terakhir Ayah", ["SD", "SMP", "SMA", "D3", "S1", "S2", "S3"])
            pek_ayah = ay2.text_input("Pekerjaan Ayah")
            gaji_ayah = st.selectbox("Penghasilan Bulanan Ayah", ["< 1 Juta", "1 - 3 Juta", "3 - 5 Juta", "> 5 Juta"])

        with tab_ibu:
            ib1, ib2 = st.columns(2)
            n_ibu = ib1.text_input("Nama Ibu Kandung")
            nik_ibu = ib2.text_input("NIK Ibu")
            tmp_ibu = ib1.text_input("Tempat Lahir Ibu")
            # RENTANG TAHUN 1945-2100
            tgl_ibu = ib2.date_input("Tanggal Lahir Ibu", key="tgl_ib", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
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
                    
                    # DATA LENGKAP 37 KOLOM
                    row_data = [
                        reg_id, nama, nisn, nis_lokal, kewarganegaraan, f"'{nik_siswa}", 
                        str(tgl_lahir), tmp_lahir, jk, jml_saudara, anak_ke, 
                        agama, f"'{no_kk}", nama_kepala_kk, wa_fix,
                        n_ayah, f"'{nik_ayah}", tmp_ayah, str(tgl_ayah), pend_ayah, pek_ayah, gaji_ayah,
                        n_ibu, f"'{nik_ibu}", tmp_ibu, str(tgl_ibu), pend_ibu, pek_ibu, gaji_ibu,
                        status_rumah, provinsi, kabupaten, kecamatan, kelurahan, alamat_lengkap, kode_pos,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Belum Diverifikasi"
                    ]
                    
                    sheet.append_row(row_data)
                    st.success(f"✅ Data pendaftaran {nama} berhasil dikirim!")
                    pesan_wa = urllib.parse.quote(f"Assalamu'alaikum, pendaftaran Ananda {nama} berhasil. No Reg: {reg_id}")
                    wa_url = f"https://wa.me/{wa_fix}?text={pesan_wa}"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:8px; cursor:pointer;">📲 Konfirmasi via WhatsApp</button></a>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Terjadi kesalahan: {e}")
            else: st.warning("Mohon isi semua kolom bertanda (*)")

# 3. HALAMAN GALERI
elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">📸 GALERI KEGIATAN SISWA & GURU</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Unggah Foto Baru (Khusus Admin)"):
            files = st.file_uploader("Pilih Gambar", type=['png','jpg','jpeg'], accept_multiple_files=True)
            desc_val = st.text_input("Keterangan Foto")
            if st.button("Simpan"):
                if files:
                    for f in files:
                        b64 = base64.b64encode(f.getvalue()).decode()
                        st.session_state['temp_gallery'].append({"img": b64, "desc": desc_val if desc_val else "Kegiatan Sekolah"})
                    st.rerun()
    if st.session_state['temp_gallery']:
        cols = st.columns(3)
        for i, itm in enumerate(st.session_state['temp_gallery']):
            with cols[i % 3]:
                st.image(f"data:image/png;base64,{itm['img']}", use_container_width=True)
                st.markdown(f"<div class='gallery-desc'>{itm['desc']}</div>", unsafe_allow_html=True)
    else: st.info("Belum ada foto kegiatan.")

# 4. PANEL ADMIN
elif menu == "🔐 Panel Admin":
    st.markdown('<div class="section-title">DATABASE PENDAFTAR (ADMIN)</div>', unsafe_allow_html=True)
    try:
        sheet = client.open(SHEET_NAME).sheet1
        all_data = sheet.get_all_values()
        headers, rows = all_data[0], all_data[1:]
        df = pd.DataFrame(rows, columns=headers)
        tab_v, tab_e = st.tabs(["🔍 Monitoring", "✏️ Edit Data"])
        with tab_v: st.dataframe(df, use_container_width=True)
        with tab_e:
            search = st.text_input("Cari Nama/Reg")
            if search:
                res = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
                if not res.empty:
                    sel = st.selectbox("Pilih No Reg", res['No. Registrasi'].values)
                    idx = df.index[df['No. Registrasi'] == sel].tolist()[0] + 2
                    curr = sheet.row_values(idx)
                    with st.form("edit_adm"):
                        upd = [st.text_input(f"{h}", value=curr[i] if i < len(curr) else "") for i, h in enumerate(headers)]
                        if st.form_submit_button("Simpan"):
                            sheet.update(f"A{idx}", [upd])
                            st.success("Data Diperbarui!"); st.rerun()
    except: st.error("Gagal memuat database.")
