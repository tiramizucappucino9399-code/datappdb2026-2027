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

# DATA PENGUMUMAN (Bisa diedit admin)
if 'PENGUMUMAN' not in st.session_state:
    st.session_state['PENGUMUMAN'] = "Selamat Datang di PPDB Online RA AL IRSYAD KEDIRI Tahun Pelajaran 2026/2027. Pendaftaran gelombang pertama dibuka hingga Maret 2026."

# DATA LEMBAGA LENGKAP
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
        "Email": "ra.alirsyad.kediri@gmail.com",
        "Waktu Belajar": "Pagi / 6 Hari",
        "Penyelenggara": "Lembaga Pendidikan Al Irsyad Al Islamiyyah"
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

# --- 3. UI STYLING ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", page_icon="🏫", layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #F8FAFC; }}
    {f'.login-bg {{ background-image: linear-gradient(rgba(2, 132, 199, 0.75), rgba(2, 132, 199, 0.75)), url("data:image/png;base64,{BG_BASE64}"); background-size: cover; background-position: center; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }}' if BG_BASE64 else ''}
    .header-box {{ background-color: white; padding: 25px; border-radius: 12px; border: 1px solid #E2E8F0; margin-bottom: 20px; display: flex; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .announcement-box {{ background-color: #E0F2FE; border-left: 5px solid #0284C7; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #0369A1; font-weight: 500; }}
    .section-title {{ background-color: #F8FAFC; padding: 12px; font-weight: bold; border-bottom: 2px solid #E2E8F0; margin-bottom: 15px; color: #0284C7; }}
    .emis-table {{ width: 100%; font-size: 14px; color: #334155; border-collapse: collapse; }}
    .emis-table td {{ padding: 12px 8px; border-bottom: 1px solid #F1F5F9; }}
    .label-emis {{ color: #64748B; font-weight: 600; width: 200px; background-color: #F8FAFC; }}
    .login-card {{ background-color: white; padding: 40px; border-radius: 15px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); max-width: 500px; margin: auto; text-align: center; }}
    .staff-card {{ background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    .gallery-desc {{ font-size: 13px; color: #475569; margin-top: 5px; text-align: center; font-style: italic; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)

# --- GERBANG LOGIN ---
if st.session_state['role'] is None:
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        if LOGO_BASE64: st.markdown(f'<img src="data:image/png;base64,{LOGO_BASE64}" width="120">', unsafe_allow_html=True)
        st.markdown("<h2>SISTEM INFORMASI PPDB</h2><h4>RA AL IRSYAD AL ISLAMIYYAH KEDIRI</h4><p>Silakan Pilih Akses Masuk</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 WALI MURID", use_container_width=True): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMIN", use_container_width=True): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("Login Administrator")
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

# --- 1. PROFIL SEKOLAH & PENGUMUMAN ---
if menu == "🏠 Profil Sekolah":
    st.markdown(f'<div class="header-box"><img src="data:image/png;base64,{LOGO_BASE64}" width="90" style="margin-right:25px;"><div><h2 style="margin:0;">{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2><p style="margin:0; color:#64748B;">NSM: {st.session_state["INFO_LEMBAGA"]["NSM"]} | NPSN: {st.session_state["INFO_LEMBAGA"]["NPSN"]}</p></div></div>', unsafe_allow_html=True)
    
    # BOX PENGUMUMAN
    st.markdown(f'<div class="announcement-box">📢 <b>PENGUMUMAN PPDB:</b><br>{st.session_state["PENGUMUMAN"]}</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("✏️ Edit Pengumuman (Admin Only)"):
            new_ann = st.text_area("Isi Pengumuman Baru", value=st.session_state['PENGUMUMAN'])
            if st.button("Update Pengumuman"):
                st.session_state['PENGUMUMAN'] = new_ann
                st.success("Pengumuman diperbarui!"); st.rerun()

    # INFORMASI LEMBAGA
    st.markdown('<div style="background-color:white; padding:25px; border-radius:12px; border:1px solid #E2E8F0;">', unsafe_allow_html=True)
    c_t, c_e = st.columns([4, 1])
    c_t.markdown('<div class="section-title">INFORMASI UMUM LEMBAGA</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin' and c_e.button("✏️ Edit Profil"): st.session_state['is_editing_prof'] = True
    
    if st.session_state.get('is_editing_prof', False) and st.session_state['role'] == 'admin':
        with st.form("ed_prof"):
            new_inf = {k: st.text_input(k, v) for k, v in st.session_state['INFO_LEMBAGA'].items()}
            if st.form_submit_button("Simpan"): st.session_state['INFO_LEMBAGA'].update(new_inf); st.session_state['is_editing_prof'] = False; st.rerun()
    else:
        cp1, cp2 = st.columns(2)
        with cp1:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">NAMA LEMBAGA</td><td>: {st.session_state['INFO_LEMBAGA']['Nama']}</td></tr>
                <tr><td class="label-emis">NSM / NPSN</td><td>: {st.session_state['INFO_LEMBAGA']['NSM']} / {st.session_state['INFO_LEMBAGA']['NPSN']}</td></tr>
                <tr><td class="label-emis">KEPALA MADRASAH</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
            </table>""", unsafe_allow_html=True)
        with cp2:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
                <tr><td class="label-emis">KECAMATAN / KOTA</td><td>: {st.session_state['INFO_LEMBAGA']['Kecamatan']} / {st.session_state['INFO_LEMBAGA']['Kabupaten']}</td></tr>
                <tr><td class="label-emis">KONTAK</td><td>: {st.session_state['INFO_LEMBAGA']['Telepon']}</td></tr>
            </table>""", unsafe_allow_html=True)
    
    if st.session_state['temp_gallery']:
        st.markdown('<br><div class="section-title">DOKUMENTASI TERBARU</div>', unsafe_allow_html=True)
        cg = st.columns(4)
        for i, itm in enumerate(st.session_state['temp_gallery']):
            with cg[i % 4]:
                st.image(f"data:image/png;base64,{itm['img']}", use_container_width=True)
                st.markdown(f"<div class='gallery-desc'>{itm['desc']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. PENDAFTARAN (37 KOLOM)
elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<h3 style="color:#0284C7;">Formulir Pendaftaran Siswa Baru</h3>', unsafe_allow_html=True)
    with st.form("ppdb_full", clear_on_submit=True):
        st.markdown("##### I. IDENTITAS SISWA")
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap Siswa*")
        nisn = c2.text_input("NISN / Rombel (misal: RA-A)")
        nis_l = c1.text_input("NIS Lokal")
        kwn = c2.selectbox("Kewarganegaraan", ["WNI", "WNA"])
        nik_s = c1.text_input("NIK Siswa*")
        tgl_s = c2.date_input("Tanggal Lahir*", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
        tmp_s = c1.text_input("Tempat Lahir")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        saudara = c1.number_input("Jumlah Saudara", 0)
        anak_ke = c2.number_input("Anak Ke", 1)
        agama = c1.selectbox("Agama", ["Islam"])
        no_kk = c2.text_input("Nomor KK")
        n_kepala = c1.text_input("Nama Kepala Keluarga")
        no_wa = c2.text_input("WA Wali*")

        st.markdown("<br>##### II. DATA ORANG TUA", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Data Ayah", "Data Ibu"])
        with t1:
            ay1, ay2 = st.columns(2)
            n_ay = ay1.text_input("Nama Ayah")
            nik_ay = ay2.text_input("NIK Ayah")
            tgl_ay = ay1.date_input("Tgl Lahir Ayah", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31), key="ay")
            pek_ay, gaj_ay = ay2.text_input("Pekerjaan Ayah"), ay1.selectbox("Gaji Ayah", ["< 1 Juta", "1-3 Juta", "> 3 Juta"], key="gay")
        with t2:
            ib1, ib2 = st.columns(2)
            n_ib = ib1.text_input("Nama Ibu")
            nik_ib = ib2.text_input("NIK Ibu")
            tgl_ib = ib1.date_input("Tgl Lahir Ibu", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31), key="ib")
            pek_ib, gaj_ib = ib2.text_input("Pekerjaan Ibu"), ib1.selectbox("Gaji Ibu", ["< 1 Juta", "1-3 Juta", "> 3 Juta"], key="gib")

        st.markdown("<br>##### III. ALAMAT", unsafe_allow_html=True)
        st_r = st.selectbox("Status Rumah", ["Milik Sendiri", "Kontrak", "Lainnya"])
        prov, kab = c1.text_input("Provinsi", "Jawa Timur"), c2.text_input("Kabupaten", "Kediri")
        alamat, pos = st.text_area("Alamat Lengkap"), c1.text_input("Kode Pos")

        if st.form_submit_button("✅ KIRIM"):
            if nama and nik_s and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    row = [reg_id, nama, nisn, nis_l, kwn, f"'{nik_s}", str(tgl_s), tmp_s, jk, saudara, anak_ke, agama, f"'{no_kk}", n_kepala, no_wa, n_ay, f"'{nik_ay}", "", str(tgl_ay), "", pek_ay, gaj_ay, n_ib, f"'{nik_ib}", "", str(tgl_ib), "", pek_ib, gaj_ib, st_r, prov, kab, "", "", alamat, pos, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"]
                    sheet.append_row(row)
                    st.success("Berhasil!"); st.balloons()
                except: st.error("Database Gagal.")

# 3. DAFTAR SISWA (HITUNG UMUR & AKSES TERPISAH)
elif menu == "📋 Daftar Siswa Terdaftar":
    st.markdown('<div class="section-title">📋 DAFTAR SISWA TERDAFTAR</div>', unsafe_allow_html=True)
    try:
        sheet = client.open(SHEET_NAME).sheet1
        data = sheet.get_all_records()
        if data:
            df_full = pd.DataFrame(data)
            display_df = pd.DataFrame()
            display_df['NAMA'] = df_full['Nama Lengkap']
            display_df['TEMPAT LAHIR'] = df_full['Tempat Lahir']
            display_df['TANGGAL LAHIR'] = df_full['Tanggal Lahir']
            display_df['TINGKAT-ROMBEL'] = df_full['NISN']
            display_df['UMUR'] = display_df['TANGGAL LAHIR'].apply(lambda x: hitung_umur(str(x)))
            st.table(display_df)

            if st.session_state['role'] == 'admin':
                st.divider()
                st.subheader("✏️ Koreksi Cepat (Admin Only)")
                sel_siswa = st.selectbox("Pilih Siswa", df_full['Nama Lengkap'].values)
                idx_row = df_full.index[df_full['Nama Lengkap'] == sel_siswa].tolist()[0] + 2
                curr_row = sheet.row_values(idx_row)
                with st.form("edit_quick"):
                    new_n = st.text_input("Nama Siswa", value=curr_row[1])
                    new_r = st.text_input("Tingkat-Rombel", value=curr_row[2])
                    if st.form_submit_button("Simpan Perubahan"):
                        sheet.update_cell(idx_row, 2, new_n)
                        sheet.update_cell(idx_row, 3, new_r)
                        st.success("Data diperbarui!"); st.rerun()
    except: st.info("Belum ada pendaftar.")

# 4. GALERI
elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">📸 GALERI KEGIATAN</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("📤 Upload Foto"):
            up = st.file_uploader("Pilih Gambar", accept_multiple_files=True)
            tx = st.text_input("Deskripsi")
            if st.button("Simpan ke Galeri"):
                for f in up: st.session_state['temp_gallery'].append({"img": base64.b64encode(f.getvalue()).decode(), "desc": tx})
                st.rerun()
    cols = st.columns(3)
    for i, itm in enumerate(st.session_state['temp_gallery']):
        with cols[i % 3]:
            st.image(f"data:image/png;base64,{itm['img']}", use_container_width=True)
            st.markdown(f"<div class='gallery-desc'>{itm['desc']}</div>", unsafe_allow_html=True)

# 5. GURU & STAF
elif menu == "👨‍🏫 Profil Guru & Staf":
    st.markdown('<div class="section-title">👨‍🏫 PROFIL GURU & STAF</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("➕ Tambah Profil"):
            with st.form("stf"):
                n, j, p, b = st.text_input("Nama"), st.text_input("Jabatan"), st.file_uploader("Foto"), st.text_area("Bio")
                if st.form_submit_button("Simpan"):
                    st.session_state['staff_data'].append({"id": datetime.now().timestamp(), "name": n, "job": j, "photo": base64.b64encode(p.getvalue()).decode(), "bio": b})
                    st.rerun()
    cols_s = st.columns(3)
    for idx, s in enumerate(st.session_state['staff_data']):
        with cols_s[idx % 3]:
            st.markdown(f'<div class="staff-card"><img src="data:image/png;base64,{s["photo"]}" style="width:100%; border-radius:10px;"><div style="color:#0284C7; font-weight:bold; margin-top:10px;">{s["name"]}</div><div>{s["job"]}</div><div style="font-size:12px;">{s["bio"]}</div></div>', unsafe_allow_html=True)
            if st.session_state['role'] == 'admin' and st.button("🗑️ Hapus", key=idx): st.session_state['staff_data'].pop(idx); st.rerun()

# 6. PANEL ADMIN (DATABASE UTUH)
elif menu == "🔐 Panel Admin":
    st.markdown('<div class="section-title">DATABASE PENDAFTAR (ADMIN)</div>', unsafe_allow_html=True)
    try:
        sheet = client.open(SHEET_NAME).sheet1
        all_val = sheet.get_all_values()
        st.dataframe(pd.DataFrame(all_val[1:], columns=all_val[0]), use_container_width=True)
    except: st.error("Gagal.")
