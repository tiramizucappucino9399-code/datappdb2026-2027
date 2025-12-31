import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64
import requests
import urllib.parse

# --- 1. KONFIGURASI SISTEM ---
SHEET_NAME = "Database PPDB AL IRSYAD KEDIRI" 
ADMIN_PASSWORD = "adminirsyad" 

# Inisialisasi Session State
if 'role' not in st.session_state: st.session_state['role'] = None 
if 'staff_data' not in st.session_state: st.session_state['staff_data'] = []
if 'PENGUMUMAN' not in st.session_state: 
    st.session_state['PENGUMUMAN'] = "Selamat Datang di PPDB Online RA AL IRSYAD AL ISLAMIYYAH KEDIRI."

if 'INFO_LEMBAGA' not in st.session_state:
    st.session_state['INFO_LEMBAGA'] = {
        "Nama": "RA AL IRSYAD AL ISLAMIYYAH", "NSM": "101235710017", "NPSN": "69749712",
        "Status": "Swasta", "Bentuk SP": "RA", "Kepala": "IMROATUS SOLIKHAH",
        "Nama Penyelenggara": "AL IRSYAD AL ISLAMIYYAH KOTA KEDIRI", "Afiliasi": "Nahdlatul Ulama",
        "Waktu Belajar": "Pagi", "Status KKM": "Anggota", "Komite": "Sudah Terbentuk",
        "Alamat": "Jl. Tembus Kaliombo No. 3-5", "RT/RW": "29/10", "Desa": "TOSAREN",
        "Kecamatan": "PESANTREN", "Kota": "KOTA KEDIRI", "Provinsi": "JAWA TIMUR",
        "Pos": "64133", "Koordinat": "-7.8301756, 112.0168655", "Telepon": "(0354) 682524",
        "Email": "ra.alirsyad.kediri@gmail.com"
    }

# --- 2. FUNGSI DATABASE & MEDIA ---
@st.cache_resource
def init_sheets():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        if "gcp_service_account" in st.secrets:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        return gspread.authorize(creds)
    except: return None

client = init_sheets()

def save_media(tipe, b64, desc=""):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        db.append_row([tipe, b64, desc, datetime.now().strftime("%Y-%m-%d %H:%M")])
    except: pass

def load_media(tipe):
    try:
        db = client.open(SHEET_NAME).worksheet("Media_Data")
        all_data = db.get_all_records()
        return [d for d in all_data if d['Tipe_Data'] == tipe]
    except: return []

def hitung_umur(born_str):
    try:
        born = datetime.strptime(born_str, "%Y-%m-%d")
        today = datetime.today()
        return f"{today.year - born.year - ((today.month, today.day) < (born.month, born.day))} Thn"
    except: return "-"

# --- 3. UI STYLING ---
st.set_page_config(page_title="EMIS PPDB AL IRSYAD", layout="wide")

def set_dynamic_bg(menu_name):
    data = load_media(f"BG_{menu_name}")
    b64 = data[-1]['Konten_Base64'] if data else ""
    overlay = "rgba(2, 132, 199, 0.75)" if st.session_state['role'] is None else "rgba(255, 255, 255, 0.93)"
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: linear-gradient({overlay}, {overlay}), url("data:image/png;base64,{b64}");
            background-size: cover; background-attachment: fixed;
        }}
        .header-box {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; align-items: center; margin-bottom: 20px; border: 1px solid #E2E8F0; }}
        .announcement-box {{ background-color: #E0F2FE; border-left: 5px solid #0284C7; padding: 15px; border-radius: 8px; margin-bottom: 25px; color: #0369A1; font-weight: 500; }}
        .emis-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .emis-table td {{ padding: 10px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
        .label-emis {{ font-weight: bold; color: #64748B; width: 220px; text-transform: uppercase; }}
        .staff-card {{ background: white; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #E2E8F0; transition: 0.3s; }}
        .staff-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 15px rgba(0,0,0,0.1); }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. AUTHENTICATION / LOGIN ---
if st.session_state['role'] is None:
    set_dynamic_bg("LOGIN")
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div style="background:white; padding:50px; border-radius:20px; text-align:center; max-width:550px; margin:auto; box-shadow:0 20px 25px rgba(0,0,0,0.2);">', unsafe_allow_html=True)
        st.markdown("<h1 style='color:#0284C7; margin-bottom:0;'>PORTAL PPDB</h1><h4 style='color:#64748B;'>RA AL IRSYAD AL ISLAMIYYAH</h4><hr>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("👤 WALI MURID", use_container_width=True): st.session_state['role'] = 'user'; st.rerun()
        if c2.button("🔑 ADMIN", use_container_width=True): st.session_state['role'] = 'admin_auth'; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state['role'] == 'admin_auth':
    st.markdown('<div style="max-width:400px; margin:auto; background:white; padding:30px; border-radius:10px;">', unsafe_allow_html=True)
    pw = st.text_input("Sandi Keamanan Admin", type="password")
    if st.button("Masuk"):
        if pw == ADMIN_PASSWORD: st.session_state['role'] = 'admin'; st.rerun()
        else: st.error("Sandi Salah")
    if st.button("Kembali"): st.session_state['role'] = None; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- 5. SIDEBAR NAVIGASI ---
with st.sidebar:
    st.markdown(f"### LOGIN: {st.session_state['role'].upper()}")
    menu = st.selectbox("Pilih Halaman", ["🏠 Profil Sekolah", "📝 Pendaftaran Siswa Baru", "📋 Daftar Siswa Terdaftar", "📸 Galeri Sekolah", "👨‍🏫 Profil Guru & Staf", "⚙️ Pengaturan BG"])
    if st.button("Log Out 🚪"): st.session_state['role'] = None; st.rerun()

set_dynamic_bg(menu.replace(" ", "_"))

# --- 6. LOGIKA HALAMAN ---

# MENU 1: PROFIL EMIS & PENGUMUMAN
if menu == "🏠 Profil Sekolah":
    st.markdown(f'<div class="header-box"><div><h2 style="margin:0; color:#1E293B;">{st.session_state["INFO_LEMBAGA"]["Nama"]}</h2><p style="margin:0; color:#64748B;">NSM: {st.session_state["INFO_LEMBAGA"]["NSM"]} | NPSN: {st.session_state["INFO_LEMBAGA"]["NPSN"]}</p></div></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="announcement-box">📢 <b>INFO PPDB:</b> {st.session_state["PENGUMUMAN"]}</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("✏️ Edit Teks Pengumuman"):
            st.session_state['PENGUMUMAN'] = st.text_area("Tulis Pengumuman", st.session_state['PENGUMUMAN'])
            if st.button("Update"): st.rerun()

    st.markdown('<div style="background:white; padding:25px; border-radius:12px; border:1px solid #E2E8F0;">', unsafe_allow_html=True)
    c_tit, c_ed = st.columns([5,1])
    c_tit.markdown('<div class="section-title">INFORMASI UMUM LEMBAGA</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin' and c_ed.button("✏️ Edit Profil"): st.session_state['ed_prof'] = True
    
    if st.session_state.get('ed_prof', False):
        with st.form("f_ed"):
            new_inf = {k: st.text_input(k, v) for k, v in st.session_state['INFO_LEMBAGA'].items()}
            if st.form_submit_button("Simpan"): st.session_state['INFO_LEMBAGA'].update(new_inf); st.session_state['ed_prof'] = False; st.rerun()
    else:
        colL, colR = st.columns(2)
        with colL:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">KEPALA MADRASAH</td><td>: {st.session_state['INFO_LEMBAGA']['Kepala']}</td></tr>
                <tr><td class="label-emis">PENYELENGGARA</td><td>: {st.session_state['INFO_LEMBAGA']['Nama Penyelenggara']}</td></tr>
                <tr><td class="label-emis">AFILIASI</td><td>: {st.session_state['INFO_LEMBAGA']['Afiliasi']}</td></tr>
                <tr><td class="label-emis">WAKTU BELAJAR</td><td>: {st.session_state['INFO_LEMBAGA']['Waktu Belajar']}</td></tr>
                <tr><td class="label-emis">STATUS KKM</td><td>: {st.session_state['INFO_LEMBAGA']['Status KKM']}</td></tr>
                <tr><td class="label-emis">KOMITE</td><td>: {st.session_state['INFO_LEMBAGA']['Komite']}</td></tr>
            </table>""", unsafe_allow_html=True)
        with colR:
            st.markdown(f"""<table class="emis-table">
                <tr><td class="label-emis">ALAMAT</td><td>: {st.session_state['INFO_LEMBAGA']['Alamat']}</td></tr>
                <tr><td class="label-emis">RT/RW / DESA</td><td>: {st.session_state['INFO_LEMBAGA']['RT/RW']} / {st.session_state['INFO_LEMBAGA']['Desa']}</td></tr>
                <tr><td class="label-emis">KECAMATAN / KOTA</td><td>: {st.session_state['INFO_LEMBAGA']['Kecamatan']} / {st.session_state['INFO_LEMBAGA']['Kota']}</td></tr>
                <tr><td class="label-emis">KODE POS</td><td>: {st.session_state['INFO_LEMBAGA']['Pos']}</td></tr>
                <tr><td class="label-emis">KOORDINAT</td><td>: {st.session_state['INFO_LEMBAGA']['Koordinat']}</td></tr>
            </table>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# MENU 2: PENDAFTARAN (3 TABS / 37+ KOLOM)
elif menu == "📝 Pendaftaran Siswa Baru":
    st.markdown('<div class="section-title">FORMULIR PENDAFTARAN PESERTA DIDIK BARU</div>', unsafe_allow_html=True)
    with st.form("ppdb_complete", clear_on_submit=True):
        tab1, tab2, tab3 = st.tabs(["📄 1. DATA SISWA", "👨‍👩‍👧 2. DATA KELUARGA", "🏠 3. DATA ALAMAT"])
        with tab1:
            c1, c2 = st.columns(2)
            nm = c1.text_input("Nama Lengkap Siswa*")
            nsn = c2.text_input("NISN")
            nsl = c1.text_input("Nis Lokal")
            kwn = c2.selectbox("Kewarganegaraan", ["WNI", "WNA"])
            nik = c1.text_input("NIK Siswa*")
            tgl = c2.date_input("Tanggal Lahir", min_value=datetime(1945,1,1), max_value=datetime(2100,12,31))
            tmp = c1.text_input("Tempat Lahir")
            jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            sau = c1.number_input("Jumlah Saudara", 0)
            anke = c2.number_input("Anak Ke", 1)
            agm = c1.selectbox("Agama", ["Islam", "Lainnya"])
            nkk = c2.text_input("No Kartu Keluarga")
            u_kk = st.file_uploader("Upload KK (PDF/JPG/PNG - Max 2MB)", type=['pdf','jpg','png'])
            n_kepala = st.text_input("Nama Kepala Keluarga")
        with tab2:
            st.markdown("**AYAH KANDUNG**")
            ay1, ay2 = st.columns(2)
            ay_n, ay_k = ay1.text_input("Nama Ayah"), ay2.text_input("NIK Ayah")
            ay_t, ay_d = ay1.text_input("Tempat Lahir Ayah"), ay2.date_input("Tgl Lahir Ayah", key="ay_d", min_value=datetime(1945,1,1))
            ay_p, ay_j = ay1.selectbox("Pendidikan Ayah", ["SD","SMP","SMA","S1","S2","S3"]), ay2.text_input("Pekerjaan Ayah")
            ay_g = st.text_input("Penghasilan Ayah per Bulan")
            st.markdown("---")
            st.markdown("**IBU KANDUNG**")
            ib1, ib2 = st.columns(2)
            ib_n, ib_k = ib1.text_input("Nama Ibu"), ib2.text_input("NIK Ibu")
            ib_t, ib_d = ib1.text_input("Tempat Lahir Ibu"), ib2.date_input("Tgl Lahir Ibu", key="ib_d", min_value=datetime(1945,1,1))
            ib_p, ib_j = ib1.selectbox("Pendidikan Ibu", ["SD","SMP","SMA","S1","S2","S3"]), ib2.text_input("Pekerjaan Ibu")
            ib_g = st.text_input("Penghasilan Ibu per Bulan")
        with tab3:
            sh = st.selectbox("Status Kepemilikan Rumah", ["Milik Sendiri", "Kontrak/Sewa", "Lainnya"])
            al1, al2 = st.columns(2)
            pro, kab = al1.text_input("Provinsi", "Jawa Timur"), al2.text_input("Kabupaten/Kota", "Kediri")
            kec, des = al1.text_input("Kecamatan"), al2.text_input("Kelurahan/Desa")
            alm = st.text_area("Alamat Lengkap")
            kpos = st.text_input("Kode Pos")

        if st.form_submit_button("✅ KIRIM PENDAFTARAN"):
            if nm and nik:
                try:
                    db = client.open(SHEET_NAME).sheet1
                    db.append_row([datetime.now().strftime("%Y-%m-%d"), nm, nsn, nsl, kwn, f"'{nik}", str(tgl), tmp, jk, sau, anke, agm, f"'{nkk}", n_kepala, ay_n, f"'{ay_k}", ay_t, str(ay_d), ay_p, ay_j, ay_g, ib_n, f"'{ib_k}", ib_t, str(ib_d), ib_p, ib_j, ib_g, sh, pro, kab, kec, des, alm, kpos])
                    st.success("Berhasil Terdaftar!"); st.balloons()
                except: st.error("Database Gagal")

# MENU 3: DAFTAR SISWA (UMUR OTOMATIS)
elif menu == "📋 Daftar Siswa Terdaftar":
    st.markdown('<div class="section-title">DATA SISWA YANG SUDAH MENDAFTAR</div>', unsafe_allow_html=True)
    try:
        db = client.open(SHEET_NAME).sheet1
        df = pd.DataFrame(db.get_all_records())
        if not df.empty:
            df['UMUR'] = df['Tanggal Lahir'].apply(lambda x: hitung_umur(str(x)))
            # Sesuaikan nama kolom dengan header di Sheet Anda
            view_cols = ['Nama Lengkap Siswa', 'Tempat Lahir', 'Tanggal Lahir', 'NISN', 'UMUR']
            st.table(df[view_cols].rename(columns={'NISN': 'TINGKAT/ROMBEL'}))
            
            if st.session_state['role'] == 'admin':
                with st.expander("✏️ Admin: Koreksi Data"):
                    sel = st.selectbox("Pilih Siswa", df['Nama Lengkap Siswa'].values)
                    idx = df[df['Nama Lengkap Siswa'] == sel].index[0] + 2
                    new_n = st.text_input("Nama Baru", sel)
                    if st.button("Simpan Koreksi"):
                        db.update_cell(idx, 2, new_n); st.rerun()
    except: st.info("Belum ada data.")

# MENU 4: GALERI (PREVIEW)
elif menu == "📸 Galeri Sekolah":
    st.markdown('<div class="section-title">GALERI DOKUMENTASI</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("➕ Tambah Foto"):
            f = st.file_uploader("Pilih Gambar")
            d = st.text_input("Deskripsi")
            if st.button("Upload"):
                save_media("Galeri", base64.b64encode(f.getvalue()).decode(), d); st.rerun()
    
    items = load_media("Galeri")
    cols = st.columns(3)
    for i, itm in enumerate(items):
        with cols[i % 3]:
            st.image(f"data:image/png;base64,{itm['Konten_Base64']}", use_container_width=True)
            with st.expander("🔍 Zoom"):
                st.image(f"data:image/png;base64,{itm['Konten_Base64']}", caption=itm['Deskripsi'])

# MENU 5: GURU & STAF
elif menu == "👨‍🏫 Profil Guru & Staf":
    st.markdown('<div class="section-title">PROFIL PENDIDIK & TENAGA KEPENDIDIKAN</div>', unsafe_allow_html=True)
    if st.session_state['role'] == 'admin':
        with st.expander("➕ Tambah Profil Baru"):
            with st.form("f_staff"):
                n, j = st.text_input("Nama & Gelar"), st.text_input("Jabatan")
                p, b = st.file_uploader("Foto Profil"), st.text_area("Biografi/Motto")
                if st.form_submit_button("Simpan"):
                    b64_p = base64.b64encode(p.getvalue()).decode()
                    st.session_state['staff_data'].append({"id": datetime.now().timestamp(), "n": n, "j": j, "p": b64_p, "b": b})
                    st.rerun()
    
    cols = st.columns(3)
    for idx, s in enumerate(st.session_state['staff_data']):
        with cols[idx % 3]:
            st.markdown(f'<div class="staff-card"><img src="data:image/png;base64,{s["p"]}" style="width:100%; border-radius:10px;"><div style="color:#0284C7; font-weight:bold; margin-top:15px;">{s["n"]}</div><div style="font-size:12px; color:#64748B;">{s["j"]}</div><p style="font-size:13px; margin-top:10px;">{s["b"]}</p></div>', unsafe_allow_html=True)
            if st.session_state['role'] == 'admin':
                if st.button("🗑️ Hapus", key=f"del_{idx}"): st.session_state['staff_data'].pop(idx); st.rerun()

# MENU 6: PENGATURAN BG PER MENU
elif menu == "⚙️ Pengaturan BG":
    if st.session_state['role'] == 'admin':
        st.subheader("Atur Background Berbeda per Menu")
        target = st.selectbox("Pilih Menu", ["LOGIN", "🏠_Profil_Sekolah", "📝_Pendaftaran_Siswa_Baru", "📋_Daftar_Siswa_Terdaftar", "📸_Galeri_Sekolah", "👨‍🏫_Profil_Guru_&_Staf"])
        f_bg = st.file_uploader(f"Upload Gambar untuk {target}")
        if st.button("Simpan Permanen"):
            save_media(f"BG_{target}", base64.b64encode(f_bg.getvalue()).decode()); st.success("Tersimpan!"); st.rerun()
    else: st.warning("Akses Khusus Admin")
