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

# Inisialisasi Session State
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

# SILAKAN GANTI LINK INI DENGAN LINK GAMBAR BACKGROUND ANDA
BG_LINK = "https://drive.google.com/file/d/1XW_CONTOH_LINK_BG_ANDA/view" 
BG_BASE64 = get_image_base64(BG_LINK)

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

# CSS UNTUK BACKGROUND LOGIN DAN STYLING UMUM
bg_css = f"""
<style>
    .stApp {{
        background-color: #F8FAFC;
    }}
    
    /* Login Background Overlay */
    .login-bg {{
        background-image: linear-gradient(rgba(2, 132, 199, 0.8), rgba(2, 132, 199, 0.8)), url("data:image/png;base64,{BG_BASE64}");
        background-size: cover;
        background-position: center;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
    }}

    .header-box {{ background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 25px; display: flex; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .emis-table {{ width: 100%; font-size: 14px; color: #334155; border-collapse: collapse; }}
    .emis-table td {{ padding: 10px 5px; border-bottom: 1px solid #F1F5F9; }}
    .label-emis {{ color: #64748B; font-weight: 500; width: 180px; }}
    .section-title {{ background-color: #F8FAFC; padding: 12px; font-weight: bold; border-bottom: 2px solid #E2E8F0; margin-bottom: 15px; color: #0284C7; }}
    .stForm {{ background-color: white; padding: 30px; border-radius: 12px; border: 1px solid #E2E8F0; }}
    .gallery-desc {{ font-size: 13px; color: #475569; margin-top: 5px; text-align: center; font-style: italic; font-weight: bold; }}
    .login-card {{ background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); max-width: 500px; margin: auto; text-align: center; }}
</style>
"""
st.markdown(bg_css, unsafe_allow_html=True)

# --- HALAMAN LOGIN AWAL ---
if st.session_state['role'] is None:
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True) # Pasang Background Khusus Login
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_BASE64:
            st.markdown(f'<img src="data:image/png;base64,{LOGO_BASE64}" width="120">', unsafe_allow_html=True)
        st.markdown("<h1 style='color:#0284C7; margin-bottom:0;'>PPDB ONLINE</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#64748B;'>RA AL IRSYAD AL ISLAMIYYAH KEDIRI</h4><hr>", unsafe_allow_html=True)
        st.markdown("<p style='font-weight:bold;'>Silakan Pilih Akses Masuk:</p>", unsafe_allow_html=True)
        
        col_l1, col_l2 = st.columns(2)
        if col_l1.button("👤 WALI MURID / USER", use_container_width=True):
            st.session_state['role'] = 'user'
            st.rerun()
        if col_l2.button("🔑 ADMINISTRATOR", use_container_width=True):
            st.session_state['role'] = 'admin_auth'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Validasi Admin Auth
if st.session_state['role'] == 'admin_auth':
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("Akses Administrator")
    pw_input = st.text_input("Masukkan Kata Sandi Admin", type="password")
    c_log1, c_log2 = st.columns(2)
    if c_log1.button("✅ Verifikasi", use_container_width=True):
        if pw_input == ADMIN_PASSWORD:
            st.session_state['role'] = 'admin'
            st.session_state['auth'] = True
            st.rerun()
        else: st.error("Kata Sandi Salah!")
    if c_log2.button("⬅️ Kembali", use_container_width=True):
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
    if st.session_state['role'] == 'admin': nav_list.append("🔐 Panel Admin")
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
            new_info = {k: st.text_input(f"Ubah {k}", value=v) for k, v in st.session_state['INFO_LEMBAGA'].items()}
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

# 2. HALAMAN PENDAFTARAN (LENGKAP 37 KOLOM & TAHUN 1945-2100)
elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<h3 style="color: #0284C7;">Formulir Pendaftaran Peserta Didik Baru</h3>', unsafe_allow_html=True)
    with st.form("ppdb_full_form", clear_on_submit=True):
        st.markdown("##### I. IDENTITAS PESERTA DIDIK")
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap Siswa*")
        nisn = c2.text_input("NISN")
        nis_lokal = c1.text_input("NIS Lokal")
        kwn = c2.selectbox("Kewarganegaraan", ["WNI", "WNA"])
        nik_s = c1.text_input("NIK Siswa (16 Digit)*")
        tgl_s = c2.date_input("Tanggal Lahir*", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
        tmp_s = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = c1.number_input("Jumlah Saudara", min_value=0, step=1)
        anak_ke = c2.number_input("Anak Ke", min_value=1, step=1)
        agama = c1.selectbox("Agama", ["Islam"])
        no_kk = c2.text_input("Nomor Kartu Keluarga (KK)")
        nama_kepala_kk = c1.text_input("Nama Kepala Keluarga di KK")
        no_wa = c2.text_input("Nomor WhatsApp Wali (08...)*")

        st.markdown("<br>##### II. DATA ORANG TUA KANDUNG", unsafe_allow_html=True)
        tab_ay, tab_ib = st.tabs(["Data Ayah", "Data Ibu"])
        with tab_ay:
            ay1, ay2 = st.columns(2)
            n_ay = ay1.text_input("Nama Ayah Kandung")
            nik_ay = ay2.text_input("NIK Ayah")
            tmp_ay = ay1.text_input("Tempat Lahir Ayah")
            tgl_ay = ay2.date_input("Tgl Lahir Ayah", key="ay", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            pend_ay = ay1.selectbox("Pendidikan Ayah", ["SD", "SMP", "SMA", "S1", "S2", "S3"])
            pek_ay = ay2.text_input("Pekerjaan Ayah")
            gaj_ay = st.selectbox("Gaji Ayah", ["< 1 Juta", "1-3 Juta", "> 3 Juta"])
        with tab_ib:
            ib1, ib2 = st.columns(2)
            n_ib = ib1.text_input("Nama Ibu Kandung")
            nik_ib = ib2.text_input("NIK Ibu")
            tmp_ib = ib1.text_input("Tempat Lahir Ibu")
            tgl_ib = ib2.date_input("Tgl Lahir Ibu", key="ib", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            pend_ib = ib1.selectbox("Pendidikan Ibu", ["SD", "SMP", "SMA", "S1", "S2", "S3"])
            pek_ib = ib2.text_input("Pekerjaan Ibu")
            gaj_ib = st.selectbox("Gaji Ibu", ["< 1 Juta", "1-3 Juta", "> 3 Juta"])

        st.markdown("<br>##### III. DATA ALAMAT", unsafe_allow_html=True)
        st_rumah = st.selectbox("Status Rumah", ["Milik Sendiri", "Sewa/Kontrak", "Lainnya"])
        al1, al2 = st.columns(2)
        prov = al1.text_input("Provinsi", value="Jawa Timur")
        kota = al2.text_input("Kota", value="Kediri")
        kec = al1.text_input("Kecamatan")
        kel = al2.text_input("Kelurahan/Desa")
        alamat = st.text_area("Alamat Lengkap")
        kode_pos = st.text_input("Kode Pos")

        if st.form_submit_button("✅ KIRIM PENDAFTARAN"):
            if nama and nik_s and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    row = [reg_id, nama, nisn, nis_lokal, kwn, f"'{nik_s}", str(tgl_s), tmp_s, jk, saudara, anak_ke, agama, f"'{no_kk}", nama_kepala_kk, no_wa, n_ay, f"'{nik_ay}", tmp_ay, str(tgl_ay), pend_ay, pek_ay, gaj_ay, n_ib, f"'{nik_ib}", tmp_ib, str(tgl_ib), pend_ib, pek_ib, gaj_ib, st_rumah, prov, kota, kec, kel, alamat, kode_pos, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"]
                    sheet.append_row(row)
                    st.success(f"Berhasil! No Reg: {reg_id}")
                    wa_url = f"https://wa.me/{no_wa}?text=Pendaftaran%20Ananda%20{nama}%20Berhasil"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; padding:10px 20px; border-radius:8px; border:none; cursor:pointer;">📲 Konfirmasi WA</button></a>', unsafe_allow_html=True)
                except: st.error("Database Gagal.")
            else: st.warning("Isi semua data wajib (*)")

# 3. HALAMAN GALERI
elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">📸 GALERI KEGIATAN</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Unggah Foto (Khusus Admin)"):
            up_files = st.file_uploader("Pilih Gambar", type=['png','jpg','jpeg'], accept_multiple_files=True)
            txt_desc = st.text_input("Keterangan Foto")
            if st.button("Simpan"):
                if up_files:
                    for f in up_files:
                        enc = base64.b64encode(f.getvalue()).decode()
                        st.session_state['temp_gallery'].append({"img": enc, "desc": txt_desc if txt_desc else "Kegiatan"})
                    st.rerun()
    if st.session_state['temp_gallery']:
        cols = st.columns(3)
        for i, item in enumerate(st.session_state['temp_gallery']):
            with cols[i % 3]:
                st.image(f"data:image/png;base64,{item['img']}", use_container_width=True)
                st.markdown(f"<div class='gallery-desc'>{item['desc']}</div>", unsafe_allow_html=True)
    else: st.info("Belum ada foto.")

# 4. PANEL ADMIN
elif menu == "🔐 Panel Admin":
    st.markdown('<div class="section-title">DATABASE PENDAFTAR</div>', unsafe_allow_html=True)
    try:
        sheet = client.open(SHEET_NAME).sheet1
        all_val = sheet.get_all_values()
        df = pd.DataFrame(all_val[1:], columns=all_val[0])
        tab1, tab2 = st.tabs(["🔍 Monitoring", "✏️ Edit"])
        with tab1: st.dataframe(df, use_container_width=True)
        with tab2:
            search = st.text_input("Cari Nama/Reg")
            if search:
                res = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
                if not res.empty:
                    sel = st.selectbox("Pilih No Reg", res['No. Registrasi'].values)
                    idx = df.index[df['No. Registrasi'] == sel].tolist()[0] + 2
                    curr = sheet.row_values(idx)
                    with st.form("edit"):
                        upd = [st.text_input(f"Kol {i+1}", value=curr[i] if i < len(curr) else "") for i in range(len(all_val[0]))]
                        if st.form_submit_button("Update"):
                            sheet.update(f"A{idx}", [upd])
                            st.success("Berhasil!"); st.rerun()
    except: st.error("Gagal memuat.")
