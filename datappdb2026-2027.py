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

# --- 3. STANDARISASI KOLOM ---
# Menambahkan kolom "No. WhatsApp" agar bisa dikirimi pesan
KOLOM_DATABASE = [
    "No. Registrasi", "Nama Lengkap", "NISN", "NIS Lokal", "NIK Siswa", 
    "Jenis Kelamin", "No. WhatsApp Wali", "Nama Ayah", "Nama Ibu", 
    "Alamat Lengkap", "Tanggal Daftar", "Status Verifikasi"
]

# --- 4. UI SETUP ---
st.set_page_config(page_title="PPDB AL IRSYAD KEDIRI", page_icon="🏫", layout="wide")

st.markdown("""
    <style>
    .main-header {text-align: center; background-color: #1E5128; padding: 25px; border-radius: 10px; color: white; margin-bottom: 25px;}
    .stButton>button {width: 100%; border-radius: 8px; height: 3.5em; background-color: #1E5128; color: white; font-weight: bold;}
    .section-header {background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 20px; margin-bottom: 10px; border-left: 5px solid #1E5128;}
    </style>
    <div class="main-header">
        <h1>SISTEM INFORMASI PPDB & NOTIFIKASI</h1>
        <h3>KB-RA AL IRSYAD AL ISLAMIIYAH KOTA KEDIRI</h3>
    </div>
""", unsafe_allow_html=True)

client = init_google_sheets()
if not client: st.stop()

menu = st.sidebar.radio("MENU UTAMA", ["📝 Pendaftaran Murid", "📊 Dashboard Admin"])

# --- MODUL 1: PENDAFTARAN ---
if menu == "📝 Pendaftaran Murid":
    with st.form("ppdb_form", clear_on_submit=True):
        st.markdown('<div class="section-header">📑 DATA SISWA & KONTAK</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        nama = c1.text_input("Nama Lengkap*")
        nik_s = c2.text_input("NIK Siswa (16 Digit)*")
        no_wa = c1.text_input("Nomor WhatsApp Wali (Contoh: 08123xxx)*")
        jk = c2.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        
        st.markdown('<div class="section-header">👨‍👩‍👧‍👦 DATA KELUARGA & ALAMAT</div>', unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        n_ayah = a1.text_input("Nama Ayah Kandung")
        n_ibu = a2.text_input("Nama Ibu Kandung")
        alamat = st.text_area("Alamat Lengkap")

        btn_submit = st.form_submit_button("✅ DAFTAR SEKARANG")
        
        if btn_submit:
            if nama and nik_s and no_wa:
                try:
                    sheet = client.open(SHEET_NAME).sheet1
                    reg_id = f"REG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    # Format nomor WA agar depannya 62
                    wa_fix = no_wa.replace("08", "628", 1) if no_wa.startswith("08") else no_wa
                    
                    data_final = [
                        reg_id, nama, "", "", f"'{nik_s}", 
                        jk, wa_fix, n_ayah, n_ibu, 
                        alamat, datetime.now().strftime("%Y-%m-%d"), "Belum Diverifikasi"
                    ]
                    sheet.append_row(data_final)
                    
                    st.success(f"Berhasil Terdaftar! No. Registrasi Anda: {reg_id}")
                    
                    # Pesan Otomatis WhatsApp
                    pesan = f"Konfirmasi PPDB KB-RA AL IRSYAD KEDIRI\n\nAlhamdulillah, pendaftaran Ananda *{nama}* telah kami terima.\nNo. Registrasi: *{reg_id}*\nStatus: Belum Diverifikasi\n\nTerima kasih."
                    encoded_pesan = urllib.parse.quote(pesan)
                    wa_url = f"https://wa.me/{wa_fix}?text={encoded_pesan}"
                    
                    st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 KLIK DI SINI UNTUK KIRIM KONFIRMASI KE WHATSAPP</button></a>', unsafe_allow_html=True)
                    st.balloons()
                except Exception as e: st.error(f"Error: {e}")
            else: st.warning("Nama, NIK, dan Nomor WhatsApp wajib diisi!")

# --- MODUL 2: DASHBOARD ADMIN ---
elif menu == "📊 Dashboard Admin":
    st.subheader("🛠 Pusat Kendali Admin")
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        pw_input = st.text_input("Masukkan Kata Sandi Admin", type="password")
        if st.button("Masuk"):
            if pw_input == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.rerun()
            else: st.error("Salah!")
        st.stop()
    
    try:
        sheet = client.open(SHEET_NAME).sheet1
        data_records = sheet.get_all_records()
        tab1, tab2 = st.tabs(["🔍 Monitoring & Kirim Laporan", "📥 Import Excel"])
        
        with tab1:
            if data_records:
                df = pd.DataFrame(data_records)
                st.dataframe(df, use_container_width=True)
                
                st.markdown("### 📤 Kirim Laporan Verifikasi Manual")
                selected_nama = st.selectbox("Pilih Siswa untuk dikirimi laporan:", df['Nama Lengkap'].tolist())
                siswa_data = df[df['Nama Lengkap'] == selected_nama].iloc[0]
                
                if st.button(f"Kirim Laporan untuk {selected_nama}"):
                    pesan_verif = f"Yth. Wali Murid Ananda *{siswa_data['Nama Lengkap']}*,\n\nKami menginformasikan bahwa berkas pendaftaran dengan No. Reg: *{siswa_data['No. Registrasi']}* telah SELESAI DIVERIFIKASI.\n\nSilakan menunggu info selanjutnya. Terima kasih."
                    wa_link = f"https://wa.me/{siswa_data['No. WhatsApp Wali']}?text={urllib.parse.quote(pesan_verif)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank">Klik di sini untuk mengirim pesan ke {siswa_data["No. WhatsApp Wali"]}</a>', unsafe_allow_html=True)
            else: st.info("Kosong.")

        with tab2:
            # (Fitur Import Excel tetap sama seperti sebelumnya)
            df_template = pd.DataFrame(columns=KOLOM_DATABASE)
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df_template.to_excel(writer, index=False)
            st.download_button("📥 Unduh Template Excel", data=buffer.getvalue(), file_name="Template_PPDB.xlsx")
            
    except Exception as e: st.error(f"Error: {e}")
