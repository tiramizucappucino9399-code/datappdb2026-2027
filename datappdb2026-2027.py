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
if 'staff_data' not in st.session_state:
    st.session_state['staff_data'] = [] 
if 'PENGUMUMAN' not in st.session_state:
    st.session_state['PENGUMUMAN'] = "Selamat Datang di PPDB Online RA AL IRSYAD KEDIRI."

# --- DATA LEMBAGA LENGKAP (DISAMAKAN DENGAN GAMBAR) ---
if 'INFO_LEMBAGA' not in st.session_state:
    st.session_state['INFO_LEMBAGA'] = {
        "Nama": "RA AL IRSYAD AL ISLAMIYYAH",
        "NSM": "101235710017",
        "NPSN": "69749712",
        "Status": "Swasta",
        "Bentuk SP": "RA",
        "Kepala": "IMROATUS SOLIKHAH",
        "Alamat": "Jl. Tembus Kaliombo No. 3-5",
        "RT/RW": "29/10",
        "Kelurahan/Desa": "TOSAREN",
        "Kecamatan": "PESANTREN",
        "Kabupaten/Kota": "KOTA KEDIRI",
        "Provinsi": "JAWA TIMUR",
        "Kode Pos": "64133",
        "Telepon": "(0354) 682524",
        "Email": "ra.alirsyad.kediri@gmail.com",
        "Waktu Belajar": "Pagi",
        "Penyelenggara": "AL IRSYAD AL ISLAMIYYAH KOTA KEDIRI",
        "Afiliasi Keagamaan": "Nahdlatul Ulama",
        "Status KKM": "Anggota",
        "Komite Lembaga": "Sudah Terbentuk",
        "Koordinat": "-7.8301756, 112.0168655"
    }

# --- KLASTER GAMBAR ---
@st.cache_data
def get_image_base64(url):
    try:
        if "drive.google.com" in url:
            if "id=" in url: id_file = url.split("id=")[-1].split("&")[0]
            else: id_file = url.split('/')[-2]
            url = f"https://drive.google.com/uc?export=download&id={id_file}"
        response = requests.get(url, timeout=10)
        return base64.b64encode(response.content).decode()
    except: return None

LOGO_LINK = "https://drive.google.com/file/d/1DOuK4dzVSLdzb8QewaFIzOL85IDWNP9P/view?usp=drive_link"
LOGO_BASE64 = get_image_base64(LOGO_LINK)

BG_LINK = "https://drive.google.com/file/d/1XW_CONTOH_LINK_BG_ANDA/view" 
BG_BASE64 = get_image_base64(BG_LINK)

# --- FUNGSI ---
def hitung_umur(born_str):
    try:
        born = datetime.strptime(born_str, "%Y-%m-%d")
        today = datetime.today()
        return f"{today.year - born.year - ((today.month, today.day) < (born.month, born.day))} Thn"
    except: return "-"

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
    except: return None

# --- UI STYLING ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", page_icon="🏫", layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #F8FAFC; }}
    {f'.login-bg {{ background-image: linear-gradient(rgba(2, 132, 199, 0.75), rgba(2, 132, 199, 0.75)), url("data:image/png;base64,{BG_BASE64}"); background-size: cover; background-position: center; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }}' if BG_BASE64 else ''}
    .header-box {{ background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; display: flex; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .announcement-box {{ background-color: #E0F2FE; border-left: 5px solid #0284C7; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #0369A1; font-weight: 500; }}
    .section-title {{ background-color: #F8FAFC; padding: 12px; font-weight: bold; border-bottom: 2px solid #E2E8F0; margin-bottom: 15px; color: #0284C7; }}
    .emis-table {{ width: 100%; font-size: 13px; color: #334155; border-collapse: collapse; }}
    .emis-table td {{ padding: 8px 5px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
    .label-emis {{ color: #64748B; font-weight: 600; width: 180px; text-transform: uppercase; }}
    .login-card {{ background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); max-width: 500px; margin: auto; text-align: center; }}
    .staff-card {{ background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
</style>
""", unsafe_allow_html=True)

# --- LOGIN GERBANG ---
if st.session_state['role'] is None:
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_BASE64: st.markdown(f'<img src="data:image/png;base64,{LOGO_BASE64}" width="120">', unsafe_allow_html=True)
        st.markdown("<h2>PPDB ONLINE</h2><h4>RA AL IRSYAD AL ISLAMIYYAH KEDIRI</h4>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 WALI MURID", use_container_width=True): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMINISTRATOR", use_container_width=True): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("Login Admin")
    pw = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.session_state['auth'] = True; st.rerun()
        else: st.error("Salah!")
    if st.button("Kembali"): st.session_state['role'] = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- SIDEBAR ---
with st.sidebar:
    if LOGO_BASE64: st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{LOGO_BASE64}" width="110"></div>', unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; color:#0284C7; font-weight:bold;'>MODE: {st.session_state['role'].upper()}</div>", unsafe_allow_html=True)
    nav = ["🏠 Profil Sekolah", "📝 Pendaftaran Siswa Baru", "📋 Daftar Siswa Terdaftar", "📸 Galeri Sekolah", "👨‍🏫 Profil Guru & Staf"]
    if st.session_state['role'] == 'admin': nav.append("🔐 Panel Admin")
    menu = st.selectbox("NAVIGASI", nav)
    if st.button("🚪 Keluar"): st.session_state['role'] = None; st.session_state['auth'] = False; st.rerun()

client = init_google_sheets()

# --- 1. PROFIL SEKOLAH (SESUAI GAMBAR) ---
if menu == "🏠 Profil Sekolah":
    st.markdown(f"""
    <div class="header-box">
        <img src="data:image/png;base64,{LOGO_BASE64}" width="85" style="margin-right:20px;">
        <div style="flex-grow:1;">
            <h2 style="margin:0; color:#1E293B;">{st.session_state['INFO_LEMBAGA']['Nama']}</h2>
            <div style="display:flex; gap:20px; font-size:14px; color:#64748B;">
                <span>NSM: <b>{st.session_state['INFO_LEMBAGA']['NSM']}</b></span>
                <span>STATUS: <b>{st.session_state['INFO_LEMBAGA']['Status']}</b></span>
            </div>
            <div style="display:flex; gap:20px; font-size:14px; color:#64748B;">
                <span>NPSN: <b>{st.session_state['INFO_LEMBAGA']['NPSN']}</b></span>
                <span>BENTUK SP: <b>{st.session_state['INFO_LEMBAGA']['Bentuk SP']}</b></span>
            </div>
        </div>
        <div style="display:flex; gap:10px;">
            <button style="border:1px solid #CBD5E1; background:white; border-radius:20px; padding:5px 15px; font-size:12px;">📞 {st.session_state['INFO_LEMBAGA']['Telepon']}</button>
            <button style="border:1px solid #CBD5E1; background:white; border-radius:20px; padding:5px 15px; font-size:12px;">✉️ {st.session_state['INFO_LEMBAGA']['Email']}</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PENGUMUMAN
    st.markdown(f'<div class="announcement-box">📢 <b>PENGUMUMAN:</b> {st.session_state["PENGUMUMAN"]}</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("✏️ Edit Pengumuman"):
            st.session_state['PENGUMUMAN'] = st.text_area("Isi Baru", st.session_state['PENGUMUMAN'])
            if st.button("Update"): st.rerun()

    # TABEL INFORMASI UMUM (DUA KOLOM LENGKAP)
    st.markdown('<div style="background-color:white; padding:25px; border-radius:12px; border:1px solid #E2E8F0;">', unsafe_allow_html=True)
    c_t, c_e = st.columns([5, 1])
    c_t.markdown('<div class="section-title">INFORMASI UMUM</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin' and c_e.button("✏️ Edit Profil"): st.session_state['is_editing_prof'] = True
    
    if st.session_state.get('is_editing_prof', False) and st.session_state['role'] == 'admin':
        with st.form("ed_prof"):
            new_inf = {k: st.text_input(k, v) for k, v in st.session_state['INFO_LEMBAGA'].items()}
            if st.form_submit_button("Simpan"):
                st.session_state['INFO_LEMBAGA'].update(new_inf); st.session_state['is_editing_prof'] = False; st.rerun()
    else:
        col_L, col_R = st.columns(2)
        with col_L:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">KEPALA MADRASAH</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
                <tr><td class="label-emis">KODE REGISTRASI</td><td>: 4qdb8eeqOc</td></tr>
                <tr><td class="label-emis">NAMA PENYELENGGARA</td><td>: {st.session_state['INFO_LEMBAGA']['Penyelenggara']}</td></tr>
                <tr><td class="label-emis">AFILIASI ORGANISASI</td><td>: {st.session_state['INFO_LEMBAGA']['Afiliasi Keagamaan']}</td></tr>
                <tr><td class="label-emis">WAKTU BELAJAR</td><td>: {st.session_state['INFO_LEMBAGA']['Waktu Belajar']}</td></tr>
                <tr><td class="label-emis">STATUS KKM</td><td>: {st.session_state['INFO_LEMBAGA']['Status KKM']}</td></tr>
                <tr><td class="label-emis">KOMITE LEMBAGA</td><td>: {st.session_state['INFO_LEMBAGA']['Komite Lembaga']}</td></tr>
            </table>""", unsafe_allow_html=True)
        with col_R:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
                <tr><td class="label-emis">RT/RW</td><td>: {st.session_state['INFO_LEMBAGA']['RT/RW']}</td></tr>
                <tr><td class="label-emis">KELURAHAN/DESA</td><td>: {st.session_state['INFO_LEMBAGA']['Kelurahan/Desa']}</td></tr>
                <tr><td class="label-emis">KECAMATAN</td><td>: {st.session_state['INFO_LEMBAGA']['Kecamatan']}</td></tr>
                <tr><td class="label-emis">KABUPATEN/KOTA</td><td>: {st.session_state['INFO_LEMBAGA']['Kabupaten/Kota']}</td></tr>
                <tr><td class="label-emis">PROVINSI</td><td>: {st.session_state['INFO_LEMBAGA']['Provinsi']}</td></tr>
                <tr><td class="label-emis">KODE POS</td><td>: {st.session_state['INFO_LEMBAGA']['Kode Pos']}</td></tr>
                <tr><td class="label-emis">TITIK KOORDINAT</td><td>: {st.session_state['INFO_LEMBAGA']['Koordinat']}</td></tr>
            </table>""", unsafe_allow_html=True)
    
    if st.session_state['temp_gallery']:
        st.markdown('<br><div class="section-title">GALERI TERBARU</div>', unsafe_allow_html=True)
        cg = st.columns(4)
        for i, itm in enumerate(st.session_state['temp_gallery']):
            with cg[i % 4]:
                st.image(f"data:image/png;base64,{itm['img']}", use_container_width=True)
                st.markdown(f"<div class='gallery-desc'>{itm['desc']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. PENDAFTARAN (37 KOLOM)
elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<h3>Formulir Pendaftaran</h3>', unsafe_allow_html=True)
    with st.form("ppdb_full", clear_on_submit=True):
        st.markdown("##### I. IDENTITAS SISWA")
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap Siswa*")
        nisn = c2.text_input("NISN / Rombel")
        nis_l = c1.text_input("NIS Lokal")
        kwn = c2.selectbox("Kewarganegaraan", ["WNI", "WNA"])
        nik_s = c1.text_input("NIK Siswa*")
        tgl_s = c2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1))
        tmp_s = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = c1.number_input("Jumlah Saudara", 0)
        anak_ke = c2.number_input("Anak Ke", 1)
        agama = c1.selectbox("Agama", ["Islam"])
        no_kk = c2.text_input("Nomor KK")
        n_kepala = c1.text_input("Kepala Keluarga")
        no_wa = c2.text_input("WA Wali*")

        st.markdown("<br>##### II. ORANG TUA", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ayah", "Ibu"])
        with t1:
            ay1, ay2 = st.columns(2)
            n_ay = ay1.text_input("Nama Ayah")
            nik_ay = ay2.text_input("NIK Ayah")
            tgl_ay = ay1.date_input("Tgl Lahir Ayah", min_value=datetime(1945,1,1), key="ay")
            pek_ay, gaj_ay = ay2.text_input("Pekerjaan Ayah"), ay1.selectbox("Gaji Ayah", ["< 1 Jt", "1-3 Jt", "> 3 Jt"], key="gay")
        with t2:
            ib1, ib2 = st.columns(2)
            n_ib = ib1.text_input("Nama Ibu")
            nik_ib = ib2.text_input("NIK Ibu")
            tgl_ib = ib1.date_input("Tgl Lahir Ibu", min_value=datetime(1945,1,1), key="ib")
            pek_ib, gaj_ib = ib2.text_input("Pekerjaan Ibu"), ib1.selectbox("Gaji Ibu", ["< 1 Jt", "1-3 Jt", "> 3 Jt"], key="gib")

        st.markdown("<br>##### III. ALAMAT", unsafe_allow_html=True)
        st_r = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak", "Lainnya"])
        prov, kab = c1.text_input("Provinsi", "Jawa Timur"), c2.text_input("Kabupaten", "Kediri")
        alamat = st.text_area("Alamat Lengkap")

        if st.form_submit_button("✅ KIRIM"):
            if nama and nik_s and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    row = [reg_id, nama, nisn, nis_l, kwn, f"'{nik_s}", str(tgl_s), tmp_s, jk, saudara, anak_ke, agama, f"'{no_kk}", n_kepala, no_wa, n_ay, f"'{nik_ay}", "", str(tgl_ay), "", pek_ay, gaj_ay, n_ib, f"'{nik_ib}", "", str(tgl_ib), "", pek_ib, gaj_ib, st_r, prov, kab, "", "", alamat, "", datetime.now().strftime("%Y-%m-%d"), "Belum Verifikasi"]
                    sheet.append_row(row)
                    st.success("Data Terkirim!"); st.balloons()
                except: st.error("Database Error.")

# 3. DAFTAR SISWA (HITUNG UMUR)
elif menu == "📋 Daftar Siswa Terdaftar":
    st.markdown('<div class="section-title">DAFTAR SISWA</div>', unsafe_allow_html=True)
    try:
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            display = pd.DataFrame()
            display['NAMA'] = df['Nama Lengkap']
            display['TEMPAT LAHIR'] = df['Tempat Lahir']
            display['TANGGAL LAHIR'] = df['Tanggal Lahir']
            display['TINGKAT-ROMBEL'] = df['NISN']
            display['UMUR'] = display['TANGGAL LAHIR'].apply(lambda x: hitung_umur(str(x)))
            st.table(display)
        else: st.info("Kosong.")
    except: st.error("Gagal Muat.")

# 4. GALERI
elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">GALERI</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("Upload"):
            files = st.file_uploader("Foto", accept_multiple_files=True)
            tx = st.text_input("Ket")
            if st.button("Simpan"):
                for f in files: st.session_state['temp_gallery'].append({"img": base64.b64encode(f.getvalue()).decode(), "desc": tx})
                st.rerun()
    cols = st.columns(3)
    for i, itm in enumerate(st.session_state['temp_gallery']):
        with cols[i % 3]:
            st.image(f"data:image/png;base64,{itm['img']}", use_container_width=True)
            st.markdown(f"<div class='gallery-desc'>{itm['desc']}</div>", unsafe_allow_html=True)

# 5. GURU & STAF
elif menu == "👨‍🏫 Profil Guru & Staf":
    st.markdown('<div class="section-title">GURU & STAF</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("Tambah"):
            with st.form("g"):
                n, j, p, b = st.text_input("Nama"), st.text_input("Jabatan"), st.file_uploader("Foto"), st.text_area("Bio")
                if st.form_submit_button("Simpan"):
                    st.session_state['staff_data'].append({"id": datetime.now().timestamp(), "name": n, "job": j, "photo": base64.b64encode(p.getvalue()).decode(), "bio": b})
                    st.rerun()
    cols = st.columns(3)
    for idx, s in enumerate(st.session_state['staff_data']):
        with cols[idx % 3]:
            st.markdown(f'<div class="staff-card"><img src="data:image/png;base64,{s["photo"]}" style="width:100%; border-radius:10px;"><div style="color:#0284C7; font-weight:bold;">{s["name"]}</div><div>{s["job"]}</div><div>{s["bio"]}</div></div>', unsafe_allow_html=True)
            if st.session_state['role'] == 'admin' and st.button("Hapus", key=idx): st.session_state['staff_data'].pop(idx); st.rerun()

# 6. PANEL ADMIN
elif menu == "🔐 Panel Admin":
    try:
        sheet = client.open(SHEET_NAME).sheet1
        all_val = sheet.get_all_values()
        st.dataframe(pd.DataFrame(all_val[1:], columns=all_val[0]), use_container_width=True)
    except: st.error("Gagal.")
