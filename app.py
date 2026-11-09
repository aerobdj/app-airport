import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import json
import os
import pydeck as pdk

# Konfigurasi Halaman Web
st.set_page_config(
    page_title="Airport Tenant Spatial Management",
    page_icon="🛫",
    layout="wide"
)

# Folder Penyimpanan Lokal Server Cloud
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)

st.title("🛫 Bandara Tenant Spatial Management System")

# Navigasi Modul Sidebar
st.sidebar.title("Navigasi Modul")
menu = st.sidebar.radio(
    "Pilih Menu:",
    ["1. Upload Layout", "2. Plotting Area", "3. Koneksi Data Tenant", "4. Preview (2D/3D)"]
)

# Helper: Konversi Warna Berdasarkan Status Tenant
def get_status_color(block_id, tenant_data):
    info = tenant_data.get(block_id)
    if not info:
        return "rgba(156, 163, 175, 0.5)", "#6B7280"  # Abu-abu (Belum Diisi)
    elif info.get("status") == "Occupied":
        return "rgba(234, 179, 8, 0.65)", "#EAB308"   # Kuning (Terisi)
    else:
        return "rgba(59, 130, 246, 0.65)", "#3B82F6"  # Biru (Kosong/Vacant)

# ---------------------------------------------------------
# MODUL 1: UPLOAD LAYOUT
# ---------------------------------------------------------
if menu == "1. Upload Layout":
    st.header("1. Upload Maps / Layout Bandara")
    uploaded_file = st.file_uploader("Pilih file gambar denah (PNG/JPG)", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        img_path = os.path.join("uploads", "layout_current.png")
        image = Image.open(uploaded_file)
        image.save(img_path)
        st.success("✅ File denah berhasil di-upload dan disimpan di server!")
        st.image(image, caption="Preview Layout Denah Ter-upload", use_container_width=True)

# ---------------------------------------------------------
# MODUL 2: PLOTTING AREA (CANVAS EDITOR)
# ---------------------------------------------------------
elif menu == "2. Plotting Area":
    st.header("2. Plotting Area Tenant")
    img_path = os.path.join("uploads", "layout_current.png")
    
    if not os.path.exists(img_path):
        st.warning("⚠️ Silakan upload layout denah terlebih dahulu pada Modul 1.")
    else:
        bg_image = Image.open(img_path)
        st.info("💡 Buat bentuk blok baru pada denah di bawah. Gunakan toolbar di kanan atas kanvas untuk memindahkan/menggeser blok.")
        
        tool_choice = st.sidebar.selectbox("Pilih Tool Gambar:", ["Persegi (Kotak)", "Garis Bebas / Polygon"])
        drawing_mode = "rect" if tool_choice == "Persegi (Kotak)" else "freedraw"
        
        stroke_color = st.sidebar.color_picker("Warna Garis Blok:", "#2563EB")
        fill_color_hex = st.sidebar.color_picker("Warna Isi Blok:", "#2563EB")
        
        hex_val = fill_color_hex.lstrip('#')
        r, g, b = tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))
        fill_color = f"rgba({r}, {g}, {b}, 0.3)"
        
        canvas_result = st_canvas(
            fill_color=fill_color,
            stroke_width=2,
            stroke_color=stroke_color,
            background_image=bg_image,
            update_streamlit=True,
            height=bg_image.height if bg_image.height < 800 else 800,
            width=bg_image.width if bg_image.width < 1200 else 1200,
            drawing_mode=drawing_mode,
            key="canvas_plotting",
        )
        
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data.get("objects", [])
            st.info(f"📍 Jumlah blok terdeteksi saat ini: **{len(objects)} blok**")
            
            if st.button("💾 Simpan Data Plotting Blok"):
                if len(objects) == 0:
                    st.error("Belum ada blok yang digambar!")
                else:
                    with open(os.path.join("data", "shapes.json"), "w") as f:
                        json.dump(objects, f)
                    st.success(f"✅ Berhasil menyimpan {len(objects)} blok!")

# ---------------------------------------------------------
# MODUL 3: KONEKSI DATA TENANT
# ---------------------------------------------------------
elif menu == "3. Koneksi Data Tenant":
    st.header("3. Hubungkan Blok dengan Data Tenant")
    img_path = os.path.join("uploads", "layout_current.png")
    shapes_path = os.path.join("data", "shapes.json")
    
    if not (os.path.exists(img_path) and os.path.exists(shapes_path)):
        st.warning("⚠️ File layout atau data plotting belum lengkap. Selesaikan Modul 1 dan 2 terlebih dahulu.")
    else:
        bg_image = Image.open(img_path)
        with open(shapes_path, "r") as f:
            shapes = json.load(f)
            
        tenant_db_path = os.path.join("data", "tenants.json")
        tenant_data = {}
        if os.path.exists(tenant_db_path):
            with open(tenant_db_path, "r") as f:
                tenant_data = json.load(f)

        st.caption("Keterangan Warna: ⚪ Abu-abu = Belum Diisi | 🟡 Kuning = Terisi (Occupied) | 🔵 Biru = Kosong (Vacant)")

        selected_index = st.selectbox(
            "📍 Pilih Blok yang ingin diisi/edit datanya:",
            range(len(shapes)),
            format_func=lambda i: f"BLK-{i+1} [{'Terisi' if tenant_data.get(f'BLK-{i+1}',{}).get('status')=='Occupied' else ('Kosong' if tenant_data.get(f'BLK-{i+1}',{}).get('status')=='Vacant' else 'Belum Diisi')}]"
        )
        
        # Render Kanvas Locked
        colored_shapes = []
        for idx, shape in enumerate(shapes):
            block_id = f"BLK-{idx+1}"
            is_selected = (idx == selected_index)
            fill = "rgba(239, 68, 68, 0.75)" if is_selected else get_status_color(block_id, tenant_data)[0]
            stroke = "#EF4444" if is_selected else get_status_color(block_id, tenant_data)[1]
            
            s_copy = dict(shape)
            s_copy["fill"] = fill
            s_copy["stroke"] = stroke
            colored_shapes.append(s_copy)

        st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=2,
            background_image=bg_image,
            initial_drawing={"objects": colored_shapes},
            update_streamlit=False,
            height=bg_image.height if bg_image.height < 800 else 800,
            width=bg_image.width if bg_image.width < 1200 else 1200,
            drawing_mode="rect",
            key="canvas_koneksi_locked",
        )

        selected_block_id = f"BLK-{selected_index+1}"

        @st.dialog(f"📝 Form Input Data Tenant: {selected_block_id}")
        def open_tenant_form():
            current_info = tenant_data.get(selected_block_id, {})
            
            status = st.selectbox("Status Blok", ["Kosong (Vacant)", "Terisi (Occupied)"], 
                                  index=1 if current_info.get("status") == "Occupied" else 0)
            
            if status == "Terisi (Occupied)":
                nama_tenant = st.text_input("Nama Tenant / Brand", value=current_info.get("nama_tenant", ""))
                kategori = st.selectbox("Kategori", ["Food & Beverage", "Retail", "Services", "Lounge"])
                omzet = st.text_input("Realisasi Omzet (Rp)", value=current_info.get("omzet", "Rp 0"))
                listrik = st.text_input("Konsumsi Listrik", value=current_info.get("listrik", "0 kWh"))
                air = st.text_input("Konsumsi Air", value=current_info.get("air", "0 m³"))
                kontrak = st.text_input("Jatuh Tempo Kontrak", value=current_info.get("kontrak", "2027-12-31"))
            else:
                peruntukan = st.selectbox("Rekomendasi Peruntukan", ["FnB Only", "Retail Souvenir", "ATM Center", "Dry Retail"])
                luas = st.text_input("Luas Area", value=current_info.get("luas", "50 m²"))
                base_rent = st.text_input("Target Base Rent / m²", value=current_info.get("base_rent", "Rp 300.000"))

            if st.button("💾 Simpan Data Tenant", use_container_width=True):
                if status == "Terisi (Occupied)":
                    tenant_data[selected_block_id] = {
                        "status": "Occupied",
                        "nama_tenant": nama_tenant,
                        "kategori": kategori,
                        "omzet": omzet,
                        "listrik": listrik,
                        "air": air,
                        "kontrak": kontrak
                    }
                else:
                    tenant_data[selected_block_id] = {
                        "status": "Vacant",
                        "peruntukan": peruntukan,
                        "luas": luas,
                        "base_rent": base_rent
                    }
                
                with open(tenant_db_path, "w") as f:
                    json.dump(tenant_data, f, indent=4)
                st.success(f"Data untuk {selected_block_id} berhasil disimpan!")
                st.rerun()

        st.markdown("---")
        if st.button(f"🔴 Proses & Isi Data Tenant untuk {selected_block_id}", type="primary"):
            open_tenant_form()

# ---------------------------------------------------------
# MODUL 4: PREVIEW INTERAKTIF (2D / 3D)
# ---------------------------------------------------------
elif menu == "4. Preview (2D/3D)":
    st.header("4. Dashboard Preview Spatial Tenant Bandara")
    img_path = os.path.join("uploads", "layout_current.png")
    shapes_path = os.path.join("data", "shapes.json")
    tenant_db_path = os.path.join("data", "tenants.json")
    
    if not (os.path.exists(img_path) and os.path.exists(shapes_path)):
        st.warning("⚠️ File layout atau data plotting belum lengkap. Selesaikan Modul 1, 2, dan 3 terlebih dahulu.")
    else:
        bg_image = Image.open(img_path)
        with open(shapes_path, "r") as f:
            shapes = json.load(f)
        
        tenant_data = {}
        if os.path.exists(tenant_db_path):
            with open(tenant_db_path, "r") as f:
                tenant_data = json.load(f)

        view_mode = st.radio("📐 Mode Tampilan Visual:", ["Mode 2D (Flat Floorplan)", "Mode 3D (Building Extrusion)"], horizontal=True)

        if view_mode == "Mode 2D (Flat Floorplan)":
            col_preview, col_list = st.columns([3, 1])
            
            with col_list:
                st.subheader("📌 Inspeksi Blok")
                selected_index = st.selectbox(
                    "Pilih Blok untuk Dilihat Rinciannya:",
                    range(len(shapes)),
                    format_func=lambda i: f"BLK-{i+1} ({tenant_data.get(f'BLK-{i+1}',{}).get('nama_tenant', 'Vacant/Belum Diisi')})"
                )
                
                st.caption("Keterangan Warna:\n- ⚪ Abu-abu: Belum Diisi\n- 🟡 Kuning: Terisi (Occupied)\n- 🔵 Biru: Kosong (Vacant)\n- 🔴 Merah: Terpilih")

            selected_id = f"BLK-{selected_index+1}"

            with col_preview:
                show_bg = st.checkbox("🖼️ Tampilkan Gambar Denah Asli", value=True)
                display_bg = bg_image if show_bg else None

                colored_shapes = []
                for idx, shape in enumerate(shapes):
                    block_id = f"BLK-{idx+1}"
                    is_selected = (idx == selected_index)
                    fill = "rgba(239, 68, 68, 0.8)" if is_selected else get_status_color(block_id, tenant_data)[0]
                    stroke = "#EF4444" if is_selected else get_status_color(block_id, tenant_data)[1]
                    
                    s_copy = dict(shape)
                    s_copy["fill"] = fill
                    s_copy["stroke"] = stroke
                    colored_shapes.append(s_copy)

                st_canvas(
                    fill_color="rgba(0,0,0,0)",
                    stroke_width=2,
                    background_image=display_bg,
                    initial_drawing={"objects": colored_shapes},
                    update_streamlit=False,
                    height=bg_image.height if bg_image.height < 800 else 800,
                    width=bg_image.width if bg_image.width < 1200 else 1200,
                    drawing_mode="rect",
                    key="canvas_preview_locked",
                )

            @st.dialog(f"📊 Rincian Detail Spatial: {selected_id}")
            def open_detail_popup():
                detail = tenant_data.get(selected_id)
                if not detail:
                    st.warning("⚠️ Blok ini belum diisi datanya pada Modul 3.")
                elif detail.get("status") == "Occupied":
                    st.success(f"🟡 **STATUS: TERISI (OCCUPIED)**")
                    st.markdown(f"### Tenant: **{detail.get('nama_tenant')}**")
                    st.write(f"🏢 **Kategori:** {detail.get('kategori')}")
                    st.write(f"💰 **Realisasi Omzet:** {detail.get('omzet')}")
                    st.write(f"⚡ **Konsumsi Listrik:** {detail.get('listrik')}")
                    st.write(f"💧 **Konsumsi Air:** {detail.get('air')}")
                    st.write(f"📅 **Jatuh Tempo Kontrak:** {detail.get('kontrak')}")
                else:
                    st.info(f"🔵 **STATUS: KOSONG (VACANT)**")
                    st.write(f"📌 **Rekomendasi Peruntukan:** {detail.get('peruntukan')}")
                    st.write(f"📐 **Luas Area:** {detail.get('luas')}")
                    st.write(f"💵 **Target Base Rent:** {detail.get('base_rent')}")

            if st.button(f"🔴 Buka Pop-up Rincian Laporan {selected_id}", type="primary"):
                open_detail_popup()

        else:
            st.subheader("🧊 Tampilan Modellling 3D Interaktif")
            
            polygon_data = []
            for idx, shape in enumerate(shapes):
                block_id = f"BLK-{idx+1}"
                info = tenant_data.get(block_id, {})
                status = info.get("status", "Vacant")
                
                left = shape.get("left", 0)
                top = shape.get("top", 0)
                width = shape.get("width", 50) * shape.get("scaleX", 1)
                height = shape.get("height", 50) * shape.get("scaleY", 1)

                x0, y0 = left / 100, -top / 100
                x1, y1 = (left + width) / 100, -(top + height) / 100

                coords = [[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]

                if not info:
                    color = [156, 163, 175, 180]
                    elevation = 10
                elif status == "Occupied":
                    color = [234, 179, 8, 200]
                    elevation = 40
                else:
                    color = [59, 130, 246, 200]
                    elevation = 25

                polygon_data.append({
                    "name": f"{block_id} - {info.get('nama_tenant', 'Vacant/Belum Diisi')}",
                    "contour": coords,
                    "color": color,
                    "elevation": elevation
                })

            layer = pdk.Layer(
                "PolygonLayer",
                polygon_data,
                get_polygon="contour",
                get_fill_color="color",
                get_elevation="elevation",
                extruded=True,
                wireframe=True,
                pickable=True,
            )

            view_state = pdk.ViewState(latitude=0, longitude=0, zoom=14, pitch=55, bearing=30)
            r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name}"})
            st.pydeck_chart(r)
