import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import io

from scraper import scrape_speedhome_listings, slugify
from build_locations import clean_slug_to_display_name

# 1. Page Configuration & Theme Initialization
st.set_page_config(
    page_title="SPEEDHOME Price Intelligence",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS styling (Clean modern adaptive theme, Rausch accents)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    :root {
        --win-text-color: #2e7d32;
        --lose-text-color: #ff385c;
        --undervalued-color: #2e7d32;
        --slightly-undervalued-color: #388e3c;
        --overpriced-color: #d32f2f;
        --slightly-overpriced-color: #f44336;
        --fairly-priced-color: #e65100;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --win-text-color: #81c784;
            --lose-text-color: #ff6b8b;
            --undervalued-color: #81c784;
            --slightly-undervalued-color: #a5d6a7;
            --overpriced-color: #e57373;
            --slightly-overpriced-color: #ef9a9a;
            --fairly-priced-color: #ffb74d;
        }
    }
    
    /* Global font styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Title styling */
    .main-title {
        background: linear-gradient(135deg, #FF3366 0%, #FF6633 50%, #FFCC33 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 3.2rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: var(--text-color) !important;
        opacity: 0.7;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* KPI Card styling - Adaptive */
    .kpi-card {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08) !important;
        border-color: rgba(255, 51, 102, 0.3) !important;
    }
    
    .kpi-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-color) !important;
        opacity: 0.7;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-color) !important;
        font-family: 'Outfit', sans-serif;
    }
    
    .kpi-subtitle {
        font-size: 0.8rem;
        color: var(--text-color) !important;
        opacity: 0.7;
        margin-top: 4px;
    }
    
    /* Tab Styling - Adaptive */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        overflow-x: auto;
        scrollbar-width: none;
        -ms-overflow-style: none;
        flex-wrap: nowrap;
    }
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        white-space: nowrap;
        background-color: var(--secondary-background-color) !important;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--text-color) !important;
        opacity: 0.8;
        flex-shrink: 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--background-color) !important;
        border-top: 3px solid #FF3366 !important;
        color: #FF3366 !important;
        opacity: 1 !important;
    }
    
    /* Mobile responsive tabs */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px;
            font-size: 0.75rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
    }
    
    /* Winner Hero Card styling - Adaptive */
    .winner-hero-card {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    /* Comparison Table styling - Adaptive */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 24px;
        background: var(--secondary-background-color) !important;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
    }
    
    .comparison-table th {
        background: rgba(128, 128, 128, 0.08) !important;
        padding: 14px 16px;
        text-align: left;
        font-weight: 600;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2) !important;
        color: var(--text-color) !important;
    }
    
    .comparison-table td {
        padding: 14px 16px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.1) !important;
        color: var(--text-color) !important;
        opacity: 0.95;
    }
    
    .winner-cell {
        background-color: rgba(46, 125, 50, 0.15) !important;
        border: 1px solid rgba(46, 125, 50, 0.3) !important;
        font-weight: 600;
    }
    
    .winner-text {
        font-weight: 600;
        color: var(--win-text-color) !important;
    }
    
    /* Visual Comparison Bar styling - Adaptive */
    .metric-bar-container {
        margin-bottom: 16px;
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
    }
    
    .bar-track {
        background: rgba(128, 128, 128, 0.15) !important;
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin-top: 4px;
        margin-bottom: 4px;
    }
    
    .bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px 0;
        color: var(--text-color) !important;
        opacity: 0.6;
        border-top: 1px solid rgba(128, 128, 128, 0.2) !important;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Autocomplete Locations Data
@st.cache_data
def load_locations():
    locations_file = "locations.json"
    if os.path.exists(locations_file):
        try:
            with open(locations_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Basic fallback list if file doesn't exist
    return [
        {"name": "Mont Kiara, Kuala Lumpur", "slug": "mont-kiara"},
        {"name": "Bangsar, Kuala Lumpur", "slug": "bangsar"},
        {"name": "Cheras, Kuala Lumpur", "slug": "cheras"},
        {"name": "Sentul, Kuala Lumpur", "slug": "sentul"},
        {"name": "Ampang, Kuala Lumpur", "slug": "ampang"},
        {"name": "Petaling Jaya, Selangor", "slug": "petaling-jaya"},
        {"name": "Subang Jaya, Selangor", "slug": "subang-jaya"},
        {"name": "Puchong, Selangor", "slug": "puchong"},
        {"name": "Cyberjaya, Selangor", "slug": "cyberjaya"},
        {"name": "Putrajaya, Wilayah Persekutuan", "slug": "putrajaya"}
    ]

locations_list = load_locations()
location_names = [loc["name"] for loc in locations_list]
location_map = {loc["name"]: loc["slug"] for loc in locations_list}

# 3. Main Title & Description
st.markdown('<div class="main-title">🏠 SPEEDHOME Price Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analisis harga sewa properti real-time dari platform SPEEDHOME Malaysia</div>', unsafe_allow_html=True)

# 3.5 Top View Toggle (Single Area vs Compare Areas)
analysis_mode = st.radio(
    "Pilih Mode Analisis:",
    ["🏠 Single Area Analysis", "📊 Compare Areas"],
    horizontal=True,
    label_visibility="collapsed"
)

scrape_btn = False

# 4. Search and Input Section for Single Area
if analysis_mode == "🏠 Single Area Analysis":
    with st.container():
        col_input, col_action = st.columns([3, 1])
        
        with col_input:
            search_method = st.radio(
                "Pilih Metode Pencarian:",
                ["Pencarian Nama Area/Apartemen (Autocomplete)", "Input URL SPEEDHOME Secara Langsung"],
                horizontal=True
            )
            
            if search_method == "Pencarian Nama Area/Apartemen (Autocomplete)":
                search_query = st.selectbox(
                    "Ketik dan Pilih Nama Area atau Apartemen (contoh: Mont Kiara):",
                    options=location_names,
                    index=0
                )
                # Map name to slug
                target_input = location_map[search_query]
            else:
                raw_input = st.text_input(
                    "Masukkan URL SPEEDHOME (contoh: https://speedhome.com/rent/mont-kiara):",
                    placeholder="https://speedhome.com/rent/mont-kiara"
                )
                target_input = raw_input.strip() if raw_input.strip() else "https://speedhome.com/rent/mont-kiara"
                
        with col_action:
            st.write("")
            st.write("")
            st.write("")
            scrape_btn = st.button("🚀 Kumpulkan Data Harga", use_container_width=True)

# Helper function to compute mode
def get_mode(series):
    series = series.dropna()
    if series.empty:
        return np.nan
    modes = series.mode()
    return modes.iloc[0] if not modes.empty else np.nan

# Helper function to compute Fair Price (estimasi harga tengah representatif)
def get_fair_price(series):
    series = series.dropna()
    if series.empty:
        return np.nan
    # Fair price formula: uses a robust combination of median (70%) and mean (30%)
    # to represent standard pricing while accounting slightly for high/low variations.
    return round((series.median() * 0.7) + (series.mean() * 0.3))

# Comparison Mode Helper Functions
def get_winner_name(val_a, val_b, lower_is_better=False):
    if val_a == val_b:
        return "Tie"
    if lower_is_better:
        return st.session_state.get("compare_name_a", "Area A") if val_a < val_b else st.session_state.get("compare_name_b", "Area B")
    else:
        return st.session_state.get("compare_name_a", "Area A") if val_a > val_b else st.session_state.get("compare_name_b", "Area B")

def compute_property_value_scores(metrics_a, metrics_b):
    # 1. Yield Score (Higher is better)
    max_yield = max(metrics_a['yield'], metrics_b['yield'])
    if max_yield > 0:
        yield_score_a = (metrics_a['yield'] / max_yield) * 100
        yield_score_b = (metrics_b['yield'] / max_yield) * 100
    else:
        yield_score_a = yield_score_b = 0
        
    # 2. Rent per Sqft Efficiency (Lower is better)
    sqft_a = metrics_a['rent_per_sqft']
    sqft_b = metrics_b['rent_per_sqft']
    if sqft_a > 0 and sqft_b > 0:
        min_sqft = min(sqft_a, sqft_b)
        sqft_score_a = (min_sqft / sqft_a) * 100
        sqft_score_b = (min_sqft / sqft_b) * 100
    else:
        sqft_score_a = sqft_score_b = 0
        
    # 3. Listing Volume (Higher is better)
    max_vol = max(metrics_a['volume'], metrics_b['volume'])
    if max_vol > 0:
        vol_score_a = (metrics_a['volume'] / max_vol) * 100
        vol_score_b = (metrics_b['volume'] / max_vol) * 100
    else:
        vol_score_a = vol_score_b = 0
        
    # 4. Average Size (Higher is better)
    max_size = max(metrics_a['size'], metrics_b['size'])
    if max_size > 0:
        size_score_a = (metrics_a['size'] / max_size) * 100
        size_score_b = (metrics_b['size'] / max_size) * 100
    else:
        size_score_a = size_score_b = 0
        
    score_a = (0.40 * yield_score_a) + (0.25 * sqft_score_a) + (0.20 * vol_score_a) + (0.15 * size_score_a)
    score_b = (0.40 * yield_score_b) + (0.25 * sqft_score_b) + (0.20 * vol_score_b) + (0.15 * size_score_b)
    
    return round(score_a), round(score_b)

def classify_competitiveness(avg_rent, fair_price):
    if fair_price == 0:
        return "N/A", "var(--text-color)"
    diff_pct = ((avg_rent - fair_price) / fair_price) * 100
    if diff_pct < -5.0:
        return "🟢 Undervalued", "var(--undervalued-color)"
    elif diff_pct < 0:
        return "🟢 Slightly Undervalued", "var(--slightly-undervalued-color)"
    elif diff_pct > 5.0:
        return "🔴 Overpriced", "var(--overpriced-color)"
    elif diff_pct > 0:
        return "🔴 Slightly Overpriced", "var(--slightly-overpriced-color)"
    else:
        return "🟡 Fairly Priced", "var(--fairly-priced-color)"

def highlight_winner(winner_name, target_area):
    if winner_name == target_area:
        return 'class="winner-cell"'
    return ''

def render_metric_bar(label, val_a, val_b, display_a, display_b, is_winner_a, is_winner_b):
    max_val = max(val_a, val_b)
    pct_a = (val_a / max_val * 100) if max_val > 0 else 0
    pct_b = (val_b / max_val * 100) if max_val > 0 else 0
    
    color_a = "var(--win-text-color)" if is_winner_a else "var(--lose-text-color)"
    color_b = "var(--win-text-color)" if is_winner_b else "var(--lose-text-color)"
    
    name_a_label = st.session_state.get("compare_name_a", "Area A")
    name_b_label = st.session_state.get("compare_name_b", "Area B")
    
    return f"""
    <div class="metric-bar-container">
        <div style="font-weight: 600; color: var(--text-color); font-size: 0.95rem; margin-bottom: 8px;">{label}</div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-color); opacity: 0.8; margin-bottom: 2px;">
                    <span>{name_a_label}</span>
                    <span style="font-weight: 600; color: {color_a};">{display_a} {"(Winner)" if is_winner_a else ""}</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill" style="width: {pct_a}%; background-color: {color_a};"></div>
                </div>
            </div>
            <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: var(--text-color); opacity: 0.8; margin-bottom: 2px;">
                    <span>{name_b_label}</span>
                    <span style="font-weight: 600; color: {color_b};">{display_b} {"(Winner)" if is_winner_b else ""}</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill" style="width: {pct_b}%; background-color: {color_b};"></div>
                </div>
            </div>
        </div>
    </div>
    """

# 5. Data Scraping & Storage in Session State for Single Area
if analysis_mode == "🏠 Single Area Analysis" and scrape_btn:
    with st.spinner("Mengumpulkan data sewa dari SPEEDHOME... Harap tunggu sebentar."):
        listings, area_name, search_url, error = scrape_speedhome_listings(target_input)
        
        if error:
            st.error(error)
        else:
            st.session_state["listings_data"] = listings
            st.session_state["area_name"] = area_name
            st.session_state["search_url"] = search_url
            st.session_state["last_scraped"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Render metrics and tables if data exists for Single Area
if analysis_mode == "🏠 Single Area Analysis" and "listings_data" in st.session_state and st.session_state["listings_data"]:
    listings = st.session_state["listings_data"]
    area_name = st.session_state["area_name"]
    search_url = st.session_state["search_url"]
    last_scraped = st.session_state["last_scraped"]
    
    df = pd.DataFrame(listings)
    
    # Clean prices & square footage
    df["price_monthly"] = pd.to_numeric(df["price_monthly"], errors="coerce")
    df["price_yearly"] = pd.to_numeric(df["price_yearly"], errors="coerce")
    df["sqft"] = pd.to_numeric(df["sqft"], errors="coerce")
    
    # 6. KPI Cards Section
    st.markdown(f"### 📊 Ringkasan Analitik Area: **{area_name}**")
    st.caption(f"Diambil dari halaman: [{search_url}]({search_url}) | Terakhir diperbarui: {last_scraped}")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Unit Ditemukan</div>
            <div class="kpi-value">{len(df)}</div>
            <div class="kpi-subtitle">Total listings aktif</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        avg_price = df["price_monthly"].mean()
        avg_str = f"RM {round(avg_price):,}" if not np.isnan(avg_price) else "N/A"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Rata-rata Harga</div>
            <div class="kpi-value">{avg_str}</div>
            <div class="kpi-subtitle">Per bulan (Bulanan)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        med_price = df["price_monthly"].median()
        med_str = f"RM {round(med_price):,}" if not np.isnan(med_price) else "N/A"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Median Harga</div>
            <div class="kpi-value">{med_str}</div>
            <div class="kpi-subtitle">Nilai tengah pasar</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        fair_price = get_fair_price(df["price_monthly"])
        fair_str = f"RM {round(fair_price):,}" if not np.isnan(fair_price) else "N/A"
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #FF3366; background: rgba(255, 51, 102, 0.03);">
            <div class="kpi-title" style="color: #FF3366;">Harga Wajar (Fair Price)</div>
            <div class="kpi-value" style="color: #FF3366;">{fair_str}</div>
            <div class="kpi-subtitle">Estimasi harga paling wajar</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col5:
        avg_size = df["sqft"].mean()
        size_str = f"{round(avg_size):,} sqft" if not np.isnan(avg_size) else "N/A"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Rata-rata Ukuran</div>
            <div class="kpi-value">{size_str}</div>
            <div class="kpi-subtitle">Luas bangunan unit</div>
        </div>
        """, unsafe_allow_html=True)
        
    # 7. Rent Type Analysis Notice (Requirements 4)
    st.info("ℹ️ **Informasi Tipe Sewa:** SPEEDHOME adalah platform sewa jangka menengah & panjang. "
            "Sewa **Harian** tidak tersedia di platform ini (minimum durasi sewa biasanya 3 bulan). "
            "Harga sewa **Bulanan** dan kontrak **Tahunan** tertera lengkap di bawah ini.")
            
    # Tabs layout for detailed views and innovations
    tab_summary, tab_listings, tab_charts, tab_roi, tab_insights = st.tabs([
        "📋 Harga",
        "🔍 Lengkap",
        "📈 Tren",
        "💰 ROI",
        "💡 Insights"
    ])
    
    # TAB 1: Price Summary Table
    with tab_summary:
        st.markdown("#### Tabel Ringkasan Harga Per Segmen Tipe Unit")
        st.caption("Statistik di bawah dikelompokkan berdasarkan tipe kamar/unit properti.")
        
        # Room Type aggregation
        summary_df = df.groupby("room_type").agg(
            unit_count=("price_monthly", "size"),
            avg_price=("price_monthly", "mean"),
            median_price=("price_monthly", "median"),
            mode_price=("price_monthly", get_mode),
            fair_price=("price_monthly", get_fair_price),
            avg_size=("sqft", "mean")
        ).reset_index()
        
        # Round numerical metrics
        summary_df["avg_price"] = summary_df["avg_price"].round(0)
        summary_df["avg_size"] = summary_df["avg_size"].round(0)
        
        # Format table for display
        display_summary = summary_df.copy()
        display_summary.columns = [
            "Tipe Unit", 
            "Jumlah Unit", 
            "Rata-rata (RM)", 
            "Median (RM)", 
            "Modus (RM)", 
            "Harga Wajar (RM)", 
            "Rata-rata Ukuran (sqft)"
        ]
        
        # Download Summary as Excel
        def convert_summary_to_excel(summary_dataframe):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_summary = summary_dataframe.copy()
                export_summary.to_excel(writer, index=False, sheet_name='Ringkasan Harga')
            return output.getvalue()
        
        summary_excel = convert_summary_to_excel(display_summary)
        safe_area_name = "_".join(word.capitalize() for word in area_name.replace(",", "").split())
        date_str = datetime.now().strftime("%Y%m%d")
        summary_filename = f"SPEEDHOME_{safe_area_name}_Ringkasan_{date_str}.xlsx"
        
        st.download_button(
            label=f"📥 Download Ringkasan: {summary_filename}",
            data=summary_excel,
            file_name=summary_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_summary"
        )
        
        st.divider()
        
        st.dataframe(
            display_summary.style.format({
                "Jumlah Unit": "{:.0f}",
                "Rata-rata (RM)": "RM {:,.0f}",
                "Median (RM)": "RM {:,.0f}",
                "Modus (RM)": "RM {:,.0f}",
                "Harga Wajar (RM)": "RM {:,.0f}",
                "Rata-rata Ukuran (sqft)": "{:,.0f} sqft"
            }),
            use_container_width=True,
            hide_index=True
        )
        
    # TAB 2: Unit Listings Table
    with tab_listings:
        st.markdown("#### Seluruh Unit yang Ditemukan di Area Ini")
        
        # Filters inside Tab 2
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            room_filter = st.multiselect(
                "Filter Tipe Unit:",
                options=df["room_type"].unique(),
                default=df["room_type"].unique()
            )
        with f_col2:
            furnish_filter = st.multiselect(
                "Filter Furnitur:",
                options=df["furniture"].unique(),
                default=df["furniture"].unique()
            )
        with f_col3:
            price_min, price_max = int(df["price_monthly"].min()), int(df["price_monthly"].max())
            price_range = st.slider(
                "Filter Rentang Harga (RM):",
                min_value=price_min,
                max_value=price_max,
                value=(price_min, price_max)
            )
            
        # Apply filters
        filtered_df = df[
            (df["room_type"].isin(room_filter)) &
            (df["furniture"].isin(furnish_filter)) &
            (df["price_monthly"] >= price_range[0]) &
            (df["price_monthly"] <= price_range[1])
        ]
        
        st.caption(f"Menampilkan {len(filtered_df)} dari {len(df)} unit terfilter.")
        
        # Display Table Columns
        display_listings = filtered_df[[
            "title", "property_name", "room_type", "price_monthly", 
            "price_yearly", "sqft", "furniture", "link"
        ]].copy()
        
        display_listings.columns = [
            "Judul Listing", "Nama Properti/Area", "Tipe Unit", 
            "Sewa Bulanan (RM)", "Sewa Tahunan (RM)", "Ukuran (sqft)", 
            "Status Furnitur", "Link SPEEDHOME"
        ]
        
        # Download Feature - placed ABOVE the table for visibility
        # Excel generator in memory
        def convert_df_to_excel(dataframe, area_name):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Page 1: Listings Data
                export_df = dataframe.copy()
                export_df.columns = [
                    "Judul Listing", "Nama Properti/Area", "Tipe Unit", 
                    "Sewa Bulanan (RM)", "Sewa Tahunan (RM)", "Ukuran (sqft)", 
                    "Status Furnitur", "Link SPEEDHOME"
                ]
                export_df.to_excel(writer, index=False, sheet_name='Listing Lengkap')
                
                # Page 2: Summary Stats
                export_summary = summary_df.copy()
                export_summary.columns = [
                    "Tipe Unit", "Jumlah Unit", "Rata-rata Harga (RM)", 
                    "Median Harga (RM)", "Modus Harga (RM)", 
                    "Harga Wajar (RM)", "Rata-rata Ukuran (sqft)"
                ]
                export_summary.to_excel(writer, index=False, sheet_name='Ringkasan Harga')
                
            return output.getvalue()
            
        excel_data = convert_df_to_excel(filtered_df[[
            "title", "property_name", "room_type", "price_monthly", 
            "price_yearly", "sqft", "furniture", "link"
        ]], area_name)
        
        # Formatted filename e.g. SPEEDHOME_Mont_Kiara_20260624.xlsx
        safe_area_name = "_".join(word.capitalize() for word in area_name.replace(",", "").split())
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"SPEEDHOME_{safe_area_name}_{date_str}.xlsx"
        
        st.download_button(
            label=f"📥 Download Data Sewa: {filename}",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
        st.divider()
        
        st.dataframe(
            display_listings,
            column_config={
                "Sewa Bulanan (RM)": st.column_config.NumberColumn(format="RM %,.0f"),
                "Sewa Tahunan (RM)": st.column_config.NumberColumn(format="RM %,.0f"),
                "Ukuran (sqft)": st.column_config.NumberColumn(format="%,.0f sqft"),
                "Link SPEEDHOME": st.column_config.LinkColumn("Buka Halaman", display_text="Verifikasi Listing 🔗")
            },
            use_container_width=True,
            hide_index=True
        )
        
    # TAB 3: Visualizations & Charts
    with tab_charts:
        st.markdown("#### Tren Visualisasi Harga Properti")
        
        v_col1, v_col2 = st.columns(2)
        
        with v_col1:
            st.markdown("**Rata-rata Harga Bulanan Berdasarkan Tipe Unit (RM)**")
            if not summary_df.empty:
                chart_data = summary_df.set_index("room_type")[["avg_price"]].rename(columns={"avg_price": "Harga Rata-rata (RM)"})
                st.bar_chart(chart_data, color="#FF3366")
            else:
                st.write("Data tidak cukup untuk menampilkan grafik.")
                
        with v_col2:
            st.markdown("**Perbandingan Ukuran Properti vs Harga Sewa (RM)**")
            scatter_data = df.dropna(subset=["sqft", "price_monthly"]).copy()
            if not scatter_data.empty:
                scatter_data = scatter_data.rename(columns={"price_monthly": "Sewa Bulanan (RM)", "sqft": "Ukuran (sqft)"})
                st.scatter_chart(
                    data=scatter_data,
                    x="Ukuran (sqft)",
                    y="Sewa Bulanan (RM)",
                    color="room_type",
                    size="bedroom"
                )
            else:
                st.write("Data tidak cukup untuk menampilkan scatter plot.")
                
    # TAB 4: ROI Investment Yield Calculator
    with tab_roi:
        st.markdown("#### Kalkulator Estimasi ROI Sewa Properti")
        st.caption("Alat ini membantu Anda memproyeksikan yield rental tahunan (ROI) properti di area ini.")
        
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            est_purchase_price = st.number_input(
                "Harga Pembelian Properti Estimasi (RM):",
                min_value=50000,
                max_value=10000000,
                value=500000,
                step=50000,
                help="Masukkan harga pembelian properti secara keseluruhan (total purchase price), bukan harga sewa bulanan. Nilai ini digunakan untuk mengukur persentase Gross Rental Yield (ROI sewa tahunan). Batas minimum adalah RM 50.000."
            )
            
            selected_type = st.selectbox(
                "Pilih Tipe Unit untuk Referensi Sewa:",
                options=df["room_type"].unique()
            )
            
            # Get typical median rent for selected type
            median_rent = df[df["room_type"] == selected_type]["price_monthly"].median()
            if np.isnan(median_rent):
                median_rent = df["price_monthly"].median()
                
            est_monthly_rent = st.number_input(
                f"Sewa Bulanan yang Ditargetkan (RM) - Median: RM {round(median_rent):,}:",
                min_value=100,
                max_value=50000,
                value=int(median_rent) if not np.isnan(median_rent) else 1500,
                step=100
            )
            
        with c_col2:
            annual_expenses = st.slider(
                "Persentase Biaya Operasional Tahunan (Pajak, Maintenance, Asuransi, dll):",
                min_value=0.0,
                max_value=30.0,
                value=10.0,
                format="%.1f%%"
            )
            
            # Calculations
            gross_annual_rent = est_monthly_rent * 12
            net_annual_rent = gross_annual_rent * (1 - (annual_expenses / 100))
            
            gross_roi = (gross_annual_rent / est_purchase_price) * 100
            net_roi = (net_annual_rent / est_purchase_price) * 100
            
            st.markdown("##### Hasil Proyeksi Yield & Return:")
            
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.metric("Gross Rental Yield (Kotor)", f"{gross_roi:.2f}%")
            with res_col2:
                st.metric("Net Rental Yield (Bersih)", f"{net_roi:.2f}%", help="Setelah dikurangi biaya operasional")
                
            st.markdown(f"""
            - **Pendapatan Kotor Tahunan**: RM {gross_annual_rent:,.0f}
            - **Pendapatan Bersih Tahunan**: RM {net_annual_rent:,.0f}
            - **Rekomendasi**: Properti di area **{area_name}** untuk unit tipe **{selected_type}** memiliki median harga sewa bulanan **RM {est_monthly_rent:,.0f}**.
            """)
            
    # TAB 5: Smart Auto-Insights
    with tab_insights:
        st.markdown("#### Intelijen Pasar & Analisis Otomatis")
        
        # 1. Furniture premium analysis
        furn_summary = df.groupby("furniture")["price_monthly"].mean()
        furn_diff = ""
        if "Fully Furnished" in furn_summary and "Unfurnished" in furn_summary:
            diff_pct = ((furn_summary["Fully Furnished"] - furn_summary["Unfurnished"]) / furn_summary["Unfurnished"]) * 100
            furn_diff = f"Unit **Fully Furnished** memiliki harga rata-rata **{diff_pct:.1f}% lebih mahal** dibanding unit **Unfurnished**."
        elif "Fully Furnished" in furn_summary and "Partially Furnished" in furn_summary:
            diff_pct = ((furn_summary["Fully Furnished"] - furn_summary["Partially Furnished"]) / furn_summary["Partially Furnished"]) * 100
            furn_diff = f"Unit **Fully Furnished** memiliki harga rata-rata **{diff_pct:.1f}% lebih mahal** dibanding unit **Partially Furnished**."
            
        # 2. Most expensive & cheapest segment
        summary_sorted = summary_df.dropna(subset=["avg_price"]).sort_values(by="avg_price")
        cheapest_segment = summary_sorted.iloc[0]["room_type"] if not summary_sorted.empty else "N/A"
        cheapest_price = summary_sorted.iloc[0]["avg_price"] if not summary_sorted.empty else 0
        expensive_segment = summary_sorted.iloc[-1]["room_type"] if not summary_sorted.empty else "N/A"
        expensive_price = summary_sorted.iloc[-1]["avg_price"] if not summary_sorted.empty else 0
        
        # 3. Density count
        most_dense_type = df["room_type"].value_counts().index[0]
        most_dense_pct = (df["room_type"].value_counts().iloc[0] / len(df)) * 100
        
        st.markdown(f"""
        ##### Temuan Utama untuk Pasar **{area_name}**:
        1. 🏢 **Tipe Dominan**: Properti didominasi oleh unit tipe **{most_dense_type}** ({most_dense_pct:.1f}% dari seluruh listing di area ini).
        2. 💰 **Segmentasi Harga**: 
           - Segmen paling terjangkau rata-rata adalah tipe **{cheapest_segment}** (rata-rata **RM {cheapest_price:,.0f}/bulan**).
           - Segmen paling premium rata-rata adalah tipe **{expensive_segment}** (rata-rata **RM {expensive_price:,.0f}/bulan**).
        3. 🛋️ **Dampak Furnitur**: {furn_diff}
        4. 📐 **Efisiensi Ruang**: Harga rata-rata per sqft adalah **RM {round(df['price_monthly'].mean() / df['sqft'].mean(), 2) if df['sqft'].mean() > 0 else 0:.2f} per sqft**.
        """)
        
        # Display FAQ dynamically from parsed listings page if available
        st.markdown("##### 📌 Informasi Penting Sewa Area:")
        st.write(f"Pasar properti di **{area_name}** cenderung menyasar segmen kelas menengah-atas dengan spesifikasi unit yang relatif modern. "
                 "Sebagian besar landlord di SPEEDHOME menawarkan sewa **Tanpa Deposit (Zero Deposit)** bagi tenant yang lolos credit check.")

elif analysis_mode == "🏠 Single Area Analysis":
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px; margin: 40px 0; background: var(--secondary-background-color); border: 1px dashed rgba(128, 128, 128, 0.3); border-radius: 16px;">
        <div style="font-size: 3rem; margin-bottom: 16px;">🏠</div>
        <div style="font-size: 1.3rem; font-weight: 700; color: var(--text-color); font-family: 'Outfit', sans-serif; margin-bottom: 8px;">Belum ada data area yang ditampilkan</div>
        <div style="font-size: 0.95rem; color: var(--text-color); opacity: 0.6; max-width: 450px; margin: 0 auto; line-height: 1.6;">
            Pilih area atau masukkan URL di atas, lalu tekan tombol <strong>🚀 Kumpulkan Data Harga</strong> untuk memulai analisis.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- COMPARE AREAS MODE ---
if analysis_mode == "📊 Compare Areas":
    # Autocomplete indexing
    try:
        index_a = location_names.index("Mont Kiara, Kuala Lumpur")
    except ValueError:
        index_a = 0
    try:
        index_b = location_names.index("Bangsar, Kuala Lumpur")
    except ValueError:
        index_b = min(1, len(location_names) - 1)
        
    st.markdown("### 📊 Bandingkan Dua Area Berdampingan")
    st.caption("Pilih dua area/apartemen dari dropdown di bawah, masukkan perkiraan harga pembelian properti untuk menghitung yield investasi secara akurat, lalu tekan tombol Bandingkan.")
    
    with st.container():
        col_input_a, col_input_b = st.columns(2)
        with col_input_a:
            st.markdown("#### 📍 Area A")
            search_method_a = st.radio(
                "Pilih Metode Area A:",
                ["Autocomplete", "Input URL"],
                horizontal=True,
                key="compare_search_method_a"
            )
            if search_method_a == "Autocomplete":
                area_a_select = st.selectbox(
                    "Pilih Area A:",
                    options=location_names,
                    index=index_a,
                    key="compare_area_a_sel"
                )
                slug_a_input = location_map[area_a_select]
            else:
                raw_input_a = st.text_input(
                    "Masukkan URL SPEEDHOME Area A:",
                    placeholder="https://speedhome.com/rent/mont-kiara",
                    key="compare_area_a_url"
                )
                slug_a_input = raw_input_a.strip() if raw_input_a.strip() else "https://speedhome.com/rent/mont-kiara"
                
            purchase_price_a = st.number_input(
                "Harga Pembelian Properti Area A (RM):",
                min_value=50000,
                max_value=10000000,
                value=600000,
                step=50000,
                key="compare_price_a",
                help="Masukkan harga pembelian properti secara keseluruhan (total purchase price), bukan harga sewa bulanan. Nilai ini digunakan untuk mengukur persentase Gross Rental Yield (ROI sewa tahunan). Batas minimum adalah RM 50.000 karena harga pasar apartemen/kondominium di Malaysia dimulai dari rentang tersebut."
            )
        with col_input_b:
            st.markdown("#### 📍 Area B")
            search_method_b = st.radio(
                "Pilih Metode Area B:",
                ["Autocomplete", "Input URL"],
                horizontal=True,
                key="compare_search_method_b"
            )
            if search_method_b == "Autocomplete":
                area_b_select = st.selectbox(
                    "Pilih Area B:",
                    options=location_names,
                    index=index_b,
                    key="compare_area_b_sel"
                )
                slug_b_input = location_map[area_b_select]
            else:
                raw_input_b = st.text_input(
                    "Masukkan URL SPEEDHOME Area B:",
                    placeholder="https://speedhome.com/rent/bangsar",
                    key="compare_area_b_url"
                )
                slug_b_input = raw_input_b.strip() if raw_input_b.strip() else "https://speedhome.com/rent/bangsar"
                
            purchase_price_b = st.number_input(
                "Harga Pembelian Properti Area B (RM):",
                min_value=50000,
                max_value=10000000,
                value=800000,
                step=50000,
                key="compare_price_b",
                help="Masukkan harga pembelian properti secara keseluruhan (total purchase price), bukan harga sewa bulanan. Nilai ini digunakan untuk mengukur persentase Gross Rental Yield (ROI sewa tahunan). Batas minimum adalah RM 50.000 karena harga pasar apartemen/kondominium di Malaysia dimulai dari rentang tersebut."
            )
            
        compare_btn = st.button("📊 Bandingkan Area", use_container_width=True)
        
    # Only trigger scraping when the user clicks the compare button
    if compare_btn:
        slug_a = slug_a_input
        slug_b = slug_b_input
        
        with st.spinner("Sedang mengambil dan menganalisis data untuk kedua area... Harap tunggu sebentar."):
            listings_a, name_a_scraped, url_a, err_a = scrape_speedhome_listings(slug_a)
            listings_b, name_b_scraped, url_b, err_b = scrape_speedhome_listings(slug_b)
            
            if err_a:
                st.error(f"Error scraping Area A ({slug_a}): {err_a}")
            elif err_b:
                st.error(f"Error scraping Area B ({slug_b}): {err_b}")
            else:
                st.session_state["compare_listings_a"] = listings_a
                st.session_state["compare_listings_b"] = listings_b
                st.session_state["compare_name_a"] = name_a_scraped
                st.session_state["compare_name_b"] = name_b_scraped
                st.session_state["compare_url_a"] = url_a
                st.session_state["compare_url_b"] = url_b
                st.session_state["compare_scraped_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state["compare_results_ready"] = True
                
    if "compare_results_ready" in st.session_state and "compare_listings_a" in st.session_state:
        listings_a = st.session_state["compare_listings_a"]
        listings_b = st.session_state["compare_listings_b"]
        name_a = st.session_state["compare_name_a"]
        name_b = st.session_state["compare_name_b"]
        url_a = st.session_state["compare_url_a"]
        url_b = st.session_state["compare_url_b"]
        scraped_at = st.session_state["compare_scraped_at"]
        
        df_a = pd.DataFrame(listings_a)
        df_b = pd.DataFrame(listings_b)
        
        for d in [df_a, df_b]:
            if not d.empty:
                d["price_monthly"] = pd.to_numeric(d["price_monthly"], errors="coerce")
                d["price_yearly"] = pd.to_numeric(d["price_yearly"], errors="coerce")
                d["sqft"] = pd.to_numeric(d["sqft"], errors="coerce")
                
        if df_a.empty or df_b.empty:
            st.warning("⚠️ Salah satu area tidak memiliki listing aktif di SPEEDHOME untuk dianalisis.")
        else:
            # Metrics A
            vol_a = len(df_a)
            avg_rent_a = df_a["price_monthly"].mean()
            avg_rent_a = 0 if np.isnan(avg_rent_a) else round(avg_rent_a)
            med_rent_a = df_a["price_monthly"].median()
            med_rent_a = 0 if np.isnan(med_rent_a) else round(med_rent_a)
            fair_price_a = get_fair_price(df_a["price_monthly"])
            fair_price_a = 0 if np.isnan(fair_price_a) else round(fair_price_a)
            avg_size_a = df_a["sqft"].mean()
            avg_size_a = 0 if np.isnan(avg_size_a) else round(avg_size_a)
            rent_per_sqft_a = avg_rent_a / avg_size_a if avg_size_a > 0 else 0
            yield_a = (avg_rent_a * 12 / purchase_price_a) * 100 if purchase_price_a > 0 else 0
            
            # Metrics B
            vol_b = len(df_b)
            avg_rent_b = df_b["price_monthly"].mean()
            avg_rent_b = 0 if np.isnan(avg_rent_b) else round(avg_rent_b)
            med_rent_b = df_b["price_monthly"].median()
            med_rent_b = 0 if np.isnan(med_rent_b) else round(med_rent_b)
            fair_price_b = get_fair_price(df_b["price_monthly"])
            fair_price_b = 0 if np.isnan(fair_price_b) else round(fair_price_b)
            avg_size_b = df_b["sqft"].mean()
            avg_size_b = 0 if np.isnan(avg_size_b) else round(avg_size_b)
            rent_per_sqft_b = avg_rent_b / avg_size_b if avg_size_b > 0 else 0
            yield_b = (avg_rent_b * 12 / purchase_price_b) * 100 if purchase_price_b > 0 else 0
            
            # Winner determination
            winner_vol = get_winner_name(vol_a, vol_b)
            winner_avg_rent = get_winner_name(avg_rent_a, avg_rent_b, lower_is_better=True)
            winner_med_rent = get_winner_name(med_rent_a, med_rent_b, lower_is_better=True)
            winner_fair_price = get_winner_name(fair_price_a, fair_price_b, lower_is_better=True)
            winner_avg_size = get_winner_name(avg_size_a, avg_size_b)
            winner_rent_per_sqft = get_winner_name(rent_per_sqft_a, rent_per_sqft_b, lower_is_better=True)
            winner_yield = get_winner_name(yield_a, yield_b)
            
            # Property Value Scores (Relative normalized scoring)
            metrics_a = {
                'yield': yield_a,
                'rent_per_sqft': rent_per_sqft_a,
                'volume': vol_a,
                'size': avg_size_a
            }
            metrics_b = {
                'yield': yield_b,
                'rent_per_sqft': rent_per_sqft_b,
                'volume': vol_b,
                'size': avg_size_b
            }
            score_a, score_b = compute_property_value_scores(metrics_a, metrics_b)
            
            # Overall Winner determination
            if score_a > score_b:
                overall_winner = name_a
                overall_loser = name_b
            elif score_b > score_a:
                overall_winner = name_b
                overall_loser = name_a
            else:
                overall_winner = "Tie"
                overall_loser = ""
                
            # Dynamic advantages list
            reasons = []
            if overall_winner != "Tie":
                win_rent = avg_rent_a if overall_winner == name_a else avg_rent_b
                lose_rent = avg_rent_b if overall_winner == name_a else avg_rent_a
                win_sqft_price = rent_per_sqft_a if overall_winner == name_a else rent_per_sqft_b
                lose_sqft_price = rent_per_sqft_b if overall_winner == name_a else rent_per_sqft_a
                if win_rent < lose_rent or win_sqft_price < lose_sqft_price:
                    reasons.append("Harga lebih kompetitif")
                win_yield = yield_a if overall_winner == name_a else yield_b
                lose_yield = yield_b if overall_winner == name_a else yield_a
                if win_yield > lose_yield:
                    reasons.append("Yield lebih tinggi")
                win_size = avg_size_a if overall_winner == name_a else avg_size_b
                lose_size = avg_size_b if overall_winner == name_a else avg_size_a
                if win_size > lose_size:
                    reasons.append("Ukuran unit lebih besar")
                win_vol = vol_a if overall_winner == name_a else vol_b
                lose_vol = vol_b if overall_winner == name_a else vol_a
                if win_vol > lose_vol:
                    reasons.append("Lebih banyak pilihan listing")
                reasons.append("Value score tertinggi")
            else:
                reasons.append("Kedua area seimbang dalam metrik utama")
                
            # 1. Overall Winner Card Rendering
            reasons_html = "".join([f'<div style="margin-bottom: 4px;">✓ {r}</div>' for r in reasons])
            winner_card_html = f"""
            <div class="winner-hero-card" style="border-left: 6px solid #4caf50; background: rgba(46, 125, 50, 0.1); padding: 24px; border-radius: 16px; margin-bottom: 24px; border: 1px solid rgba(128, 128, 128, 0.2); border-left: 6px solid #4caf50;">
                <div style="font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; color: var(--text-color); opacity: 0.8; font-weight: 600;">🏆 Better Value Area / Overall Winner</div>
                <div style="font-size: 2.8rem; font-weight: 800; color: var(--text-color); margin-top: 8px; margin-bottom: 16px; font-family: 'Outfit', sans-serif;">{overall_winner}</div>
                <div style="display: flex; flex-wrap: wrap; gap: 24px;">
                    <div style="flex: 1; min-width: 250px;">
                        <div style="font-weight: 600; color: #4caf50; margin-bottom: 8px;">Analisis Keunggulan:</div>
                        <div style="color: var(--text-color); font-size: 0.95rem; line-height: 1.6;">
                            {reasons_html}
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 200px; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; border-left: 1px solid rgba(128, 128, 128, 0.2); padding-left: 24px;">
                        <div style="font-weight: 600; color: var(--text-color); opacity: 0.8; margin-bottom: 8px;">Final Score:</div>
                        <div style="font-size: 1.1rem; line-height: 1.8; color: var(--text-color); font-family: 'Plus Jakarta Sans', sans-serif;">
                            <strong>{name_a}</strong>: {score_a}/100<br>
                            <strong>{name_b}</strong>: {score_b}/100
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(winner_card_html, unsafe_allow_html=True)
            
            # 2. Comparison Scorecard Rendering
            st.markdown("### 📊 Tabel Perbandingan Metrik (Comparison Scorecard)")
            table_html = f"""
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>{name_a}</th>
                        <th>{name_b}</th>
                        <th>Winner</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 600;">Total Listings</td>
                        <td {highlight_winner(winner_vol, name_a)}>{vol_a}</td>
                        <td {highlight_winner(winner_vol, name_b)}>{vol_b}</td>
                        <td class="winner-text">{winner_vol}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">Average Rent (RM)</td>
                        <td {highlight_winner(winner_avg_rent, name_a)}>RM {avg_rent_a:,}</td>
                        <td {highlight_winner(winner_avg_rent, name_b)}>RM {avg_rent_b:,}</td>
                        <td class="winner-text">{winner_avg_rent}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">Median Rent (RM)</td>
                        <td {highlight_winner(winner_med_rent, name_a)}>RM {med_rent_a:,}</td>
                        <td {highlight_winner(winner_med_rent, name_b)}>RM {med_rent_b:,}</td>
                        <td class="winner-text">{winner_med_rent}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">Fair Price (RM)</td>
                        <td {highlight_winner(winner_fair_price, name_a)}>RM {fair_price_a:,}</td>
                        <td {highlight_winner(winner_fair_price, name_b)}>RM {fair_price_b:,}</td>
                        <td class="winner-text">{winner_fair_price}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">Average Size</td>
                        <td {highlight_winner(winner_avg_size, name_a)}>{avg_size_a:,} sqft</td>
                        <td {highlight_winner(winner_avg_size, name_b)}>{avg_size_b:,} sqft</td>
                        <td class="winner-text">{winner_avg_size}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">Rent per Sqft (RM)</td>
                        <td {highlight_winner(winner_rent_per_sqft, name_a)}>RM {rent_per_sqft_a:.2f}</td>
                        <td {highlight_winner(winner_rent_per_sqft, name_b)}>RM {rent_per_sqft_b:.2f}</td>
                        <td class="winner-text">{winner_rent_per_sqft}</td>
                    </tr>
                    <tr>
                        <td style="font-weight: 600;">Gross Rental Yield</td>
                        <td {highlight_winner(winner_yield, name_a)}>{yield_a:.2f}%</td>
                        <td {highlight_winner(winner_yield, name_b)}>{yield_b:.2f}%</td>
                        <td class="winner-text">{winner_yield}</td>
                    </tr>
                </tbody>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            
            # 3. Price Competitiveness Analysis Side-by-Side Rendering
            class_a, color_a = classify_competitiveness(avg_rent_a, fair_price_a)
            class_b, color_b = classify_competitiveness(avg_rent_b, fair_price_b)
            competitiveness_html = f"""
            <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px;">
                <div style="flex: 1; min-width: 250px; background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                    <div style="font-size: 0.85rem; text-transform: uppercase; color: var(--text-color); opacity: 0.7; font-weight: 600; letter-spacing: 0.5px;">Price Competitiveness: {name_a}</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: {color_a}; margin-top: 10px; margin-bottom: 12px; font-family: 'Outfit', sans-serif;">{class_a}</div>
                    <div style="font-size: 0.9rem; color: var(--text-color); opacity: 0.85; line-height: 1.5;">
                        Fair Price: <strong>RM {fair_price_a:,}</strong><br>
                        Current Average: <strong>RM {avg_rent_a:,}</strong>
                    </div>
                </div>
                <div style="flex: 1; min-width: 250px; background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                    <div style="font-size: 0.85rem; text-transform: uppercase; color: var(--text-color); opacity: 0.7; font-weight: 600; letter-spacing: 0.5px;">Price Competitiveness: {name_b}</div>
                    <div style="font-size: 1.6rem; font-weight: 700; color: {color_b}; margin-top: 10px; margin-bottom: 12px; font-family: 'Outfit', sans-serif;">{class_b}</div>
                    <div style="font-size: 0.9rem; color: var(--text-color); opacity: 0.85; line-height: 1.5;">
                        Fair Price: <strong>RM {fair_price_b:,}</strong><br>
                        Current Average: <strong>RM {avg_rent_b:,}</strong>
                    </div>
                </div>
            </div>
            """
            st.markdown(competitiveness_html, unsafe_allow_html=True)
            
            # 4. Investor & Tenant Perspectives Cards Side-by-Side Rendering
            if yield_a > yield_b:
                yield_text = f"yield lebih tinggi ({yield_a:.2f}% vs {yield_b:.2f}%)"
                yield_winner = name_a
            else:
                yield_text = f"yield lebih tinggi ({yield_b:.2f}% vs {yield_a:.2f}%)"
                yield_winner = name_b

            if purchase_price_a < purchase_price_b:
                entry_text = f"harga masuk yang lebih rendah (RM {purchase_price_a:,} vs RM {purchase_price_b:,})"
                entry_winner = name_a
            else:
                entry_text = f"harga masuk yang lebih rendah (RM {purchase_price_b:,} vs RM {purchase_price_a:,})"
                entry_winner = name_b

            roi_winner = name_a if score_a > score_b else name_b
            investor_desc = f"Area <strong>{yield_winner}</strong> menawarkan {yield_text} dan area <strong>{entry_winner}</strong> memiliki {entry_text}. Secara keseluruhan, <strong>{roi_winner}</strong> menawarkan estimasi ROI dan profil nilai investasi yang lebih menarik bagi investor yang mencari cashflow optimal."

            cheaper_area = name_a if avg_rent_a < avg_rent_b else name_b
            expensive_area = name_b if avg_rent_a < avg_rent_b else name_a

            rent_diff_pct = round(abs(avg_rent_a - avg_rent_b) / max(avg_rent_a, avg_rent_b) * 100) if max(avg_rent_a, avg_rent_b) > 0 else 0
            size_diff_pct = round(abs(avg_size_a - avg_size_b) / min(avg_size_a, avg_size_b) * 100) if min(avg_size_a, avg_size_b) > 0 else 0

            if avg_size_a > avg_size_b:
                larger_area = name_a
            else:
                larger_area = name_b

            tenant_desc = f"Berdasarkan harga rata-rata dan ukuran unit, area <strong>{cheaper_area}</strong> menawarkan harga sewa sekitar {rent_diff_pct}% lebih rendah. Selain itu, unit di area <strong>{larger_area}</strong> rata-rata memiliki ruang sekitar {size_diff_pct}% lebih besar dibanding area <strong>{expensive_area}</strong>, memberikan nilai (value per sqft) yang lebih baik bagi penyewa."
            
            investor_tenant_html = f"""
            <div style="display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px;">
                <div style="flex: 1; min-width: 250px; background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                    <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-color); margin-bottom: 12px; font-family: 'Outfit', sans-serif; display: flex; align-items: center; gap: 8px;">
                        <span>💰</span> Investor Perspective
                    </div>
                    <div style="font-size: 0.95rem; color: var(--text-color); opacity: 0.85; line-height: 1.6; font-family: 'Plus Jakarta Sans', sans-serif;">
                        {investor_desc}
                    </div>
                </div>
                <div style="flex: 1; min-width: 250px; background: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.02);">
                    <div style="font-size: 1.1rem; font-weight: 700; color: var(--text-color); margin-bottom: 12px; font-family: 'Outfit', sans-serif; display: flex; align-items: center; gap: 8px;">
                        <span>🏠</span> Tenant Perspective
                    </div>
                    <div style="font-size: 0.95rem; color: var(--text-color); opacity: 0.85; line-height: 1.6; font-family: 'Plus Jakarta Sans', sans-serif;">
                        {tenant_desc}
                    </div>
                </div>
            </div>
            """
            st.markdown(investor_tenant_html, unsafe_allow_html=True)
            
            # 6. Visual Comparison Charts Rendering (using custom columns & widgets)
            st.markdown("### 📈 Grafik Perbandingan Visual (Visual Comparison)")
            
            bar_avg_rent = render_metric_bar(
                "Average Rent (Sewa Rata-rata) - Lebih Rendah Lebih Baik",
                avg_rent_a, avg_rent_b,
                f"RM {avg_rent_a:,}", f"RM {avg_rent_b:,}",
                winner_avg_rent == name_a, winner_avg_rent == name_b
            )

            bar_med_rent = render_metric_bar(
                "Median Rent (Nilai Tengah Sewa) - Lebih Rendah Lebih Baik",
                med_rent_a, med_rent_b,
                f"RM {med_rent_a:,}", f"RM {med_rent_b:,}",
                winner_med_rent == name_a, winner_med_rent == name_b
            )

            bar_yield = render_metric_bar(
                "Gross Rental Yield (Imbal Hasil) - Lebih Tinggi Lebih Baik",
                yield_a, yield_b,
                f"{yield_a:.2f}%", f"{yield_b:.2f}%",
                winner_yield == name_a, winner_yield == name_b
            )

            bar_size = render_metric_bar(
                "Average Size (Luas Unit Rata-rata) - Lebih Besar Lebih Baik",
                avg_size_a, avg_size_b,
                f"{avg_size_a:,} sqft", f"{avg_size_b:,} sqft",
                winner_avg_size == name_a, winner_avg_size == name_b
            )

            bar_rent_per_sqft = render_metric_bar(
                "Rent per Sqft (Biaya per Luas) - Lebih Rendah Lebih Baik",
                rent_per_sqft_a, rent_per_sqft_b,
                f"RM {rent_per_sqft_a:.2f}", f"RM {rent_per_sqft_b:.2f}",
                winner_rent_per_sqft == name_a, winner_rent_per_sqft == name_b
            )
            
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.markdown(bar_avg_rent, unsafe_allow_html=True)
                st.markdown(bar_med_rent, unsafe_allow_html=True)
                st.markdown(bar_rent_per_sqft, unsafe_allow_html=True)
            with chart_col2:
                st.markdown(bar_yield, unsafe_allow_html=True)
                st.markdown(bar_size, unsafe_allow_html=True)

    else:
        # Empty state - no comparison done yet
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; margin: 40px 0; background: var(--secondary-background-color); border: 1px dashed rgba(128, 128, 128, 0.3); border-radius: 16px;">
            <div style="font-size: 3rem; margin-bottom: 16px;">📊</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: var(--text-color); font-family: 'Outfit', sans-serif; margin-bottom: 8px;">Belum ada area yang dibandingkan</div>
            <div style="font-size: 0.95rem; color: var(--text-color); opacity: 0.6; max-width: 450px; margin: 0 auto; line-height: 1.6;">
                Pilih dua area dari dropdown di atas, lalu tekan tombol <strong>📊 Bandingkan Area</strong> untuk melihat hasil analisis perbandingan secara lengkap.
            </div>
        </div>
        """, unsafe_allow_html=True)

# 8. Page Footer
st.markdown("""
<div class="footer">
    SPEEDHOME Price Intelligence App • Dibuat untuk Technical Test CEO Office Jendela360 • 2026
</div>
""", unsafe_allow_html=True)
