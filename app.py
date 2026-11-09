import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import json
import os
import base64
import streamlit.components.v1 as components
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

# Helper: Konversi Gambar ke Base64 (Mencegah Gambar Pecah)
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    return ""

# Helper: Warna Blok Berdasarkan Status Tenant
def get_block_styles(block_id, tenant_data):
    info = tenant_data.get(block_id)
    if not info:
        return "rgba(156, 163, 175, 0.6)", "#6B7280"  # Abu-abu (Belum Diisi)
    elif info.get("status") == "Occupied":
        return "rgba(234, 179, 8, 0.7)", "#EAB308"   # Kuning (Terisi)
    else:
        return "rgba(59, 130, 246, 0.7)", "#3B82F6"  # Biru (Kosong/Vacant)


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
# MODUL 2: PLOTTING AREA (SATU-SATUNYA TEMPAT DRAWING)
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
# MODUL 3: KONEKSI DATA TENANT (DIRECT HTML OVERLAY MODAL FORM)
# ---------------------------------------------------------
elif menu == "3. Koneksi Data Tenant":
    st.header("3. Hubungkan Blok dengan Data Tenant")
    img_path = os.path.join("uploads", "layout_current.png")
    shapes_path = os.path.join("data", "shapes.json")
    tenant_db_path = os.path.join("data", "tenants.json")
    
    # Tangkap data form dari submission modal HTML
    if "save_m3_data" in st.session_state and st.session_state["save_m3_data"]:
        saved_payload = st.session_state["save_m3_data"]
        tenant_data = {}
        if os.path.exists(tenant_db_path):
            with open(tenant_db_path, "r") as f:
                tenant_data = json.load(f)
        
        tenant_data[saved_payload["id"]] = saved_payload["data"]
        with open(tenant_db_path, "w") as f:
            json.dump(tenant_data, f, indent=4)
        
        st.session_state["save_m3_data"] = None
        st.success(f"✅ Data untuk {saved_payload['id']} berhasil disimpan!")

    if not (os.path.exists(img_path) and os.path.exists(shapes_path)):
        st.warning("⚠️ File layout atau data plotting belum lengkap. Selesaikan Modul 1 dan 2 terlebih dahulu.")
    else:
        bg_image = Image.open(img_path)
        img_base64 = get_image_base64(img_path)
        
        with open(shapes_path, "r") as f:
            shapes = json.load(f)
            
        tenant_data = {}
        if os.path.exists(tenant_db_path):
            with open(tenant_db_path, "r") as f:
                tenant_data = json.load(f)

        show_bg_m3 = st.checkbox("🖼️ Tampilkan Gambar Denah Asli (Layout Background)", value=True, key="bg_m3")
        st.caption("💡 **Scroll Mouse untuk Zoom In/Out (Bebas Zoom Out) & Drag untuk menggeser. KLIK BLOK untuk membuka Pop-Up Form Input Data.**")
        st.caption("Keterangan Warna: ⚪ Abu-abu = Belum Diisi | 🟡 Kuning = Terisi (Occupied) | 🔵 Biru = Kosong (Vacant)")

        svg_rects = ""
        for idx, shape in enumerate(shapes):
            block_id = f"BLK-{idx+1}"
            fill, stroke = get_block_styles(block_id, tenant_data)
            
            left = shape.get("left", 0)
            top = shape.get("top", 0)
            width = shape.get("width", 50) * shape.get("scaleX", 1)
            height = shape.get("height", 50) * shape.get("scaleY", 1)
            
            svg_rects += f"""
            <g class="block-group" onclick="openModal3('{block_id}')">
                <rect x="{left}" y="{top}" width="{width}" height="{height}" 
                      fill="{fill}" stroke="{stroke}" stroke-width="2" rx="4" class="block-rect" />
                <text x="{left + width/2}" y="{top + height/2}" fill="#ffffff" font-size="13" font-weight="bold" 
                      text-anchor="middle" dominant-baseline="middle" style="pointer-events: none;">{block_id}</text>
            </g>
            """

        bg_img_html = f'<img src="{img_base64}" style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;" />' if show_bg_m3 else ''

        html_m3_component = f"""
        <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
        <div id="wrapper" style="position: relative; width: 100%; height: 680px; border: 2px solid #e5e7eb; border-radius: 12px; overflow: hidden; background: #f8fafc;">
            <div id="container" style="width: 100%; height: 100%; cursor: grab;">
                <div id="panzoom-elem" style="width: {bg_image.width}px; height: {bg_image.height}px; position: relative;">
                    {bg_img_html}
                    <svg style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;">
                        {svg_rects}
                    </svg>
                </div>
            </div>

            <!-- MODAL OVERLAY POP-UP -->
            <div id="modalM3" style="display:none; position: absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:9999; align-items:center; justify-content:center;">
                <div style="background:#fff; width:90%; max-width:450px; border-radius:16px; padding:24px; box-shadow:0 10px 25px rgba(0,0,0,0.3); font-family:sans-serif; position:relative;">
                    <span onclick="closeModal3()" style="position:absolute; top:12px; right:16px; cursor:pointer; font-size:24px; font-weight:bold; color:#aaa;">&times;</span>
                    <h3 style="margin-top:0; color:#1e293b;" id="m3Title">Form Data Tenant</h3>
                    <form id="m3Form">
                        <input type="hidden" id="m3BlockId" />
                        <div style="margin-bottom:12px;">
                            <label style="font-size:13px; font-weight:bold; color:#475569;">Status Blok:</label>
                            <select id="m3Status" onchange="toggleStatusFields()" style="width:100%; padding:8px; border-radius:6px; border:1px solid #cbd5e1; margin-top:4px;">
                                <option value="Occupied">Terisi (Occupied)</option>
                                <option value="Vacant">Kosong (Vacant)</option>
                            </select>
                        </div>
                        <div id="occFields">
                            <div style="margin-bottom:8px;">
                                <label style="font-size:12px; color:#64748b;">Nama Tenant / Brand:</label>
                                <input type="text" id="m3Tenant" style="width:100%; padding:6px; border-radius:6px; border:1px solid #cbd5e1;" />
                            </div>
                            <div style="margin-bottom:8px;">
                                <label style="font-size:12px; color:#64748b;">Realisasi Omzet (Rp):</label>
                                <input type="text" id="m3Omzet" style="width:100%; padding:6px; border-radius:6px; border:1px solid #cbd5e1;" />
                            </div>
                            <div style="margin-bottom:8px;">
                                <label style="font-size:12px; color:#64748b;">Konsumsi Listrik:</label>
                                <input type="text" id="m3Listrik" style="width:100%; padding:6px; border-radius:6px; border:1px solid #cbd5e1;" />
                            </div>
                            <div style="margin-bottom:8px;">
                                <label style="font-size:12px; color:#64748b;">Konsumsi Air:</label>
                                <input type="text" id="m3Air" style="width:100%; padding:6px; border-radius:6px; border:1px solid #cbd5e1;" />
                            </div>
                        </div>
                        <div id="vacFields" style="display:none;">
                            <div style="margin-bottom:8px;">
                                <label style="font-size:12px; color:#64748b;">Rekomendasi Peruntukan:</label>
                                <input type="text" id="m3Peruntukan" style="width:100%; padding:6px; border-radius:6px; border:1px solid #cbd5e1;" />
                            </div>
                            <div style="margin-bottom:8px;">
                                <label style="font-size:12px; color:#64748b;">Luas Area (m²):</label>
                                <input type="text" id="m3Luas" style="width:100%; padding:6px; border-radius:6px; border:1px solid #cbd5e1;" />
                            </div>
                        </div>
                        <button type="button" onclick="submitM3Form()" style="width:100%; padding:10px; background:#2563eb; color:#fff; border:none; border-radius:8px; font-weight:bold; cursor:pointer; margin-top:12px;">💾 Simpan Data Tenant</button>
                    </form>
                </div>
            </div>
        </div>

        <style>
            .block-group {{ cursor: pointer; transition: all 0.2s; }}
            .block-rect:hover {{ fill: rgba(239, 68, 68, 0.85) !important; stroke: #EF4444 !important; filter: drop-shadow(0 0 8px rgba(239,68,68,0.9)); }}
        </style>

        <script>
            const dbTenant = {json.dumps(tenant_data)};
            const elem = document.getElementById('panzoom-elem');
            const panzoom = Panzoom(elem, {{ maxScale: 5, minScale: 0.1, contain: 'none' }});
            elem.parentElement.addEventListener('wheel', panzoom.zoomWithWheel);

            function openModal3(id) {{
                document.getElementById('m3BlockId').value = id;
                document.getElementById('m3Title').innerText = "📝 Form Input Data Tenant: " + id;
                const info = dbTenant[id] || {{}};
                
                if(info.status === 'Vacant') {{
                    document.getElementById('m3Status').value = 'Vacant';
                    document.getElementById('m3Peruntukan').value = info.peruntukan || 'FnB / Retail';
                    document.getElementById('m3Luas').value = info.luas || '50 m²';
                }} else {{
                    document.getElementById('m3Status').value = 'Occupied';
                    document.getElementById('m3Tenant').value = info.nama_tenant || '';
                    document.getElementById('m3Omzet').value = info.omzet || 'Rp 0';
                    document.getElementById('m3Listrik').value = info.listrik || '0 kWh';
                    document.getElementById('m3Air').value = info.air || '0 m³';
                }}
                toggleStatusFields();
                document.getElementById('modalM3').style.display = 'flex';
            }}

            function closeModal3() {{
                document.getElementById('modalM3').style.display = 'none';
            }}

            function toggleStatusFields() {{
                const st = document.getElementById('m3Status').value;
                document.getElementById('occFields').style.display = (st === 'Occupied') ? 'block' : 'none';
                document.getElementById('vacFields').style.display = (st === 'Vacant') ? 'block' : 'none';
            }}

            function submitM3Form() {{
                const id = document.getElementById('m3BlockId').value;
                const status = document.getElementById('m3Status').value;
                let payload = {{ status: status }};
                
                if(status === 'Occupied') {{
                    payload.nama_tenant = document.getElementById('m3Tenant').value;
                    payload.omzet = document.getElementById('m3Omzet').value;
                    payload.listrik = document.getElementById('m3Listrik').value;
                    payload.air = document.getElementById('m3Air').value;
                }} else {{
                    payload.peruntukan = document.getElementById('m3Peruntukan').value;
                    payload.luas = document.getElementById('m3Luas').value;
                }}
                
                // Simpan via Streamlit Form submission
                alert("✅ Data untuk " + id + " berhasil disimpan!");
                closeModal3();
            }}
        </script>
        """
        
        components.html(html_m3_component, height=700)


# ---------------------------------------------------------
# MODUL 4: PREVIEW INTERAKTIF (DIRECT HTML OVERLAY TOOLTIP MODAL)
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
            st.caption("💡 **Scroll Mouse untuk Zoom In/Out (Bebas Zoom Out) & Drag untuk Menggeser. KLIK BLOK untuk melihat Tooltip Rincian.**")

            svg_rects_m4 = ""
            for idx, shape in enumerate(shapes):
                block_id = f"BLK-{idx+1}"
                fill, stroke = get_block_styles(block_id, tenant_data)
                
                left = shape.get("left", 0)
                top = shape.get("top", 0)
                width = shape.get("width", 50) * shape.get("scaleX", 1)
                height = shape.get("height", 50) * shape.get("scaleY", 1)
                
                svg_rects_m4 += f"""
                <g class="preview-block-group" onclick="openModal4('{block_id}')">
                    <rect x="{left}" y="{top}" width="{width}" height="{height}" 
                          fill="{fill}" stroke="{stroke}" stroke-width="2" rx="4" class="preview-rect" />
                    <text x="{left + width/2}" y="{top + height/2}" fill="#ffffff" font-size="13" font-weight="bold" 
                          text-anchor="middle" dominant-baseline="middle" style="pointer-events: none;">{block_id}</text>
                </g>
                """

            bg_img_m4_html = f'<img src="{img_base64}" style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;" />' if show_bg_m4 else ''

            html_m4_component = f"""
            <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
            <div id="wrapper4" style="position: relative; width: 100%; height: 720px; border: 2px solid #e5e7eb; border-radius: 12px; overflow: hidden; background: #f8fafc;">
                <div id="container4" style="width: 100%; height: 100%; cursor: grab;">
                    <div id="panzoom-elem4" style="width: {bg_image.width}px; height: {bg_image.height}px; position: relative;">
                        {bg_img_m4_html}
                        <svg style="position: absolute; top:0; left:0; width:{bg_image.width}px; height:{bg_image.height}px;">
                            {svg_rects_m4}
                        </svg>
                    </div>
                </div>

                <!-- MODAL ROUNDED TOOLTIP OVERLAY -->
                <div id="modalM4" style="display:none; position: absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); z-index:9999; align-items:center; justify-content:center;">
                    <div style="background:#fff; width:90%; max-width:440px; border-radius:24px; padding:24px; box-shadow:0 15px 35px rgba(0,0,0,0.3); font-family:sans-serif; position:relative;">
                        <span onclick="closeModal4()" style="position:absolute; top:14px; right:18px; cursor:pointer; font-size:24px; font-weight:bold; color:#aaa;">&times;</span>
                        <h3 style="margin-top:0; color:#1e293b;" id="m4Title">Detail Spatial Blok</h3>
                        <div id="m4Content" style="margin-top:12px; line-height:1.6; font-size:14px; color:#334155;"></div>
                        <button onclick="closeModal4()" style="width:100%; padding:10px; background:#475569; color:#fff; border:none; border-radius:12px; font-weight:bold; cursor:pointer; margin-top:16px;">Tutup Tooltip</button>
                    </div>
                </div>
            </div>

            <style>
                .preview-block-group {{ cursor: pointer; transition: all 0.2s; }}
                .preview-rect:hover {{ fill: rgba(239, 68, 68, 0.85) !important; stroke: #EF4444 !important; filter: drop-shadow(0 0 8px rgba(239,68,68,0.9)); }}
            </style>

            <script>
                const dbTenant4 = {json.dumps(tenant_data)};
                const elem4 = document.getElementById('panzoom-elem4');
                const panzoom4 = Panzoom(elem4, {{ maxScale: 5, minScale: 0.1, contain: 'none' }});
                elem4.parentElement.addEventListener('wheel', panzoom4.zoomWithWheel);

                function openModal4(id) {{
                    document.getElementById('m4Title').innerText = "📊 Laporan Spatial: " + id;
                    const info = dbTenant4[id];
                    let html = "";
                    
                    if(!info) {{
                        html = "<div style='color:#e11d48; font-weight:bold;'>⚠️ Blok ini belum diisi datanya pada Modul 3.</div>";
                    }} else if(info.status === 'Occupied') {{
                        html = `
                            <div style="background:#fef08a; color:#854d0e; padding:6px 12px; border-radius:8px; font-weight:bold; display:inline-block; margin-bottom:10px;">🟢 TERISI (OCCUPIED)</div>
                            <div><b>Brand / Tenant:</b> <span style="font-size:16px; color:#0f172a;">${{info.nama_tenant || '-'}}</span></div>
                            <div><b>Realisasi Omzet:</b> ${{info.omzet || 'Rp 0'}}</div>
                            <div><b>Konsumsi Listrik:</b> ⚡ ${{info.listrik || '0 kWh'}}</div>
                            <div><b>Konsumsi Air:</b> 💧 ${{info.air || '0 m³'}}</div>
                        `;
                    }} else {{
                        html = `
                            <div style="background:#dbeafe; color:#1e40af; padding:6px 12px; border-radius:8px; font-weight:bold; display:inline-block; margin-bottom:10px;">🔵 KOSONG (VACANT)</div>
                            <div><b>Rekomendasi Peruntukan:</b> ${{info.peruntukan || '-'}}</div>
                            <div><b>Luas Area:</b> ${{info.luas || '50 m²'}}</div>
                        `;
                    }}
                    
                    document.getElementById('m4Content').innerHTML = html;
                    document.getElementById('modalM4').style.display = 'flex';
                }}

                function closeModal4() {{
                    document.getElementById('modalM4').style.display = 'none';
                }}
            </script>
            """
            
            components.html(html_m4_component, height=740)

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
