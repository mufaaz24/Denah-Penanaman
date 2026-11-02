import os
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MousePosition, Search
from streamlit_folium import st_folium

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Denah Penanaman Pohon - Prau via Igirmranak",
    layout="wide"
)

st.title(" DENAH PENANAMAN POHON")
st.subheader("Jalur Pendakian Gunung Prau via Igirmranak")

# ---------------------------------------------------------
# 2. PENYIMPANAN DATA PERMANEN VIA FILE CSV
# ---------------------------------------------------------
CSV_FILE = "pohon_data.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=['ID_Pohon', 'Jenis_Pohon', 'Latitude', 'Longitude'])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

if 'pohon_db' not in st.session_state:
    st.session_state['pohon_db'] = load_data()

COLOR_MAP = {
    'Salam': '#22c55e',       # Hijau Muda
    'Trembesi': '#0284c7',    # Biru
    'Beringin': '#15803d',    # Hijau Tua
    'Gayam': '#a855f7',       # Ungu
    'Jambu Biji': '#f97316'   # Oranye
}

# ---------------------------------------------------------
# 3. DATA KOORDINAT JALUR IGIRMRANAK (SUDAH DISESUAIKAN KE JALUR MERAH)
# ---------------------------------------------------------
pos_igirmranak = [
    {"nama": "Base camp Igirmranak", "lat": -7.223212, "lon": 109.951675, "tipe": "pos", "desc": "Base camp Igirmranak"},
    {"nama": "Pos 1", "lat": -7.216562, "lon": 109.945841, "tipe": "pos", "desc": "Pos 1 Igirmranak"},
    {"nama": "Gapura Pandan Wangi", "lat": -7.214831, "lon": 109.944603, "tipe": "pos", "desc": "Gapura Pandan Wangi"},
    {"nama": "Simpang Jalur Setapak", "lat": -7.212785, "lon": 109.943239, "tipe": "pos", "desc": "Belokan ke Jalur Setapak Hutan"},
    

    {"nama": "Pos 2 Bukit Cendani (Baru)", "lat": -7.212183, "lon": 109.940699, "tipe": "pos", "desc": "Bukit Cendani"},
    
    {"nama": "Pos 3", "lat": -7.210354, "lon": 109.940953, "tipe": "pos", "desc": "Pos 3 Igirmranak"},
    {"nama": "Campsite Plawangan", "lat": -7.205644, "lon": 109.939861, "tipe": "camp", "desc": "Area Camping Plawangan"},
    {"nama": "Campsite Cemoro Tunggal", "lat": -7.203698, "lon": 109.938740, "tipe": "camp", "desc": "Area Camping Cemoro Tunggal"},
    {"nama": "Puncak", "lat": -7.190508, "lon": 109.927627, "tipe": "puncak", "desc": "Puncak Gunung Prau"}
]

line_coords = [[p["lat"], p["lon"]] for p in pos_igirmranak]

# ---------------------------------------------------------
# 4. SIDEBAR INPUT MANUAL & KONTROL
# ---------------------------------------------------------
st.sidebar.header("➕ Form Input Manual Pohon")

with st.sidebar.form(key="form_input_pohon", clear_on_submit=True):
    jenis_pohon = st.selectbox(
        "Pilih Jenis Pohon", 
        options=['Salam', 'Trembesi', 'Beringin', 'Gayam', 'Jambu Biji']
    )
    input_lat = st.number_input("Latitude", value=-7.216562, format="%.6f")
    input_lon = st.number_input("Longitude", value=109.945841, format="%.6f")
    
    btn_submit = st.form_submit_button("Tambahkan ke Denah")

if btn_submit:
    df_current = load_data()
    new_id = f"PHN-{len(df_current) + 1:03d}"
    new_row = pd.DataFrame([{
        'ID_Pohon': new_id,
        'Jenis_Pohon': jenis_pohon,
        'Latitude': input_lat,
        'Longitude': input_lon
    }])
    df_updated = pd.concat([df_current, new_row], ignore_index=True)
    save_data(df_updated)
    st.session_state['pohon_db'] = df_updated
    st.sidebar.success(f"Berhasil menambahkan {jenis_pohon} ({new_id})!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("Keterangan Warna Lingkaran Pohon")
for jenis, color in COLOR_MAP.items():
    st.sidebar.markdown(f"<span style='color:{color}; font-size:16px;'>██</span> <b>{jenis}</b>", unsafe_allow_html=True)

# SIDEBAR: KELOLA DATA (HAPUS SATU & RESET ALL)
st.sidebar.markdown("---")
st.sidebar.markdown("Kelola Data Pohon")

df_pohon = load_data()
st.session_state['pohon_db'] = df_pohon

if not df_pohon.empty:
    pohon_to_delete = st.sidebar.selectbox(
        "Pilih ID Pohon yang Ingin Dihapus",
        options=df_pohon['ID_Pohon'].tolist()
    )
    
    if st.sidebar.button(f"❌ Hapus {pohon_to_delete}"):
        df_updated = df_pohon[df_pohon['ID_Pohon'] != pohon_to_delete].reset_index(drop=True)
        save_data(df_updated)
        st.session_state['pohon_db'] = df_updated
        st.sidebar.success(f"Berhasil menghapus {pohon_to_delete}!")
        st.rerun()

    st.sidebar.markdown("---")
    
    if st.sidebar.button("⚠️ Reset Semua Data Denah"):
        df_empty = pd.DataFrame(columns=['ID_Pohon', 'Jenis_Pohon', 'Latitude', 'Longitude'])
        save_data(df_empty)
        st.session_state['pohon_db'] = df_empty
        st.rerun()
else:
    st.sidebar.info("Belum ada data pohon yang diinput.")

# ---------------------------------------------------------
# 5. MEMBUAT PETA DENAH INTERAKTIF (FOLIUM)
# ---------------------------------------------------------
m = folium.Map(
    location=[-7.2035, 109.9367],
    zoom_start=14,
    tiles="OpenStreetMap"
)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery",
    name="Peta Satelit"
).add_to(m)

folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap",
    name="Peta Topografi"
).add_to(m)

MousePosition(
    position="topright",
    separator=" | Longitude: ",
    empty_string="Arahkan kursor ke peta",
    lng_first=False,
    num_digits=6,
    prefix="Latitude: "
).add_to(m)

# DRAWING JALUR PENDAKIAN IGIRMRANAK
folium.PolyLine(
    locations=line_coords,
    weight=8,
    color="#111827",
    opacity=0.8,
    tooltip="Jalur Pendakian Igirmranak"
).add_to(m)

folium.PolyLine(
    locations=line_coords,
    weight=4,
    color="#f97316",
    opacity=1.0
).add_to(m)

# MARKER SEGITIGA POS & TITIK PENTING
pos_group = folium.FeatureGroup(name="Pos & Titik Penting Igirmranak").add_to(m)

for pos in pos_igirmranak:
    if pos["tipe"] == "puncak":
        color_fill = "#dc2626"
    elif pos["tipe"] == "camp":
        color_fill = "#3b82f6"
    else:
        color_fill = "#f97316"
        
    popup_pos = f"<b>{pos['nama']}</b><br>{pos['desc']}<br><small>Lat: {pos['lat']:.6f}, Lon: {pos['lon']:.6f}</small>"
    
    folium.RegularPolygonMarker(
        location=[pos["lat"], pos["lon"]],
        number_of_sides=3,
        radius=12,
        color="#000000",
        fill_color=color_fill,
        fill_opacity=1.0,
        popup=folium.Popup(popup_pos, max_width=220),
        tooltip=pos["nama"],
        title=pos["nama"]
    ).add_to(pos_group)

Search(
    layer=pos_group,
    geom_type="Point",
    placeholder="Cari Pos / Campsite / Puncak...",
    collapsed=False,
    search_label="title"
).add_to(m)

# RENDER LINGKARAN POHON HASIL INPUT MANUAL
for _, row in df_pohon.iterrows():
    pohon_color = COLOR_MAP.get(row['Jenis_Pohon'], 'blue')
    popup_text = f"<b>ID Pohon:</b> {row['ID_Pohon']}<br><b>Jenis:</b> {row['Jenis_Pohon']}<br><b>Koordinat:</b> {row['Latitude']:.6f}, {row['Longitude']:.6f}"
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=9,
        popup=folium.Popup(popup_text, max_width=200),
        tooltip=f"{row['ID_Pohon']} - {row['Jenis_Pohon']}",
        color="#ffffff",
        weight=2,
        fill=True,
        fill_color=pohon_color,
        fill_opacity=0.9
    ).add_to(m)

folium.LayerControl().add_to(m)

# ---------------------------------------------------------
# RENDER DASHBOARD STREAMLIT
# ---------------------------------------------------------
col_map, col_table = st.columns([3, 1])

with col_map:
    st_folium(m, width=950, height=600)

with col_table:
    st.markdown("Statistik Denah")
    st.metric("Total Pohon Ditanam", len(df_pohon))
    if not df_pohon.empty:
        st.dataframe(df_pohon['Jenis_Pohon'].value_counts(), use_container_width=True)

st.markdown("---")
st.markdown("#Daftar Koordinat Penanaman Pohon")
st.dataframe(df_pohon, use_container_width=True)