import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
import time
import json
import threading
import websocket
import base64

# Page configuration
st.set_page_config(
    page_title="MediNomix | AI Medication Safety",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL
BACKEND_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/dashboard"

# Medical Theme Color Scheme
COLORS = {
    'primary': '#10B981',
    'primary_hover': '#059669',
    'secondary': '#3B82F6',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'info': '#0EA5E9',
    'purple': '#8B5CF6',
    'yellow': '#FBBF24',
    'pink': '#EC4899',
    'dark': '#1F2937',
    'light': '#FFFFFF',
    'card_bg': '#FFFFFF',
    'sidebar_bg': '#F0FDF4',
    'border': '#E5E7EB',
    'text_primary': '#111827',
    'text_secondary': '#4B5563',
    'text_muted': '#9CA3AF',
    'shadow': 'rgba(16, 185, 129, 0.15)',
    'shadow_hover': 'rgba(16, 185, 129, 0.25)',
    'gradient_primary': 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
    'gradient_secondary': 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
    'gradient_success': 'linear-gradient(135deg, #10B981 0%, #34D399 100%)',
    'gradient_warning': 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
    'gradient_danger': 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)',
    'gradient_purple': 'linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)',
    'gradient_dark': 'linear-gradient(135deg, #1F2937 0%, #374151 100%)',
    'gradient_medical': 'linear-gradient(135deg, #10B981 0%, #0EA5E9 50%, #3B82F6 100%)'
}

# ================================
# COMPLETE CSS STYLING WITH ALL COMPONENTS
# ================================

st.markdown(f"""
<style>
/* ========== GLOBAL STYLES & SCROLLBAR ========== */
.stApp {{
    background: linear-gradient(135deg, #F9FAFB 0%, #F0FDF4 100%);
    color: {COLORS['text_primary']};
    font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}

/* Custom scrollbar */
::-webkit-scrollbar {{
    width: 12px;
    height: 12px;
}}

::-webkit-scrollbar-track {{
    background: #F3F4F6;
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb {{
    background: {COLORS['primary']};
    border-radius: 10px;
    border: 3px solid #F3F4F6;
}}

::-webkit-scrollbar-thumb:hover {{
    background: {COLORS['primary_hover']};
}}

/* ========== MODERN TABS STYLING ========== */
.stTabs {{
    background: transparent !important;
    padding: 0 !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
    background: white !important;
    padding: 8px !important;
    border-radius: 20px !important;
    border: 2px solid {COLORS['border']} !important;
    margin-bottom: 30px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
    overflow-x: auto;
    white-space: nowrap;
}}

.stTabs [data-baseweb="tab"] {{
    height: 50px !important;
    padding: 0 24px !important;
    color: {COLORS['text_secondary']} !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    background: transparent !important;
    border-radius: 12px !important;
    border: none !important;
    transition: all 0.3s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: 120px !important;
}}

.stTabs [data-baseweb="tab"]:hover {{
    background: {COLORS['primary']}10 !important;
    color: {COLORS['primary']} !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px {COLORS['shadow']} !important;
}}

.stTabs [aria-selected="true"] {{
    background: {COLORS['gradient_primary']} !important;
    color: white !important;
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3) !important;
    transform: translateY(-2px) !important;
    font-weight: 700 !important;
}}

.stTabs [data-baseweb="tab"]:first-child {{
    margin-left: 0 !important;
}}

.stTabs [data-baseweb="tab"]:last-child {{
    margin-right: 0 !important;
}}

/* ========== ALERT MESSAGES AS CARDS ========== */
.alert-card {{
    background: white !important;
    border-radius: 16px !important;
    padding: 20px !important;
    margin: 16px 0 !important;
    border-left: 6px solid !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    display: flex !important;
    align-items: center !important;
    gap: 16px !important;
    animation: slideIn 0.5s ease !important;
    border: 2px solid rgba(0, 0, 0, 0.05) !important;
}}

@keyframes slideIn {{
    from {{ transform: translateY(-10px); opacity: 0; }}
    to {{ transform: translateY(0); opacity: 1; }}
}}

.alert-success {{
    border-left-color: {COLORS['success']} !important;
    background: linear-gradient(90deg, #F0FDF4 0%, white 100%) !important;
}}

.alert-danger {{
    border-left-color: {COLORS['danger']} !important;
    background: linear-gradient(90deg, #FEF2F2 0%, white 100%) !important;
}}

.alert-warning {{
    border-left-color: {COLORS['warning']} !important;
    background: linear-gradient(90deg, #FFFBEB 0%, white 100%) !important;
}}

.alert-info {{
    border-left-color: {COLORS['info']} !important;
    background: linear-gradient(90deg, #F0F9FF 0%, white 100%) !important;
}}

.alert-icon {{
    font-size: 24px !important;
    min-width: 40px !important;
    text-align: center !important;
}}

.alert-content {{
    flex: 1 !important;
}}

.alert-title {{
    font-weight: 700 !important;
    font-size: 16px !important;
    margin-bottom: 4px !important;
    color: {COLORS['text_primary']} !important;
}}

.alert-message {{
    font-size: 14px !important;
    color: {COLORS['text_secondary']} !important;
    line-height: 1.5 !important;
}}

/* ========== ALL STREAMLIT COMPONENTS STYLING ========== */

/* Radio buttons */
.stRadio [role="radiogroup"] {{
    background: white !important;
    padding: 16px !important;
    border-radius: 16px !important;
    border: 2px solid {COLORS['border']} !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}}

.stRadio [role="radio"] {{
    margin-right: 12px !important;
}}

.stRadio label {{
    color: {COLORS['text_primary']} !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}}

/* Select boxes */
.stSelectbox {{
    background: white !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}

.stSelectbox select {{
    background: white !important;
    color: {COLORS['text_primary']} !important;
    border: 2px solid {COLORS['border']} !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    width: 100% !important;
}}

.stSelectbox select:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15) !important;
    outline: none !important;
}}

/* Text area */
.stTextArea textarea {{
    background: white !important;
    color: {COLORS['text_primary']} !important;
    border: 2px solid {COLORS['border']} !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    min-height: 100px !important;
}}

.stTextArea textarea:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15) !important;
    outline: none !important;
}}

/* Dataframe tables */
.dataframe {{
    background: white !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    border: 2px solid {COLORS['border']} !important;
    margin: 16px 0 !important;
}}

.dataframe th {{
    background: {COLORS['gradient_primary']} !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 16px 20px !important;
    font-size: 14px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    border: none !important;
}}

.dataframe td {{
    padding: 14px 20px !important;
    border-bottom: 1px solid {COLORS['border']} !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    color: {COLORS['text_primary']} !important;
}}

.dataframe tr:hover {{
    background: {COLORS['primary']}08 !important;
}}

/* Metric cards */
[data-testid="stMetric"] {{
    background: white !important;
    border-radius: 16px !important;
    padding: 20px !important;
    border: 2px solid {COLORS['border']} !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
    transition: all 0.3s ease !important;
}}

[data-testid="stMetric"]:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
    border-color: {COLORS['primary']} !important;
}}

[data-testid="stMetricLabel"] {{
    font-size: 12px !important;
    font-weight: 600 !important;
    color: {COLORS['text_secondary']} !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}}

[data-testid="stMetricValue"] {{
    font-size: 24px !important;
    font-weight: 800 !important;
    color: {COLORS['primary']} !important;
}}

[data-testid="stMetricDelta"] {{
    font-size: 12px !important;
    font-weight: 600 !important;
}}

/* Expander */
.streamlit-expanderHeader {{
    background: {COLORS['gradient_primary']} !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    border: none !important;
    margin-bottom: 8px !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2) !important;
    transition: all 0.3s ease !important;
}}

.streamlit-expanderHeader:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3) !important;
}}

.streamlit-expanderContent {{
    background: white !important;
    border: 2px solid {COLORS['border']} !important;
    border-top: none !important;
    border-radius: 0 0 12px 12px !important;
    padding: 20px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}}

/* Progress bar */
.stProgress > div > div > div > div {{
    background: {COLORS['gradient_primary']} !important;
    border-radius: 10px !important;
}}

.stProgress > div > div {{
    background: {COLORS['border']} !important;
    border-radius: 10px !important;
    height: 8px !important;
}}

/* Spinner */
.stSpinner > div {{
    border-color: {COLORS['primary']} transparent transparent transparent !important;
}}

/* Checkbox */
.stCheckbox {{
    margin: 8px 0 !important;
}}

.stCheckbox label {{
    color: {COLORS['text_primary']} !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}}

/* Slider */
.stSlider {{
    margin: 16px 0 !important;
}}

.stSlider [data-baseweb="slider"] {{
    padding: 8px 0 !important;
}}

.stSlider [data-baseweb="thumb"] {{
    background: {COLORS['primary']} !important;
    border: 3px solid white !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
}}

.stSlider [data-baseweb="track"] {{
    background: {COLORS['border']} !important;
    height: 6px !important;
    border-radius: 3px !important;
}}

.stSlider [data-baseweb="inner-track"] {{
    background: {COLORS['gradient_primary']} !important;
    height: 6px !important;
    border-radius: 3px !important;
}}

/* Number input */
.stNumberInput input {{
    background: white !important;
    color: {COLORS['text_primary']} !important;
    border: 2px solid {COLORS['border']} !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
}}

.stNumberInput input:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15) !important;
    outline: none !important;
}}

/* ========== BUTTONS STYLING ========== */
div.stButton > button:first-child {{
    background: {COLORS['gradient_primary']} !important;
    color: white !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    min-height: 44px !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2) !important;
    position: relative !important;
    overflow: hidden !important;
}}

div.stButton > button:first-child:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3) !important;
}}

div.stButton > button:first-child::before {{
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent) !important;
    transition: 0.5s !important;
}}

div.stButton > button:first-child:hover::before {{
    left: 100% !important;
}}

div.stButton > button[kind="secondary"] {{
    background: white !important;
    color: {COLORS['primary']} !important;
    border: 2px solid {COLORS['primary']} !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.1) !important;
}}

div.stButton > button[kind="secondary"]:hover {{
    background: {COLORS['primary']}08 !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2) !important;
}}

/* ========== INPUT FIELDS ========== */
.stTextInput input {{
    background: white !important;
    color: {COLORS['text_primary']} !important;
    border: 2px solid {COLORS['border']} !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    width: 100% !important;
}}

.stTextInput input:focus {{
    border-color: {COLORS['primary']} !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.15) !important;
    outline: none !important;
}}

.stTextInput input::placeholder {{
    color: {COLORS['text_muted']} !important;
    opacity: 1 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}}

/* ========== CUSTOM CARDS ========== */
.glass-card {{
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 20px !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 8px 30px {COLORS['shadow']} !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
}}

.glass-card:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px {COLORS['shadow_hover']} !important;
    border-color: {COLORS['primary']} !important;
}}

.glass-card-header {{
    margin: -24px -24px 20px -24px !important;
    padding: 24px !important;
    background: {COLORS['gradient_primary']} !important;
    border-radius: 20px 20px 0 0 !important;
    position: relative !important;
    overflow: hidden !important;
}}

.glass-card-header h2 {{
    color: white !important;
    margin: 0 !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}}

/* ========== STAT CARDS ========== */
.stat-card {{
    background: white !important;
    border-radius: 16px !important;
    padding: 24px !important;
    text-align: center !important;
    border: 2px solid transparent !important;
    background-clip: padding-box !important;
    background: linear-gradient(white, white) padding-box,
                {COLORS['gradient_primary']} border-box !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
    height: 100% !important;
}}

.stat-card:hover {{
    transform: translateY(-5px) !important;
    box-shadow: 0 12px 30px {COLORS['shadow_hover']} !important;
}}

.stat-icon {{
    font-size: 40px !important;
    margin-bottom: 12px !important;
    color: {COLORS['primary']} !important;
}}

.stat-number {{
    font-size: 32px !important;
    font-weight: 800 !important;
    margin: 8px 0 !important;
    color: {COLORS['text_primary']} !important;
}}

.stat-label {{
    color: {COLORS['text_secondary']} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}}

/* ========== GUIDE SECTION ========== */
.guide-card {{
    background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    margin: 20px 0 !important;
    border: 2px solid {COLORS['primary']} !important;
    box-shadow: 0 8px 25px rgba(16, 185, 129, 0.15) !important;
}}

.guide-step {{
    display: flex !important;
    align-items: flex-start !important;
    gap: 16px !important;
    margin-bottom: 24px !important;
    padding: 20px !important;
    background: white !important;
    border-radius: 16px !important;
    border-left: 4px solid {COLORS['primary']} !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
}}

.step-icon {{
    font-size: 24px !important;
    min-width: 40px !important;
    text-align: center !important;
    color: {COLORS['primary']} !important;
}}

.step-content h4 {{
    color: {COLORS['text_primary']} !important;
    margin: 0 0 8px 0 !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}}

.step-content ul {{
    margin: 0 !important;
    padding-left: 20px !important;
    color: {COLORS['text_secondary']} !important;
}}

.step-content li {{
    margin-bottom: 6px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
}}

/* ========== METRIC BOXES ========== */
.metric-box {{
    background: white !important;
    border-radius: 12px !important;
    padding: 16px !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
    border: 1px solid {COLORS['border']} !important;
    height: 100% !important;
}}

.metric-box:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1) !important;
    border-color: {COLORS['primary']} !important;
}}

.metric-label {{
    color: {COLORS['text_secondary']} !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 6px !important;
}}

.metric-value {{
    font-size: 20px !important;
    font-weight: 800 !important;
    color: {COLORS['primary']} !important;
}}

/* ========== RISK BADGES ========== */
.risk-badge {{
    display: inline-flex !important;
    align-items: center !important;
    padding: 6px 16px !important;
    border-radius: 50px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    gap: 4px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}}

.badge-critical {{
    background: {COLORS['gradient_danger']} !important;
    color: white !important;
}}

.badge-high {{
    background: {COLORS['gradient_warning']} !important;
    color: white !important;
}}

.badge-medium {{
    background: {COLORS['gradient_purple']} !important;
    color: white !important;
}}

.badge-low {{
    background: {COLORS['gradient_success']} !important;
    color: white !important;
}}

/* ========== CHART CONTAINERS ========== */
.chart-container {{
    background: white !important;
    border-radius: 16px !important;
    padding: 20px !important;
    margin: 16px 0 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
    border: 2px solid {COLORS['border']} !important;
    height: 100% !important;
}}

.chart-title {{
    font-size: 16px !important;
    font-weight: 700 !important;
    color: {COLORS['text_primary']} !important;
    margin-bottom: 16px !important;
    text-align: center !important;
}}

/* ========== IMAGE STYLING ========== */
.medical-image {{
    width: 100% !important;
    height: 180px !important;
    object-fit: cover !important;
    border-radius: 12px !important;
    margin: 8px 0 !important;
    border: 2px solid {COLORS['primary']} !important;
    box-shadow: 0 4px 15px {COLORS['shadow']} !important;
    transition: all 0.3s ease !important;
}}

.medical-image:hover {{
    transform: scale(1.02) !important;
    box-shadow: 0 8px 25px {COLORS['shadow_hover']} !important;
}}

/* ========== FOOTER ========== */
.neon-footer {{
    margin-top: 60px !important;
    padding: 40px 0 !important;
    background: {COLORS['gradient_medical']} !important;
    border-radius: 30px 30px 0 0 !important;
    text-align: center !important;
    position: relative !important;
    overflow: hidden !important;
}}

.neon-footer h3 {{
    color: white !important;
    font-size: 24px !important;
    font-weight: 700 !important;
    margin-bottom: 12px !important;
}}

.neon-footer p {{
    color: rgba(255, 255, 255, 0.9) !important;
    font-size: 14px !important;
    max-width: 600px !important;
    margin: 0 auto 20px !important;
}}

/* ========== HERO SECTION ========== */
.hero-section {{
    background: {COLORS['gradient_medical']} !important;
    border-radius: 24px !important;
    padding: 40px !important;
    margin-bottom: 30px !important;
    position: relative !important;
    overflow: hidden !important;
    text-align: center !important;
    box-shadow: 0 8px 30px rgba(16, 185, 129, 0.2) !important;
}}

.hero-title {{
    color: white !important;
    font-size: 32px !important;
    font-weight: 800 !important;
    margin-bottom: 12px !important;
}}

.hero-subtitle {{
    color: rgba(255, 255, 255, 0.95) !important;
    font-size: 16px !important;
    max-width: 600px !important;
    margin: 0 auto 24px !important;
    line-height: 1.6 !important;
}}

/* ========== FEATURE CARDS ========== */
.feature-card {{
    background: white !important;
    border-radius: 16px !important;
    padding: 24px !important;
    text-align: center !important;
    border: 2px solid {COLORS['border']} !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
    height: 100% !important;
}}

.feature-card:hover {{
    transform: translateY(-5px) !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1) !important;
    border-color: {COLORS['primary']} !important;
}}

.feature-icon {{
    font-size: 40px !important;
    margin-bottom: 16px !important;
    color: {COLORS['primary']} !important;
}}

.feature-title {{
    font-size: 18px !important;
    font-weight: 700 !important;
    margin-bottom: 8px !important;
    color: {COLORS['text_primary']} !important;
}}

.feature-desc {{
    color: {COLORS['text_secondary']} !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
}}

/* ========== SEARCH CONTAINER ========== */
.search-container {{
    background: white !important;
    border-radius: 20px !important;
    padding: 32px !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08) !important;
    border: 2px solid {COLORS['border']} !important;
    margin: 30px 0 !important;
    position: relative !important;
    overflow: hidden !important;
}}

.search-title {{
    font-size: 20px !important;
    font-weight: 700 !important;
    margin-bottom: 8px !important;
    color: {COLORS['text_primary']} !important;
}}

.search-subtitle {{
    color: {COLORS['text_secondary']} !important;
    font-size: 14px !important;
    margin-bottom: 24px !important;
}}

/* ========== SIDEBAR ========== */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F0FDF4 100%) !important;
    border-right: 2px solid {COLORS['primary']} !important;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.05) !important;
}}

/* Responsive adjustments */
@media (max-width: 768px) {{
    .stTabs [data-baseweb="tab"] {{
        min-width: 100px !important;
        padding: 0 16px !important;
        font-size: 12px !important;
    }}
    
    .hero-title {{
        font-size: 24px !important;
    }}
    
    .stat-card {{
        padding: 16px !important;
    }}
    
    .stat-number {{
        font-size: 24px !important;
    }}
}}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'dashboard_data' not in st.session_state:
    st.session_state.dashboard_data = {}
if 'selected_risk' not in st.session_state:
    st.session_state.selected_risk = "all"
if 'realtime_metrics' not in st.session_state:
    st.session_state.realtime_metrics = {}
if 'websocket_connected' not in st.session_state:
    st.session_state.websocket_connected = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Home"

# ================================
# NEW ALERT FUNCTION AS CARDS
# ================================

def render_alert_card(message, alert_type="info", title=None):
    """Render alert messages as beautiful cards"""
    
    if alert_type == "success":
        icon = "✅"
        alert_class = "alert-success"
        default_title = "Success!"
    elif alert_type == "warning":
        icon = "⚠️"
        alert_class = "alert-warning"
        default_title = "Warning!"
    elif alert_type == "danger":
        icon = "❌"
        alert_class = "alert-danger"
        default_title = "Error!"
    else:
        icon = "ℹ️"
        alert_class = "alert-info"
        default_title = "Info"
    
    alert_title = title if title else default_title
    
    st.markdown(f"""
    <div class="alert-card {alert_class}">
        <div class="alert-icon">{icon}</div>
        <div class="alert-content">
            <div class="alert-title">{alert_title}</div>
            <div class="alert-message">{message}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================
# REAL-TIME WEBSOCKET MANAGER
# ================================

class RealTimeWebSocketManager:
    def __init__(self):
        self.connected = False
        self.ws = None
        
    def start_connection(self):
        try:
            self.ws = websocket.WebSocketApp(
                WS_URL,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            threading.Thread(target=self.ws.run_forever, daemon=True).start()
        except Exception as e:
            render_alert_card(f"WebSocket connection error: {e}", "danger")
    
    def _on_open(self, ws):
        self.connected = True
        st.session_state.websocket_connected = True
        render_alert_card("Real-time WebSocket connection established successfully!", "success", "Connected!")
    
    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get('type') in ['initial', 'update']:
                st.session_state.realtime_metrics = data.get('data', {})
        except:
            pass
    
    def _on_error(self, ws, error):
        self.connected = False
        st.session_state.websocket_connected = False
        render_alert_card(f"WebSocket error: {error}", "warning", "Connection Issue")
    
    def _on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        st.session_state.websocket_connected = False
        render_alert_card("WebSocket connection closed", "info", "Disconnected")

websocket_manager = RealTimeWebSocketManager()

# ================================
# CORE FUNCTIONS
# ================================

def search_drug(drug_name):
    """Search for drug and analyze confusion risks"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/search/{drug_name}", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        return None

def load_examples():
    """Load example drugs for demonstration"""
    try:
        response = requests.post(f"{BACKEND_URL}/api/seed-database", timeout=30)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        return False

def load_dashboard_data():
    """Load dashboard analytics data"""
    try:
        # Load metrics
        metrics_response = requests.get(f"{BACKEND_URL}/api/metrics")
        if metrics_response.status_code == 200:
            st.session_state.dashboard_data['metrics'] = metrics_response.json()
        
        # Load top risks
        risks_response = requests.get(f"{BACKEND_URL}/api/top-risks?limit=10")
        if risks_response.status_code == 200:
            st.session_state.dashboard_data['top_risks'] = risks_response.json()
        
        # Load risk breakdown
        breakdown_response = requests.get(f"{BACKEND_URL}/api/risk-breakdown")
        if breakdown_response.status_code == 200:
            st.session_state.dashboard_data['breakdown'] = breakdown_response.json()
        
        # Load heatmap data
        heatmap_response = requests.get(f"{BACKEND_URL}/api/heatmap?limit=15")
        if heatmap_response.status_code == 200:
            st.session_state.dashboard_data['heatmap'] = heatmap_response.json()
            
        return True
    except Exception as e:
        return False

def create_heatmap_chart():
    """Create interactive drug confusion heatmap with annotations"""
    if 'heatmap' not in st.session_state.dashboard_data:
        return None
    
    heatmap_data = st.session_state.dashboard_data['heatmap']
    drug_names = heatmap_data.get("drug_names", [])
    risk_matrix = heatmap_data.get("risk_matrix", [])
    
    if not drug_names or not risk_matrix:
        return None
    
    # Create annotations for high-risk cells
    annotations = []
    for i, row in enumerate(risk_matrix):
        for j, value in enumerate(row):
            if value > 70:  # High risk values
                annotations.append(
                    dict(
                        x=j,
                        y=i,
                        text=f"<b>{value:.0f}%</b>",
                        showarrow=False,
                        font=dict(color="white", size=10, family="Poppins"),
                        bgcolor="rgba(239, 68, 68, 0.8)",
                        bordercolor="white",
                        borderwidth=1,
                        borderpad=4
                    )
                )
    
    fig = go.Figure(data=go.Heatmap(
        z=risk_matrix,
        x=drug_names,
        y=drug_names,
        colorscale=[
            [0, COLORS['success']],
            [0.25, COLORS['purple']],
            [0.5, COLORS['warning']],
            [0.75, COLORS['danger']],
            [1, COLORS['primary']]
        ],
        zmin=0,
        zmax=100,
        hovertemplate="<b>%{y}</b> ↔ <b>%{x}</b><br>Risk: <b>%{z:.1f}%</b><extra></extra>",
        colorbar=dict(
            title="Risk %",
            titleside="right",
            titlefont=dict(color=COLORS['text_primary'], size=12, family="Poppins"),
            tickfont=dict(color=COLORS['text_secondary'], size=10, family="Poppins"),
            bgcolor="white",
            bordercolor=COLORS['border'],
            borderwidth=2
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="🎯 Drug Confusion Risk Heatmap",
            font=dict(color=COLORS['text_primary'], size=18, family="Poppins"),
            x=0.5,
            xanchor="center"
        ),
        height=500,
        xaxis_title="Drug Names",
        yaxis_title="Drug Names",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color=COLORS['text_primary'],
        xaxis=dict(
            tickfont=dict(color=COLORS['text_secondary'], size=10, family="Poppins"),
            gridcolor=COLORS['border'],
            linecolor=COLORS['border'],
            linewidth=1
        ),
        yaxis=dict(
            tickfont=dict(color=COLORS['text_secondary'], size=10, family="Poppins"),
            gridcolor=COLORS['border'],
            linecolor=COLORS['border'],
            linewidth=1
        ),
        margin=dict(l=80, r=50, t=60, b=80),
        annotations=annotations
    )
    
    return fig

def create_risk_breakdown_chart():
    """Create risk breakdown chart"""
    if 'breakdown' not in st.session_state.dashboard_data:
        return None
    
    breakdown = st.session_state.dashboard_data['breakdown']
    if not breakdown:
        return None
    
    categories = [item['category'].title() for item in breakdown]
    counts = [item['count'] for item in breakdown]
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=counts,
        hole=0.5,
        marker_colors=[COLORS['danger'], COLORS['warning'], COLORS['purple'], COLORS['success']],
        textinfo='label+percent',
        textposition='inside',
        hoverinfo='label+value+percent',
        textfont=dict(color='white', size=12, family='Poppins'),
        marker_line=dict(color='white', width=2),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title=dict(
            text="Risk Distribution",
            font=dict(color=COLORS['text_primary'], size=16, family="Poppins"),
            x=0.5,
            xanchor="center"
        ),
        height=400,
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color=COLORS['text_primary'],
        legend=dict(
            font=dict(size=12, color=COLORS['text_secondary'], family="Poppins"),
            bgcolor='white',
            bordercolor=COLORS['border'],
            borderwidth=1
        )
    )
    
    return fig

def create_top_risks_chart():
    """Create top risks chart"""
    if 'top_risks' not in st.session_state.dashboard_data:
        return None
    
    top_risks = st.session_state.dashboard_data['top_risks']
    if not top_risks:
        return None
    
    pairs = [f"💊 {item['drug1']} ↔ {item['drug2']}" for item in top_risks]
    scores = [item['risk_score'] for item in top_risks]
    
    fig = go.Figure(data=[
        go.Bar(
            x=scores,
            y=pairs,
            orientation='h',
            marker_color=COLORS['primary'],
            text=[f"🔥 {score:.0f}%" for score in scores],
            textposition='outside',
            marker_line_color='white',
            marker_line_width=1,
            textfont=dict(size=12, color=COLORS['text_primary'], family="Poppins"),
            hovertemplate="<b>%{y}</b><br>Risk Score: <b>%{x:.1f}%</b><extra></extra>"
        )
    ])
    
    fig.update_layout(
        title=dict(
            text="🚨 Top 10 High-Risk Drug Pairs",
            font=dict(color=COLORS['text_primary'], size=16, family="Poppins"),
            x=0.5,
            xanchor="center"
        ),
        xaxis_title="Risk Score (%)",
        yaxis_title="",
        height=450,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font_color=COLORS['text_primary'],
        xaxis=dict(
            gridcolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_secondary'], size=10, family="Poppins")
        ),
        yaxis=dict(
            tickfont=dict(color=COLORS['text_secondary'], size=10, family="Poppins")
        ),
        margin=dict(l=150, r=50, t=60, b=50)
    )
    
    return fig

# ================================
# UI COMPONENTS
# ================================

def render_stat_card(icon, value, label, col):
    """Render a statistic card"""
    with col:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">{icon}</div>
            <div class="stat-number">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

def render_feature_card(icon, title, description, col):
    """Render a feature card"""
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{description}</div>
        </div>
        """, unsafe_allow_html=True)

def render_metric_box(label, value, col):
    """Render a metric box"""
    with col:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

def render_glass_card(title, content=None):
    """Render a glassmorphism card"""
    st.markdown(f"""
    <div class="glass-card">
        <div class="glass-card-header">
            <h2>{title}</h2>
        </div>
        <div style="color: {COLORS['text_primary']};">{content if content else ""}</div>
    </div>
    """, unsafe_allow_html=True)

def render_guide_section():
    """Render user guide section with improved styling"""
    st.markdown("""
    <div class="guide-card">
        <h2 style="color: #111827 !important; margin-bottom: 24px !important; text-align: center; font-size: 20px !important;">📚 User Guide & Tips</h2>
    """, unsafe_allow_html=True)
    
    # Step 1
    st.markdown("""
    <div class="guide-step">
        <div class="step-icon">🚀</div>
        <div class="step-content">
            <h4>Step 1: Search for a Medication</h4>
            <ul>
                <li>Navigate to the <b>Drug Analysis</b> tab</li>
                <li>Enter any medication name (brand or generic)</li>
                <li>Click <b>Analyze Drug</b> to start the AI analysis</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 2
    st.markdown("""
    <div class="guide-step">
        <div class="step-icon">📊</div>
        <div class="step-content">
            <h4>Step 2: Review Risk Assessment</h4>
            <ul>
                <li>View all similar drugs with confusion risks</li>
                <li>Filter by risk level (Critical, High, Medium, Low)</li>
                <li>Examine detailed similarity metrics</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 3
    st.markdown("""
    <div class="guide-step">
        <div class="step-icon">🛡️</div>
        <div class="step-content">
            <h4>Step 3: Take Preventive Action</h4>
            <ul>
                <li>Check <b>Analytics</b> tab for overall statistics</li>
                <li>Monitor <b>Real-Time</b> dashboard for live updates</li>
                <li>Use quick examples for demonstration</li>
            </ul>
        </div>
    </div>
    
    <div style="background: linear-gradient(135deg, #F0F9FF 0%, #F0FDF4 100%); padding: 20px; border-radius: 12px; margin-top: 24px; border: 2px solid #D1FAE5;">
        <h4 style="color: #111827 !important; margin-bottom: 12px !important; font-size: 16px !important;">💡 Pro Tips:</h4>
        <ul style="color: #4B5563 !important; font-size: 14px !important; font-weight: 500 !important;">
            <li style="margin-bottom: 8px !important;">Always double-check medication names before administration</li>
            <li style="margin-bottom: 8px !important;">Use Tall Man lettering for look-alike drug names</li>
            <li style="margin-bottom: 8px !important;">Consult the FDA high-alert drug list regularly</li>
            <li>Report any confusion incidents through your institution's safety reporting system</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# HOMEPAGE
# ================================

def render_hero_section():
    """Render hero section"""
    
    st.markdown(f"""
    <div class="hero-section">
        <h1 class="hero-title">💊 MediNomix AI</h1>
        <p class="hero-subtitle">Advanced AI-powered system that analyzes drug names for potential confusion risks, helping healthcare professionals prevent medication errors and improve patient safety.</p>
    </div>
    """, unsafe_allow_html=True)

# ================================
# DRUG ANALYSIS TAB
# ================================

def render_drug_analysis_tab():
    """Render Drug Analysis tab"""
    
    render_glass_card(
        "🔍 Drug Confusion Risk Analysis",
        "Search any medication to analyze confusion risks with similar drugs"
    )
    
    # Search Section
    st.markdown("""
    <div class="search-container">
        <div class="search-title">Search Medication</div>
        <div class="search-subtitle">Enter any drug name to analyze potential confusion risks</div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        drug_name = st.text_input(
            "",
            placeholder="Enter drug name (e.g., metformin, lamictal, celebrex...)",
            key="search_input",
            label_visibility="collapsed"
        )
    
    with col2:
        search_clicked = st.button("Analyze Drug", type="primary", use_container_width=True)
    
    with col3:
        if st.button("Load Examples", type="secondary", use_container_width=True):
            with st.spinner("Loading examples..."):
                if load_examples():
                    render_alert_card("Examples loaded successfully! Try searching: lamictal, celebrex, metformin", "success")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Examples with Images
    st.markdown("""
    <div style="margin: 24px 0;">
        <h3 style="color: #111827; margin-bottom: 16px; font-weight: 700;">✨ Quick Examples:</h3>
    </div>
    """, unsafe_allow_html=True)
    
    examples = ["Lamictal", "Metformin", "Celebrex", "Clonidine"]
    example_images = [
        "https://www.shutterstock.com/image-photo/lamotrigine-drug-prescription-medication-pills-260nw-2168515791.jpg",
        "https://t3.ftcdn.net/jpg/05/99/37/68/360_F_599376857_qFxGlExvZ576RG5CyNFajllibkCF7TAZ.jpg",
        "https://www.verywellhealth.com/thmb/6DChoTv1r2NyRc4HmOHvv46uO3A=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/VWH.GettyImages-471365176-dcb658055f7540a788a3382a0628ea32.jpg",
        "https://t4.ftcdn.net/jpg/06/00/08/53/360_F_600085338_S9G1HlJKiZpSKKTLZKaoa6Y8l752W8M6.jpg"
    ]
    
    cols = st.columns(4)
    for idx, col in enumerate(cols):
        with col:
            # Display image
            st.markdown(f"""
            <img src="{example_images[idx]}" class="medical-image" alt="{examples[idx]}">
            """, unsafe_allow_html=True)
            
            # Display button
            if st.button(f"💊 {examples[idx]}", use_container_width=True, key=f"ex_{idx}"):
                with st.spinner(f"🔬 Analyzing {examples[idx]}..."):
                    result = search_drug(examples[idx])
                    if result:
                        st.session_state.search_results = result.get('similar_drugs', [])
                        render_alert_card(f"Analysis complete! Found {len(st.session_state.search_results)} similar drugs.", "success")
                        st.rerun()
    
    # Handle Search
    if search_clicked and drug_name:
        with st.spinner(f"🧠 Analyzing '{drug_name}'..."):
            result = search_drug(drug_name)
            if result:
                st.session_state.search_results = result.get('similar_drugs', [])
                render_alert_card(f"✅ Analysis complete! Found {len(st.session_state.search_results)} similar drugs.", "success")
                st.rerun()
            else:
                render_alert_card("❌ Could not analyze drug. Please check backend connection.", "danger")
    
    # Results Section
    if st.session_state.search_results:
        st.markdown("""
        <div style="margin-top: 40px;">
            <h2 style="color: #111827; margin-bottom: 24px; font-weight: 700;">Analysis Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk Filters
        risk_filters = st.radio(
            " Filter by risk level:",
            ["All Risks", "Critical (≥75%)", "High (50-74%)", "Medium (25-49%)", "Low (<25%)"],
            horizontal=True,
            key="risk_filter"
        )
        
        # Filter results
        if risk_filters == "All Risks":
            filtered_results = st.session_state.search_results
        else:
            risk_map = {
                "Critical (≥75%)": "critical",
                "High (50-74%)": "high",
                "Medium (25-49%)": "medium",
                "Low (<25%)": "low"
            }
            risk_level = risk_map[risk_filters]
            filtered_results = [
                r for r in st.session_state.search_results 
                if r['risk_category'] == risk_level
            ]
        
        # Display Results
        for result in filtered_results[:20]:
            risk_color_class = f"badge-{result['risk_category']}"
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 24px; gap: 20px;">
                    <div style="flex: 1;">
                        <h3 style="margin: 0 0 8px 0; color: #111827; font-weight: 700; font-size: 18px;">{result['target_drug']['brand_name']}</h3>
                        {f"<p style='margin: 0 0 12px 0; color: #4B5563; font-size: 14px; font-weight: 500;'>Generic: {result['target_drug']['generic_name']}</p>" if result['target_drug']['generic_name'] else ""}
                    </div>
                    <div style="text-align: center; min-width: 100px;">
                        <div style="font-size: 32px; font-weight: 800; color: {COLORS['primary']}; margin-bottom: 8px;">
                            {result['combined_risk']:.0f}%
                        </div>
                        <span class="risk-badge {risk_color_class}">{result['risk_category'].upper()}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Metrics Grid
            cols = st.columns(4)
            metrics = [
                ("Spelling Similarity", f"{result['spelling_similarity']:.1f}%"),
                ("Phonetic Similarity", f"{result['phonetic_similarity']:.1f}%"),
                ("Therapeutic Context", f"{result['therapeutic_context_risk']:.1f}%"),
                ("Overall Risk", f"{result['combined_risk']:.1f}%")
            ]
            
            for col, (label, value) in zip(cols, metrics):
                with col:
                    render_metric_box(label, value, col)
            
            st.markdown("</div>")

# ================================
# ANALYTICS DASHBOARD TAB
# ================================

def render_analytics_tab():
    """Render Analytics Dashboard tab"""
    
    render_glass_card(
        "Medication Safety Analytics Dashboard",
        "Real-time insights and analytics for medication safety monitoring"
    )
    
    # Load data if needed
    if 'metrics' not in st.session_state.dashboard_data:
        with st.spinner("📡 Loading analytics data..."):
            load_dashboard_data()
    
    # KPI Cards
    if 'metrics' in st.session_state.dashboard_data:
        metrics = st.session_state.dashboard_data['metrics']
        
        col1, col2, col3, col4 = st.columns(4)
        
        render_stat_card("💊", metrics.get('total_drugs', 0), "Total Drugs", col1)
        render_stat_card("🔥", metrics.get('critical_risk_pairs', 0), "Critical Pairs", col2)
        render_stat_card("⚠️", metrics.get('high_risk_pairs', 0), "High Risk Pairs", col3)
        render_stat_card("📈", f"{metrics.get('avg_risk_score', 0):.1f}%", "Avg Risk Score", col4)
    
    # Charts Section with proper card headers
    st.markdown('<div class="glass-card"><div class="glass-card-header"><h2>Analytics Charts</h2></div></div>', unsafe_allow_html=True)
    
    # First row: Two charts side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Risk Distribution</div>', unsafe_allow_html=True)
        breakdown_chart = create_risk_breakdown_chart()
        if breakdown_chart:
            st.plotly_chart(breakdown_chart, use_container_width=True)
        else:
            st.info("No risk breakdown data available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🚨 Top 10 High-Risk Drug Pairs</div>', unsafe_allow_html=True)
        risks_chart = create_top_risks_chart()
        if risks_chart:
            st.plotly_chart(risks_chart, use_container_width=True)
        else:
            st.info("No top risk data available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row: Heatmap full width with annotations
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title"> Drug Confusion Risk Heatmap</div>', unsafe_allow_html=True)
    
    heatmap_chart = create_heatmap_chart()
    if heatmap_chart:
        st.plotly_chart(heatmap_chart, use_container_width=True)
        st.markdown(f"""
        <div style="display: flex; justify-content: center; gap: 16px; margin-top: 20px; color: #4B5563; font-size: 12px; font-weight: 600;">
            <div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background: {COLORS['success']}; border-radius: 2px;"></div> Low Risk</div>
            <div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background: {COLORS['purple']}; border-radius: 2px;"></div> Medium Risk</div>
            <div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background: {COLORS['warning']}; border-radius: 2px;"></div> High Risk</div>
            <div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background: {COLORS['danger']}; border-radius: 2px;"></div> Critical Risk</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No heatmap data available. Search for drugs first.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # FDA Alerts Section
    render_glass_card("🚨 FDA High Alert Drug Pairs", "Most commonly confused drug pairs according to FDA")
    
    risky_pairs = pd.DataFrame([
        {"Drug 1": "Lamictal", "Drug 2": "Lamisil", "Risk Level": "Critical", "Reason": "Epilepsy medication vs Antifungal"},
        {"Drug 1": "Celebrex", "Drug 2": "Celexa", "Risk Level": "Critical", "Reason": "Arthritis vs Depression medication"},
        {"Drug 1": "Metformin", "Drug 2": "Metronidazole", "Risk Level": "High", "Reason": "Diabetes vs Antibiotic"},
        {"Drug 1": "Clonidine", "Drug 2": "Klonopin", "Risk Level": "High", "Reason": "Blood Pressure vs Anxiety medication"},
        {"Drug 1": "Zyprexa", "Drug 2": "Zyrtec", "Risk Level": "Medium", "Reason": "Antipsychotic vs Allergy medication"},
    ])
    
    st.dataframe(
        risky_pairs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Drug 1": st.column_config.TextColumn("💊 Drug 1", width="medium"),
            "Drug 2": st.column_config.TextColumn("💊 Drug 2", width="medium"),
            "Risk Level": st.column_config.TextColumn("⚠️ Risk Level", width="small"),
            "Reason": st.column_config.TextColumn("📝 Reason", width="large")
        }
    )

# ================================
# REAL-TIME DASHBOARD TAB
# ================================

def render_realtime_tab():
    """Render Real-Time Dashboard tab"""
    
    render_glass_card(
        "⚡ Real-Time Medication Safety Dashboard",
        "Live monitoring and real-time analytics for medication safety"
    )
    
    # Connection Status
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.websocket_connected:
            render_alert_card("✅ Real-time Connection Active - Live data streaming enabled", "success", "Connected!")
        else:
            render_alert_card("🔌 Connecting to Real-Time Server - Live updates will appear here", "info", "Connecting...")
    
    with col2:
        if st.button("Refresh Connection", type="primary", use_container_width=True):
            websocket_manager.start_connection()
            st.rerun()
    
    # Auto-start WebSocket if not connected
    if not st.session_state.websocket_connected:
        websocket_manager.start_connection()
    
    # Display Real-time Metrics
    metrics = st.session_state.realtime_metrics or {}
    
    if metrics:
        # Real-time KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        render_stat_card("📊", metrics.get('total_drugs', 0), "Live Drugs", col1)
        render_stat_card("🔥", metrics.get('critical_risk_pairs', 0), "Critical Now", col2)
        render_stat_card("📈", f"{metrics.get('avg_risk_score', 0):.1f}%", "Avg Risk", col3)
        render_stat_card("👥", metrics.get('connected_clients', 0), "Connected", col4)
        
        # Recent Activity Section
        render_glass_card("🕒 Recent Activity Timeline", "Latest drug analysis activities")
        
        if metrics.get('recent_searches'):
            for idx, search in enumerate(metrics['recent_searches'][:5]):
                timestamp = search.get('timestamp', '')
                drug_name = search.get('drug_name', 'Unknown')
                similar_drugs = search.get('similar_drugs_found', 0)
                highest_risk = search.get('highest_risk', 0)
                
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f'<div style="text-align: center; padding: 12px; background: {COLORS["primary"]}20; border-radius: 12px;"><div style="font-size: 20px; font-weight: 800; color: {COLORS["primary"]};">{idx+1}</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div style="padding: 12px 0;">
                        <div style="font-weight: 700; color: {COLORS['text_primary']}; font-size: 14px;">💊 {drug_name}</div>
                        <div style="color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;">Found {similar_drugs} similar drugs • Highest risk: {highest_risk:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f'<div style="color: {COLORS["text_muted"]}; font-size: 11px; font-weight: 600; text-align: right; padding-top: 12px;">{timestamp[:19] if timestamp else "Just now"}</div>', unsafe_allow_html=True)
        else:
            st.info("No recent activity data available")
    else:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px; color: {COLORS['primary']}">⏳</div>
            <h2 style="color: {COLORS['text_primary']}; margin-bottom: 12px; font-weight: 700;">Waiting for Real-Time Data</h2>
            <p style="color: {COLORS['text_secondary']}; max-width: 400px; margin: 0 auto; font-size: 14px; font-weight: 500;">Live updates will appear here once connection is established.</p>
        </div>
        """, unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================

def render_sidebar():
    """Render sidebar with system status"""
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 24px; padding: 20px 16px; background: {COLORS['gradient_primary']}; border-radius: 16px; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.2);">
            <div style="font-size: 48px; margin-bottom: 8px; filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2));">💊</div>
            <h2 style="margin: 0; color: white !important; font-weight: 800; font-size: 20px;">MediNomix</h2>
            <p style="color: rgba(255, 255, 255, 0.9); margin: 4px 0 0 0; font-size: 12px; font-weight: 600;">AI Medication Safety</p>
        </div>
        """, unsafe_allow_html=True)
        
        # System Status Card with alert card
        st.markdown('<div class="glass-card"><div class="glass-card-header"><h2>📡 System Status</h2></div></div>', unsafe_allow_html=True)
        
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    render_alert_card("Backend server is running smoothly", "success", "✅ Backend Connected")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("💊 Drugs", data.get('metrics', {}).get('drugs_in_database', 0))
                    with col2:
                        st.metric("📊 Analyses", data.get('metrics', {}).get('total_analyses', 0))
                else:
                    render_alert_card("Backend server has issues", "warning", "⚠️ Backend Issues")
            else:
                render_alert_card("Cannot connect to backend server", "danger", "❌ Cannot Connect")
        except:
            render_alert_card("Backend server is not running", "danger", "🔌 Backend Not Running")
            st.code("python backend.py", language="bash")
        
        # Quick Links
        st.markdown('<div class="glass-card"><div class="glass-card-header"><h2>🔗 Quick Links</h2></div></div>', unsafe_allow_html=True)
        
        if st.button("📚 Documentation", use_container_width=True):
            render_alert_card("Documentation coming soon!", "info")
        
        if st.button("🐛 Report Bug", use_container_width=True):
            render_alert_card("Bug reporting coming soon!", "info")
        
        if st.button("🔄 Clear Cache", use_container_width=True):
            st.session_state.search_results = []
            st.session_state.dashboard_data = {}
            render_alert_card("Cache cleared successfully!", "success")
            st.rerun()
        
        # Risk Categories Guide
        st.markdown('<div class="glass-card"><div class="glass-card-header"><h2>⚠️ Risk Categories</h2></div></div>', unsafe_allow_html=True)
        
        risk_levels = [
            ("Critical", "≥75%", "Immediate attention required", COLORS['danger']),
            ("High", "50-74%", "Review and verify", COLORS['warning']),
            ("Medium", "25-49%", "Monitor closely", COLORS['purple']),
            ("Low", "<25%", "Low priority", COLORS['success'])
        ]
        
        for name, score, desc, color in risk_levels:
            st.markdown(f"""
            <div style="margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #E5E7EB; last-child: border-bottom: none;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="padding: 4px 12px; background: {color}; color: white; border-radius: 20px; font-size: 11px; font-weight: 700;">{name}</div>
                    <div style="font-weight: 700; color: #111827; font-size: 12px;">{score}</div>
                </div>
                <div style="color: #4B5563; font-size: 11px; font-weight: 500;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ================================
# FOOTER
# ================================

def render_footer():
    """Render footer"""
    
    st.markdown(f"""
    <div class="neon-footer">
        <div style="max-width: 600px; margin: 0 auto; padding: 0 20px;">
            <div style="margin-bottom: 24px;">
                <div style="font-size: 32px; margin-bottom: 12px;">💊</div>
                <h3 style="color: white !important; margin-bottom: 8px; font-weight: 700;">MediNomix AI</h3>
                <p style="color: rgba(255, 255, 255, 0.95) !important; font-size: 14px; max-width: 500px; margin: 0 auto;">
                    Preventing medication errors with artificial intelligence
                </p>
            </div>
            <div style="border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 20px; color: rgba(255, 255, 255, 0.8) !important; font-size: 12px;">
                <div style="margin-bottom: 8px; font-weight: 600;">© 2024 MediNomix AI. All rights reserved.</div>
                <div>Disclaimer: This tool is for educational purposes and should not replace professional medical advice.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================================
# MAIN APPLICATION
# ================================

def main():
    """Main application renderer"""
    
    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([" Home", " Drug Analysis", " Analytics", "⚡ Real-Time"])
    
    with tab1:
        render_hero_section()
        
        # Stats Counter
        col1, col2, col3, col4 = st.columns(4)
        render_stat_card("👥", "1.5M+", "Patients Protected", col1)
        render_stat_card("💰", "$42B", "Cost Saved", col2)
        render_stat_card("🎯", "99.8%", "Accuracy Rate", col3)
        render_stat_card("💊", "50K+", "Drugs Analyzed", col4)
        
        # Features Section with Images
        st.markdown("""
        <div style="margin: 40px 0;">
            <h2 style="text-align: center; margin-bottom: 32px; color: #111827; font-weight: 800;">✨ How MediNomix Works</h2>
        </div>
        """, unsafe_allow_html=True)
        
        features_cols = st.columns(3)
        features = [
            {"icon": "🔍", "title": "Search Medication", "desc": "Enter any drug name to analyze potential confusion risks"},
            {"icon": "🧠", "title": "AI Analysis", "desc": "Our AI analyzes spelling, phonetic, and therapeutic similarities"},
            {"icon": "🛡️", "title": "Risk Prevention", "desc": "Get detailed risk assessments and prevention recommendations"}
        ]
        
        # Add images for features
        feature_images = [
            "https://img.freepik.com/premium-photo/modern-vital-sign-monitor-patient-background-ward-hospital_1095508-6659.jpg?semt=ais_hybrid&w=740&q=80",
            "https://www.workingbuildings.com/images/hazardousdrugs.png",
            "https://www.shutterstock.com/image-photo/bluewhite-antibiotic-capsule-pills-spread-260nw-2317028543.jpg"
        ]
        
        for idx, col in enumerate(features_cols):
            with col:
                # Display image
                st.markdown(f"""
                <img src="{feature_images[idx]}" class="medical-image" alt="{features[idx]['title']}">
                """, unsafe_allow_html=True)
                
                # Display feature card
                feature = features[idx]
                render_feature_card(feature['icon'], feature['title'], feature['desc'], col)
        
        # User Guide Section
        render_guide_section()
        
        # Trust Section with Images
        render_glass_card("Trusted by Healthcare Professionals")
        
        # Medical images grid
        medical_images = [
            "https://www.shutterstock.com/image-photo/portrait-man-doctor-standing-team-260nw-2478537933.jpg",
            "https://thumbs.dreamstime.com/b/healthcare-professionals-including-doctors-nurses-applauding-together-contemporary-medical-setting-representing-teamwork-398717867.jpg",
            "https://thumbs.dreamstime.com/b/four-healthcare-workers-scrubs-walking-corridor-104862472.jpg",
            "https://t3.ftcdn.net/jpg/02/19/91/48/360_F_219914874_fcqxEeJ6clfwf43OcCNAMGNBySKzF5hl.jpg"
        ]
        
        cols = st.columns(4)
        for idx, col in enumerate(cols):
            with col:
                st.markdown(f"""
                <img src="{medical_images[idx]}" class="medical-image" alt="Medical Facility {idx+1}">
                """, unsafe_allow_html=True)
    
    with tab2:
        render_drug_analysis_tab()
    
    with tab3:
        render_analytics_tab()
    
    with tab4:
        render_realtime_tab()
    
    # Render Sidebar
    render_sidebar()
    
    # Render Footer
    render_footer()

# ================================
# START APPLICATION
# ================================

if __name__ == "__main__":
    main()