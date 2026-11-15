"""Visual-only login page. No authentication or data storage changes."""
import streamlit as st
import base64
from pathlib import Path
from i18n import t
from html import escape


def render_login_visual():
    logo_path = Path(__file__).parent / "assets" / "space_on_earth_logo.png"
    logo_data = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    st.markdown(f"""
    <style>
    /* This stylesheet is injected only while the user is logged out. */
    .stApp {{background: radial-gradient(ellipse at 82% 8%, #173e40 0%, transparent 38%),
           radial-gradient(ellipse at 4% 100%, #102a43 0%, transparent 38%), #080f1b;}}
    [data-testid="stMainBlockContainer"] {{max-width: 1040px !important; padding-top: 5.5rem !important;}}
    .soe-hero {{position:relative; overflow:hidden; border-radius:24px; padding:30px 36px 28px;
       border:1px solid #2b6963; padding-right:245px; background:linear-gradient(115deg,#102e36 0%,#10263d 62%,#141d34 100%);
       box-shadow:0 16px 50px #0006; margin-bottom:26px;}}
    .soe-hero:before,.soe-hero:after {{content:none !important;display:none !important;}}
    .soe-brand {{font-size:13px; letter-spacing:2px; text-transform:uppercase; font-weight:800;
       color:#75e3ca; margin-bottom:13px;}}
    .soe-title {{font-size:clamp(31px,4vw,52px);font-weight:850;line-height:1.1;
       color:#f8fafc; margin:0 0 13px;}}
    .soe-title em{{font-style:normal;color:#65e3b2;}}
    .soe-sub {{color:#c2d4df;max-width:640px;font-size:16px;line-height:1.65;}}
    .soe-chips {{display:flex;flex-wrap:wrap;gap:9px;margin-top:18px;}}
    .soe-hero-logo {{position:absolute; top:22px; right:20px; width:198px; height:auto;
       border-radius:12px; object-fit:contain; opacity:.98;}}
    @media(max-width:770px) {{.soe-hero {{padding-right:20px;}}
       .soe-hero-logo {{position:relative; display:block; margin:14px auto 2px; right:auto; top:auto;
           width:min(220px,75%);}}}}
    .soe-chip {{border:1px solid #396b66;border-radius:20px;padding:7px 12px;
        color:#d8f6eb;background:#122b34;font-size:12px;font-weight:600;}}
    /* The login module has its own generic heading; the hero replaces it visually. */
    [data-testid="stMain"] h1 {{display:none !important;}}
    [data-testid="stTabs"] {{background:#0d1929; padding:20px 24px 22px;
        border-radius:20px; border:1px solid #2b425a; box-shadow:0 14px 34px #0005;}}
    [data-testid="stTabs"] [data-baseweb="tab-list"] {{gap:18px;}}
    [data-testid="stTabs"] [data-baseweb="tab"] {{font-size:15px; font-weight:750;}}
    [data-testid="stTabs"] [aria-selected="true"] {{color:#65e3b2 !important;}}
    [data-testid="stForm"] {{border:0 !important; padding:12px 0 0 !important;}}
    [data-testid="stTextInput"] input {{background:#152a3c !important;border-radius:10px !important;
      border:1px solid #476074 !important;color:#f6fafc !important;min-height:45px !important;}}
    [data-testid="stFormSubmitButton"] button {{background:linear-gradient(90deg,#1aba81,#48d7ad) !important;
      color:#07271e !important;border:none !important;min-height:45px;font-weight:800;border-radius:11px;}}
    [data-testid="stMain"] .stButton > button {{min-height:43px;border:1px solid #65bbaf;
      background:#153a40;color:#e7fff7;border-radius:11px;font-weight:750;}}
    .soe-note {{padding:12px 18px;border:1px solid #3c5166;border-radius:12px;
       background:#101e30;color:#9eb2c5;font-size:13px;margin:16px 0;}}
    @media(max-width:650px) {{.soe-hero {{padding:22px 20px;}} [data-testid="stTabs"] {{padding:14px;}}}}
    </style>
    <div class="soe-hero">
      <img class="soe-hero-logo" src="data:image/png;base64,{logo_data}" alt="Space on Earth logo">
      <div class="soe-brand">🌍 SPACE ON EARTH · {escape(t("NASA-POWERED RESEARCH PROTOTYPE"))}</div>
      <div class="soe-title">{escape(t('Grow smarter.'))}<br><em>{escape(t('Understand your land.'))}</em></div>
      <div class="soe-sub">{escape(t('Discover climate trends, explore crop rotation options, and plan your farm with clear, data-informed insights.'))}</div>
      <div class="soe-chips"><span class="soe-chip">🌱 {escape(t("Crop planning"))}</span>
      <span class="soe-chip">💧 {escape(t("Irrigation context"))}</span><span class="soe-chip">🛰️ {escape(t("NASA climate data"))}</span>
      <span class="soe-chip">🗺️ {escape(t("Global locations"))}</span></div>
    </div>
    """, unsafe_allow_html=True)
