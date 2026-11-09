import streamlit as st
import pandas as pd
import pdfplumber
import re
from rapidfuzz import fuzz
import io
from streamlit_pdf_viewer import pdf_viewer

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN & BRANDING INJOURNEY
# -----------------------------------------------------------------------------
LOGO_GREY = "https://injourneyairports.id/assets/injourney-logo-grey-BHunbWo1.png"
KAWUNG_ICON = "https://www.injourneyairports.id/assets/kawung-logo-side-CktPU2GK.png"

st.set_page_config(
    page_title="E - Reconciliation System",
    page_icon=KAWUNG_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.logo(
    image=KAWUNG_ICON,
    icon_image=KAWUNG_ICON,
    size="large"
)

# Custom CSS
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        overflow: auto !important;
    }
    section.main {
        overflow: visible !important;
    }
    [data-testid="stMainBlockContainer"] {
        overflow: visible !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem !important;
    }
    div[data-testid="stSidebarUserContent"] {
        padding-top: 0rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] img {
        display: none !important;
    }
    [data-testid="stSidebarHeader"] {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        background: transparent !important;
    }
    
    /* Styling Khusus Button agar Menyerupai Custom Card */
    div[data-testid="stElementContainer"]:has(.card-btn-marker) + div[data-testid="stElementContainer"] button {
        text-align: left !important;
        padding: 8px 12px !important;
        display: block !important;
    }
    div[data-testid="stElementContainer"]:has(.card-btn-marker) + div[data-testid="stElementContainer"] button p {
        white-space: pre-line !important; 
        margin: 0 !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        line-height: 1.5 !important;
    }
    
    /* Warna Status */
    div[data-testid="stElementContainer"]:has(.btn-match) + div[data-testid="stElementContainer"] button { border-left: 4px solid #22c55e !important; } /* Hijau */
    div[data-testid="stElementContainer"]:has(.btn-offload) + div[data-testid="stElementContainer"] button { border-left: 4px solid #ef4444 !important; } /* Merah */
    div[data-testid="stElementContainer"]:has(.btn-change) + div[data-testid="stElementContainer"] button { border-left: 4px solid #f97316 !important; } /* Orange */
    div[data-testid="stElementContainer"]:has(.btn-notscan) + div[data-testid="stElementContainer"] button { border-left: 4px solid #94a3b8 !important; } /* Abu-abu */
    div[data-testid="stElementContainer"]:has(.btn-infant) + div[data-testid="stElementContainer"] button { border-left: 4px solid #3b82f6 !important; } /* Biru */
    div[data-testid="stElementContainer"]:has(.btn-confirm) + div[data-testid="stElementContainer"] button { border-left: 4px solid #eab308 !important; } /* Kuning */

    .sidebar-logo-card {
        background-color: #ffffff !important;
        border-radius: 12px;
        padding: 10px 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.12);
        margin-top: -10px;
        margin-bottom: 12px;
    }
    .brand-logo-card {
        width: 155px;
        height: auto;
        display: block;
        filter: none !important;
    }

    .sidebar-mini-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 3px 10px;
        margin-top: 6px;
    }
    .sidebar-mini-icon {
        width: 14px;
        height: 14px;
    }
    .sidebar-mini-text {
        font-size: 11px;
        font-weight: 600;
        color: #334155;
        letter-spacing: 0.5px;
    }

    .main-header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(148, 163, 184, 0.3);
        margin-bottom: 16px;
    }
    .main-title {
        font-family: 'Segoe UI', -apple-system, Roboto, sans-serif;
        font-weight: 700;
        font-size: 28px;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 4px;
    }

    .custom-card {
        background: rgba(30, 41, 59, 0.03);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-left: 4px solid #0284c7;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    .custom-card-label {
        font-size: 11px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
    }
    .custom-card-value {
        font-size: 14px;
        font-weight: 700;
        color: #0284c7;
    }

    div.stButton > button {
        background: rgba(30, 41, 59, 0.03) !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        height: 100% !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        border-color: #0284c7 !important;
        background: rgba(2, 132, 199, 0.08) !important;
        transform: translateY(-2px);
    }

    div[data-testid="stVerticalBlock"] > div:has(#sticky-flight-marker) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 3.5rem !important;
        z-index: 999 !important;
        background-color: var(--background-color, inherit) !important;
        backdrop-filter: blur(12px);
        padding-top: 14px !important;
        padding-bottom: 10px !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    }

    .section-header {
        font-size: 16px;
        font-weight: 700;
        margin-top: 4px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .welcome-card {
        background: rgba(30, 41, 59, 0.03);
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        padding: 24px;
        margin-top: 20px;
    }
    .welcome-title {
        font-size: 18px;
        font-weight: 700;
        color: #0284c7;
        margin-bottom: 8px;
    }
    .welcome-text {
        font-size: 14px;
        color: #64748b;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

if "filter_status" not in st.session_state:
    st.session_state["filter_status"] = "ALL"
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

# -----------------------------------------------------------------------------
# HELPER DISPLAY PDF PREVIEW
# -----------------------------------------------------------------------------
def display_pdf_preview(uploaded_file, height=650):
    try:
        uploaded_file.seek(0)
        bytes_data = uploaded_file.read()
        uploaded_file.seek(0)
        
        with st.container(height=height):
            pdf_viewer(
                input=bytes_data,
                width="100%",
                render_text=True
            )
            
    except Exception as e:
        st.error(f"Gagal memuat preview PDF: {e}")

# -----------------------------------------------------------------------------
# POP-UP INFORMASI MASKAPAI (MODAL DIALOG)
# -----------------------------------------------------------------------------
@st.dialog("ℹ️ Maskapai Terdukung Sistem Rekonsiliasi")
def show_supported_airlines():
    st.markdown("""
    Sistem E-Reconciliation saat ini mendukung parsing manifest untuk **25 maskapai/sistem DCS** berikut:

    1. **Fly Jaya (KS)** - *Fly Jaya Manifest*
    2. **Lion Air Group (ID / IU / IW / JT / OD / SL)** - *Lion Systems Report*
    3. **Pelita Air (IP)** - *Pelita DCS Report*
    4. **Royal Brunei Airlines (BI)** - *Royal Brunei DCS*
    5. **AirAsia (AK / FD / QZ)** - *AirAsia DCS / Navitaire Report*
    6. **Citilink (QG)** - *Citilink DCS / Navitaire Report*
    7. **Cebu Pacific (5J)** - *Navitaire Flight Close Report*
    8. **IndiGo (6E)** - *Navitaire Flight Close Report*
    9. **Jetstar Airways (JQ)** - *Navitaire Flight Close Report*
    10. **Jeju Air Co. Ltd. (7C)** - *Navitaire Flight Close Report*
    11. **Scoot (TR)** - *Scoot DCS / Navitaire Report*
    12. **Air India (AI)** - *Amadeus Generic Report*
    13. **Cathay Pacific (CX)** - *Amadeus Generic Report*
    14. **Etihad Airways (EY)** - *Amadeus Generic Report*
    15. **EVA Air (BR)** - *Amadeus Generic Report*
    16. **Garuda Indonesia (GA)** - *Amadeus Generic Report*
    17. **KLM Royal Dutch Airlines (KL)** - *Amadeus Generic Report*
    18. **Malaysia Airlines (MH)** - *Amadeus Generic Report*
    19. **Philippine Airlines (PR)** - *Amadeus Generic Report*
    20. **Qantas Airways (QF)** - *Amadeus Generic Report*
    21. **Qatar Airways (QR)** - *Amadeus Generic Report*
    22. **Saudia (SV)** - *Amadeus Generic Report (With Ticket No)*
    23. **Singapore Airlines (SQ)** - *Amadeus Generic Report*
    24. **Thai Airways (TG)** - *Amadeus Generic Report*
    25. **Vietnam Airlines (VN)** - *Amadeus Generic Report*
    26. **Sriwijaya Air/Nam Air (SJ/IN)** - *Amadeus Generic Report*

    ---
    *Catatan: Sistem akan mendeteksi format maskapai secara otomatis berdasarkan isi dokumen PDF/TXT.*
    """)

# -----------------------------------------------------------------------------
# 2. HELPER NAMA, SEAT & SORTING
# -----------------------------------------------------------------------------

def clean_passenger_name(name):
    if not name or name == "-":
        return ""
    name_str = str(name).upper().strip()
    
    # Hapus tanda petik tunggal & ganda
    name_str = name_str.replace("'", "").replace('"', "")

    if "/" in name_str:
        parts = name_str.split("/")
        if len(parts) >= 2 and re.match(r"^\s*[A-Z0-9]{5,7}\b", parts[1]):
            name_str = parts[0].strip()
        else:
            lname = parts[0].strip()
            fname = parts[1].strip()
            name_str = f"{fname} {lname}"
            
    if "," in name_str:
        parts = name_str.split(",")
        if len(parts) >= 2:
            lname = parts[0].strip()
            fname = parts[1].strip()
            name_str = f"{fname} {lname}"

    name_str = re.sub(r"\bMUHAMMAD([A-Z]+)\b", r"MUHAMMAD \1", name_str)
    name_str = re.sub(r"\bMOHAMMAD([A-Z]+)\b", r"MOHAMMAD \1", name_str)
    name_str = re.sub(r"\bMUHAMAD([A-Z]+)\b", r"MUHAMAD \1", name_str)
    name_str = re.sub(r"\bMUHMR\b", "MUHAMMAD", name_str)

    # TAMBAHAN BARU: Tangani gelar yang menempel langsung tanpa spasi (Contoh: DWIHERYMR -> DWIHERY)
    name_str = re.sub(r"\b([A-Z]{3,})(MR|MRS|MS|MSTR|MISS|MAST)\b", r"\1", name_str)

    # Gelar Umum & Kehormatan/Kebangsawanan
    name_str = re.sub(r"\b(MR|MRS|MS|MSTR|MISS|MAST|MR\.|MRS\.|MS\.)\b", " ", name_str)
    name_str = re.sub(r"\b(HJ|HJJ|H|RR|RRA|R\.|R\.R\.)\b", " ", name_str)
        
    name_str = re.sub(r"[^A-Z\s]", "", name_str)
    
    words = name_str.split()
    if words:
        if words[0] == "ABDU":
            words[0] = "ABDUL"
        elif words[0] in ["MUH", "MHA"]:
            words[0] = "MUHAMMAD"
        name_str = " ".join(words)
        
    return " ".join(name_str.split())

def clean_amadeus_name(raw_name):
    if not raw_name or raw_name == "-":
        return ""
    
    name_str = str(raw_name).upper().strip()
    
    if "/" in name_str:
        parts = name_str.split("/")
        lname = parts[0].strip()
        rest = parts[1].strip() if len(parts) > 1 else ""
        
        # Hapus gelar kehormatan
        rest = re.sub(r"\b(MR|MRS|MS|MISS|MSTR|MR\.|MRS\.|MS\.)\b", " ", rest)
        # Hapus kode gender/pax di ujung, TAPI JANGAN HAPUS 'I' jika itu bagian dari nama (misal UWAN I)
        # Kita hanya hapus M, F, C di ujung string jika berdiri sendiri sebagai single character
        rest = re.sub(r"\b([MFC])\b$", " ", rest)
        
        fname = rest.strip()
        if fname:
            name_str = f"{fname} {lname}"
        else:
            name_str = lname
    else:
        name_str = re.sub(r"\b(MR|MRS|MS|MSTR|MISS|MAST|MR\.|MRS\.|MS\.)\b", " ", name_str)

    name_str = re.sub(r"\bMUHAMMAD([A-Z]+)\b", r"MUHAMMAD \1", name_str)
    name_str = re.sub(r"\bMOHAMMAD([A-Z]+)\b", r"MOHAMMAD \1", name_str)
    name_str = re.sub(r"\bMUHAMAD([A-Z]+)\b", r"MUHAMAD \1", name_str)
    name_str = re.sub(r"\bMUHMR\b", "MUHAMMAD", name_str)
    name_str = re.sub(r"\b(HJ|HJJ|H)\b", " ", name_str)
    name_str = re.sub(r"[^A-Z\s]", "", name_str)
    
    words = name_str.split()
    if words:
        if words[0] == "ABDU":
            words[0] = "ABDUL"
        elif words[0] in ["MUH", "MHA"]:
            words[0] = "MUHAMMAD"
        name_str = " ".join(words)
        
    return " ".join(name_str.split())

def determine_pax_type(type_val, is_transit=False):
    t = str(type_val).strip().upper()
    if t in ["I", "INF", "INFANT"]:
        return "Infant (Transit)" if is_transit else "Infant"
    elif t in ["C", "CHD", "CHILD"]:
        return "Child (Transit)" if is_transit else "Child"
    elif t in ["M", "F", "ADULT", "ADT"]:
        return "Adult (Transit)" if is_transit else "Adult"
    else:
        return "Adult (Transit)" if is_transit else "Adult"

def clean_seat_number(seat_raw):
    if not seat_raw or str(seat_raw).strip() in ["-", "", "NAN", "NONE", "0CGK", "0"]:
        return "-"
    seat_clean = str(seat_raw).strip().upper().replace(" ", "")
    if seat_clean in ["INF", "INFT"]:
        return "INF"
    
    if seat_clean.startswith("0") and len(seat_clean) > 3 and seat_clean[1:].isalpha():
        return "-"

    match = re.search(r"^0*([1-9]\d*[A-Z])$", seat_clean)
    if match:
        return match.group(1)
    match_any = re.search(r"([1-9]\d*[A-Z])", seat_clean)
    if match_any:
        return match_any.group(1)
    match_num = re.search(r"0*([1-9]\d*)", seat_clean)
    if match_num:
        return match_num.group(1)
    return seat_clean

def seat_sort_key(seat_str):
    if not seat_str or seat_str in ["-", "INF"]:
        return (999, "Z")
    match = re.match(r"^(\d+)([A-Z]?)$", str(seat_str).upper())
    if match:
        num = int(match.group(1))
        letter = match.group(2) if match.group(2) else "A"
        return (num, letter)
    return (998, str(seat_str))

# -----------------------------------------------------------------------------
# 3. LOADERS & PARSERS MASKAPAI
# -----------------------------------------------------------------------------

def load_single_tapping_file(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame(), "-", "-"

    filename = uploaded_file.name.lower()
    df = None
    flight_no = "-"
    route = "-"

    if filename.endswith((".xlsx", ".xls")):
        try:
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file)
        except Exception:
            df = None

    if df is None or df.empty:
        try:
            uploaded_file.seek(0)
            tables = pd.read_html(uploaded_file)
            if tables and len(tables) > 0:
                df = tables[0]
        except Exception:
            df = None

    if df is None or df.empty:
        for enc in ["utf-8", "latin1", "iso-8859-1", "cp1252", "utf-16"]:
            for sep in ["\t", ",", ";", "|"]:
                try:
                    uploaded_file.seek(0)
                    temp_df = pd.read_csv(uploaded_file, sep=sep, encoding=enc, on_bad_lines="skip")
                    if temp_df is not None and len(temp_df.columns) > 1 and len(temp_df) > 0:
                        df = temp_df
                        break
                except Exception:
                    continue
            if df is not None and not df.empty:
                break

    if df is not None and not df.empty:
        df.columns = [str(col).strip().upper() for col in df.columns]
        for col in ["FLIGHT", "FLIGHT NO", "FLIGHT_NO", "FLIGHTNO", "NO FLIGHT"]:
            if col in df.columns:
                val = str(df[col].dropna().iloc[0]).strip() if not df[col].dropna().empty else "-"
                if val != "-":
                    flight_no = val
                    break

        for col in ["ROUTE", "FLIGHT ROUTE", "RUTE", "DESTINATION", "SECTOR"]:
            if col in df.columns:
                val_r = str(df[col].dropna().iloc[0]).strip() if not df[col].dropna().empty else "-"
                if val_r != "-":
                    route = val_r
                    break

        return df, flight_no, route
    return pd.DataFrame(), "-", "-"

def load_multiple_tapping_files(uploaded_files):
    if not uploaded_files:
        return pd.DataFrame(), "Tidak ada scan"

    combined_dfs = []
    scan_summaries = []

    for idx, f in enumerate(uploaded_files):
        df, fl_no, fl_route = load_single_tapping_file(f)
        if not df.empty:
            combined_dfs.append(df)
            if fl_route != "-":
                scan_summaries.append(f"{fl_no} ({fl_route})")
            else:
                scan_summaries.append(f"{fl_no}")

    if combined_dfs:
        final_df = pd.concat(combined_dfs, ignore_index=True)
        scan_text = " | ".join(scan_summaries)
        return final_df, scan_text
    return pd.DataFrame(), "Data Scan Kosong"

def detect_and_parse_manifest(pdf_file):
    full_text = ""
    if hasattr(pdf_file, "name") and pdf_file.name.endswith(".txt"):
        full_text = pdf_file.getvalue().decode("utf-8", errors="ignore")
    else:
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception:
            pdf_file.seek(0)
            full_text = pdf_file.read().decode("utf-8", errors="ignore")

    if "GARUDA" in full_text.upper() or re.search(r"\bGA\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_generic_report_from_text(full_text, "GA"), "Garuda Indonesia (GA)"
    if "IndiGo" in full_text or re.search(r"\b6E[\.\s]*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_navitaire_from_text(full_text, "6E"), "IndiGo (6E)"
    if "Cebu Pacific" in full_text or "Cebu" in full_text or re.search(r"\b5J\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_navitaire_from_text(full_text, "5J"), "Cebu Pacific (5J)"
    if "Jetstar" in full_text or re.search(r"\bJQ\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_navitaire_from_text(full_text, "JQ"), "Jetstar Airways (JQ)"
    if "Jeju Air" in full_text or re.search(r"\b7C\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_navitaire_from_text(full_text, "7C"), "Jeju Air (7C)"
    if "CITILINK" in full_text.upper() or "BDJJOG" in full_text.upper() or re.search(r"\bQG\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_citilink_from_text(full_text), "Citilink (QG)"
    if "Sriwijaya" in full_text or re.search(r"\bSJ\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_sriwijaya_from_text(full_text), "Sriwijaya Air (SJ)"
    if "Royal Brunei" in full_text or re.search(r"\bBI\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_royal_brunei_from_text(full_text), "Royal Brunei (BI)"
    if "Scoot" in full_text or re.search(r"\bTR\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_scoot_from_text(full_text), "Scoot (TR)"
    if "AirAsia" in full_text or "AIRASIA" in full_text.upper() or re.search(r"\b(AK|QZ|FD)\s*\d{3,4}\b", full_text, re.IGNORECASE):
        return parse_manifest_airasia_from_text(full_text), "AirAsia (AK/QZ/FD)"
    if "MANIFEST LIST" in full_text or "CONFIDENTIAL" in full_text or "SEATOPTION" in full_text:
        if re.search(r"\bKS\s*\d{3,4}\b", full_text, re.IGNORECASE):
            return parse_manifest_pelita_from_text(full_text), "Fly Jaya (KS)"
        return parse_manifest_pelita_from_text(full_text), "Pelita Air (IP)"
    if "LIST OF:" in full_text or "Generic Report" in full_text or "ACCEPTANCECUSTOMER" in full_text:
        return parse_manifest_generic_report_from_text(full_text, "GA"), "Garuda Indonesia (GA)"
        
    return parse_manifest_lion_group_from_text(full_text), "Lion Group (JT/IW/ID/IU)"

def parse_manifest_lion_group_from_text(full_text):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(r"FLIGHT\s*[:\.-]?\s*([A-Z0-9]{2,3}\s*\d{3,4})", full_text, re.IGNORECASE)
    if fl_match:
        flight_no_mnf = re.sub(r"\s+", " ", fl_match.group(1).upper().strip())
        
    date_match = re.search(r"DATE\s*[:\.-]?\s*(\d{1,2}[A-Z]{3}\d{2})", full_text, re.IGNORECASE)
    if date_match:
        flight_date_mnf = date_match.group(1).strip()

    emb_match = re.search(r"PT\.OF\s*EMBARKATION\s*[:\.-]?\s*([A-Z]{3})", full_text, re.IGNORECASE)
    if emb_match:
        origin = emb_match.group(1).strip()

    dest_match = re.search(r"PT\.OF\s*DEST\s*[:\.-]?\s*([A-Z]{3})", full_text, re.IGNORECASE)
    if dest_match:
        destination = dest_match.group(1).strip()

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"

    lines = full_text.split("\n")
    for line in lines:
        line_str = line.strip()
        parts = line_str.split("/")
        if len(parts) >= 8:
            part0 = re.sub(r"^[0-9\s]+", "", parts[0]).strip()
            part1 = parts[1].strip() if len(parts) > 1 else ""

            gender_or_titles = ["M.", "F.", "M", "F", "MR", "MRS", "MS", "MISS", "MSTR"]
            titles_prefix = ["ST", "SE", "HJ", "HJJ", "H", "DR", "DARS"]

            if part1 in gender_or_titles or not part1:
                raw_full_name = part0
            elif part0 in titles_prefix:
                raw_full_name = f"{part1} {part0}".strip()
            else:
                raw_full_name = f"{part1} {part0}".strip()
            
            if "FNAME" in part1.upper() or "LNAME" in part0.upper() or "TYPE" in line_str.upper() or "TOTALS" in line_str.upper() or "Y CLASS" in line_str.upper():
                continue

            clean_name = clean_passenger_name(raw_full_name)
            
            seat = "-"
            for part in parts:
                p_str = part.strip().replace(".", "")
                if re.match(r"^[0-9]{1,2}[A-F]$", p_str):
                    seat = p_str
                    break

            tkt_no = "NO_PNR_LION"
            tkt_idx = -1
            for idx_p, part in enumerate(parts):
                part_clean = part.strip()
                if part_clean.isdigit() and len(part_clean) >= 10:
                    tkt_no = part_clean
                    tkt_idx = idx_p
                    break

            special_val = parts[-1].strip() if len(parts) > 0 else ""

            is_transit = False
            if tkt_idx != -1 and len(parts) > tkt_idx + 2:
                in_flt_raw = parts[tkt_idx + 1].strip()
                tr_org_raw = parts[tkt_idx + 2].strip()
                
                clean_in_flt = re.sub(r"[^\w]", "", in_flt_raw)
                clean_tr_org = re.sub(r"[^\w]", "", tr_org_raw)
                
                if len(clean_in_flt) > 0 or len(clean_tr_org) > 0:
                    is_transit = True

            pax_code_field = parts[2].upper() if len(parts) > 2 else ""
            line_upper = line_str.upper()
            
            is_standalone_infant = (
                pax_code_field in ["INF", "INFT"] or 
                "/INFT/" in line_upper or 
                "/INF/" in line_upper or
                seat.upper() == "INF"
            )

            is_infant_attached = ("INF" in special_val or "INFANT" in line_upper) and not is_standalone_infant

            if is_standalone_infant:
                base_type = "Infant"
                seat = "INF"
            elif "CHD" in special_val or "CHILD" in line_upper or pax_code_field == "CHD":
                base_type = "Child"
            else:
                base_type = "Adult"

            type_pax_final = determine_pax_type(base_type, is_transit)

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": raw_full_name,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": clean_seat_number(seat),
                    "pnr_manifest": tkt_no,
                    "type_manifest": type_pax_final,
                    "section": "BOARDED",
                    "is_matched": False
                })

                if is_infant_attached:
                    inf_type_final = determine_pax_type("Infant", is_transit)
                    manifest_data.append({
                        "raw_nama_manifest": f"INFANT ({raw_full_name})",
                        "clean_nama_manifest": f"INFANT OF {clean_name}",
                        "seat_manifest": "INF",
                        "pnr_manifest": tkt_no,
                        "type_manifest": inf_type_final,
                        "section": "BOARDED",
                        "is_matched": False
                    })

    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

# =============================================================================
# FIXED PARSER GARUDA INDONESIA / AMADEUS (Exact Full Name & Pax Type Fix)
# =============================================================================
def parse_manifest_generic_report_from_text(full_text, default_code="GA"):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(rf"\b({default_code}\s*\d{{3,4}})\s+(\d{{1,2}}[A-Z]{{3}})\s+([A-Z]{{3}})", full_text, re.IGNORECASE)
    if not fl_match:
        fl_match = re.search(r"\b([A-Z0-9]{2}\s*\d{3,4})\s+(\d{1,2}[A-Z]{3})", full_text, re.IGNORECASE)

    if fl_match:
        flight_no_mnf = re.sub(r"\s+", " ", fl_match.group(1).upper().strip())
        flight_date_mnf = fl_match.group(2).upper()
        if len(fl_match.groups()) >= 3 and fl_match.group(3):
            origin = fl_match.group(3).upper()

    lines = full_text.split("\n")
    for line in lines:
        line_str = line.strip()
        line_clean = re.sub(r"^[\*\s]+", "", line_str)
        
        if not line_clean or line_clean.startswith("Generic Report") or line_clean.startswith("Report content") or "FLIGHT RELATED COMMENTS" in line_clean or line_clean.startswith("LIST OF"):
            continue

        # Regex Amadeus: Menangkap nama, gelar, gender (M/F/C/I), rute, status boarding, dan nomor kursi
        pattern = r"^\d+\.\s*([A-Za-z0-9\/\+\s\.-]+?)\s+(?:(MR|MRS|MS|MISS|MSTR)\s+)?\b([AMFCI])\b\s+([A-Z]{3})\s+([A-Z]{3})\s+.*?\s+\b([BN])\b\s+([0-9]{1,3}[A-Za-z]|\d+|INF|-)?(?:\s+(\d{10,14}))?"
        match = re.search(pattern, line_clean)
        
        if not match:
            pattern_fallback = r"^\d+\.\s*([A-Za-z0-9\/\+\s\.-]+?)\s+.*?\s+\b([BN])\b\s+0*([1-9]\d*[A-Za-z]|INF|-)"
            match_fb = re.search(pattern_fallback, line_clean)
            if match_fb:
                raw_name = match_fb.group(1).strip()
                board_status = match_fb.group(2).upper()
                seat_raw = match_fb.group(3) if match_fb.group(3) else "-"
                
                clean_name = clean_amadeus_name(raw_name)
                section_val = "NO_SHOW" if board_status == "N" else "BOARDED"
                
                if len(clean_name) > 2:
                    manifest_data.append({
                        "raw_nama_manifest": raw_name,
                        "clean_nama_manifest": clean_name,
                        "seat_manifest": clean_seat_number(seat_raw),
                        "pnr_manifest": "-",
                        "type_manifest": "Adult",
                        "section": section_val,
                        "is_matched": False
                    })
            continue

        raw_name = match.group(1).strip()
        title_str = match.group(2).upper() if match.group(2) else ""
        gender_pax_code = match.group(3).upper() # M, F, C, atau I
        orig_pax = match.group(4)
        dest_pax = match.group(5)
        board_status = match.group(6).upper()    # B atau N
        seat_raw = match.group(7) if match.group(7) else "-"
        tkt_no = match.group(8) if match.group(8) else "-"

        if origin == "-":
            origin = orig_pax
        destination = dest_pax

        clean_name = clean_amadeus_name(raw_name)
        section_val = "NO_SHOW" if board_status == "N" else "BOARDED"
        
        # Penentuan Tipe Penumpang yang Lebih Aman:
        # Jika kodenya 'I' TAPI gelarnya MRS/MR/MS atau nomor kursinya berupa kursi normal (bukan 'INF'),
        # maka 'I' tersebut adalah inisial nama tengah (seperti UWAN I GASAN), bukan bayi.
        seat_cleaned_check = clean_seat_number(seat_raw)
        is_truly_infant = (gender_pax_code == "I" and seat_raw == "INF" and title_str not in ["MR", "MRS", "MS"])

        if is_truly_infant:
            pax_type = "Infant"
            seat_val = "INF"
        elif gender_pax_code == "C" or title_str in ["MSTR", "MISS"]:
            pax_type = "Child"
            seat_val = seat_cleaned_check
        else: # Adult (M, F, atau 'I' yang menyamar sebagai inisial nama dewasa)
            pax_type = "Adult"
            seat_val = seat_cleaned_check

        if len(clean_name) > 2:
            manifest_data.append({
                "raw_nama_manifest": raw_name,
                "clean_nama_manifest": clean_name,
                "seat_manifest": seat_val,
                "pnr_manifest": tkt_no,
                "type_manifest": pax_type,
                "section": section_val,
                "is_matched": False
            })

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"
    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

def parse_manifest_navitaire_from_text(full_text, default_code="JQ"):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(r"Fli[g|h|r]*t\s*[:\.-]?\s*([A-Z0-9]{2}[\.\s]*)?(\d{2,4})\s+([A-Za-z0-9]{6})?", full_text, re.IGNORECASE)
    if fl_match:
        prefix = fl_match.group(1)
        num = fl_match.group(2)
        if prefix:
            prefix_clean = re.sub(r"[\.\s]+", "", prefix).upper()
            flight_no_mnf = f"{prefix_clean} {num}"
        else:
            flight_no_mnf = f"{default_code} {num}"

        route_raw = fl_match.group(3).upper().strip() if fl_match.group(3) else ""
        if len(route_raw) == 6:
            origin = route_raw[:3]
            destination = route_raw[3:]

    date_match = re.search(r"Date\s*[:\.-]?\s*(\d{1,2}[\/\-]?[A-Za-z]{3}[\/\-]?\d{2})", full_text, re.IGNORECASE)
    if date_match:
        raw_d = date_match.group(1).upper().replace("/", "").replace("-", "")
        flight_date_mnf = raw_d[:7] if len(raw_d) >= 7 else raw_d

    lines = full_text.split("\n")
    current_section = "BOARDED"
    last_parent_pnr = f"NO_PNR_{default_code}"

    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("Weight") or "Flight Close" in line_str or line_str.startswith("Totals") or line_str.startswith("Manifested") or "Pax Checked-In" in line_str or line_str.startswith("---") or "Cnt Name" in line_str or line_str.startswith("TKT:") or line_str.startswith("=") or line_str.startswith("Zone"):
            continue

        line_upper = line_str.upper()

        # DETEKSI SEKSI BERDASARKAN ATURAN NAVITAIRE
        if "THRU NO SHOW" in line_upper:
            current_section = "THRU_NO_SHOW"
            continue
        elif "THRU CHECKED-IN" in line_upper or "THRU BOARDED" in line_upper:
            current_section = "THRU_BOARDED"
            continue
        elif "NO SHOWS" in line_upper:
            current_section = "NO_SHOW"
            continue
        elif "UNCONFIRMED" in line_upper:
            current_section = "IGNORE"  # Abaikan bagian Unconfirmed sesuai permintaan
            continue
        elif "STAND-BY" in line_upper or "CHECKED-IN/BOARDED" in line_upper or "PAX CHECKED-IN" in line_upper:
            current_section = "BOARDED"
            continue

        # Jika berada di seksi Unconfirmed, lewati baris data
        if current_section == "IGNORE":
            continue

        if "INFT:" in line_str:
            infant_raw = line_str.replace("INFT:", "").strip()
            clean_name = clean_passenger_name(infant_raw)
            if len(clean_name) > 2:
                is_transit = (current_section in ["THRU_BOARDED", "THRU_NO_SHOW"])
                pax_type = determine_pax_type("Infant", is_transit)
                manifest_data.append({
                    "raw_nama_manifest": infant_raw,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": "INF",
                    "pnr_manifest": last_parent_pnr,
                    "type_manifest": pax_type,
                    "section": current_section,
                    "is_matched": False
                })
            continue

        match_pax = re.search(
            r"^\d+\s+([A-Za-z,\s\.-]+?)\s+([A-Z0-9]{6})\s+[A-Za-z0-9]{1,3}\s+\d+\s+\d+[A-Za-z]{3}\d{2}\s+([0-9]{1,3}[A-F])",
            line_str,
            re.IGNORECASE
        )

        if not match_pax:
            match_pax = re.search(
                r"^\d+\s+([A-Za-z,\s\.-]+?)\s+([A-Z0-9]{6})\s+.*?\s*([0-9]{1,3}[A-F])(?:\s+.*)?$",
                line_str,
                re.IGNORECASE
            )

        if match_pax:
            raw_name = match_pax.group(1).strip()
            pnr_val = match_pax.group(2).strip()
            seat_raw = match_pax.group(3).strip()

            clean_name = clean_passenger_name(raw_name)
            seat_val = clean_seat_number(seat_raw)
            last_parent_pnr = pnr_val

            # Penentuan transit murni hanya jika berada di seksi THRU
            is_transit = (current_section in ["THRU_BOARDED", "THRU_NO_SHOW"])
            pax_type = determine_pax_type("Adult", is_transit)

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": raw_name,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": seat_val,
                    "pnr_manifest": pnr_val,
                    "type_manifest": pax_type,
                    "section": current_section,
                    "is_matched": False
                })

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"
    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

def parse_manifest_citilink_from_text(full_text):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(r"Flight\s*[:\.-]?\s*(?:QG\s*)?(\d{3,4})\s*([A-Z]{3})?([A-Z]{3})?", full_text, re.IGNORECASE)
    if fl_match:
        fl_num = fl_match.group(1).strip()
        flight_no_mnf = f"QG {fl_num}"
        if fl_match.group(2) and fl_match.group(3):
            origin = fl_match.group(2).upper()
            destination = fl_match.group(3).upper()

    date_match = re.search(r"Date\s*[:\.-]?\s*(\d{1,2}[A-Za-z]{3}\d{2})", full_text, re.IGNORECASE)
    if date_match:
        flight_date_mnf = date_match.group(1).upper()

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"

    lines = full_text.split("\n")
    current_section = "BOARDED"
    last_parent_name = ""
    last_parent_pnr = "NO_PNR_CITILINK"
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        line_upper = line_str.upper()

        # ATURAN SEKSI NAVITAIRE CITILINK
        if "THRU NO SHOW" in line_upper:
            current_section = "THRU_NO_SHOW"
            continue
        elif "THRU CHECKED-IN" in line_upper or "THRU BOARDED" in line_upper:
            current_section = "THRU_BOARDED"
            continue
        elif "NO SHOWS" in line_upper or "NO SHOW" in line_upper:
            current_section = "NO_SHOW"
            continue
        elif "UNCONFIRMED" in line_upper:
            current_section = "IGNORE"
            continue
        elif "STAND-BY" in line_upper or "CHECKED-IN/BOARDED:" in line_upper or "CHECKED-IN" in line_upper or "PAX CHECKED-IN" in line_upper:
            current_section = "BOARDED"
            continue

        if current_section == "IGNORE":
            continue

        if "INFT:" in line_str:
            infant_raw = line_str.replace("INFT:", "").strip()
            clean_infant = clean_passenger_name(infant_raw)
            is_transit = (current_section in ["THRU_BOARDED", "THRU_NO_SHOW"])
            pax_type = determine_pax_type("Infant", is_transit)
            
            full_infant_display = f"INFANT OF {last_parent_name} ({clean_infant})" if last_parent_name else clean_infant
            
            if len(clean_infant) > 2:
                manifest_data.append({
                    "raw_nama_manifest": infant_raw,
                    "clean_nama_manifest": full_infant_display,
                    "seat_manifest": "INF",
                    "pnr_manifest": last_parent_pnr,
                    "type_manifest": pax_type,
                    "section": current_section,
                    "is_matched": False
                })
            continue

        match_pax = re.search(
            r"^\d+\s+([A-Za-z\s,\.\/'\-]+?)\s+([A-Z0-9]{6})\s+[A-Z0-9]+\s+\d+\s+\d+[A-Za-z]{3}\d{2}\s*([0-9]{1,3}[A-Za-z]+)?",
            line_str, 
            re.IGNORECASE
        )
        
        if match_pax:
            raw_name = match_pax.group(1).strip()
            pnr_val = match_pax.group(2).strip()
            seat_raw = match_pax.group(3).strip() if match_pax.group(3) else "-"

            clean_name = clean_passenger_name(raw_name)
            seat_val = clean_seat_number(seat_raw)
            is_transit = (current_section in ["THRU_BOARDED", "THRU_NO_SHOW"])
            pax_type = determine_pax_type("Adult", is_transit)

            last_parent_name = clean_name
            last_parent_pnr = pnr_val

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": raw_name,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": seat_val,
                    "pnr_manifest": pnr_val,
                    "type_manifest": pax_type,
                    "section": current_section,
                    "is_matched": False
                })

    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

def parse_manifest_airasia_from_text(full_text):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(r"Flight\s*:\s*([A-Z0-9]{2}\s*\d{3,4})\s+([A-Z]{6})", full_text, re.IGNORECASE)
    if fl_match:
        flight_no_mnf = re.sub(r"\s+", " ", fl_match.group(1).upper().strip())
        route_raw = fl_match.group(2).upper().strip()
        if len(route_raw) == 6:
            origin = route_raw[:3]
            destination = route_raw[3:]

    date_match = re.search(r"Date\s*:\s*(\d{1,2}[A-Za-z]{3}\d{2})", full_text, re.IGNORECASE)
    if date_match:
        flight_date_mnf = date_match.group(1).upper()

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"

    lines = full_text.split("\n")
    current_section = "BOARDED"
    last_parent_pnr = "NO_PNR_AIRASIA"

    for line in lines:
        line_str = line.strip()

        if not line_str or line_str.startswith("Weight") or "Flight Close" in line_str or line_str.startswith("Totals") or line_str.startswith("---") or line_str.startswith("Cnt Name") or line_str.startswith("TKT:") or line_str.startswith("="):
            continue

        line_upper = line_str.upper()

        # ATURAN SEKSI NAVITAIRE AIRASIA
        if "THRU NO SHOW" in line_upper:
            current_section = "THRU_NO_SHOW"
            continue
        elif "THRU CHECKED-IN" in line_upper or "THRU BOARDED" in line_upper:
            current_section = "THRU_BOARDED"
            continue
        elif "NO SHOWS" in line_upper or "NO SHOW" in line_upper:
            current_section = "NO_SHOW"
            continue
        elif "UNCONFIRMED" in line_upper:
            current_section = "IGNORE"
            continue
        elif "STAND-BY" in line_upper or "CHECKED-IN/BOARDED:" in line_upper or "CHECKED-IN" in line_upper or "PAX CHECKED-IN" in line_upper:
            current_section = "BOARDED"
            continue

        if current_section == "IGNORE":
            continue

        if "INFT:" in line_str:
            infant_raw = line_str.replace("INFT:", "").strip()
            clean_name = clean_passenger_name(infant_raw)
            is_transit = (current_section in ["THRU_BOARDED", "THRU_NO_SHOW"])
            pax_type = determine_pax_type("Infant", is_transit)

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": infant_raw,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": "INF",
                    "pnr_manifest": last_parent_pnr,
                    "type_manifest": pax_type,
                    "section": current_section,
                    "is_matched": False
                })
            continue

        match_pax = re.search(
            r"^\d+\s+([A-Za-z\s,\.-]+?)\s+([A-Z0-9]{6})\s+[A-Z0-9]{1,3}\s+\d+\s+\d+[A-Za-z]{3}\d{2}\s*([0-9]{1,3}[A-F])?",
            line_str
        )

        if not match_pax:
            match_pax = re.search(
                r"^\d+\s+([A-Za-z\s,\.-]+?)\s+([A-Z0-9]{6})\s+.*?\s*([0-9]{1,3}[A-F])(?:\s+.*)?$",
                line_str
            )

        if match_pax:
            raw_name = match_pax.group(1).strip()
            pnr_val = match_pax.group(2).strip()
            seat_raw = match_pax.group(3).strip() if match_pax.group(3) else "-"

            clean_name = clean_passenger_name(raw_name)
            seat_val = clean_seat_number(seat_raw) if seat_raw != "-" else "-"
            last_parent_pnr = pnr_val

            is_transit = (current_section in ["THRU_BOARDED", "THRU_NO_SHOW"])
            pax_type = determine_pax_type("Adult", is_transit)

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": raw_name,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": seat_val,
                    "pnr_manifest": pnr_val,
                    "type_manifest": pax_type,
                    "section": current_section,
                    "is_matched": False
                })

    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

def parse_manifest_sriwijaya_from_text(full_text):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(r"Flight\s*No\.?\s*[:\.-]?\s*(SJ\s*\d{3,4})", full_text, re.IGNORECASE)
    if not fl_match:
        fl_match = re.search(r"\b(SJ\s*\d{3,4})\b", full_text, re.IGNORECASE)
    if fl_match:
        flight_no_mnf = re.sub(r"\s+", " ", fl_match.group(1).upper().strip())

    date_match = re.search(r"Date\s*[:\.-]?\s*(\d{1,2}-[A-Za-z]{3}-\d{2})", full_text, re.IGNORECASE)
    if date_match:
        flight_date_mnf = date_match.group(1).upper().replace("-", "")

    route_match = re.search(r"\b([A-Z]{3})\s*-\s*([A-Z]{3})\b", full_text)
    if route_match:
        origin = route_match.group(1).upper()
        destination = route_match.group(2).upper()

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"

    lines = full_text.split("\n")
    for line in lines:
        line_str = line.strip()

        if not line_str or "Passanger List" in line_str or "Ticket No" in line_str or "Sriwijaya Air" in line_str:
            continue

        match_pax = re.search(
            r"^\d+\s+(\d{10,14})\s+((?:Mr\.|Mrs\.|Ms\.|Miss|Mstr\.)?\s*[A-Za-z\s\.-]+?)\s+(?:SJ\d*|BEJ|BPN)?.*?\s+([A-Z0-9]{6}(?:\/[A-Z0-9]+)?)\s+([A-Z])\s+(Boarded|Open|Cancel)?\s*([0-9]{1,3}[A-F])?",
            line_str,
            re.IGNORECASE
        )

        if match_pax:
            tkt_no = match_pax.group(1).strip()
            raw_name = match_pax.group(2).strip()
            pnr_val = match_pax.group(3).strip()
            board_stat = match_pax.group(5).strip() if match_pax.group(5) else "Boarded"
            seat_raw = match_pax.group(6).strip() if match_pax.group(6) else "-"

            clean_name = clean_passenger_name(raw_name)
            seat_val = clean_seat_number(seat_raw) if seat_raw != "-" else "-"

            pax_type = "Adult"
            if "MSTR" in raw_name.upper() or "MISS" in raw_name.upper():
                pax_type = "Child"

            section_val = "BOARDED" if board_stat.lower() == "boarded" else "NO_SHOW"

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": raw_name,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": seat_val,
                    "pnr_manifest": pnr_val if "/" not in pnr_val else pnr_val.split("/")[0],
                    "type_manifest": pax_type,
                    "section": section_val,
                    "is_matched": False
                })

    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

def parse_manifest_scoot_from_text(full_text):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(r"Flight\s*:\s*([A-Z0-9]{2}\s*\d{3,4})\s+([A-Z]{6})", full_text, re.IGNORECASE)
    if fl_match:
        flight_no_mnf = re.sub(r"\s+", " ", fl_match.group(1).upper().strip())
        route_raw = fl_match.group(2).upper().strip()
        if len(route_raw) == 6:
            origin = route_raw[:3]
            destination = route_raw[3:]

    date_match = re.search(r"Date\s*:\s*(\d{1,2}[A-Za-z]{3}\d{2})", full_text, re.IGNORECASE)
    if date_match:
        flight_date_mnf = date_match.group(1).upper()

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"

    lines = full_text.split("\n")
    current_section = "BOARDED"
    last_parent_pnr = "NO_PNR_SCOOT"

    for line in lines:
        line_str = line.strip()

        if not line_str or "Displayed:" in line_str or line_str.startswith("TKT:") or "MU=move up" in line_str:
            continue

        if "Checked-in/Boarded:" in line_str and "Thru" not in line_str:
            current_section = "BOARDED"
            continue
        elif "No Shows:" in line_str and "Thru" not in line_str:
            current_section = "NO_SHOW"
            continue

        if "INFT:" in line_str:
            infant_raw = line_str.replace("INFT:", "").strip()
            clean_name = clean_passenger_name(infant_raw)
            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": infant_raw,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": "INF",
                    "pnr_manifest": last_parent_pnr,
                    "type_manifest": "Infant",
                    "section": current_section,
                    "is_matched": False
                })
            continue

        match_pax = re.search(
            r"^\d+\s+([A-Za-z\s,\.-]+?)\s+([A-Z0-9]{6})\s+[A-Z0-9]{1,2}\s+\d+\s+\d+[A-Za-z]{3}\d{2}\s*([0-9]{1,3}[A-F])?",
            line_str
        )

        if match_pax:
            raw_name = match_pax.group(1).strip()
            pnr_val = match_pax.group(2).strip()
            seat_raw = match_pax.group(3).strip() if match_pax.group(3) else "-"

            clean_name = clean_passenger_name(raw_name)
            seat_val = clean_seat_number(seat_raw) if seat_raw != "-" else "-"
            last_parent_pnr = pnr_val

            is_transit = (current_section in ["THRU_BOARDED", "THRU_NO_SHOW"])
            pax_type = determine_pax_type("Adult", is_transit)

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": raw_name,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": seat_val,
                    "pnr_manifest": pnr_val,
                    "type_manifest": pax_type,
                    "section": current_section,
                    "is_matched": False
                })

    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

def parse_manifest_royal_brunei_from_text(full_text):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    head_match = re.search(r"(\d{1,2}/[A-Za-z]{3}/\d{4})\s+([A-Z0-9]{2}\d{3,4})\s+([A-Z]{3})\s*-\s*([A-Z]{3})", full_text, re.IGNORECASE)
    if head_match:
        raw_d = head_match.group(1).upper().split("/")
        flight_date_mnf = f"{raw_d[0]}{raw_d[1]}{raw_d[2][-2:]}" if len(raw_d) == 3 else head_match.group(1)
        flight_no_mnf = re.sub(r"([A-Z]+)(\d+)", r"\1 \2", head_match.group(2).upper())
        origin = head_match.group(3).upper()
        destination = head_match.group(4).upper()

    flight_route_mnf = f"{origin}-{destination}" if origin != "-" and destination != "-" else "-"

    lines = full_text.split("\n")
    for line in lines:
        line_str = line.strip()
        if not line_str or "Check-In List" in line_str or "Total Pax" in line_str or "END LIST" in line_str or line_str.startswith("No Surname"):
            continue

        match_pax = re.search(r"^\d+\s+([A-Za-z\s]+?)\s+([M|F|C|I])\s+([0-9]{1,3}[A-Z]|INF)\s+([A-Z0-9]{6})", line_str)
        if match_pax:
            raw_name = match_pax.group(1).strip()
            gender_code = match_pax.group(2).strip()
            seat_raw = match_pax.group(3).strip()
            pnr_val = match_pax.group(4).strip()

            clean_name = clean_passenger_name(raw_name)
            pax_type = determine_pax_type(gender_code)

            if gender_code == "I" or seat_raw == "INF":
                seat_val = "INF"
                pax_type = "Infant"
            else:
                seat_val = clean_seat_number(seat_raw)

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": raw_name,
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": seat_val,
                    "pnr_manifest": pnr_val,
                    "type_manifest": pax_type,
                    "section": "BOARDED",
                    "is_matched": False
                })

    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

def parse_manifest_pelita_from_text(full_text):
    manifest_data = []
    flight_no_mnf = "-"
    flight_date_mnf = "-"
    origin = "-"
    destination = "-"

    fl_match = re.search(r"(\d{1,2}\s+[A-Za-z]{3}\s+\d{4}|\d{1,2}[A-Za-z]{3}\d{2})?\s*[\d:]*\s*([A-Z0-9]{2}\s*\d{3,4})\s+([A-Z]{3})-([A-Z]{3})", full_text, re.IGNORECASE)
    if fl_match:
        if fl_match.group(1):
            raw_d = fl_match.group(1).upper()
            d_sub = re.search(r"(\d{1,2})\s*([A-Z]{3})", raw_d)
            if d_sub:
                flight_date_mnf = f"{d_sub.group(1)}{d_sub.group(2)}"
            else:
                flight_date_mnf = raw_d
        fl_prefix = re.search(r"([A-Z]+)", fl_match.group(2), re.I).group(1).upper()
        fl_num = re.sub(r"[^0-9]", "", fl_match.group(2))
        flight_no_mnf = f"{fl_prefix} {fl_num}"
        origin = fl_match.group(3).upper()
        destination = fl_match.group(4).upper()
        flight_route_mnf = f"{origin}-{destination}"
    else:
        fl_simple = re.search(r"([A-Z0-9]{2}\s*\d{3,4})", full_text, re.IGNORECASE)
        if fl_simple:
            fl_prefix = re.search(r"([A-Z]+)", fl_simple.group(1), re.I).group(1).upper()
            fl_num = re.sub(r"[^0-9]", "", fl_simple.group(1))
            flight_no_mnf = f"{fl_prefix} {fl_num}"
        
        date_simple = re.search(r"(\d{1,2}\s+[A-Z]{3}\s+\d{4}|\d{1,2}[A-Za-z]{3}\d{2})", full_text, re.IGNORECASE)
        if date_simple:
            raw_d = date_simple.group(1).upper()
            d_sub = re.search(r"(\d{1,2})\s*([A-Z]{3})", raw_d)
            if d_sub:
                flight_date_mnf = f"{d_sub.group(1)}{d_sub.group(2)}"
            else:
                flight_date_mnf = raw_d

        route_simple = re.search(r"([A-Z]{3})-([A-Z]{3})", full_text)
        if route_simple:
            flight_route_mnf = f"{route_simple.group(1)}-{route_simple.group(2)}"
        else:
            flight_route_mnf = "-"

    lines = full_text.split("\n")
    last_parent_pnr = "NO_PNR_PELITA"
    last_parent_name = ""
    
    for line in lines:
        line_str = line.strip()
        if not line_str or line_str.startswith("CONFIDENTIAL") or line_str.startswith("MANIFEST") or line_str.startswith("TOTAL") or line_str.startswith("BAGGAGE") or line_str.startswith("WEIGHT") or line_str.startswith("QTY") or line_str.startswith("SSR") or "SEATOPTION" in line_str:
            continue
            
        if line_str.startswith("~"):
            infant_raw = line_str.replace("~", "").strip()
            infant_clean_str = re.sub(r"\s+\d+.*$", "", infant_raw).strip()
            infant_clean_str = re.split(r"[\d,]", infant_clean_str)[0].strip()
            clean_name = clean_passenger_name(infant_clean_str)
            
            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": infant_clean_str,
                    "clean_nama_manifest": clean_name if clean_name else f"INFANT OF {last_parent_name}",
                    "seat_manifest": "INF",
                    "pnr_manifest": last_parent_pnr,
                    "type_manifest": "Infant",
                    "section": "BOARDED",
                    "is_matched": False
                })
            continue

        match_pax = re.search(r"^\d+\)\s+([A-Za-z\s\.-]+?)\s+(Mr|Mrs|Ms|Miss|Mstr)\.?\s*([A-Z0-9]{6})\s+[A-Z]\s+(\d{1,3}[A-Z])", line_str, re.IGNORECASE)
        if match_pax:
            raw_name = match_pax.group(1).strip()
            title = match_pax.group(2) if match_pax.group(2) else ""
            pnr_val = match_pax.group(3).strip().upper()
            seat_val = clean_seat_number(match_pax.group(4).strip())

            last_parent_pnr = pnr_val
            clean_name = clean_passenger_name(f"{raw_name} {title}".strip())
            last_parent_name = clean_name

            pax_type = "Adult"
            if title and title.upper().replace(".", "") in ["MSTR", "MISS"]:
                pax_type = "Child"

            if len(clean_name) > 2:
                manifest_data.append({
                    "raw_nama_manifest": f"{raw_name} {title}".strip(),
                    "clean_nama_manifest": clean_name,
                    "seat_manifest": seat_val,
                    "pnr_manifest": pnr_val,
                    "type_manifest": pax_type,
                    "section": "BOARDED",
                    "is_matched": False
                })

    return pd.DataFrame(manifest_data), flight_no_mnf, flight_date_mnf, flight_route_mnf

# =============================================================================
# 4. RECONCILE ENGINE & SCORING LOGIC (CHANGE SEAT & STRICT MATCHING FIX)
# =============================================================================

def calculate_name_score(tap_nama_raw, mnf_nama, same_seat=False):
    clean_tap = clean_passenger_name(tap_nama_raw)
    clean_mnf = clean_passenger_name(mnf_nama)

    if not clean_tap or not clean_mnf:
        clean_tap = re.sub(r"[^A-Z]", "", str(tap_nama_raw).upper())
        clean_mnf = re.sub(r"[^A-Z]", "", str(mnf_nama).upper())

    words_tap = clean_tap.split()
    words_mnf = clean_mnf.split()

    # TAMBAHAN BARU: Jika nama belakang sama & nama depan saling singkatan/prefix (DWIHERY vs DWI)
    if len(words_tap) >= 1 and len(words_mnf) >= 1:
        if words_tap[-1] == words_mnf[-1]:
            w1, w2 = words_tap[0], words_mnf[0]
            if (len(w1) >= 3 and len(w2) >= 3) and (w1.startswith(w2) or w2.startswith(w1)):
                return 95  # Skor tinggi otomatis menjamin MATCH / CHANGE SEAT

    s_sort = fuzz.token_sort_ratio(clean_tap, clean_mnf)
    s_set = fuzz.token_set_ratio(clean_tap, clean_mnf)
    s_ratio = fuzz.ratio(clean_tap.replace(" ", ""), clean_mnf.replace(" ", ""))

    tap_no_space = clean_tap.replace(" ", "")
    mnf_no_space = clean_mnf.replace(" ", "")

    # 1. ATURAN BILA KURSINYA SAMA (EXACT SEAT MATCH)
    if same_seat:
        if tap_no_space == mnf_no_space or tap_no_space in mnf_no_space or mnf_no_space in tap_no_space:
            return 98

        raw_tap_ns = re.sub(r"[^A-Z]", "", str(tap_nama_raw).upper())
        raw_mnf_ns = re.sub(r"[^A-Z]", "", str(mnf_nama).upper())
        raw_no_space_ratio = fuzz.ratio(raw_tap_ns, raw_mnf_ns)
        
        if raw_no_space_ratio >= 70 or s_ratio >= 70 or s_set >= 70:
            return max(raw_no_space_ratio, s_ratio, s_set, s_sort)

        if len(words_tap) >= 1 and len(words_mnf) >= 1:
            if words_tap[0] == words_mnf[0] or words_tap[-1] == words_mnf[-1]:
                if s_sort >= 45 or s_set >= 45 or s_ratio >= 45:
                    return max(s_sort, s_set, s_ratio)

        if s_sort >= 60 or s_set >= 65:
            return max(s_sort, s_set)

        return 0

    # 2. ATURAN BILA KURSINYA BEDA (SEAT CONFLICT / CROSS-MATCHING)
    if len(words_tap) >= 3 and len(words_mnf) >= 3:
        if words_tap[-1] != words_mnf[-1] and not (words_tap[-1].startswith(words_mnf[-1]) or words_mnf[-1].startswith(words_tap[-1])):
            return min(s_sort, s_ratio)

    if len(words_tap) >= 2 and len(words_mnf) >= 2:
        if words_tap[0] == words_mnf[0] and words_tap[-1] == words_mnf[-1]:
            return max(88, s_sort, s_set)

    if tap_no_space == mnf_no_space or tap_no_space in mnf_no_space or mnf_no_space in tap_no_space:
        return 90

    words_tap_set = set(words_tap)
    words_mnf_set = set(words_mnf)

    common_words = {"MUHAMMAD", "MOHAMMAD", "MUHAMAD", "ABDUL", "SITI", "NUR", "AHMAD", "INFANT", "OF", "WAYAN", "NI"}
    significant_tap = words_tap_set - common_words
    significant_mnf = words_mnf_set - common_words

    if not significant_tap.intersection(significant_mnf):
        has_prefix = False
        for wt in significant_tap:
            for wm in significant_mnf:
                # DIPERBAIKI DI SINI: Ubah dari len(...) > 3 menjadi len(...) >= 2 
                # agar nama 3 huruf seperti DWI, TRI, EKA bisa diuji prefiksnya
                if len(wt) >= 2 and len(wm) >= 2 and (wt.startswith(wm) or wm.startswith(wt)):
                    has_prefix = True
                    break
            if has_prefix:
                break
        if not has_prefix:
            return 0

    return max(s_sort, s_set, s_ratio)

def reconcile_engine(df_tapping, df_manifest, airline_name):
    if df_tapping.empty and df_manifest.empty:
        return pd.DataFrame()

    results = []
    df_manifest["is_matched"] = False
    
    # Set untuk melacak baris tapping mana saja yang sudah sukses di-match di Tahap 1
    processed_tap_indices = set()

    is_lion_group = "LION" in airline_name.upper() or any(code in airline_name.upper() for code in ["JT", "IW", "ID", "IU", "OD", "SL"])

    # -------------------------------------------------------------------------
    # TAHAP 1: PRIORITAS UTAMA - EXACT SEAT MATCH (Seat Scan == Seat Manifest)
    # -------------------------------------------------------------------------
    for idx, tap in df_tapping.iterrows():
        tap_nama_raw = str(tap.get("NAME", tap.get("NAMA", tap.get("PASSENGER NAME", "")))).strip()
        tap_seat = clean_seat_number(str(tap.get("SEAT", tap.get("NO SEAT", ""))).strip().replace(".", ""))
        tap_pnr = str(tap.get("PNR", tap.get("NO PNR", ""))).strip()
        
        raw_type = str(tap.get("TYPE", tap.get("PAX TYPE", "Adult"))).strip()
        raw_cat = str(tap.get("CATEGORY", "")).strip()
        is_transit = "TRANSIT" in raw_cat.upper() or "TRANSIT" in raw_type.upper()
        tap_type_final = determine_pax_type(raw_type, is_transit)

        if tap_seat == "-" or tap_seat == "INF":
            continue # Lewati baris tanpa kursi / infant di tahap ini

        available_manifest = df_manifest[~df_manifest["is_matched"]]
        if available_manifest.empty:
            break

        # Cari manifest yang kursinya SAMA PERSIS dengan kursi scan
        same_seat_rows = available_manifest[available_manifest["seat_manifest"] == tap_seat]
        if not same_seat_rows.empty:
            best_score = 0
            best_m_idx = None
            for m_idx, m_row in same_seat_rows.iterrows():
                score = calculate_name_score(tap_nama_raw, m_row["clean_nama_manifest"], same_seat=True)
                if score >= 45 and score > best_score:
                    best_score = score
                    best_m_idx = m_idx

            if best_m_idx is not None:
                # Kunci manifest agar tidak bisa diambil orang lain
                df_manifest.at[best_m_idx, "is_matched"] = True
                processed_tap_indices.add(idx)
                m_row = df_manifest.loc[best_m_idx]
                
                m_section = str(m_row.get("section", "")).upper()
                if m_section in ["NO_SHOW", "THRU_NO_SHOW", "N"]:
                    status = "🔴 OFFLOAD"
                    catatan = f"Offload (Penumpang No Show / Kode N pada seat {tap_seat})"
                else:
                    status = "🟢 MATCH"
                    catatan = "Match Perfect (Seat & Name Match)"

                results.append({
                    "NAMA SCAN": tap_nama_raw,
                    "SEAT SCAN": tap_seat,
                    "PNR SCAN": tap_pnr,
                    "TYPE SCAN": tap_type_final,
                    "NAMA MANIFEST": m_row["clean_nama_manifest"],
                    "SEAT MANIFEST": m_row["seat_manifest"],
                    "PNR MANIFEST": m_row["pnr_manifest"],
                    "TYPE MANIFEST": m_row["type_manifest"],
                    "HASIL": status,
                    "CATATAN": catatan
                })

    # -------------------------------------------------------------------------
    # TAHAP 2: PROSES SISA TAPPING (Infant, Change Seat, Offload, Confirmation)
    # DIJAMIN SEMUA BARIS SCAN YANG BELUM DIPROSES AKAN MASUK KE TABEL (TIDAK HILANG)
    # -------------------------------------------------------------------------
    for idx, tap in df_tapping.iterrows():
        if idx in processed_tap_indices:
            continue # Lewati yang sudah sukses di Tahap 1

        tap_nama_raw = str(tap.get("NAME", tap.get("NAMA", tap.get("PASSENGER NAME", "")))).strip()
        tap_seat = clean_seat_number(str(tap.get("SEAT", tap.get("NO SEAT", ""))).strip().replace(".", ""))
        tap_pnr = str(tap.get("PNR", tap.get("NO PNR", ""))).strip()
        
        raw_type = str(tap.get("TYPE", tap.get("PAX TYPE", "Adult"))).strip()
        raw_cat = str(tap.get("CATEGORY", "")).strip()
        is_transit = "TRANSIT" in raw_cat.upper() or "TRANSIT" in raw_type.upper()
        tap_type_final = determine_pax_type(raw_type, is_transit)

        matched_idx = None
        status = ""
        catatan = ""
        available_manifest = df_manifest[~df_manifest["is_matched"]]

        # 1. Cek Infant
        is_tap_infant = (tap_seat == "INF" or "INFANT" in tap_type_final.upper())
        infant_manifests = available_manifest[
            (available_manifest["seat_manifest"] == "INF") | 
            (available_manifest["type_manifest"].str.contains("Infant", case=False))
        ]

        if is_tap_infant or not infant_manifests.empty:
            best_inf_score = 0
            best_inf_idx = None
            for m_idx, m_row in infant_manifests.iterrows():
                m_pnr = str(m_row.get("pnr_manifest", "")).strip()
                if tap_pnr != "-" and tap_pnr != "" and tap_pnr == m_pnr:
                    best_inf_idx = m_idx
                    break
                score = calculate_name_score(tap_nama_raw, m_row["clean_nama_manifest"])
                if score >= 50 and score > best_inf_score:
                    best_inf_score = score
                    best_inf_idx = m_idx

            if best_inf_idx is not None:
                matched_idx = best_inf_idx
                status = "👶 INFANT"
                catatan = f"Match Infant Pax (Seat Scan {tap_seat})"

        # 2. Cek Change Seat (Nama sama, beda kursi)
        if matched_idx is None and tap_seat != "INF" and not available_manifest.empty:
            best_name_score = 0
            best_name_idx = None

            for m_idx, m_row in available_manifest.iterrows():
                if m_row["seat_manifest"] == "INF":
                    continue
                score = calculate_name_score(tap_nama_raw, m_row["clean_nama_manifest"], same_seat=False)
                if score >= 85 and score > best_name_score:
                    best_name_score = score
                    best_name_idx = m_idx

            if best_name_idx is not None:
                matched_idx = best_name_idx
                mnf_seat = df_manifest.loc[matched_idx, "seat_manifest"]
                m_section = str(df_manifest.loc[matched_idx, "section"]).upper()
                
                if m_section in ["NO_SHOW", "THRU_NO_SHOW", "N"]:
                    status = "🔴 OFFLOAD"
                    catatan = f"Offload (Penumpang No Show di seat manifest {mnf_seat})"
                else:
                    status = "🟠 CHANGE SEAT"
                    catatan = f"penumpang di scan seat {tap_seat} dan di manifest seat {mnf_seat}"

        # 3. Simpan Hasil Match / Change Seat / Infant
        if matched_idx is not None:
            df_manifest.at[matched_idx, "is_matched"] = True
            match_row = df_manifest.loc[matched_idx]
            results.append({
                "NAMA SCAN": tap_nama_raw,
                "SEAT SCAN": tap_seat,
                "PNR SCAN": tap_pnr,
                "TYPE SCAN": tap_type_final,
                "NAMA MANIFEST": match_row["clean_nama_manifest"],
                "SEAT MANIFEST": match_row["seat_manifest"],
                "PNR MANIFEST": match_row["pnr_manifest"],
                "TYPE MANIFEST": match_row["type_manifest"],
                "HASIL": status,
                "CATATAN": catatan
            })
        else:
            # 4. Tangani Unmatched Scan (Offload / Confirmation / Double Tap)
            # --- CEK APAKAH INI DOUBLE TAPPING / SCAN 2X DENGAN KURSI BERBEDA ---
            prev_matches = [
                r for r in results 
                if r["NAMA SCAN"] != "-" and 
                clean_passenger_name(r["NAMA SCAN"]) == clean_passenger_name(tap_nama_raw) and
                ("MATCH" in r["HASIL"] or "INFANT" in r["HASIL"])
            ]

            if prev_matches:
                prev_seat = prev_matches[0]["SEAT SCAN"]
                prev_mnf_seat = prev_matches[0]["SEAT MANIFEST"]
                seat_ref = prev_seat if prev_seat != "-" else prev_mnf_seat
                
                # Cek khusus untuk Lion Group atau kasus scan 2x beda kursi
                if is_lion_group or tap_seat != seat_ref:
                    status = "🔴 OFFLOAD"
                    catatan = f"Pax Tapping 2x. Seat Match {seat_ref}"
                else:
                    status = "🟨 CONFIRMATION"
                    catatan = f"Double Tapping / Scan 2x (Penumpang sudah Match di Seat {seat_ref})"
            elif tap_seat == "INF" or "INFANT" in tap_type_final.upper():
                status = "👶 INFANT"
                catatan = "Infant Scan Tidak Ada di Manifest"
            else:
                if is_lion_group:
                    status = "🔴 OFFLOAD"
                    catatan = "Offload (Seat/Pax tidak ada di manifest Lion Group)"
                else:
                    status = "🟨 CONFIRMATION"
                    catatan = "Confirmation (Seat & Nama scan tidak ditemukan di manifest)"

            results.append({
                "NAMA SCAN": tap_nama_raw,
                "SEAT SCAN": tap_seat,
                "PNR SCAN": tap_pnr,
                "TYPE SCAN": tap_type_final,
                "NAMA MANIFEST": "-",
                "SEAT MANIFEST": "-",
                "PNR MANIFEST": "-",
                "TYPE MANIFEST": "-",
                "HASIL": status,
                "CATATAN": catatan
            })

    # -------------------------------------------------------------------------
    # MANIFEST YANG TIDAK DI-SCAN (NOT SCAN / GHOST PAX)
    # -------------------------------------------------------------------------
    unscanned = df_manifest[~df_manifest["is_matched"]]
    for m_idx, mnf in unscanned.iterrows():
        mnf_type = mnf.get("type_manifest", "Adult")
        mnf_seat = mnf.get("seat_manifest", "-")
        mnf_section = str(mnf.get("section", "")).upper()

        if mnf_type == "Infant" or mnf_seat == "INF":
            results.append({
                "NAMA SCAN": "-", "SEAT SCAN": "-", "PNR SCAN": "-", "TYPE SCAN": "-",
                "NAMA MANIFEST": mnf["clean_nama_manifest"], "SEAT MANIFEST": mnf["seat_manifest"],
                "PNR MANIFEST": mnf["pnr_manifest"], "TYPE MANIFEST": mnf["type_manifest"],
                "HASIL": "👶 INFANT", "CATATAN": "Pax Infant (Manifest Only)"
            })
        else:
            catatan_not_scan = "Passenger No Show Not Scan" if (mnf_section in ["NO_SHOW", "THRU_NO_SHOW"] or mnf_seat == "-") else "Passenger did not scan / Ghost Pax"
            results.append({
                "NAMA SCAN": "-", "SEAT SCAN": "-", "PNR SCAN": "-", "TYPE SCAN": "-",
                "NAMA MANIFEST": mnf["clean_nama_manifest"], "SEAT MANIFEST": mnf["seat_manifest"],
                "PNR MANIFEST": mnf["pnr_manifest"], "TYPE MANIFEST": mnf["type_manifest"],
                "HASIL": "⚪ NOT SCAN", "CATATAN": catatan_not_scan
            })

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res["effective_seat"] = df_res.apply(
            lambda r: r["SEAT SCAN"] if r["SEAT SCAN"] != "-" else r["SEAT MANIFEST"], axis=1
        )
        df_res["sort_key"] = df_res["effective_seat"].apply(seat_sort_key)
        df_res = df_res.sort_values(by="sort_key").reset_index(drop=True)
        df_res["NO"] = df_res.index + 1
        
        cols = [
            "NO", "NAMA SCAN", "SEAT SCAN", "PNR SCAN", "TYPE SCAN",
            "NAMA MANIFEST", "SEAT MANIFEST", "PNR MANIFEST", "TYPE MANIFEST",
            "HASIL", "CATATAN"
        ]
        df_res = df_res[cols]

    return df_res

# -----------------------------------------------------------------------------
# 5. SIDEBAR & UPLOAD DOKUMEN
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
        <div class="sidebar-logo-card">
            <img src="{LOGO_GREY}" class="brand-logo-card" alt="InJourney Logo">
            <div class="sidebar-mini-badge">
                <img src="{KAWUNG_ICON}" class="sidebar-mini-icon" alt="Kawung">
                <span class="sidebar-mini-text">Pax Reconciliation System</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📁 Upload Dokumen")
    allowed_types = ["txt", "csv", "xlsx", "xls"]
    
    files_tapping = st.file_uploader(
        "Upload File Gate Tapping (bisa >1 file):",
        type=allowed_types,
        accept_multiple_files=True,
        key=f"tapping_{st.session_state['uploader_key']}"
    )
        
    file_manifest = st.file_uploader(
        "Upload File Manifest (PDF/TXT):",
        type=["pdf", "txt"],
        key=f"manifest_{st.session_state['uploader_key']}"
    )
    
    st.write("")
    if st.button("🗑️ Reset / Mulai Awal", use_container_width=True):
        st.session_state["uploader_key"] += 1
        st.session_state["filter_status"] = "ALL"
        st.rerun()

    st.divider()
    col_info, col_empty = st.columns([1, 4])
    with col_info:
        if st.button("ℹ️", help="Klik untuk melihat daftar maskapai terdukung", key="btn_info_pax"):
            show_supported_airlines()

# -----------------------------------------------------------------------------
# 6. KONTEN UTAMA & TAMPILAN DASHBOARD
# -----------------------------------------------------------------------------
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("""
        <div class="main-header-container">
            <div>
                <h1 class="main-title">Passenger Reconciliation System</h1>
                <div class="sub-title">Sistem Rekonsiliasi Otomatis Data Gate Tapping vs Manifest Penumpang</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col_head2:
    st.markdown(f'''
        <div class="sidebar-logo-card" style="margin-top: 0; padding: 8px 12px;">
            <img src="{LOGO_GREY}" class="brand-logo-card" style="width: 140px;" alt="InJourney Logo">
        </div>
    ''', unsafe_allow_html=True)

if file_manifest and files_tapping:
    df_tapping, scan_summary_text = load_multiple_tapping_files(files_tapping)
    (df_manifest, flight_no_mnf, flight_date_mnf, flight_route_mnf), detected_airline = detect_and_parse_manifest(file_manifest)
    
    if df_tapping.empty:
        st.error("❌ Proses dibatalkan karena data Gate Tapping tidak berhasil terbaca atau kosong.")
    elif df_manifest.empty:
        st.error("❌ Proses dibatalkan karena data Manifest PDF/TXT tidak berhasil terbaca atau kosong.")
    else:
        df_result = reconcile_engine(df_tapping, df_manifest, detected_airline)
        manifest_card_val = f"{flight_no_mnf} ({flight_route_mnf})"
        clean_airline_display = detected_airline.split("(")[0].strip()

        # DETAIL PENERBANGAN
        with st.container():
            st.markdown('<div id="sticky-flight-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-header" style="margin-top:0;">✈️ Detail Penerbangan</div>', unsafe_allow_html=True)
            
            fc1, fc2, fc3, fc4, fc5, fc6 = st.columns([1.2, 1.2, 1.2, 1.2, 2.5, 1.8])
            with fc1:
                st.markdown(f'<div class="custom-card"><div class="custom-card-label">🏢 Airline</div><div class="custom-card-value">{clean_airline_display}</div></div>', unsafe_allow_html=True)
            with fc2:
                st.markdown(f'<div class="custom-card"><div class="custom-card-label">📄 No Flight</div><div class="custom-card-value">{flight_no_mnf}</div></div>', unsafe_allow_html=True)
            with fc3:
                st.markdown(f'<div class="custom-card" style="border-left-color: #eab308;"><div class="custom-card-label">📍 Rute</div><div class="custom-card-value">{flight_route_mnf}</div></div>', unsafe_allow_html=True)
            with fc4:
                st.markdown(f'<div class="custom-card"><div class="custom-card-label">📅 Tanggal</div><div class="custom-card-value">{flight_date_mnf}</div></div>', unsafe_allow_html=True)
            with fc5:
                st.markdown(f'<div class="custom-card" style="border-left-color: #38bdf8;"><div class="custom-card-label">📲 Data Scan</div><div class="custom-card-value">{scan_summary_text}</div></div>', unsafe_allow_html=True)
            with fc6:
                st.markdown(f'<div class="custom-card" style="border-left-color: #a855f7;"><div class="custom-card-label">📌 Manifest</div><div class="custom-card-value">{manifest_card_val}</div></div>', unsafe_allow_html=True)

        st.write("")

        # RINGKASAN REKONSILIASI
        raw_mnf_adult = len(df_manifest[df_manifest["type_manifest"].str.contains("Adult")])
        mnf_child = len(df_manifest[df_manifest["type_manifest"].str.contains("Child")])
        mnf_infant = len(df_manifest[df_manifest["type_manifest"].str.contains("Infant")])
        mnf_transit = len(df_manifest[df_manifest["type_manifest"].str.contains("Transit")])

        is_lion = "LION" in detected_airline.upper()
        if is_lion:
            mnf_adult = raw_mnf_adult
            cnt_manifest_total = mnf_adult + mnf_child + mnf_infant
        else:
            mnf_adult = raw_mnf_adult
            cnt_manifest_total = len(df_manifest)

        st.markdown('<div class="section-header">📈 Ringkasan Hasil Rekonsiliasi</div>', unsafe_allow_html=True)
        
        cnt_scan = len(df_result[df_result["NAMA SCAN"] != "-"])
        cnt_match = len(df_result[df_result["HASIL"].str.contains("MATCH")])
        cnt_offload = len(df_result[df_result["HASIL"].str.contains("OFFLOAD")])
        cnt_seat_conflict = len(df_result[df_result["HASIL"].str.contains("CHANGE SEAT")])
        cnt_not_scan = len(df_result[df_result["HASIL"].str.contains("NOT SCAN")])
        cnt_infant = len(df_result[df_result["HASIL"].str.contains("INFANT")])
        cnt_confirm = len(df_result[df_result["HASIL"].str.contains("CONFIRMATION")])

        r_col1, r_col2, r_col3, r_col4, r_col5, r_col6, r_col7, r_col8 = st.columns(8)
        with r_col1:
            st.markdown(f'<div class="custom-card" style="border-left-color: #38bdf8;"><div class="custom-card-label">📊 Pax Scan</div><div class="custom-card-value">{cnt_scan} Pax</div></div>', unsafe_allow_html=True)
        with r_col2:
            st.markdown(f'<div class="custom-card" style="border-left-color: #a855f7;"><div class="custom-card-label">📋 Pax Manifest</div><div class="custom-card-value">{cnt_manifest_total} Pax</div></div>', unsafe_allow_html=True)
        
        with r_col3:
            st.markdown('<div class="card-btn-marker btn-match" style="display:none;"></div>', unsafe_allow_html=True)
            if st.button(f"🟢 MATCH\n{cnt_match} Pax", use_container_width=True):
                st.session_state["filter_status"] = "MATCH"
                st.rerun()
                
        with r_col4:
            st.markdown('<div class="card-btn-marker btn-offload" style="display:none;"></div>', unsafe_allow_html=True)
            if st.button(f"🔴 OFFLOAD\n{cnt_offload} Pax", use_container_width=True):
                st.session_state["filter_status"] = "OFFLOAD"
                st.rerun()
                
        with r_col5:
            st.markdown('<div class="card-btn-marker btn-change" style="display:none;"></div>', unsafe_allow_html=True)
            if st.button(f"🟠 CHANGE SEAT\n{cnt_seat_conflict} Pax", use_container_width=True):
                st.session_state["filter_status"] = "CHANGE SEAT"
                st.rerun()
                
        with r_col6:
            st.markdown('<div class="card-btn-marker btn-notscan" style="display:none;"></div>', unsafe_allow_html=True)
            if st.button(f"⚪ NOT SCAN\n{cnt_not_scan} Pax", use_container_width=True):
                st.session_state["filter_status"] = "NOT SCAN"
                st.rerun()
                
        with r_col7:
            st.markdown('<div class="card-btn-marker btn-infant" style="display:none;"></div>', unsafe_allow_html=True)
            if st.button(f"👶 INFANT\n{cnt_infant} Pax", use_container_width=True):
                st.session_state["filter_status"] = "INFANT"
                st.rerun()
                
        with r_col8:
            st.markdown('<div class="card-btn-marker btn-confirm" style="display:none;"></div>', unsafe_allow_html=True)
            if st.button(f"🟨 CONFIRM\n{cnt_confirm} Pax", use_container_width=True):
                st.session_state["filter_status"] = "CONFIRMATION"
                st.rerun()

        st.write("")

        # RINGKASAN TYPE PAX
        st.markdown('<div class="section-header">👥 Ringkasan Type Pax</div>', unsafe_allow_html=True)
        
        df_scan_only = df_result[df_result["NAMA SCAN"] != "-"]
        scan_adult = len(df_scan_only[df_scan_only["TYPE SCAN"].str.contains("Adult")])
        scan_child = len(df_scan_only[df_scan_only["TYPE SCAN"].str.contains("Child")])
        scan_infant = len(df_scan_only[df_scan_only["TYPE SCAN"].str.contains("Infant")])
        scan_transit = len(df_scan_only[df_scan_only["TYPE SCAN"].str.contains("Transit")])

        pax_col1, pax_col2 = st.columns(2)
        with pax_col1:
            with st.container(border=True):
                st.markdown('<div style="font-size: 14px; font-weight: 700; color: #0284c7; margin-bottom: 8px;">📲 DATA SCAN</div>', unsafe_allow_html=True)
                ps1, ps2, ps3, ps4 = st.columns(4)
                ps1.metric("Adult Scan", f"{scan_adult}")
                ps2.metric("Child Scan", f"{scan_child}")
                ps3.metric("Infant Scan", f"{scan_infant}")
                ps4.metric("Transit Scan", f"{scan_transit}")

        with pax_col2:
            with st.container(border=True):
                st.markdown('<div style="font-size: 14px; font-weight: 700; color: #a855f7; margin-bottom: 8px;">📋 DATA MANIFEST</div>', unsafe_allow_html=True)
                pm1, pm2, pm3, pm4 = st.columns(4)
                pm1.metric("Adult Mnf", f"{mnf_adult}")
                pm2.metric("Child Mnf", f"{mnf_child}")
                pm3.metric("Infant Mnf", f"{mnf_infant}")
                pm4.metric("Transit Mnf", f"{mnf_transit}")

        st.write("")

        # HEADER TABEL & CONTROL TOGGLE PREVIEW PDF SIDE-BY-SIDE
        col_t1, col_t2, col_t3 = st.columns([2.5, 1.2, 1])
        with col_t1:
            st.markdown(f'<div class="section-header" style="margin-bottom:0;">📋 Detail Pencocokan Penumpang <span style="font-size: 13px; font-weight: normal; color: #0284c7;">(Filter Active: {st.session_state["filter_status"]})</span></div>', unsafe_allow_html=True)
        
        show_pdf_preview = False
        with col_t2:
            if file_manifest.name.lower().endswith(".pdf"):
                show_pdf_preview = st.toggle("👁️ Preview PDF (Side-by-Side)", value=False)
            else:
                st.caption("ℹ️ Preview hanya untuk file .PDF")
                
        with col_t3:
            if st.button("🔄 Reset Filter", use_container_width=True):
                st.session_state["filter_status"] = "ALL"
                st.rerun()

        st.write("")

        # Filter Data
        df_display = df_result.copy()
        if st.session_state["filter_status"] != "ALL":
            df_display = df_display[df_display["HASIL"].str.contains(st.session_state["filter_status"])]

        # TAMPILAN DINAMIS: FULL WIDTH vs SIDE-BY-SIDE
        if show_pdf_preview and file_manifest.name.lower().endswith(".pdf"):
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("##### 📊 Tabel Hasil Rekonsiliasi")
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    height=650,
                    hide_index=True,
                    column_config={
                        "HASIL": st.column_config.TextColumn(
                            "HASIL REKONSILIASI",
                            width="medium"
                        )
                    }
                )
                
            with col_right:
                st.markdown("##### 📄 Preview Dokumen Manifest PDF Asli")
                display_pdf_preview(file_manifest, height=650)
        else:
            st.dataframe(
                df_display,
                use_container_width=True,
                height=520,
                hide_index=True,
                column_config={
                    "HASIL": st.column_config.TextColumn(
                        "HASIL REKONSILIASI",
                        help="Status Hasil Pencocokan Data Gate Tapping vs Manifest",
                        width="medium"
                    )
                }
            )

        st.write("")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_result.to_excel(writer, index=False, sheet_name="Rekonsiliasi")
        
        st.download_button(
            label="📥 Download Laporan Hasil (.XLSX)",
            data=output.getvalue(),
            file_name=f"InJourney_Rekonsiliasi_{clean_airline_display.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

else:
    st.markdown("""
        <div class="welcome-card">
            <div class="welcome-title">Selamat Datang di E - Reconciliation System InJourney Airports</div>
            <div class="welcome-text">
                Silakan upload file <b>Gate Tapping</b> dan <b>Passenger Manifest</b> pada sidebar di sebelah kiri. Sistem akan langsung memproses rekonsiliasi secara otomatis.
            </div>
        </div>
    """, unsafe_allow_html=True)
