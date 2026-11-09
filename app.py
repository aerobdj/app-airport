import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import json
import os
import base64
import pydeck as pdk

# Konfigurasi Halaman Web Full Width
st.set_page_config(
    page_title="Airport Tenant Spatial Management",
    page_icon="🛫",
    layout="wide"
)

# Folder Penyimpanan Server Cloud
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)

st.title("🛫 Bandara Tenant Spatial Management System")

# Navigasi Modul Sidebar
st.sidebar.title("Navigasi Modul")
menu = st.sidebar.radio(
    "Pilih Menu:",
    ["1. Upload Layout", "2. Plotting Area", "3. Koneksi Data Tenant", "4. Preview (2D/3D)"]
)

# Helper: Konversi Gambar ke Base64
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""

# Helper: Warna & Label Status
def get_block_status_info(block_id, tenant_data):
    info = tenant_data.get(block_id)
    if not info:
        return "rgba(156, 163, 175, 0.5)", "#6B7280", "Belum Diisi"
    elif info.get("status") == "Occupied":
        return "rgba(234, 179, 8, 0.65)", "#EAB308", f"Terisi: {info.get('nama_tenant', '')}"
    else:
        return "rgba(59, 130, 246, 0.65)", "#3B82F6", "Vacant (Kosong)"


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
        st.success("✅ File denah berhasil di-upload dan disimpan!")
        st.image(image, caption="Preview Layout Denah Ter-upload", use_container_width=True)


# ---------------------------------------------------------
# MODUL 2: PLOTTING AREA
# ---------------------------------------------------------
elif menu == "2. Plotting Area":
    st.header("2. Plotting Area Tenant")
    img_path = os.path.join("uploads", "layout_current.png")
    
    if not os.path.exists(img_path):
        st.warning("⚠️ Silakan upload layout denah terlebih dahulu pada Modul 1.")
    else:
        bg_image = Image.open(img_path)
        st.info("💡 Gambar dan bentuk blok baru di bawah ini. Gunakan toolbar di kanan atas kanvas untuk memindahkan/menggeser blok.")
        
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
# MODUL 3: KONEKSI DATA TENANT (NATIVE STREAMLIT DIALOG)
# ---------------------------------------------------------
elif menu == "3. Koneksi Data Tenant":
    st.header("3. Hubungkan Blok dengan Data Tenant")
    img_path = os.path.join("uploads", "layout_current.png")
    shapes_path = os.path.join("data", "shapes.json")
    
    if not (os.path.exists(img_path) and os.path.exists(shapes_path)):
        st.warning("⚠️ File layout atau data plotting belum lengkap. Selesaikan Modul 1 dan 2 terlebih dahulu.")
    else:
        bg_image = Image.open(img_path)
        img_base64 = get_image_base64(img_path)
        
        with open(shapes_path, "r") as f:
            shapes = json.load(f)
            
        tenant_db_path = os.path.join("data", "tenants.json")
        tenant_data = {}
        if os.path.exists(tenant_db_path):
            with open(tenant_db_path, "r") as f:
                tenant_data = json.load(f)

        st.caption("Keterangan Warna Status: ⚪ Abu-abu = Belum Diisi | 🟡 Kuning = Terisi (Occupied) | 🔵 Biru = Kosong (Vacant)")
        
        # Pop-Up Form Input Tenant (Modal)
        @st.dialog("📝 Form Input Data Tenant")
        def open_tenant_form_dialog(block_id):
            st.markdown(f"### Mengedit Blok: `{block_id}`")
            current_info = tenant_data.get(block_id, {})
            
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
                    tenant_data[block_id] = {
                        "status": "Occupied",
                        "nama_tenant": nama_tenant,
                        "kategori": kategori,
                        "omzet": omzet,
                        "listrik": listrik,
                        "air": air,
                        "kontrak": kontrak
                    }
                else:
                    tenant_data[block_id] = {
                        "status": "Vacant",
                        "peruntukan": peruntukan,
                        "luas": luas,
                        "base_rent": base_rent
                    }
                
                with open(tenant_db_path, "w") as f:
                    json.dump(tenant_data, f, indent=4)
                
                st.success(f"Data untuk {block_id} berhasil disimpan!")
                st.rerun()

        # Grid Tombol Interaktif Blok
        st.markdown("### 📍 Pilih Blok Ruangan:")
        cols = st.columns(4)
        for idx, shape in enumerate(shapes):
            block_id = f"BLK-{idx+1}"
            fill, stroke, status_text = get_block_status_info(block_id, tenant_data)
            
            with cols[idx % 4]:
                if st.button(f"📌 {block_id}\n({status_text})", key=f"btn_m3_{block_id}", use_container_width=True):
                    open_tenant_form_dialog(block_id)

        st.markdown("---")
        show_bg_m3 = st.checkbox("🖼️ Tampilkan Gambar Denah Asli (Visual Preview)", value=True, key="bg_m3")

        # Layout Viewer
        svg_rects = ""
        for idx, shape in enumerate(shapes):
            block_id = f"BLK-{idx+1}"
            fill, stroke, _ = get_block_status_info(block_id, tenant_data)
            left = shape.get("left", 0)
            top = shape.get("top", 0)
            width = shape.get("width", 50) * shape.get("scaleX", 1)
            height = shape.get("height", 50) * shape.get("scaleY", 1)
            
            svg_rects += f"""
            <rect x="{left}" y="{top}" width="{width}" height="{height}" 
                  fill="{fill}" stroke="{stroke}" stroke-width="2" rx="4" />
            <text x="{left + width/2}" y="{top + height/2}" fill="#ffffff" font-size="13" font-weight="bold" 
                  text-anchor="middle" dominant-baseline="middle">{block_id}</text>
            """

        bg_img_html = f'<img src="{img_base64}" style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;" />' if show_bg_m3 else ''

        html_preview = f"""
        <div style="width: 100%; height: 600px; border: 2px solid #e5e7eb; border-radius: 12px; overflow: auto; background: #f8fafc; position: relative;">
            <div style="width: {bg_image.width}px; height: {bg_image.height}px; position: relative;">
                {bg_img_html}
                <svg style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;">
                    {svg_rects}
                </svg>
            </div>
        </div>
        """
        st.components.v1.html(html_preview, height=620)


# ---------------------------------------------------------
# MODUL 4: PREVIEW INTERAKTIF (NATIVE DIALOG TOOLTIP)
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
        img_base64 = get_image_base64(img_path)

        with open(shapes_path, "r") as f:
            shapes = json.load(f)
        
        tenant_data = {}
        if os.path.exists(tenant_db_path):
            with open(tenant_db_path, "r") as f:
                tenant_data = json.load(f)

        col1, col2 = st.columns([2, 2])
        with col1:
            view_mode = st.radio("📐 Mode Tampilan Visual:", ["Mode 2D (Flat Floorplan)", "Mode 3D (Building Extrusion)"], horizontal=True)
        with col2:
            show_bg_m4 = st.checkbox("🖼️ Hide/Show Gambar Denah Asli (Background)", value=True)

        st.markdown("---")

        if view_mode == "Mode 2D (Flat Floorplan)":
            @st.dialog("📊 Tooltip Laporan Detail Spatial")
            def open_detail_dialog(block_id):
                detail = tenant_data.get(block_id)
                st.markdown(f"### Detail Blok: `{block_id}`")
                
                if not detail:
                    st.warning("⚠️ Blok ini belum diisi datanya pada Modul 3.")
                elif detail.get("status") == "Occupied":
                    st.success(f"🟡 **STATUS: TERISI (OCCUPIED)**")
                    st.markdown(f"### Brand: **{detail.get('nama_tenant')}**")
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

            # Grid Inspeksi Laporan Blok
            st.markdown("### 🔍 Klik Blok untuk Membuka Pop-up Laporan Rincian:")
            cols = st.columns(4)
            for idx, shape in enumerate(shapes):
                block_id = f"BLK-{idx+1}"
                _, _, status_text = get_block_status_info(block_id, tenant_data)
                
                with cols[idx % 4]:
                    if st.button(f"📊 {block_id}\n({status_text})", key=f"btn_m4_{block_id}", use_container_width=True):
                        open_detail_dialog(block_id)

            st.markdown("---")

            # Layout Map Preview
            svg_rects_m4 = ""
            for idx, shape in enumerate(shapes):
                block_id = f"BLK-{idx+1}"
                fill, stroke, _ = get_block_status_info(block_id, tenant_data)
                left = shape.get("left", 0)
                top = shape.get("top", 0)
                width = shape.get("width", 50) * shape.get("scaleX", 1)
                height = shape.get("height", 50) * shape.get("scaleY", 1)
                
                svg_rects_m4 += f"""
                <rect x="{left}" y="{top}" width="{width}" height="{height}" 
                      fill="{fill}" stroke="{stroke}" stroke-width="2" rx="4" />
                <text x="{left + width/2}" y="{top + height/2}" fill="#ffffff" font-size="13" font-weight="bold" 
                      text-anchor="middle" dominant-baseline="middle">{block_id}</text>
                """

            bg_img_m4_html = f'<img src="{img_base64}" style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;" />' if show_bg_m4 else ''

            html_preview_m4 = f"""
            <div style="width: 100%; height: 600px; border: 2px solid #e5e7eb; border-radius: 12px; overflow: auto; background: #f8fafc; position: relative;">
                <div style="width: {bg_image.width}px; height: {bg_image.height}px; position: relative;">
                    {bg_img_m4_html}
                    <svg style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;">
                        {svg_rects_m4}
                    </svg>
                </div>
            </div>
            """
            st.components.v1.html(html_preview_m4, height=620)

        # Mode 3D
        else:
            st.subheader("🧊 Tampilan Modellling 3D Interaktif (Thick Extrusion)")
            st.caption("Tanpa gambar latar belakang denah. Ketebalan ketinggian blok 3D ditambah secara dinamis.")
            
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
                    color = [156, 163, 175, 200]
                    elevation = 80
                elif status == "Occupied":
                    color = [234, 179, 8, 220]
                    elevation = 160
                else:
                    color = [59, 130, 246, 220]
                    elevation = 110

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
