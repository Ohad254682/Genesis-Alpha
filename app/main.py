"""
Streamlit App: Optimize Stocks with GenAI
Main application file
"""
# #region agent log
import json, time; _log_path = r"c:\Users\ohada\OneDrive\Desktop\Gen AI for Stock Analysis (2)\Gen AI for Stock Analysis\.cursor\debug.log"; _log_write = lambda d: open(_log_path, 'a', encoding='utf-8').write(json.dumps(d, ensure_ascii=False) + '\n')
_log_write({"id": "log_entry_point", "timestamp": int(time.time() * 1000), "location": "app/main.py:7", "message": "Script entry point reached", "data": {"hypothesisId": "A"}, "sessionId": "debug-session", "runId": "run1"})
# #endregion
import streamlit as st
import streamlit.components.v1 as components
# #region agent log
_log_write({"id": "log_streamlit_imported", "timestamp": int(time.time() * 1000), "location": "app/main.py:10", "message": "Streamlit imported successfully", "data": {"hypothesisId": "A"}, "sessionId": "debug-session", "runId": "run1"})
# #endregion
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from pathlib import Path
import html
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
# #region agent log
_log_write({"id": "log_path_modified", "timestamp": int(time.time() * 1000), "location": "app/main.py:24", "message": "Sys path modified", "data": {"parentDir": parent_dir, "hypothesisId": "C"}, "sessionId": "debug-session", "runId": "run1"})
# #endregion

# #region agent log
try:
    from utils.llm_utils import initialize_llm, get_llm_response
    from utils.date_utils import calculate_date_range
    from utils.kpi_calculator import calculate_kpis, get_beta_values
    try:
        from utils.portfolio_optimizer import (
            optimize_portfolio_mpt,
            optimize_portfolio_black_litterman,
            optimize_portfolio_risk_parity,
        )
        PORTFOLIO_OPT_AVAILABLE = True
    except ImportError:
        PORTFOLIO_OPT_AVAILABLE = False
        optimize_portfolio_mpt = None
        optimize_portfolio_black_litterman = None
        optimize_portfolio_risk_parity = None
    from utils.visualizations import (
        plot_rsi, plot_bollinger_bands, plot_pe_ratios, 
        plot_beta_comparison, plot_macd
    )
    from config.settings import (
        DEFAULT_YEARS, DEFAULT_ASSETS, DEFAULT_RISK_FREE_RATE_MPT, 
        DEFAULT_RISK_FREE_RATE_BL, OPENAI_API_KEY
)
    # #region agent log
    _log_write({"id": "log_utils_imported", "timestamp": int(time.time() * 1000), "location": "app/main.py:43", "message": "All utility modules imported successfully", "data": {"hypothesisId": "A"}, "sessionId": "debug-session", "runId": "run1"})
    # #endregion
    import yfinance as yf
    import matplotlib.pyplot as plt
    import plotly.graph_objects as go
    import plotly.express as px
    from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout, RequestException
    from utils.data_cache import get_ticker_history, get_ticker_info as get_ticker_info_cached
    # #region agent log
    _log_write({"id": "log_all_imports_done", "timestamp": int(time.time() * 1000), "location": "app/main.py:50", "message": "All imports completed successfully", "data": {"hypothesisId": "A"}, "sessionId": "debug-session", "runId": "run1"})
    # #endregion
# #region agent log
except Exception as e:
    _log_write({"id": "log_import_error", "timestamp": int(time.time() * 1000), "location": "app/main.py:53", "message": "Import error occurred", "data": {"error": str(e), "errorType": type(e).__name__, "hypothesisId": "A"}, "sessionId": "debug-session", "runId": "run1"})
    raise
# #endregion

# Page configuration
# #region agent log
_log_write({"id": "log_before_page_config", "timestamp": int(time.time() * 1000), "location": "app/main.py:57", "message": "Before Streamlit page config", "data": {"hypothesisId": "D"}, "sessionId": "debug-session", "runId": "run1"})
# #endregion
try:
    # Load logo for favicon
    from PIL import Image
    _logo_path = Path(__file__).parent.parent / "assets" / "profile_robot.png"
    _favicon = Image.open(_logo_path) if _logo_path.exists() else "📈"
except Exception:
    _favicon = "📈"

try:
    st.set_page_config(
        page_title="GENESIS ALPHA",
        page_icon=_favicon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    # #region agent log
    _log_write({"id": "log_page_config_success", "timestamp": int(time.time() * 1000), "location": "app/main.py:65", "message": "Streamlit page config successful", "data": {"hypothesisId": "D"}, "sessionId": "debug-session", "runId": "run1"})
    # #endregion
except Exception as e:
    # #region agent log
    _log_write({"id": "log_page_config_error", "timestamp": int(time.time() * 1000), "location": "app/main.py:67", "message": "Streamlit page config error", "data": {"error": str(e), "errorType": type(e).__name__, "hypothesisId": "D"}, "sessionId": "debug-session", "runId": "run1"})
    # #endregion
    raise

# Custom CSS - Modern Stock Market Design
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --danger-gradient: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        --dark-bg: #0a0e27;
        --card-bg: #ffffff;
        --text-primary: #1a1a2e;
        --text-secondary: #6c757d;
        --border-color: #e9ecef;
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
        --shadow-lg: 0 10px 25px rgba(0,0,0,0.1);
        --shadow-xl: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: #1a1a2e;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }
    
    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Cards and Containers */
    .stMetric {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    /* Buttons */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        background: var(--primary-gradient);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-md);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        opacity: 0.9;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 1.5rem 3rem !important;
        font-size: 2.5rem !important;
        border-radius: 12px;
        background-color: #f8f9fa;
        color: var(--text-secondary);
        transition: all 0.3s ease;
        height: auto !important;
        min-height: 75px !important;
        line-height: 1.5 !important;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        color: #667eea !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-gradient);
        color: white;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stTabs [aria-selected="true"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Dataframes - Auto-sizing */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        table-layout: auto !important;
        width: 100% !important;
    }
    
    /* Force auto-sizing on all Streamlit dataframes */
    div[data-testid="stDataFrame"] table {
        table-layout: auto !important;
        width: 100% !important;
    }
    
    div[data-testid="stDataFrame"] colgroup,
    div[data-testid="stDataFrame"] col {
        display: none !important;
        width: auto !important;
    }
    
    div[data-testid="stDataFrame"] td,
    div[data-testid="stDataFrame"] th {
        width: auto !important;
        max-width: none !important;
        min-width: auto !important;
    }
    
    div[data-testid="stDataFrame"] td[style*="width"],
    div[data-testid="stDataFrame"] th[style*="width"] {
        width: auto !important;
        min-width: auto !important;
        max-width: none !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(17, 153, 142, 0.1) 0%, rgba(56, 239, 125, 0.1) 100%);
        border-left: 4px solid #11998e;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(238, 9, 121, 0.1) 0%, rgba(255, 106, 0, 0.1) 100%);
        border-left: 4px solid #ee0979;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%);
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 0.75rem;
    }
    
    /* Risk Assessment Expander Styling */
    /* Target expanders within risk assessment section */
    div[data-testid="stExpander"] {
        margin-bottom: 0.5rem;
    }
    
    /* Low Risk Expander - Green background */
    div[data-testid="stExpander"]:has(+ div .risk-badge.risk-low),
    div:has(.risk-badge.risk-low) ~ div[data-testid="stExpander"] {
        background-color: #d4edda !important;
    }
    
    div:has(.risk-badge.risk-low) ~ div[data-testid="stExpander"] .streamlit-expanderHeader {
        background-color: #d4edda !important;
        border: 1px solid #11998e !important;
        color: #155724 !important;
        border-radius: 8px !important;
    }
    
    div:has(.risk-badge.risk-low) ~ div[data-testid="stExpander"] .streamlit-expanderHeader:hover {
        background-color: #c3e6cb !important;
    }
    
    /* Moderate Risk Expander - Yellow background */
    div:has(.risk-badge.risk-moderate) ~ div[data-testid="stExpander"] .streamlit-expanderHeader {
        background-color: #fff3cd !important;
        border: 1px solid #ffc107 !important;
        color: #856404 !important;
        border-radius: 8px !important;
    }
    
    div:has(.risk-badge.risk-moderate) ~ div[data-testid="stExpander"] .streamlit-expanderHeader:hover {
        background-color: #ffeaa7 !important;
    }
    
    /* High Risk Expander - Red background */
    div:has(.risk-badge.risk-high) ~ div[data-testid="stExpander"] .streamlit-expanderHeader {
        background-color: #f8d7da !important;
        border: 1px solid #ee0979 !important;
        color: #721c24 !important;
        border-radius: 8px !important;
    }
    
    div:has(.risk-badge.risk-high) ~ div[data-testid="stExpander"] .streamlit-expanderHeader:hover {
        background-color: #f5c6cb !important;
    }
    
    /* Alternative approach: Use data attributes if available */
    .risk-expander-low .streamlit-expanderHeader,
    [data-risk-level="low"] .streamlit-expanderHeader {
        background-color: #d4edda !important;
        border: 1px solid #11998e !important;
        color: #155724 !important;
        border-radius: 8px !important;
    }
    
    .risk-expander-low .streamlit-expanderHeader:hover,
    [data-risk-level="low"] .streamlit-expanderHeader:hover {
        background-color: #c3e6cb !important;
    }
    
    .risk-expander-moderate .streamlit-expanderHeader,
    [data-risk-level="moderate"] .streamlit-expanderHeader {
        background-color: #fff3cd !important;
        border: 1px solid #ffc107 !important;
        color: #856404 !important;
        border-radius: 8px !important;
    }
    
    .risk-expander-moderate .streamlit-expanderHeader:hover,
    [data-risk-level="moderate"] .streamlit-expanderHeader:hover {
        background-color: #ffeaa7 !important;
    }
    
    .risk-expander-high .streamlit-expanderHeader,
    [data-risk-level="high"] .streamlit-expanderHeader {
        background-color: #f8d7da !important;
        border: 1px solid #ee0979 !important;
        color: #721c24 !important;
        border-radius: 8px !important;
    }
    
    .risk-expander-high .streamlit-expanderHeader:hover,
    [data-risk-level="high"] .streamlit-expanderHeader:hover {
        background-color: #f5c6cb !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    /* Custom Skeleton Loading */
    .skeleton-card {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s ease-in-out infinite;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Radio Buttons */
    .stRadio > div {
        display: flex;
        gap: 1rem;
    }
    
    .stRadio > div > label {
        font-family: 'Inter', sans-serif;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        background-color: #f8f9fa;
        border: 2px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .stRadio > div > label:hover {
        border-color: #667eea;
        background-color: rgba(102, 126, 234, 0.05);
    }
    
    /* Selectbox */
    .stSelectbox label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: var(--text-primary);
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
        margin: 2rem 0;
    }
    
    /* Code Blocks */
    .stCode {
        border-radius: 12px;
        border: 1px solid var(--border-color);
    }
    
    /* AI Recommendations Styling */
    .ai-recommendations {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        padding: 2.5rem;
        border-radius: 20px;
        border-left: 5px solid #667eea;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        margin: 2rem 0;
        font-family: 'Inter', sans-serif;
        line-height: 1.8;
        color: #1a1a2e;
    }
    
    .ai-recommendations h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
        padding-bottom: 1rem;
    }
    
    .ai-recommendations h2 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.5rem;
        color: #667eea;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-left: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .ai-recommendations h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.25rem;
        color: #764ba2;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    .ai-recommendations ul, .ai-recommendations ol {
        margin: 1rem 0;
        padding-left: 2rem;
    }
    
    .ai-recommendations li {
        margin: 0.75rem 0;
        padding-left: 0.5rem;
        position: relative;
    }
    
    .ai-recommendations li::marker {
        color: #667eea;
        font-weight: 600;
    }
    
    .ai-recommendations strong {
        color: #667eea;
        font-weight: 600;
    }
    
    .ai-recommendations p {
        margin: 1rem 0;
        color: #4a5568;
    }
    
    .stock-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .stock-card h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.75rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid rgba(102, 126, 234, 0.2);
        letter-spacing: -0.01em;
    }
    
    .stock-name {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
        margin: 0.5rem 0;
        letter-spacing: -0.01em;
    }
    
    .recommendation-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        margin: 0.25rem;
    }
    
    .badge-buy {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .badge-hold {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
    }
    
    .badge-sell {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .risk-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 12px;
        font-weight: 500;
        font-size: 0.8rem;
        margin: 0.25rem;
    }
    
    .risk-high {
        background: rgba(238, 9, 121, 0.1);
        color: #ee0979;
        border: 1px solid rgba(238, 9, 121, 0.3);
    }
    
    .risk-moderate {
        background: rgba(255, 193, 7, 0.1);
        color: #ffc107;
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    
    .risk-low {
        background: rgba(17, 153, 142, 0.1);
        color: #11998e;
        border: 1px solid rgba(17, 153, 142, 0.3);
    }
    
    /* Risk Assessment Button Styling - Use CSS :has() selector to target buttons after risk badges */
    /* Low Risk buttons - teal color */
    div:has(.risk-badge.risk-low) ~ div button[data-testid="baseButton-secondary"]:nth-of-type(n+1):nth-of-type(-n+10) {
        background-color: #11998e !important;
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        border: none !important;
    }
    
    /* Moderate Risk buttons - yellow color */
    div:has(.risk-badge.risk-moderate) ~ div button[data-testid="baseButton-secondary"]:nth-of-type(n+1):nth-of-type(-n+15) {
        background-color: #ffc107 !important;
        color: #856404 !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        border: none !important;
    }
    
    /* High Risk buttons - pink color */
    div:has(.risk-badge.risk-high) ~ div button[data-testid="baseButton-secondary"]:nth-of-type(n+1):nth-of-type(-n+10) {
        background-color: #ee0979 !important;
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        border: none !important;
    }
    
    .portfolio-suggestion {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-highlight {
        display: inline-block;
        background: rgba(102, 126, 234, 0.1);
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
        font-weight: 600;
        color: #667eea;
        margin: 0.25rem;
    }
    
    .kpi-metric {
        display: inline-block;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        padding: 0.4rem 1rem;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        color: #667eea;
        margin: 0.3rem 0.5rem;
        border: 2px solid rgba(102, 126, 234, 0.2);
        font-family: 'Inter', sans-serif;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.1);
    }
    
    .kpi-label {
        font-weight: 600;
        color: #764ba2;
        margin-right: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .kpi-value {
        font-weight: 700;
        color: #667eea;
        font-family: 'Inter', sans-serif;
    }
    
    /* Stock Analysis Table */
    .stock-analysis-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 2rem 0;
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    .stock-analysis-table thead {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stock-analysis-table th {
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .stock-analysis-table th:first-child {
        border-top-left-radius: 16px;
    }
    
    .stock-analysis-table th:last-child {
        border-top-right-radius: 16px;
    }
    
    .stock-analysis-table tbody tr {
        border-bottom: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.2s ease;
    }
    
    .stock-analysis-table tbody tr:hover {
        background: rgba(102, 126, 234, 0.05);
        transform: scale(1.01);
    }
    
    .stock-analysis-table tbody tr:last-child {
        border-bottom: none;
    }
    
    .stock-analysis-table td {
        padding: 1rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        color: #1a1a2e;
    }
    
    .stock-analysis-table .ticker-cell {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stock-analysis-table .kpi-cell {
        font-weight: 600;
        color: #667eea;
    }
    
    .stock-analysis-table .status-badge {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-oversold {
        background: rgba(17, 153, 142, 0.15);
        color: #11998e;
    }
    
    .status-overbought {
        background: rgba(238, 9, 121, 0.15);
        color: #ee0979;
    }
    
    .status-neutral {
        background: rgba(102, 126, 234, 0.15);
        color: #667eea;
    }
    
    .status-bullish {
        background: rgba(17, 153, 142, 0.15);
        color: #11998e;
    }
    
    .status-bearish {
        background: rgba(238, 9, 121, 0.15);
        color: #ee0979;
    }
    
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'llm' not in st.session_state:
    st.session_state.llm = None
if 'tickers' not in st.session_state:
    st.session_state.tickers = []
if 'kpi_data' not in st.session_state:
    st.session_state.kpi_data = {}
if 'kpi_tickers' not in st.session_state:
    st.session_state.kpi_tickers = ""

# ==================== CACHED HELPER FUNCTIONS ====================
@st.cache_data(ttl=1800, show_spinner=False)  # Cache for 30 minutes - AI recommendations are expensive
def generate_ai_recommendations_cached(kpi_data_str, kpi_data_dict, llm, regenerate_counter=0):
    """
    Generate AI recommendations with caching.
    Cached based on KPI data hash to avoid regenerating for same data.
    
    Parameters:
    kpi_data_str (str): String representation of KPI data for hash comparison.
    kpi_data_dict (dict): The actual KPI data dictionary.
    llm: The LLM instance (not used in cache key, but needed for API call).
    
    Returns:
    str: AI-generated recommendations.
    """
    prompt = f"""
    Based on the following KPI data for these stocks: {kpi_data_dict}
    
    Provide a comprehensive executive summary with:
    1. Overall Market Assessment
       This section should provide a comprehensive analysis of the overall market conditions by synthesizing the technical indicators (RSI, MACD, P/E ratios) into a cohesive market assessment. The analysis should:
       - Incorporate RSI data to assess whether stocks are generally overbought, oversold, or in neutral territory, and what this suggests about overall market momentum
       - Incorporate MACD data to evaluate overall market momentum trends (bullish vs bearish signals across the portfolio)
       - Incorporate P/E ratio data to assess overall market valuations and whether stocks appear overvalued, fairly valued, or undervalued on aggregate
       - Synthesize these technical indicators to provide insights about overall market sentiment, momentum, and valuation levels
       - Provide a cohesive market assessment that integrates these technical insights rather than listing them separately
       - Use the technical data to inform conclusions about market conditions, investor sentiment, and investment climate
       - Example format: "Based on the technical indicators, the market shows [specific RSI insights - e.g., 'several stocks approaching overbought conditions'] suggesting [market momentum assessment]. MACD analysis reveals [specific MACD trends - e.g., 'mixed signals with some stocks showing bullish momentum'] indicating [momentum interpretation]. P/E ratios across the portfolio [specific P/E observations - e.g., 'range from moderate to high'] reflect [valuation assessment]. Overall, these indicators suggest [integrated market assessment]."
    2. Stock-by-stock analysis
    3. Buy/Hold/Sell Recommendations (Tier List)
       Create a tier list categorizing each stock ticker into BUY, HOLD, or SELL based on the KPI data.
       IMPORTANT: This section MUST be formatted EXACTLY as follows (one line per category):
       
       Buy: TICKER1, TICKER2, TICKER3
       Hold: TICKER1, TICKER2, TICKER3, TICKER4
       Sell: None
       
       Rules:
       - Use ONLY ticker symbols from the KPI data provided (e.g., AAPL, MSFT, TSLA, NVDA)
       - Separate tickers with commas and a space
       - Do NOT include brackets [ ] around the tickers
       - Do NOT include explanations or additional text
       - If a category has no recommendations, write "None" for that category
       - Each category must be on its own line starting with "Buy:", "Hold:", or "Sell:"
       - Example format:
         Buy: META, TSLA
         Hold: AAPL, AMZN, GOOGL, MSFT, NVDA, SPY
         Sell: None
    4. Risk Assessment (Tier List)
       Create a tier list categorizing each stock ticker into HIGH RISK, MODERATE RISK, or LOW RISK based on the KPI data.
       IMPORTANT: This section MUST be formatted EXACTLY as follows:
       
       First, provide the tier list (one line per category):
       High Risk: TICKER1, TICKER2, TICKER3
       Moderate Risk: TICKER1, TICKER2, TICKER3, TICKER4
       Low Risk: TICKER1, TICKER2
       
       Then, provide detailed risk assessment for each ticker (one line per ticker):
       TICKER1: Brief risk description with specific reasons (e.g., "AAPL: Moderate risk due to high P/E ratio and bearish momentum.")
       TICKER2: Brief risk description with specific reasons
       TICKER3: Brief risk description with specific reasons
       
       Rules:
       - Use ONLY ticker symbols from the KPI data provided (e.g., AAPL, MSFT, TSLA, NVDA)
       - Separate tickers with commas and a space in the tier list
       - Do NOT include brackets [ ] around the tickers
       - For detailed risk descriptions, use format: "TICKER: Description"
       - Include specific reasons (P/E ratio, momentum, volatility, etc.)
       - If a category has no recommendations, write "None" for that category
       - Each category must be on its own line starting with "High Risk:", "Moderate Risk:", or "Low Risk:"
       - Example format:
         High Risk: NVDA, TSLA
         Moderate Risk: AAPL, AMZN, GOOGL, META, MSFT
         Low Risk: SPY
         
         AAPL: Moderate risk due to high P/E ratio and bearish momentum.
         AMZN: Moderate risk with bearish momentum and moderate P/E ratio.
         GOOGL: Moderate risk with bearish momentum and moderate P/E ratio.
         META: Moderate risk with bullish momentum and reasonable P/E ratio.
         MSFT: Moderate risk with bearish momentum and high P/E ratio.
         NVDA: High risk due to high P/E ratio and bearish momentum.
         SPY: Low to moderate risk as a diversified index fund.
         TSLA: High risk due to high P/E ratio and overbought conditions.
    5. Portfolio allocation suggestions
       For section 4 (Portfolio Allocation Suggestions), you MUST provide THREE portfolio types with specific percentage allocations:
       
       **Conservative Portfolio:**
       - List each ticker with its percentage allocation (e.g., "50% SPY, 20% AAPL, 10% MSFT, 10% GOOGL, 10% NVDA")
       - OR use bullet points format:
         * 50% SPY
         * 20% AAPL
         * 10% MSFT
         * 10% GOOGL
         * 10% NVDA
       
       **Balanced Portfolio:**
       - List each ticker with its percentage allocation (e.g., "30% SPY, 20% AAPL, 15% AMZN, 15% MSFT, 10% GOOGL, 10% NVDA")
       - OR use bullet points format:
         * 30% SPY
         * 20% AAPL
         * 15% AMZN
         * 15% MSFT
         * 10% GOOGL
         * 10% NVDA
       
       **Aggressive Portfolio:**
       - List each ticker with its percentage allocation (e.g., "20% SPY, 20% AAPL, 15% TSLA, 15% NVDA, 10% AMZN, 10% META, 10% GOOGL")
       - OR use bullet points format:
         * 20% SPY
         * 20% AAPL
         * 15% TSLA
         * 15% NVDA
         * 10% AMZN
         * 10% NVDA
         * 10% META
       
       IMPORTANT: The percentages must add up to 100% for each portfolio type. Use only the tickers from the KPI data provided.
       
       Format your response in a clear, structured manner with sections and bullet points.
       """
    
    return get_llm_response(llm, prompt)


def get_ticker_info(ticker, info_key='longName'):
    """
    Get ticker info with caching to reduce API calls.
    Uses centralized cached function from data_cache module.
    
    Parameters:
    ticker (str): Stock ticker symbol.
    info_key (str): The info key to retrieve (e.g., 'longName', 'shortName', 'trailingEps', 'beta').
    
    Returns:
    The requested info value or None if not available.
    """
    try:
        # Use centralized cached function
        if info_key == 'longName':
            # Try longName first, fallback to shortName
            result = get_ticker_info_cached(ticker, 'longName')
            if result:
                return result
            return get_ticker_info_cached(ticker, 'shortName')
        return get_ticker_info_cached(ticker, info_key)
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def download_ticker_data(ticker, start_date, end_date):
    """
    Download ticker data with caching to reduce API calls.
    Uses centralized data cache to avoid redundant downloads.
    
    Parameters:
    ticker (str): Stock ticker symbol.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    
    Returns:
    pd.DataFrame: Historical stock data.
    """
    try:
        # Use centralized cached function instead of direct yf.download
        data = get_ticker_history(ticker, start_date, end_date)
        return data
    except Exception:
        return pd.DataFrame()


def _preload_ticker_data(tickers, start_date, end_date):
    """
    Pre-load ticker data in background to populate cache using parallel processing.
    This ensures data is ready when user navigates to other tabs.
    
    Uses get_multiple_tickers_history_cached() for efficient batch downloading,
    which is much faster than downloading each ticker separately.
    
    Parameters:
    tickers (list): List of ticker symbols to preload.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    """
    if not tickers:
        return
    
    # Calculate date range if not provided
    if not start_date or not end_date:
        from utils.date_utils import calculate_date_range
        years = st.session_state.get('years', DEFAULT_YEARS)
        start_date, end_date = calculate_date_range(years)
    
    try:
        # Use get_multiple_tickers_history_cached() - it already does parallel downloads!
        # This is MUCH faster than downloading each ticker separately (batch download)
        from utils.data_cache import get_multiple_tickers_history_cached
        get_multiple_tickers_history_cached(tickers, start_date, end_date)
        
        # Pre-load ticker info in parallel (company names, etc.)
        # This is separate from history download and can run in parallel
        max_workers = min(10, len(tickers))  # Increased from 5 to 10 for better performance
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(get_ticker_info_cached, ticker, 'longName'): ticker 
                for ticker in tickers
            }
            # Wait for all to complete (we don't need the results, just populate cache)
            for future in as_completed(future_to_ticker):
                try:
                    future.result()  # Just wait for completion to populate cache
                except Exception:
                    pass  # Silently continue on errors - individual failures shouldn't block others
    except Exception as e:
        # Log error but don't fail completely - some tickers might still work
        print(f"Warning: Error in preload: {str(e)}")
    
    # KPIs will be calculated when user visits the KPIs tab
    # This makes preload much faster - we only load the raw data here
    # KPIs calculation is deferred to when the user actually needs them

# Auto-initialize LLM if API key is available
# Check Streamlit Secrets first (for Streamlit Cloud), then fallback to config
_api_key = None
try:
    # Try Streamlit Secrets (for Streamlit Cloud deployment)
    if hasattr(st, 'secrets') and hasattr(st.secrets, 'get'):
        _api_key = st.secrets.get("OPENAI_API_KEY", None)
except Exception:
    pass

# Fallback to config OPENAI_API_KEY (from environment variable)
if not _api_key:
    _api_key = OPENAI_API_KEY

if _api_key and st.session_state.llm is None:
    try:
        st.session_state.llm = initialize_llm(_api_key)
    except Exception:
        # Silently fail - will show error if user tries to use LLM features
        pass

def main():
    # #region agent log
    _log_write({"id": "log_main_entry", "timestamp": int(time.time() * 1000), "location": "app/main.py:694", "message": "Main function entered", "data": {"hypothesisId": "E"}, "sessionId": "debug-session", "runId": "run1"})
    # #endregion
    
    # Initialize home page state early
    if 'show_home' not in st.session_state:
        st.session_state.show_home = True
    
    # Only show header when not on home page
    if not st.session_state.show_home:
        st.markdown('<h1 class="main-header">GENESIS ALPH<span style="color: #7c3aed;">A</span></h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Advanced Portfolio Optimization & AI-Powered Stock Analysis</p>', unsafe_allow_html=True)
        st.markdown("---")
    
    # Auto-load API key from config (reads from env, .env, or api_key.txt)
    from config.settings import OPENAI_API_KEY as CONFIG_API_KEY
    api_key = CONFIG_API_KEY if CONFIG_API_KEY else ""
    # #region agent log
    _log_write({"id": "log_api_key_loaded", "timestamp": int(time.time() * 1000), "location": "app/main.py:717", "message": "API key loaded from config", "data": {"hasKey": bool(api_key), "keyLength": len(api_key) if api_key else 0, "hypothesisId": "B"}, "sessionId": "debug-session", "runId": "run1"})
    # #endregion
    
    # Fallback: Try to load directly from api_key.txt if not found in config
    if not api_key:
        try:
            api_key_file = Path(__file__).parent.parent / "api_key.txt"
            if api_key_file.exists():
                with open(api_key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
        except Exception:
            pass
        
        # Initialize LLM silently in the background if API key is available
        if api_key and st.session_state.llm is None:
            try:
                st.session_state.llm = initialize_llm(api_key)
            except Exception:
                pass
    
    # ==================== HOME PAGE ====================
    if st.session_state.show_home:
        # Load background video as base64 (cached)
        @st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
        def load_video_base64(video_path_str):
            """Load video file and encode as base64 with caching."""
            import base64
            try:
                video_path = Path(video_path_str)
                if video_path.exists():
                    with open(video_path, "rb") as video_file:
                        video_base64 = base64.b64encode(video_file.read()).decode()
                    return f"data:video/mp4;base64,{video_base64}"
            except Exception:
                pass
            return None
        
        video_path = Path(__file__).parent.parent / "assets" / "home_page_video.mp4"
        video_data_url = load_video_base64(str(video_path))
        
        
        # Use components.html for full HTML rendering
        home_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                
                body {{
                    font-family: 'Inter', sans-serif;
                    overflow: hidden;
                    margin: 0;
                    padding: 0;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}
                
                .home-container {{
                    position: relative;
                    width: 100vw;
                    height: 100vh;
                    overflow: hidden;
                    min-height: 500px;
                }}
                
                /* Background - gradient base */
                .bg-gradient {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(135deg, #1a1a2e 0%, #2d2d44 50%, #1a1a2e 100%);
                    z-index: 0;
                }}
                
                /* Full-width background video */
                .bg-video {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    z-index: 1;
                    opacity: 0.8;
                    animation: pulseGlowMove 12s ease-in-out infinite;
                }}
                
                /* Fallback background image (if video not available) */
                .bg-image {{
                    position: absolute;
                    top: -2%;
                    left: -2%;
                    width: 104%;
                    height: 104%;
                    background: linear-gradient(-45deg, #667eea, #764ba2, #1a1a2e, #667eea);
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    z-index: 1;
                    opacity: 0.6;
                    animation: pulseGlowMove 12s ease-in-out infinite;
                }}
                
                @keyframes pulseGlowMove {{
                    0%, 100% {{
                        filter: brightness(1) saturate(1);
                        opacity: 0.8;
                    }}
                    25% {{
                        filter: brightness(1.1) saturate(1.05);
                        opacity: 0.85;
                    }}
                    50% {{
                        filter: brightness(1.15) saturate(1.08);
                        opacity: 0.9;
                    }}
                    75% {{
                        filter: brightness(1.1) saturate(1.05);
                        opacity: 0.85;
                    }}
                }}
                
                /* Subtle overlay */
                .overlay {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: radial-gradient(
                        circle at center,
                        transparent 0%,
                        rgba(26, 26, 46, 0.3) 50%,
                        rgba(26, 26, 46, 0.7) 100%
                    );
                    z-index: 2;
                }}
                
                /* Floating orbs for depth effect */
                .orb {{
                    position: absolute;
                    border-radius: 50%;
                    filter: blur(80px);
                    opacity: 0.4;
                    animation: float 20s ease-in-out infinite;
                    z-index: 2;
                }}
                
                .orb-1 {{
                    width: 400px;
                    height: 400px;
                    background: rgba(102, 126, 234, 0.5);
                    top: -100px;
                    left: -100px;
                }}
                
                .orb-2 {{
                    width: 300px;
                    height: 300px;
                    background: rgba(118, 75, 162, 0.5);
                    bottom: -50px;
                    right: -50px;
                    animation-delay: -7s;
                }}
                
                @keyframes float {{
                    0%, 100% {{ transform: translate(0, 0) scale(1); }}
                    25% {{ transform: translate(30px, -30px) scale(1.05); }}
                    50% {{ transform: translate(-20px, 20px) scale(0.95); }}
                    75% {{ transform: translate(20px, 30px) scale(1.02); }}
                }}
                
                /* Content */
                .content {{
                    position: relative;
                    z-index: 10;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    text-align: center;
                    padding: 2rem;
                }}
                
                .title {{
                    font-family: 'Space Grotesk', sans-serif;
                    font-size: 4.5rem;
                    font-weight: 700;
                    color: #ffffff;
                    margin-bottom: 1rem;
                    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                    white-space: nowrap;
                    border-right: 4px solid #ffffff;
                    width: 0;
                    animation: typing 2.5s steps(13, end) forwards, blink-caret 0.75s step-end infinite;
                    animation-delay: 0.5s;
                }}
                
                .purple-letter {{
                    color: #7c3aed;
                }}
                
                @keyframes typing {{
                    from {{ width: 0; }}
                    to {{ width: 13ch; }}
                }}
                
                @keyframes blink-caret {{
                    from, to {{ border-color: transparent; }}
                    50% {{ border-color: #ffffff; }}
                }}
                
                .subtitle {{
                    font-size: 1.4rem;
                    color: rgba(255, 255, 255, 0.95);
                    max-width: 700px;
                    line-height: 1.8;
                    margin-bottom: 2.5rem;
                    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
                    animation: slideUp 1s ease-out 0.2s both;
                }}
                
                @keyframes slideUp {{
                    from {{ opacity: 0; transform: translateY(40px); }}
                    to {{ opacity: 1; transform: translateY(0); }}
                }}
                
                /* Mobile Responsive Styles */
                @media screen and (max-width: 768px) {{
                    .title {{
                        font-size: 2.5rem !important;
                        padding: 0 1rem;
                        animation: typing 2s steps(13, end) forwards, blink-caret 0.75s step-end infinite;
                    }}
                    
                    .subtitle {{
                        font-size: 1rem !important;
                        padding: 0 1.5rem;
                        line-height: 1.6;
                        margin-bottom: 2rem;
                    }}
                    
                    .content {{
                        padding: 1rem;
                        height: 100vh;
                        justify-content: center;
                    }}
                    
                    .home-container {{
                        height: 100vh;
                        min-height: 600px;
                    }}
                    
                    .orb-1 {{
                        width: 250px;
                        height: 250px;
                        top: -50px;
                        left: -50px;
                    }}
                    
                    .orb-2 {{
                        width: 200px;
                        height: 200px;
                        bottom: -30px;
                        right: -30px;
                    }}
                    
                    .bg-video {{
                        opacity: 0.7;
                    }}
                    
                    .bg-image {{
                        opacity: 0.5;
                    }}
                }}
                
                @media screen and (max-width: 480px) {{
                    .title {{
                        font-size: 2rem !important;
                        padding: 0 0.5rem;
                        line-height: 1.2;
                    }}
                    
                    .subtitle {{
                        font-size: 0.9rem !important;
                        padding: 0 1rem;
                        line-height: 1.5;
                        margin-bottom: 1.5rem;
                    }}
                    
                    .content {{
                        padding: 0.5rem;
                    }}
                    
                    .orb-1 {{
                        width: 200px;
                        height: 200px;
                    }}
                    
                    .orb-2 {{
                        width: 150px;
                        height: 150px;
                    }}
                }}
                
                /* Tablet Styles */
                @media screen and (min-width: 769px) and (max-width: 1024px) {{
                    .title {{
                        font-size: 3.5rem;
                    }}
                    
                    .subtitle {{
                        font-size: 1.2rem;
                        max-width: 600px;
                    }}
                }}
                
                /* Touch-friendly adjustments */
                @media (hover: none) and (pointer: coarse) {{
                    .content {{
                        padding: 2rem 1rem;
                    }}
                    
                    .title {{
                        font-size: clamp(2rem, 8vw, 4.5rem);
                    }}
                    
                    .subtitle {{
                        font-size: clamp(0.9rem, 3vw, 1.4rem);
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="home-container">
                <div class="bg-gradient"></div>
                {f"<video class='bg-video' autoplay loop muted playsinline preload='auto'><source src='{video_data_url}' type='video/mp4'></video>" if video_data_url else "<div class='bg-image'></div>"}
                <div class="overlay"></div>
                <div class="orb orb-1"></div>
                <div class="orb orb-2"></div>
                
                <div class="content">
                    <h1 class="title">GENESIS ALPH<span class="purple-letter">A</span></h1>
                    <p class="subtitle">
                        Harness the power of Artificial Intelligence for smarter investment decisions.
                        Analyze stocks, optimize portfolios, and get AI-powered recommendations.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Render the home page using components.html (responsive height)
        # Use viewport height for better mobile support
        components.html(home_html, height=600, scrolling=False)
        
        # Styled "CLICK ME TO ENTER" button - white background, purple text, cool font
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;600;700&display=swap');
            
            .click-enter-btn {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: -50px;
                position: relative;
                z-index: 100;
            }
            .click-enter-btn button {
                background: #ffffff !important;
                border: none !important;
                border-radius: 16px !important;
                padding: 1.3rem 3.5rem !important;
                font-family: 'Orbitron', sans-serif !important;
                font-size: 1.15rem !important;
                font-weight: 600 !important;
                color: #7c3aed !important;
                letter-spacing: 4px !important;
                text-transform: uppercase !important;
                transition: all 0.3s ease !important;
                cursor: pointer !important;
                box-shadow: 0 10px 35px rgba(0, 0, 0, 0.15) !important;
                min-height: 48px !important; /* Touch-friendly minimum size */
            }
            .click-enter-btn button:hover {
                background: #f5f3ff !important;
                transform: translateY(-3px) scale(1.02) !important;
                box-shadow: 0 15px 45px rgba(124, 58, 237, 0.3) !important;
            }
            .click-enter-btn button:active {
                transform: translateY(-1px) scale(0.98) !important;
            }
            .arrows-above {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 25px;
            }
            .arrows-above span {
                display: block;
                width: 12px;
                height: 12px;
                border-bottom: 3px solid #7c3aed;
                border-right: 3px solid #7c3aed;
                transform: rotate(45deg);
                margin: -4px;
                opacity: 0.8;
            }
            
            /* Mobile Responsive Button Styles */
            @media screen and (max-width: 768px) {
                .click-enter-btn {
                    margin-top: -30px;
                }
                .click-enter-btn button {
                    padding: 1rem 2rem !important;
                    font-size: 0.9rem !important;
                    letter-spacing: 2px !important;
                    min-height: 50px !important;
                    width: 90% !important;
                    max-width: 300px;
                }
                .arrows-above {
                    margin-bottom: 15px;
                }
                .arrows-above span {
                    width: 10px;
                    height: 10px;
                    border-bottom-width: 2px;
                    border-right-width: 2px;
                }
            }
            
            @media screen and (max-width: 480px) {
                .click-enter-btn {
                    margin-top: -20px;
                }
                .click-enter-btn button {
                    padding: 0.9rem 1.5rem !important;
                    font-size: 0.8rem !important;
                    letter-spacing: 1.5px !important;
                    min-height: 48px !important;
                    width: 85% !important;
                }
                .arrows-above {
                    margin-bottom: 10px;
                }
            }
            
            /* Touch device optimizations */
            @media (hover: none) and (pointer: coarse) {
                .click-enter-btn button {
                    padding: 1.1rem 2.5rem !important;
                    min-height: 52px !important;
                    font-size: clamp(0.75rem, 3vw, 1.15rem) !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="click-enter-btn">', unsafe_allow_html=True)
            st.markdown('''
                <div class="arrows-above">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            ''', unsafe_allow_html=True)
            if st.button("CLICK ME TO ENTER", key="get_started_btn", use_container_width=True):
                st.session_state.show_home = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Stop here - don't render the rest of the app
        return
    
    # ==================== MAIN APP ====================
    # Show info message at top if no tickers selected
    if not st.session_state.tickers or len(st.session_state.tickers) == 0:
        st.info("💡 Go to the '🎯 Select Assets' tab, choose your stocks, and click '🚀 Extract Tickers with GenAI' to begin.")
    
    # Tabs for different sections - Select Assets first, KPIs & Analysis second
    tab0, tab1, tab_ai, tab2, tab3 = st.tabs(
        [
            "🎯 Select Assets",
            "📊 KPIs & Analysis",
            "🤖 AI Recommendations",
            "📈 Technical Indicators",
            "💼 Portfolio Optimization",
        ]
    )
    
    # Add spacing after tabs
    st.markdown("<br>", unsafe_allow_html=True)
    
    with tab0:
        # Initialize selected tickers in session state if not exists
        if 'selected_tickers_temp' not in st.session_state:
            st.session_state.selected_tickers_temp = st.session_state.tickers.copy() if st.session_state.tickers else []
        
        # Initialize years in session state if not exists
        if 'years' not in st.session_state:
            st.session_state.years = DEFAULT_YEARS
        
        st.markdown("""
        <div style='margin: 1rem 0 2rem 0;'>
            <h1 style='font-family: "Inter", sans-serif; font-weight: 600; 
                      color: #1a1a2e; margin-bottom: 0.5rem;'>
                🎯 Select Assets
            </h1>
            <p style='color: #6c757d; font-size: 1rem; margin-bottom: 2rem;'>
                Choose the tickers you want to analyze. Selected tickers will be highlighted.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Years input in Select Assets tab
        col_year1, col_year2 = st.columns([1, 3])
        with col_year1:
            st.markdown("""
            <div style='display: flex; align-items: center; height: 100%;'>
                <label style='font-size: 1.1rem; font-weight: 600; color: #1a1a2e; font-family: "Inter", sans-serif;'>
                    Years of Historical Data:
                </label>
            </div>
            """, unsafe_allow_html=True)
        with col_year2:
            years = st.number_input(
                "",
                min_value=1,
                max_value=10,
                value=st.session_state.years,
                help="Number of years of historical data to analyze",
                label_visibility="collapsed",
                key="years_input_select_assets"
            )
            st.session_state.years = years
        
        st.markdown("---")
        
        # Available tickers list (with company names for GenAI extraction)
        available_tickers = {
            'AAPL': 'Apple Inc.',
            'AMZN': 'Amazon.com, Inc.',
            'GOOGL': 'Alphabet Inc.',
            'META': 'Meta Platforms, Inc.',
            'MSFT': 'Microsoft Corporation',
            'NVDA': 'NVIDIA Corporation',
            'SPY': 'SPDR S&P 500 ETF',
            'TSLA': 'Tesla, Inc.',
            'JPM': 'JPMorgan Chase & Co.',
            'V': 'Visa Inc.',
            'JNJ': 'Johnson & Johnson',
            'WMT': 'Walmart Inc.',
            'MA': 'Mastercard Inc.',
            'PG': 'Procter & Gamble Co.',
            'DIS': 'The Walt Disney Company',
            'NFLX': 'Netflix, Inc.',
            'AMD': 'Advanced Micro Devices, Inc.',
            'INTC': 'Intel Corporation',
            'CSCO': 'Cisco Systems, Inc.',
            'ORCL': 'Oracle Corporation'
        }
        
        # Create mapping from company name to ticker for GenAI
        company_to_ticker = {company: ticker for ticker, company in available_tickers.items()}
        
        # Display tickers in a grid (OUTSIDE the form)
        st.markdown("<h3 style='font-size: 1.2rem; color: #1a1a2e; margin-bottom: 1rem;'>Available Tickers:</h3>", unsafe_allow_html=True)
        
        # Select All / Deselect All buttons styling
        st.markdown("""
        <style>
        /* Style Select All / Deselect All buttons with white background */
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button,
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button,
        button[kind="secondary"],
        div[data-testid="column"] button[data-testid="baseButton-secondary"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            color: #667eea !important;
            border: 2px solid #667eea !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) button:hover,
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) button:hover,
        button[kind="secondary"]:hover,
        div[data-testid="column"] button[data-testid="baseButton-secondary"]:hover {
            background: #f0f0ff !important;
            background-color: #f0f0ff !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Select All / Deselect All buttons
        btn_col1, btn_col2, spacer = st.columns([1, 1, 3])
        with btn_col1:
            if st.button("✅ Select All", key="select_all_btn", use_container_width=True):
                # #region agent log
                import json as json_debug_sel
                log_path_sel = r"c:\Users\ohada\OneDrive\Desktop\Gen AI for Stock Analysis (2)\Gen AI for Stock Analysis\.cursor\debug.log"
                with open(log_path_sel, "a") as f:
                    f.write(json_debug_sel.dumps({"location": "main.py:SELECT_ALL", "message": "Select All clicked", "data": {"hypothesisId": "F", "before_temp": list(st.session_state.selected_tickers_temp), "available_keys": list(available_tickers.keys())}, "timestamp": __import__('time').time(), "sessionId": "debug-session"}) + "\n")
                # #endregion
                st.session_state.selected_tickers_temp = list(available_tickers.keys())
                # Increment input_version to force text input refresh (FIX for sync issue)
                if 'input_version' not in st.session_state:
                    st.session_state.input_version = 0
                st.session_state.input_version += 1
                # #region agent log
                with open(log_path_sel, "a") as f:
                    f.write(json_debug_sel.dumps({"location": "main.py:SELECT_ALL_AFTER", "message": "Select All completed", "data": {"hypothesisId": "F", "after_temp": list(st.session_state.selected_tickers_temp), "input_version": st.session_state.input_version}, "timestamp": __import__('time').time(), "sessionId": "debug-session"}) + "\n")
                # #endregion
                st.rerun()
        with btn_col2:
            if st.button("❌ Deselect All", key="deselect_all_btn", use_container_width=True):
                st.session_state.selected_tickers_temp = []
                # Increment input_version to force text input refresh (FIX for sync issue)
                if 'input_version' not in st.session_state:
                    st.session_state.input_version = 0
                st.session_state.input_version += 1
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        cols_per_row = 4
        ticker_list = list(available_tickers.items())

        # Render ticker cards with SELECT button
        selected_tickers = list(st.session_state.selected_tickers_temp)
        
        # Ticker cards grid
        for i in range(0, len(ticker_list), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(ticker_list):
                    ticker, company = ticker_list[i + j]
                    with col:
                        is_selected = ticker in st.session_state.selected_tickers_temp
                        
                        # Card styling based on selection
                        if is_selected:
                            card_bg = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                            card_border = "#667eea"
                            card_shadow = "0 8px 24px rgba(102, 126, 234, 0.4)"
                            text_color = "#ffffff"
                            btn_text = "✓ Selected"
                        else:
                            card_bg = "linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%)"
                            card_border = "rgba(102, 126, 234, 0.2)"
                            card_shadow = "0 2px 8px rgba(0, 0, 0, 0.05)"
                            text_color = "#667eea"
                            btn_text = "Select"
                        
                        # Render card as HTML
                        st.markdown(f"""
                        <div style="
                            background: {card_bg};
                            border: 2px solid {card_border};
                            border-radius: 18px;
                            padding: 1.5rem;
                            min-height: 120px;
                            box-shadow: {card_shadow};
                            transition: all 0.3s ease;
                            text-align: center;
                            margin-bottom: 0.5rem;
                        ">
                            <div style="font-size: 1.2rem; font-weight: 700; color: {text_color}; margin-bottom: 0.5rem;">
                                {ticker}
                            </div>
                            <div style="font-size: 0.85rem; color: {text_color}; opacity: 0.9;">
                                {company}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # SELECT button
                        if st.button(btn_text, key=f"select_{ticker}", use_container_width=True, type="primary" if is_selected else "secondary"):
                            if ticker in st.session_state.selected_tickers_temp:
                                st.session_state.selected_tickers_temp.remove(ticker)
                            else:
                                st.session_state.selected_tickers_temp.append(ticker)
                            # Increment version to refresh the text input
                            if 'input_version' not in st.session_state:
                                st.session_state.input_version = 0
                            st.session_state.input_version += 1
                            st.rerun()
        
        # Update selected_tickers from session state
        selected_tickers = list(st.session_state.selected_tickers_temp)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---", unsafe_allow_html=True)
        
        # Manual ticker input option (synced with card selection - bidirectional sync)
        st.markdown("""
        <h3 style='font-size: 1.2rem; color: #1a1a2e; margin: 1rem 0 1rem 0; font-weight: 600;'>
            Or Enter Tickers Manually
        </h3>
        """, unsafe_allow_html=True)
        
        # Track input version to force refresh when cards change
        if 'input_version' not in st.session_state:
            st.session_state.input_version = 0
        
        # Callback function to sync input to cards
        def sync_input_to_cards():
            input_key = f"manual_tickers_input_v{st.session_state.input_version}"
            if input_key in st.session_state:
                typed_value = st.session_state[input_key]
                if typed_value:
                    typed_tickers = [t.strip().upper() for t in typed_value.split(",") if t.strip()]
                    st.session_state.selected_tickers_temp = typed_tickers
                else:
                    st.session_state.selected_tickers_temp = []
                st.session_state.input_version += 1  # Force input refresh on next rerun
        
        # Calculate expected value from card selection
        expected_from_cards = ",".join(sorted(st.session_state.selected_tickers_temp)) if st.session_state.selected_tickers_temp else ""
        
        # Text input with on_change callback for automatic sync
        manual_tickers = st.text_input(
            "Enter tickers (comma-separated)",
            value=expected_from_cards,
            help="Example: AAPL,MSFT,GOOGL - Changes sync automatically with cards",
            key=f"manual_tickers_input_v{st.session_state.input_version}",
            on_change=sync_input_to_cards
        )
        
        # Show info about selection
        if st.session_state.selected_tickers_temp:
            st.info(f"💡 {len(st.session_state.selected_tickers_temp)} ticker(s) selected: {', '.join(sorted(st.session_state.selected_tickers_temp))}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit button (outside form)
        submitted = st.button("🚀 Extract Tickers with GenAI", type="primary", use_container_width=True)
        
        if submitted:
            # #region agent log
            import json as json_debug
            import time as time_module
            log_path = r"c:\Users\ohada\OneDrive\Desktop\Gen AI for Stock Analysis (2)\Gen AI for Stock Analysis\.cursor\debug.log"
            extract_start_time = time_module.time()
            with open(log_path, "a") as f:
                f.write(json_debug.dumps({"location": "main.py:EXTRACT_START", "message": "Extract button clicked - starting", "data": {"hypothesisId": "A,B,C,D", "timestamp": extract_start_time, "has_llm": "llm" in st.session_state and st.session_state.llm is not None}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
            # #endregion
            
            # Show immediate loading indicator
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                with st.spinner("🔄 Initializing..."):
                    pass
            
            # Calculate date range for preloading
            years = st.session_state.get('years', DEFAULT_YEARS)
            start_date, end_date = calculate_date_range(years)
            
            # #region agent log
            with open(log_path, "a") as f:
                f.write(json_debug.dumps({"location": "main.py:EXTRACT_DATE_CALCULATED", "message": "Date range calculated", "data": {"hypothesisId": "A", "start_date": str(start_date), "end_date": str(end_date), "elapsed": time_module.time() - extract_start_time}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
            # #endregion
            # Check if manual tickers were entered
            if manual_tickers and manual_tickers.strip():
                # #region agent log
                with open(log_path, "a") as f:
                    f.write(json_debug.dumps({"location": "main.py:MANUAL_BRANCH", "message": "Using manual tickers branch", "data": {"hypothesisId": "H", "manual_tickers": manual_tickers}, "timestamp": __import__('time').time(), "sessionId": "debug-session"}) + "\n")
                # #endregion
                manual_tickers_list = [t.strip().upper() for t in manual_tickers.split(",") if t.strip()]
                if manual_tickers_list:
                    st.session_state.tickers = manual_tickers_list
                    st.session_state.selected_tickers_temp = manual_tickers_list.copy()
                    
                    # #region agent log
                    preload_start = time_module.time()
                    with open(log_path, "a") as f:
                        f.write(json_debug.dumps({"location": "main.py:PRELOAD_START_MANUAL", "message": "Starting data preload (manual)", "data": {"hypothesisId": "D", "tickers": manual_tickers_list, "num_tickers": len(manual_tickers_list)}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                    # #endregion
                    
                    # Pre-load data in background for all tickers with loading indicator
                    with loading_placeholder.container():
                        with st.spinner(f"📥 Loading data for {len(manual_tickers_list)} ticker(s)... This may take a moment."):
                            _preload_ticker_data(manual_tickers_list, start_date, end_date)
                    
                    # #region agent log
                    with open(log_path, "a") as f:
                        f.write(json_debug.dumps({"location": "main.py:PRELOAD_SUCCESS_MANUAL", "message": "Data preload completed (manual)", "data": {"hypothesisId": "D", "elapsed": time_module.time() - preload_start, "total_elapsed": time_module.time() - extract_start_time}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                    # #endregion
                    
                    loading_placeholder.empty()
                    st.success(f"✅ Successfully loaded {len(manual_tickers_list)} ticker(s) from manual input!")
                    st.rerun()
                else:
                    st.warning("⚠️ Please enter at least one valid ticker.")
            elif selected_tickers:
                # Extract tickers using GenAI from selected company names
                # Get API key - try Streamlit Secrets first, then config
                api_key = None
                try:
                    # Try Streamlit Secrets (for Streamlit Cloud deployment)
                    if hasattr(st, 'secrets') and hasattr(st.secrets, 'get'):
                        api_key = st.secrets.get("OPENAI_API_KEY", None)
                except Exception:
                    pass
                
                # Fallback to config
                if not api_key:
                    from config.settings import OPENAI_API_KEY as CONFIG_API_KEY
                    api_key = CONFIG_API_KEY if CONFIG_API_KEY else ""
                
                # Final fallback: Try to load directly from api_key.txt
                if not api_key:
                    try:
                        api_key_file = Path(__file__).parent.parent / "api_key.txt"
                        if api_key_file.exists():
                            with open(api_key_file, 'r', encoding='utf-8') as f:
                                api_key = f.read().strip()
                    except Exception:
                        pass
                
                if not api_key:
                    loading_placeholder.empty()
                    st.error("⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY in Streamlit Secrets, environment variable, or create api_key.txt file.")
                else:
                    # Initialize LLM if needed
                    if not st.session_state.llm:
                        # #region agent log
                        llm_init_start = time_module.time()
                        with open(log_path, "a") as f:
                            f.write(json_debug.dumps({"location": "main.py:LLM_INIT_START", "message": "Starting LLM initialization", "data": {"hypothesisId": "B", "timestamp": llm_init_start}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                        # #endregion
                        
                        with loading_placeholder.container():
                            with st.spinner("🤖 Initializing AI model... This may take a moment on first use."):
                                try:
                                    st.session_state.llm = initialize_llm(api_key)
                                    # #region agent log
                                    with open(log_path, "a") as f:
                                        f.write(json_debug.dumps({"location": "main.py:LLM_INIT_SUCCESS", "message": "LLM initialized successfully", "data": {"hypothesisId": "B", "elapsed": time_module.time() - llm_init_start}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                                    # #endregion
                                except Exception as e:
                                    loading_placeholder.empty()
                                    # #region agent log
                                    with open(log_path, "a") as f:
                                        f.write(json_debug.dumps({"location": "main.py:LLM_INIT_ERROR", "message": "LLM initialization failed", "data": {"hypothesisId": "B", "error": str(e), "elapsed": time_module.time() - llm_init_start}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                                    # #endregion
                                    st.error(f"⚠️ Failed to initialize AI: {str(e)}")
                                    return
                    
                    # Show loading skeleton for GenAI extraction
                    loading_placeholder.empty()
                    skeleton_placeholder = st.empty()
                    with skeleton_placeholder.container():
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                                    padding: 2rem; border-radius: 16px; margin: 1rem 0;'>
                            <h3 style='font-family: "Inter", sans-serif; font-weight: 600; 
                                       color: #1a1a2e; margin-bottom: 1.5rem; text-align: center;'>
                                🤖 Extracting Tickers with GenAI
                            </h3>
                            <div class='skeleton-card' style='height: 80px; margin-bottom: 1rem;'></div>
                            <div class='skeleton-card' style='height: 80px; margin-bottom: 1rem;'></div>
                            <div class='skeleton-card' style='height: 80px;'></div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    try:
                        # If user already selected tickers, use them directly - no need for LLM call!
                        # This is MUCH faster (saves 2-5 seconds)
                        if selected_tickers:
                            skeleton_placeholder.empty()  # Clear skeleton
                            extracted_tickers = selected_tickers
                            
                            # #region agent log
                            with open(log_path, "a") as f:
                                f.write(json_debug.dumps({"location": "main.py:SKIP_LLM_USE_SELECTED", "message": "Using selected tickers directly (skipping LLM call)", "data": {"hypothesisId": "C", "num_tickers": len(extracted_tickers), "tickers": extracted_tickers}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                            # #endregion
                            
                            if extracted_tickers:
                                st.session_state.tickers = extracted_tickers
                                st.session_state.selected_tickers_temp = extracted_tickers.copy()
                                
                                # #region agent log
                                preload_start = time_module.time()
                                with open(log_path, "a") as f:
                                    f.write(json_debug.dumps({"location": "main.py:PRELOAD_START", "message": "Starting data preload", "data": {"hypothesisId": "D", "tickers": extracted_tickers, "num_tickers": len(extracted_tickers)}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                                # #endregion
                                
                                # Pre-load data in background for all tickers with loading indicator
                                with st.spinner(f"📥 Loading data for {len(extracted_tickers)} ticker(s)... This may take a moment."):
                                    _preload_ticker_data(extracted_tickers, start_date, end_date)
                                
                                # #region agent log
                                with open(log_path, "a") as f:
                                    f.write(json_debug.dumps({"location": "main.py:PRELOAD_SUCCESS", "message": "Data preload completed", "data": {"hypothesisId": "D", "elapsed": time_module.time() - preload_start, "total_elapsed": time_module.time() - extract_start_time}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                                # #endregion
                                
                                st.success(f"✅ Successfully extracted and loaded {len(extracted_tickers)} ticker(s) with GenAI: {', '.join(extracted_tickers)}")
                                st.rerun()
                            else:
                                st.error("⚠️ Could not extract tickers from GenAI response. Using selected tickers directly.")
                                st.session_state.tickers = selected_tickers
                                st.session_state.selected_tickers_temp = selected_tickers.copy()
                                
                                # #region agent log
                                preload_start = time_module.time()
                                with open(log_path, "a") as f:
                                    f.write(json_debug.dumps({"location": "main.py:PRELOAD_START_FALLBACK", "message": "Starting data preload (fallback)", "data": {"hypothesisId": "D", "tickers": selected_tickers, "num_tickers": len(selected_tickers)}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                                # #endregion
                                
                                # Pre-load data in background for all tickers with loading indicator
                                with st.spinner(f"📥 Loading data for {len(selected_tickers)} ticker(s)... This may take a moment."):
                                    _preload_ticker_data(selected_tickers, start_date, end_date)
                                
                                # #region agent log
                                with open(log_path, "a") as f:
                                    f.write(json_debug.dumps({"location": "main.py:PRELOAD_SUCCESS_FALLBACK", "message": "Data preload completed (fallback)", "data": {"hypothesisId": "D", "elapsed": time_module.time() - preload_start, "total_elapsed": time_module.time() - extract_start_time}, "sessionId": "debug-session", "runId": "run1"}) + "\n")
                                # #endregion
                                
                                st.rerun()
                    except Exception as e:
                        skeleton_placeholder.empty()
                        st.error(f"❌ Error extracting tickers: {str(e)}")
            else:
                # #region agent log
                with open(log_path, "a") as f:
                    f.write(json_debug.dumps({"location": "main.py:ELSE_WARNING", "message": "Both manual_tickers and selected_tickers are empty/falsy", "data": {"hypothesisId": "I", "manual_tickers_bool": bool(manual_tickers), "manual_tickers_strip_bool": bool(manual_tickers.strip()) if manual_tickers else False, "selected_tickers_bool": bool(selected_tickers), "selected_tickers_len": len(selected_tickers) if selected_tickers else 0}, "timestamp": __import__('time').time(), "sessionId": "debug-session"}) + "\n")
                # #endregion
                st.warning("⚠️ Please select at least one ticker or enter tickers manually.")
    
    with tab1:
        # Check if tickers are selected
        if not st.session_state.tickers or len(st.session_state.tickers) == 0:
            st.stop()
        
        # Calculate date range (use years from session state)
        years = st.session_state.get('years', DEFAULT_YEARS)
        start_date, end_date = calculate_date_range(years)
        
        # Display tickers (modern stylish design - smaller and uniform)
        st.markdown("""
        <div style='margin-bottom: 1.5rem;'>
            <h2 style='font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                       margin-bottom: 1rem; font-family: "Inter", sans-serif;'>
                📋 Selected Tickers
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                        padding: 1.5rem; border-radius: 16px; border: 2px solid rgba(102, 126, 234, 0.2);
                        box-shadow: 0 6px 18px rgba(102, 126, 234, 0.12); transition: all 0.3s ease;
                        margin-bottom: 1rem; min-height: 140px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div style='font-size: 0.85rem; color: #667eea; margin-bottom: 0.5rem; font-weight: 600;
                            text-transform: uppercase; letter-spacing: 0.05em; font-family: "Inter", sans-serif;'>
                    Number of Tickers
                </div>
                <div style='font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                            font-family: "Inter", sans-serif; line-height: 1;'>
                    {len(st.session_state.tickers)}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                        padding: 1.5rem; border-radius: 16px; border: 2px solid rgba(102, 126, 234, 0.2);
                        box-shadow: 0 6px 18px rgba(102, 126, 234, 0.12); transition: all 0.3s ease;
                        margin-bottom: 1rem; min-height: 140px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div style='font-size: 0.85rem; color: #667eea; margin-bottom: 0.5rem; font-weight: 600;
                            text-transform: uppercase; letter-spacing: 0.05em; font-family: "Inter", sans-serif;'>
                    Start Date
                </div>
                <div style='font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                            font-family: "Inter", sans-serif; line-height: 1;'>
                    {start_date}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                        padding: 1.5rem; border-radius: 16px; border: 2px solid rgba(102, 126, 234, 0.2);
                        box-shadow: 0 6px 18px rgba(102, 126, 234, 0.12); transition: all 0.3s ease;
                        margin-bottom: 1rem; min-height: 140px; display: flex; flex-direction: column; justify-content: space-between;'>
                <div style='font-size: 0.85rem; color: #667eea; margin-bottom: 0.5rem; font-weight: 600;
                            text-transform: uppercase; letter-spacing: 0.05em; font-family: "Inter", sans-serif;'>
                    End Date
                </div>
                <div style='font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
                            font-family: "Inter", sans-serif; line-height: 1;'>
                    {end_date}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div style='margin: 1rem 0 2rem 0;'>
            <h1 style='font-family: "Inter", sans-serif; font-weight: 600; 
                      color: #1a1a2e; margin-bottom: 0.5rem;'>
                📊 Key Performance Indicators
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Add explanation about KPIs
        with st.expander("📚 What are KPIs?"):
            st.markdown("""
            **KPIs (Key Performance Indicators)** are metrics used to evaluate the performance of stocks:
            - **RSI:** Momentum indicator (0-100 scale)
            - **Bollinger Bands:** Volatility bands around price
            - **P/E Ratio:** Price relative to earnings
            - **Beta:** Volatility relative to market
            - **MACD:** Trend-following momentum indicator
            
            These indicators help identify buy/sell opportunities and assess risk.
            """)
        
        # Auto-calculate KPIs when tickers are available
        # This ensures KPIs are ready for all tabs without manual button click
        if st.session_state.tickers:
            # Check if we need to recalculate (tickers changed or no data)
            tickers_str = ",".join(sorted(st.session_state.tickers))
            needs_calculation = (
                'kpi_tickers' not in st.session_state or 
                st.session_state.kpi_tickers != tickers_str or 
                not st.session_state.kpi_data
            )
            
            # Auto-calculate KPIs automatically (no button needed)
            if needs_calculation:
                # Show skeleton while loading
                skeleton_placeholder = st.empty()
                with skeleton_placeholder.container():
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                                padding: 2rem; border-radius: 16px; margin: 1rem 0;'>
                        <h3 style='font-family: "Inter", sans-serif; font-weight: 600; 
                                   color: #1a1a2e; margin-bottom: 1.5rem; text-align: center;'>
                            📊 Calculating KPIs...
                        </h3>
                        <div class='skeleton-card' style='height: 200px; margin-bottom: 1rem;'></div>
                        <div class='skeleton-card' style='height: 150px;'></div>
                        <p style='text-align: center; color: #6c757d; margin-top: 1.5rem; font-weight: 500;'>
                            Analyzing stock data and calculating indicators...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                try:
                    with st.spinner("Calculating KPIs... This may take a moment."):
                        st.session_state.kpi_data = calculate_kpis(
                            st.session_state.tickers, 
                            start_date, 
                            end_date
                        )
                        st.session_state.kpi_tickers = tickers_str
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.success("✅ KPIs calculated successfully!")
                    st.rerun()  # Refresh to show results
                except (RequestsConnectionError, Timeout, RequestException) as e:
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.error(
                        f"🔌 Connection Error: {str(e)}\n\n"
                        "**Troubleshooting steps:**\n"
                        "1. Check your internet connection\n"
                        "2. Verify your VPN is working (if using one)\n"
                        "3. Check if Yahoo Finance is accessible from your network\n"
                        "4. Try again in a few moments"
                    )
                except Exception as e:
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.error(f"❌ Error calculating KPIs: {str(e)}")
        
        # Manual recalculation button (optional)
        if st.session_state.tickers and st.session_state.kpi_data:
            if st.button("🔄 Recalculate KPIs", type="secondary", key="recalculate_kpis_btn"):
                # Clear existing data to force recalculation
                st.session_state.kpi_data = None
                st.session_state.kpi_tickers = None
                st.rerun()
        
        if st.session_state.kpi_data:
            # Display KPI table with modern styling
            kpi_df_data = []
            for ticker, kpis in st.session_state.kpi_data.items():
                row = {'Ticker': ticker}
                
                # Get company full name (cached)
                company_name = get_ticker_info(ticker, 'longName') or ticker
                
                row['Full Name'] = company_name
                row['RSI'] = f"{kpis.get('RSI', 'N/A'):.2f}" if kpis.get('RSI') else 'N/A'
                row['Beta'] = f"{kpis.get('Beta', 'N/A'):.2f}" if kpis.get('Beta') else 'N/A'
                row['P/E Ratio'] = f"{kpis.get('P/E Ratio', 'N/A'):.2f}" if kpis.get('P/E Ratio') else 'N/A'
                if 'Bollinger Bands' in kpis and kpis['Bollinger Bands'].get('Current Price'):
                    row['Current Price'] = f"${kpis['Bollinger Bands']['Current Price']:.2f}"
                else:
                    row['Current Price'] = 'N/A'
                kpi_df_data.append(row)
            
            if kpi_df_data:
                kpi_df = pd.DataFrame(kpi_df_data)
                # Reorder columns to have Ticker, Full Name, then the rest
                column_order = ['Ticker', 'Full Name', 'RSI', 'Beta', 'P/E Ratio', 'Current Price']
                # Only include columns that exist in the dataframe
                column_order = [col for col in column_order if col in kpi_df.columns]
                kpi_df = kpi_df[column_order]
                
                # Style the dataframe with gradients
                styled_df = kpi_df.style.format({
                    'RSI': lambda x: f'{float(x):.2f}' if x != 'N/A' else 'N/A',
                    'Beta': lambda x: f'{float(x):.2f}' if x != 'N/A' else 'N/A',
                    'P/E Ratio': lambda x: f'{float(x):.2f}' if x != 'N/A' else 'N/A'
                })
                st.dataframe(styled_df, use_container_width=True, height=400)
    
    with tab2:
        st.markdown("""
        <div style='margin: 1rem 0 2rem 0;'>
            <h1 style='font-family: "Inter", sans-serif; font-weight: 600; 
                      color: #1a1a2e; margin-bottom: 0.5rem;'>
                📈 Technical Indicators
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # #region agent log
        import json as json_tab2
        log_path_tab2 = r"c:\Users\ohada\OneDrive\Desktop\Gen AI for Stock Analysis (2)\Gen AI for Stock Analysis\.cursor\debug.log"
        with open(log_path_tab2, "a") as f:
            f.write(json_tab2.dumps({"location": "main.py:TAB2_CHECK", "message": "Tab2 ticker check", "data": {"tickers": list(st.session_state.tickers) if st.session_state.tickers else [], "tickers_bool": bool(st.session_state.tickers), "not_tickers": not st.session_state.tickers}, "timestamp": __import__('time').time(), "sessionId": "debug-session"}) + "\n")
        # #endregion
        
        # Check if tickers are selected
        if not st.session_state.tickers or len(st.session_state.tickers) == 0:
            st.stop()
        
        # #region agent log
        with open(log_path_tab2, "a") as f:
            f.write(json_tab2.dumps({"location": "main.py:TAB2_CONTINUE", "message": "Tab2 continuing - tickers exist", "data": {"tickers": list(st.session_state.tickers)}, "timestamp": __import__('time').time(), "sessionId": "debug-session"}) + "\n")
        # #endregion
        
        # Add expandable explanations
        with st.expander("📚 Learn about Technical Indicators"):
            st.markdown("""
            **RSI (Relative Strength Index):** A momentum oscillator that measures the speed and change of price movements. 
            - Values above 70 indicate overbought conditions (potential sell signal)
            - Values below 30 indicate oversold conditions (potential buy signal)
            
            **Bollinger Bands:** Consist of a middle band (simple moving average) and two outer bands (standard deviations).
            - Price touching upper band = potentially overbought
            - Price touching lower band = potentially oversold
            
            **P/E Ratio (Price-to-Earnings):** Measures a company's current share price relative to its per-share earnings.
            - High P/E = potentially overvalued or high growth expected
            - Low P/E = potentially undervalued
            
            **Beta:** Measures a stock's volatility relative to the overall market.
            - Beta > 1 = more volatile than market (higher risk/return)
            - Beta < 1 = less volatile than market (more stable)
            
            **MACD (Moving Average Convergence Divergence):** A trend-following momentum indicator.
            - MACD crossing above signal line = bullish signal (buy)
            - MACD crossing below signal line = bearish signal (sell)
            """)
        
        # Ticker selection - show all indicators for selected ticker
        if st.session_state.tickers:
            # Create display labels with full company names
            ticker_options = []
            ticker_map = {}  # Maps display label to actual ticker
            
            for tick in st.session_state.tickers:
                # Get company name (cached)
                company_name = get_ticker_info(tick, 'longName')
                display_label = f"{tick} ({company_name})" if company_name else tick
                ticker_options.append(display_label)
                ticker_map[display_label] = tick
            
            selected_display = st.selectbox("Select Ticker", ticker_options)
            ticker = ticker_map[selected_display]  # Get the actual ticker from the selected display label
            
            # Auto-generate all visualizations for the selected ticker
            if ticker:
                # Show skeleton while loading
                skeleton_placeholder = st.empty()
                with skeleton_placeholder.container():
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                                padding: 2rem; border-radius: 16px; margin: 1rem 0;'>
                        <h3 style='font-family: "Inter", sans-serif; font-weight: 600; 
                                   color: #1a1a2e; margin-bottom: 1.5rem; text-align: center;'>
                            📊 Loading Technical Indicators...
                        </h3>
                        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;'>
                            <div class='skeleton-card' style='height: 200px;'></div>
                            <div class='skeleton-card' style='height: 200px;'></div>
                        </div>
                        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;'>
                            <div class='skeleton-card' style='height: 200px;'></div>
                            <div class='skeleton-card' style='height: 200px;'></div>
                        </div>
                        <div class='skeleton-card' style='height: 250px;'></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                try:
                    # Download data once for all indicators (cached)
                    data = download_ticker_data(ticker, start_date, end_date)
                    skeleton_placeholder.empty()  # Clear skeleton
                    
                    if data.empty:
                        st.error(f"No data available for {ticker} in the selected date range.")
                    else:
                        # Handle multi-index columns from yfinance (when downloading single ticker)
                        if isinstance(data.columns, pd.MultiIndex):
                            try:
                                if 'Close' in data.columns.get_level_values(0):
                                    close_data = data['Close']
                                    if isinstance(close_data, pd.Series):
                                        data = close_data.to_frame(name='Close')
                                    elif isinstance(close_data, pd.DataFrame):
                                        if len(close_data.columns) > 0:
                                            data = close_data.iloc[:, [0]].rename(columns={close_data.columns[0]: 'Close'})
                                        else:
                                            data = close_data.copy()
                                            data.columns = ['Close']
                                    else:
                                        data = close_data.copy()
                                else:
                                    st.error(f"Could not find 'Close' column in data for {ticker}.")
                                    data = None
                            except Exception as e:
                                st.error(f"Error processing multi-index data: {str(e)}")
                                data = None
                        # Handle regular DataFrame
                        elif isinstance(data, pd.DataFrame):
                            if 'Close' not in data.columns:
                                close_cols = [col for col in data.columns if 'close' in str(col).lower() or 'Close' in str(col)]
                                if close_cols:
                                    data = data[[close_cols[0]]].rename(columns={close_cols[0]: 'Close'})
                                else:
                                    if len(data.columns) > 0:
                                        data = data.iloc[:, [0]].rename(columns={data.columns[0]: 'Close'})
                                    else:
                                        st.error(f"No valid columns found in data for {ticker}.")
                                        data = None
                        # Handle Series
                        elif isinstance(data, pd.Series):
                            data = data.to_frame(name='Close')
                        else:
                            st.error(f"Unexpected data type: {type(data)}")
                            data = None
                        
                        # Check if we have valid data before proceeding
                        if data is None or data.empty:
                            st.error(f"Invalid data structure for {ticker}. Please try again.")
                        elif 'Close' not in data.columns:
                            st.error(f"Missing 'Close' column in processed data for {ticker}.")
                        else:
                            # Display all indicators in columns
                            col1, col2 = st.columns(2)
                            
                            # RSI
                            with col1:
                                st.subheader("📊 RSI (Relative Strength Index)")
                                if len(data) >= 14:
                                    try:
                                        fig = plot_rsi(data, ticker)
                                        if fig:
                                            st.pyplot(fig)
                                            plt.close(fig)
                                    except Exception as e:
                                        st.error(f"Error generating RSI: {str(e)}")
                                else:
                                    st.warning(f"Not enough data for RSI (need 14 days, got {len(data)})")
                            
                            # Bollinger Bands
                            with col2:
                                st.subheader("📈 Bollinger Bands")
                                if len(data) >= 20:
                                    try:
                                        fig = plot_bollinger_bands(data, ticker)
                                        if fig:
                                            st.pyplot(fig)
                                            plt.close(fig)
                                    except Exception as e:
                                        st.error(f"Error generating Bollinger Bands: {str(e)}")
                                else:
                                    st.warning(f"Not enough data for Bollinger Bands (need 20 days, got {len(data)})")
                            
                            # P/E Ratio
                            with col1:
                                st.subheader("💰 P/E Ratio")
                                # Get EPS (cached)
                                eps = get_ticker_info(ticker, 'trailingEps')
                                try:
                                    fig = plot_pe_ratios(data, ticker, eps)
                                    if fig:
                                        st.pyplot(fig)
                                        plt.close(fig)
                                    else:
                                        st.warning(f"EPS not available for {ticker}")
                                except Exception as e:
                                    st.warning(f"Could not retrieve EPS for {ticker}: {str(e)}")
                            
                            # MACD
                            with col2:
                                st.subheader("📉 MACD")
                                if len(data) >= 26:
                                    try:
                                        fig = plot_macd(data, ticker)
                                        if fig:
                                            st.pyplot(fig)
                                            plt.close(fig)
                                    except Exception as e:
                                        st.error(f"Error generating MACD: {str(e)}")
                                else:
                                    st.warning(f"Not enough data for MACD (need 26 days, got {len(data)})")
                
                except (RequestsConnectionError, Timeout, RequestException) as e:
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.error(
                        f"🔌 Connection Error: {str(e)}\n\n"
                        "**Troubleshooting steps:**\n"
                        "1. Check your internet connection\n"
                        "2. Verify your VPN is working (if using one)\n"
                        "3. Check if Yahoo Finance is accessible from your network\n"
                        "4. Try again in a few moments"
                    )
                except Exception as e:
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.error(f"❌ Error generating visualizations: {str(e)}")
        else:
            st.info("👈 Please select tickers first in the sidebar.")
        
        # Beta Comparison (for all tickers) - independent of selected single ticker
        if st.session_state.tickers:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📊 Beta Comparison (All Tickers)")
            try:
                # Cache in session_state to avoid recalculating within the same extract
                tickers_key = ",".join(sorted(st.session_state.tickers))
                beta_cache_key = f"{tickers_key}|{start_date}|{end_date}"

                if (
                    'beta_comparison_cache_key' not in st.session_state or
                    st.session_state.beta_comparison_cache_key != beta_cache_key
                ):
                    betas = get_beta_values(st.session_state.tickers, start_date, end_date)
                    st.session_state.beta_comparison_betas = betas
                    st.session_state.beta_comparison_cache_key = beta_cache_key
                else:
                    betas = st.session_state.get('beta_comparison_betas', {})

                if betas:
                    fig = plot_beta_comparison(betas)
                    if fig:
                        st.pyplot(fig)
                        plt.close(fig)
                else:
                    st.warning("No beta data available for selected tickers.")
            except Exception as e:
                st.warning(f"Could not generate beta comparison: {str(e)}")
    
    with tab3:
        st.markdown("""
        <div style='margin: 1rem 0 2rem 0;'>
            <h1 style='font-family: "Inter", sans-serif; font-weight: 600; 
                      color: #1a1a2e; margin-bottom: 0.5rem;'>
                💼 Portfolio Optimization
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if tickers are selected
        if not st.session_state.tickers or len(st.session_state.tickers) == 0:
            st.stop()
        
        # Add expandable explanations
        with st.expander("📚 Learn about Optimization Methods"):
            st.markdown("""
            **Black-Litterman Model:**
            Combines the CAPM equilibrium market returns with subjective views to create a more stable and intuitive 
            expected return vector. It helps in adjusting the market equilibrium returns based on the investor's views 
            and confidence levels, resulting in a more personalized and optimized portfolio.

            **Risk Parity:**
            Focuses on balancing the risk contribution of each asset in the portfolio. Instead of maximizing return, 
            the goal is that each asset contributes an equal share of the overall portfolio risk. This often leads to 
            more diversified and stable portfolios, especially when assets have very different volatilities.
            """)
        
        if not PORTFOLIO_OPT_AVAILABLE:
            st.warning(
                "⚠️ Portfolio optimization is not available. PyPortfolioOpt requires Microsoft Visual C++ Build Tools.\n\n"
                "**To enable portfolio optimization:**\n"
                "1. Install Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/\n"
                "2. Select 'Desktop development with C++' workload\n"
                "3. After installation, run: `pip install PyPortfolioOpt`\n"
                "4. Restart the app"
            )
        
        optimization_method = st.radio(
            "Select Optimization Method",
            ["Black-Litterman Model", "Risk Parity"],
            horizontal=True,
            disabled=not PORTFOLIO_OPT_AVAILABLE
        )
        
        # Risk-free rates - shown inside the selected optimization method
        # Initialize risk-free rates in session state if not exists
        if 'risk_free_rate_mpt' not in st.session_state:
            st.session_state.risk_free_rate_mpt = DEFAULT_RISK_FREE_RATE_MPT
        if 'risk_free_rate_bl' not in st.session_state:
            st.session_state.risk_free_rate_bl = DEFAULT_RISK_FREE_RATE_BL
        if 'risk_free_rate_rp' not in st.session_state:
            # Use the same default as MPT for reporting Sharpe
            st.session_state.risk_free_rate_rp = DEFAULT_RISK_FREE_RATE_MPT
        
        # Use form to prevent automatic reruns on input changes
        with st.form("portfolio_optimization_form", clear_on_submit=False):
            # Display input fields (values are stored temporarily, not in session_state yet)
            if optimization_method == "Black-Litterman Model":
                st.subheader("Black-Litterman Risk-Free Rate")
                temp_risk_free_rate_bl = st.number_input(
                    "Black-Litterman Risk-Free Rate",
                    min_value=0.0,
                    max_value=0.2,
                    value=st.session_state.risk_free_rate_bl,
                    step=0.001,
                    format="%.3f",
                    key="bl_risk_free_rate_input"
                )
            elif optimization_method == "Risk Parity":
                st.subheader("Risk Parity Risk-Free Rate (for Sharpe calculation only)")
                temp_risk_free_rate_rp = st.number_input(
                    "Risk Parity Risk-Free Rate",
                    min_value=0.0,
                    max_value=0.2,
                    value=st.session_state.risk_free_rate_rp,
                    step=0.001,
                    format="%.3f",
                    key="rp_risk_free_rate_input"
                )
            
            # Optimize only when user clicks the submit button
            submitted = st.form_submit_button("Optimize Portfolio", type="primary", disabled=not PORTFOLIO_OPT_AVAILABLE)
        
        if submitted:
            # Require tickers before running optimization
            if not st.session_state.tickers:
                st.warning("⚠️ Please configure and extract tickers before optimizing the portfolio.")
                return
            
            # Update session state with new values only when button is clicked
            if optimization_method == "Black-Litterman Model":
                st.session_state.risk_free_rate_bl = temp_risk_free_rate_bl
                risk_free_rate_bl = st.session_state.risk_free_rate_bl
            elif optimization_method == "Risk Parity":
                st.session_state.risk_free_rate_rp = temp_risk_free_rate_rp
                risk_free_rate_rp = st.session_state.risk_free_rate_rp
            
            try:
                if optimization_method == "Black-Litterman Model":
                    # #region agent log
                    try:
                        log_entry = {
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'E',
                            'location': 'main.py:1516',
                            'message': 'About to call optimize_portfolio_black_litterman',
                            'data': {
                                'tickers': st.session_state.tickers,
                                'start_date': str(start_date),
                                'end_date': str(end_date),
                                'risk_free_rate': float(risk_free_rate_bl)
                            },
                            'timestamp': int(time.time() * 1000)
                        }
                        _log_write(log_entry)
                    except Exception:
                        pass
                    # #endregion
                    try:
                        with st.spinner("Optimizing portfolio with Black-Litterman model..."):
                            result = optimize_portfolio_black_litterman(
                                st.session_state.tickers,
                                start_date,
                                end_date,
                                risk_free_rate_bl
                            )
                    except Exception as bl_err:
                        # #region agent log
                        try:
                            _log_write({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'E',
                                'location': 'main.py:BL_EXCEPTION',
                                'message': 'optimize_portfolio_black_litterman exception caught',
                                'data': {
                                    'error_type': type(bl_err).__name__,
                                    'error_message': str(bl_err)
                                },
                                'timestamp': int(time.time() * 1000)
                            })
                        except Exception:
                            pass
                        # #endregion
                        st.error(f"❌ Black-Litterman optimization failed: {bl_err}")
                        return
                elif optimization_method == "Risk Parity":
                    result = optimize_portfolio_risk_parity(
                        st.session_state.tickers,
                        start_date,
                        end_date,
                        risk_free_rate_rp
                    )
                
                st.success("✅ Portfolio optimized successfully!")
                
                # Display results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Expected Annual Return", f"{result['expected_return']*100:.2f}%")
                with col2:
                    st.metric("Annual Volatility", f"{result['volatility']*100:.2f}%")
                with col3:
                    st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
                
                # Display weights
                st.subheader("Optimal Portfolio Weights")
                weights_df = pd.DataFrame(
                    list(result['weights'].items()),
                    columns=['Ticker', 'Weight']
                )
                weights_df['Weight'] = weights_df['Weight'].apply(lambda x: f"{x*100:.2f}%")
                weights_df = weights_df[weights_df['Weight'] != '0.00%']  # Filter out zero weights
                st.dataframe(weights_df, use_container_width=True)
                
                # Create a pie chart of weights (similar to AI recommendations)
                filtered_weights = {k: v for k, v in result['weights'].items() if v > 0.001}
                
                if filtered_weights:
                    # Prepare data
                    labels = list(filtered_weights.keys())
                    values = list(filtered_weights.values())
                    
                    # Use a modern color palette
                    colors = [px.colors.qualitative.Set3[i % len(px.colors.qualitative.Set3)] for i in range(len(labels))]
                    
                    # Create interactive Plotly pie chart using plotly.express
                    fig = px.pie(
                        values=values,
                        names=labels,
                        title='Optimal Portfolio Allocation',
                        color_discrete_sequence=colors,
                        hole=0.3  # Creates a donut chart
                    )
                    
                    # Update traces for better styling
                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        textfont=dict(
                            size=12,
                            family='Inter',
                            color='#1a1a2e'
                        ),
                        marker=dict(
                            line=dict(color='#FFFFFF', width=2)
                        ),
                        hovertemplate='<b>%{label}</b><br>' +
                                      'Allocation: %{percent}<br>' +
                                      'Weight: %{value:.4f}<br>' +
                                      '<extra></extra>',
                        pull=[0.02] * len(labels)  # Slight separation
                    )
                    
                    # Update layout for modern styling
                    fig.update_layout(
                        title={
                            'text': 'Optimal Portfolio Allocation',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {
                                'size': 18,
                                'family': 'Inter',
                                'color': '#667eea'
                            }
                        },
                        showlegend=True,
                        legend=dict(
                            orientation="v",
                            yanchor="middle",
                            y=0.5,
                            xanchor="left",
                            x=1.05,
                            font=dict(
                                family='Inter',
                                size=11,
                                color='#1a1a2e'
                            )
                        ),
                        height=500,
                        margin=dict(l=20, r=20, t=60, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)
                
            except (RequestsConnectionError, Timeout, RequestException) as e:
                st.error(
                    f"🔌 Connection Error: {str(e)}\n\n"
                    "**Troubleshooting steps:**\n"
                    "1. Check your internet connection\n"
                    "2. Verify your VPN is working (if using one)\n"
                    "3. Check if Yahoo Finance is accessible from your network\n"
                    "4. Try again in a few moments"
                )
            except Exception as e:
                st.error(f"❌ Error optimizing portfolio: {str(e)}")
                st.exception(e)
    
    with tab_ai:
        st.markdown("""
        <div style='margin: 1rem 0 2rem 0;'>
            <h1 style='font-family: "Inter", sans-serif; font-weight: 600; 
                      color: #1a1a2e; margin-bottom: 0.5rem;'>
                🤖 AI-Powered Recommendations
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if tickers are selected
        if not st.session_state.tickers or len(st.session_state.tickers) == 0:
            st.stop()
        
        # Get API key - try Streamlit Secrets first, then config
        api_key = None
        try:
            # Try Streamlit Secrets (for Streamlit Cloud deployment)
            if hasattr(st, 'secrets') and hasattr(st.secrets, 'get'):
                api_key = st.secrets.get("OPENAI_API_KEY", None)
        except Exception:
            pass
        
        # Fallback to config
        if not api_key:
            from config.settings import OPENAI_API_KEY as CONFIG_API_KEY
            api_key = CONFIG_API_KEY if CONFIG_API_KEY else ""
        
        if not api_key or not st.session_state.llm:
            st.warning("⚠️ OpenAI API key not configured. Please set OPENAI_API_KEY in Streamlit Secrets or environment variable.")
        elif not st.session_state.kpi_data:
            st.info("📊 Please calculate KPIs first to get AI recommendations.")
        else:
            # Auto-generate AI recommendations if KPI data is available
            # Create hash of KPI data to check if recommendations need regeneration
            kpi_data_str = str(sorted(st.session_state.kpi_data.items()))
            
            # Initialize regenerate counter if not exists
            if 'ai_recommendations_regenerate_counter' not in st.session_state:
                st.session_state.ai_recommendations_regenerate_counter = 0
            
            # Check if we need to regenerate recommendations
            # Only regenerate if:
            # 1. No recommendations exist, OR
            # 2. KPI data has changed (hash mismatch), OR
            # 3. Regenerate counter has changed (user clicked "Regenerate")
            last_counter = st.session_state.get('ai_recommendations_last_counter', -1)
            current_counter = st.session_state.ai_recommendations_regenerate_counter
            needs_regeneration = (
                'ai_recommendations' not in st.session_state or
                st.session_state.get('ai_recommendations_kpi_hash') != kpi_data_str or
                last_counter != current_counter
            )
            
            if needs_regeneration:
                # Show skeleton while loading
                skeleton_placeholder = st.empty()
                with skeleton_placeholder.container():
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
                                padding: 2rem; border-radius: 16px; margin: 1rem 0;'>
                        <h3 style='font-family: "Inter", sans-serif; font-weight: 600; 
                                   color: #1a1a2e; margin-bottom: 1.5rem; text-align: center;'>
                            🤖 AI Analysis & Recommendations
                        </h3>
                        <div class='skeleton-card' style='height: 100px; margin-bottom: 1rem;'></div>
                        <div class='skeleton-card' style='height: 100px; margin-bottom: 1rem;'></div>
                        <div class='skeleton-card' style='height: 100px; margin-bottom: 1rem;'></div>
                        <div class='skeleton-card' style='height: 100px;'></div>
                        <p style='text-align: center; color: #6c757d; margin-top: 1.5rem; font-weight: 500;'>
                            🤖 Generating AI recommendations...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                try:
                    # Use cached function - will use cache if KPI data hash matches (30 min TTL)
                    # Include regenerate_counter in cache key to allow forced regeneration
                    response = generate_ai_recommendations_cached(
                        kpi_data_str,
                        st.session_state.kpi_data,
                        st.session_state.llm,
                        st.session_state.ai_recommendations_regenerate_counter
                    )
                    st.session_state.ai_recommendations = response
                    st.session_state.ai_recommendations_kpi_hash = kpi_data_str
                    # Store current counter value to track if it changes later
                    st.session_state.ai_recommendations_last_counter = st.session_state.ai_recommendations_regenerate_counter
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.success("✅ AI recommendations generated!")
                except (RequestsConnectionError, ConnectionError) as e:
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.error(
                        f"🔌 Connection Error: {str(e)}\n\n"
                        "**Troubleshooting steps:**\n"
                        "1. Check your internet connection\n"
                        "2. Verify your VPN is working (if using one)\n"
                        "3. Check if OpenAI API is accessible from your network\n"
                        "4. Try again in a few moments"
                    )
                except ValueError as e:
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.error(f"❌ API Error: {str(e)}")
                except Exception as e:
                    skeleton_placeholder.empty()  # Clear skeleton
                    st.error(f"❌ Error generating recommendations: {str(e)}")
            
            # Display recommendations if available - but hide the text, only show pie charts
            if 'ai_recommendations' in st.session_state and st.session_state.ai_recommendations:
                # Process recommendations to extract portfolio data for pie charts only
                # Don't display the recommendation text - we only want the charts
                recommendations_text = st.session_state.ai_recommendations
                import re
                
                # Initialize portfolio allocations tracking
                if 'portfolio_allocations' not in st.session_state:
                    st.session_state.portfolio_allocations = {}
                if 'current_portfolio' in st.session_state:
                    del st.session_state.current_portfolio
                
                # Save original text BEFORE removing section 5 (for data extraction)
                original_recommendations_text = recommendations_text
                
                # First, extract portfolio allocations from the entire text before removing section 5
                # Look for portfolio sections in various formats
                portfolio_section_pattern = r'(?:##\s*5\.\s*Portfolio\s+Allocation\s+Suggestions|Portfolio\s+Allocation\s+Suggestions)(.*?)(?=##|$)'
                portfolio_section_match = re.search(portfolio_section_pattern, original_recommendations_text, re.DOTALL | re.IGNORECASE)
                
                if portfolio_section_match:
                    portfolio_section = portfolio_section_match.group(1)
                else:
                    # If section 5 not found, search in the entire text
                    portfolio_section = original_recommendations_text
                
                # Try to find each portfolio type
                for portfolio_type in ['Conservative', 'Balanced', 'Aggressive']:
                    allocations = {}
                    
                    # Pattern 1: **Portfolio Type Portfolio:** followed by bullet points or text
                    pattern1 = rf'\*\*{portfolio_type}\s+Portfolio:\*\*\s*\n(.*?)(?=\*\*(?:Conservative|Balanced|Aggressive)\s+Portfolio:\*\*|$)'
                    # Pattern 2: Portfolio Type Portfolio: (without bold) followed by content
                    pattern2 = rf'{portfolio_type}\s+Portfolio:\s*\n(.*?)(?=(?:Conservative|Balanced|Aggressive)\s+Portfolio:|$)'
                    # Pattern 3: Just the portfolio type as header (with or without colon)
                    pattern3 = rf'{portfolio_type}\s+Portfolio[:\s]*(.*?)(?=(?:Conservative|Balanced|Aggressive)\s+Portfolio|$)'
                    # Pattern 4: In bullet format: - **Portfolio Type Portfolio:**
                    pattern4 = rf'[-*]\s*\*\*{portfolio_type}\s+Portfolio:\*\*\s*\n(.*?)(?=[-*]\s*\*\*(?:Conservative|Balanced|Aggressive)\s+Portfolio:\*\*|$)'
                    
                    for pattern in [pattern1, pattern2, pattern3, pattern4]:
                        match = re.search(pattern, portfolio_section, re.DOTALL | re.IGNORECASE)
                        if match:
                            content = match.group(1)
                            
                            # Extract allocations from bullet points (e.g., "- 50% SPY" or "* 50% SPY")
                            bullet_matches = re.findall(r'[-*]\s*(\d+(?:\.\d+)?)%\s+([A-Z]{2,5}(?:-USD)?)', content, re.IGNORECASE)
                            for percentage, ticker in bullet_matches:
                                allocations[ticker.upper()] = float(percentage)
                            
                            # Also try to extract from inline format (e.g., "50% SPY, 20% AAPL")
                            inline_matches = re.findall(r'(\d+(?:\.\d+)?)%\s+([A-Z]{2,5}(?:-USD)?)', content, re.IGNORECASE)
                            for percentage, ticker in inline_matches:
                                if ticker.upper() not in allocations:  # Don't overwrite if already found
                                    allocations[ticker.upper()] = float(percentage)
                            
                            if allocations:
                                break
                    
                    if allocations:
                        st.session_state.portfolio_allocations[portfolio_type] = allocations
                
                # NOW remove section 5 (Portfolio Allocation Suggestions) from the text for display
                # This ensures it won't be displayed at all
                # Pattern to match section 5 header and all content until next section or end
                section5_pattern = r'(?:##\s*)?5\.\s*Portfolio\s+Allocation\s+Suggestions?.*?(?=(?:##\s*\d+\.|##\s*[A-Z]|$))'
                recommendations_text = re.sub(section5_pattern, '', recommendations_text, flags=re.DOTALL | re.IGNORECASE)
                
                # Also try pattern without "##" header (plain text format) - more comprehensive
                section5_pattern2 = r'(?:^|\n)\s*5\.\s*Portfolio\s+Allocation\s+Suggestions?.*?(?=(?:^\s*\d+\.\s+[A-Z]|$))'
                recommendations_text = re.sub(section5_pattern2, '', recommendations_text, flags=re.DOTALL | re.IGNORECASE | re.MULTILINE)
                
                # Clean up any extra blank lines that might have been left
                recommendations_text = re.sub(r'\n\n\n+', '\n\n', recommendations_text)
                
                # Check if we have a "Stock-by-Stock Analysis" section and replace it with a table from KPI data
                stock_analysis_match = re.search(r'##\s*2\.\s*Stock-by-Stock Analysis(.*?)(?=##\s*3\.|$)', recommendations_text, re.DOTALL | re.IGNORECASE)
                if stock_analysis_match and st.session_state.kpi_data:
                    # Create table HTML directly from KPI data
                    table_html = '<table class="stock-analysis-table"><thead><tr><th>Ticker</th><th>RSI</th><th>MACD</th><th>P/E Ratio</th></tr></thead><tbody>'
                    
                    # Sort tickers alphabetically for consistent display
                    sorted_tickers = sorted(st.session_state.kpi_data.keys())
                    
                    for ticker in sorted_tickers:
                        kpis = st.session_state.kpi_data[ticker]
                        
                        # Format RSI
                        rsi_value = kpis.get('RSI')
                        if rsi_value is not None:
                            rsi_display = f'{rsi_value:.2f}'
                            # Add status badge based on RSI value
                            rsi_badge = ''
                            if rsi_value > 70:
                                rsi_badge = ' <span class="status-badge status-overbought">Overbought</span>'
                            elif rsi_value < 30:
                                rsi_badge = ' <span class="status-badge status-oversold">Oversold</span>'
                            rsi_display += rsi_badge
                        else:
                            rsi_display = 'N/A'
                        
                        # Format MACD
                        macd_data = kpis.get('MACD')
                        if macd_data and isinstance(macd_data, dict):
                            macd_value = macd_data.get('MACD')
                            if macd_value is not None:
                                macd_display = f'{macd_value:.4f}'
                                # Add status badge based on MACD value (positive = bullish, negative = bearish)
                                macd_badge = ''
                                signal_value = macd_data.get('Signal Line')
                                if signal_value is not None:
                                    if macd_value > signal_value:
                                        macd_badge = ' <span class="status-badge status-bullish">Bullish</span>'
                                    elif macd_value < signal_value:
                                        macd_badge = ' <span class="status-badge status-bearish">Bearish</span>'
                                macd_display += macd_badge
                            else:
                                macd_display = 'N/A'
                        else:
                            macd_display = 'N/A'
                        
                        # Format P/E Ratio
                        pe_value = kpis.get('P/E Ratio')
                        if pe_value is not None:
                            pe_display = f'{pe_value:.2f}'
                        else:
                            pe_display = 'N/A'
                        
                        table_html += f'''
                        <tr>
                            <td class="ticker-cell">{ticker}</td>
                            <td class="kpi-cell">{rsi_display}</td>
                            <td class="kpi-cell">{macd_display}</td>
                            <td class="kpi-cell">{pe_display}</td>
                        </tr>
                        '''
                    
                    table_html += '</tbody></table>'
                    
                    # Replace the stock analysis section with the table
                    recommendations_text = recommendations_text[:stock_analysis_match.start()] + \
                                         '## 2. Stock-by-Stock Analysis\n\n' + table_html + '\n\n' + \
                                         recommendations_text[stock_analysis_match.end():]
                
                # Split into lines for better processing
                lines = recommendations_text.split('\n')
                formatted_lines = []
                in_list = False
                in_stock_card = False
                skip_portfolio_section = False  # Flag to skip section 5 content
                
                for i, line in enumerate(lines):
                    line_stripped = line.strip()
                    
                    # Skip lines that are part of the table HTML we already inserted
                    if '<table class="stock-analysis-table">' in line_stripped or '</table>' in line_stripped or '<tr>' in line_stripped or '<td' in line_stripped or '<th' in line_stripped:
                        formatted_lines.append(line)
                        continue
                    
                    # Check if we're entering section 5 (Portfolio Allocation Suggestions)
                    # Check for headers (## or #) or plain text "5. Portfolio Allocation Suggestions"
                    is_section5_header = (
                        (line_stripped.startswith('## ') or line_stripped.startswith('# ')) and
                        ('Portfolio Allocation Suggestions' in line_stripped or 
                         'Portfolio allocation suggestions' in line_stripped or
                         re.search(r'5\.\s*Portfolio\s+Allocation', line_stripped, re.IGNORECASE))
                    ) or (
                        # Also check for plain text format "5. Portfolio Allocation Suggestions"
                        re.match(r'^5\.\s*Portfolio\s+Allocation\s+Suggestions?', line_stripped, re.IGNORECASE)
                    )
                    
                    if is_section5_header:
                        skip_portfolio_section = True
                        # Don't add the header, but continue processing to extract data
                        # Continue to next line (skip this header)
                        continue
                    
                    # Check if we're leaving section 5 (next section starts or end of document)
                    if skip_portfolio_section:
                        # Check if this is a new section header (not part of section 5)
                        is_new_section = False
                        if (line_stripped.startswith('## ') or line_stripped.startswith('# ')):
                            if not ('Portfolio Allocation Suggestions' in line_stripped or 
                                    'Portfolio allocation suggestions' in line_stripped or
                                    re.search(r'5\.\s*Portfolio\s+Allocation', line_stripped, re.IGNORECASE)):
                                is_new_section = True
                        elif re.match(r'^\d+\.\s+[A-Z]', line_stripped):
                            # Check if it's a numbered section (like "6. Something" or "4. Risk")
                            if not re.match(r'^5\.\s*Portfolio', line_stripped, re.IGNORECASE):
                                is_new_section = True
                        
                        if is_new_section:
                            skip_portfolio_section = False
                        else:
                            # Skip all content while in section 5 (but data extraction happens before this loop)
                            continue
                    
                    # Handle headers
                    if line_stripped.startswith('# '):
                        if in_list:
                            formatted_lines.append('</ul>')
                            in_list = False
                        if in_stock_card:
                            formatted_lines.append('</div>')
                            in_stock_card = False
                        formatted_lines.append(f'<h1>{line_stripped[2:]}</h1>')
                    elif line_stripped.startswith('## '):
                        if in_list:
                            formatted_lines.append('</ul>')
                            in_list = False
                        if in_stock_card:
                            formatted_lines.append('</div>')
                            in_stock_card = False
                        formatted_lines.append(f'<h2>{line_stripped[3:]}</h2>')
                    elif line_stripped.startswith('### '):
                        if in_list:
                            formatted_lines.append('</ul>')
                            in_list = False
                        if in_stock_card:
                            formatted_lines.append('</div>')
                            in_stock_card = False
                        
                        # Check if it's a stock ticker (e.g., "### AAPL (Apple Inc.)")
                        stock_match = re.match(r'^### ([A-Z]{2,5}(?:-USD)?)\s*\(([^)]+)\)', line_stripped)
                        if stock_match:
                            in_stock_card = True
                            ticker = stock_match.group(1)
                            company_name = stock_match.group(2)
                            formatted_lines.append(f'<div class="stock-card"><h3><span class="stock-name">{ticker}</span> ({company_name})</h3>')
                        else:
                            formatted_lines.append(f'<h3>{line_stripped[4:]}</h3>')
                    
                    # Handle bullet points
                    elif line_stripped.startswith('- '):
                        # Skip ALL bullet points in Portfolio Allocation Suggestions section
                        if skip_portfolio_section:
                            # Still extract data for pie charts, but don't display
                            content = line_stripped[2:]
                            
                            # Check if this is a portfolio header
                            portfolio_header_match = re.search(r'\*\*(Conservative|Balanced|Aggressive)\s+Portfolio:\*\*', content, re.IGNORECASE)
                            if portfolio_header_match:
                                portfolio_type = portfolio_header_match.group(1)
                                if 'portfolio_allocations' not in st.session_state:
                                    st.session_state.portfolio_allocations = {}
                                if portfolio_type not in st.session_state.portfolio_allocations:
                                    st.session_state.portfolio_allocations[portfolio_type] = {}
                                if 'current_portfolio' not in st.session_state:
                                    st.session_state.current_portfolio = portfolio_type
                                else:
                                    st.session_state.current_portfolio = portfolio_type
                            # Check if this is a portfolio allocation (e.g., "25% SPY")
                            elif 'current_portfolio' in st.session_state and st.session_state.current_portfolio:
                                allocation_match = re.search(r'(\d+(?:\.\d+)?)%\s+([A-Z]{2,5}(?:-USD)?)', content)
                                if allocation_match:
                                    percentage = float(allocation_match.group(1))
                                    ticker = allocation_match.group(2)
                                    st.session_state.portfolio_allocations[st.session_state.current_portfolio][ticker] = percentage
                                    if 'portfolio_charts' not in st.session_state:
                                        st.session_state.portfolio_charts = {}
                                    if st.session_state.current_portfolio not in st.session_state.portfolio_charts:
                                        st.session_state.portfolio_charts[st.session_state.current_portfolio] = {}
                                    st.session_state.portfolio_charts[st.session_state.current_portfolio][ticker] = percentage
                            # Skip displaying - continue to next line
                            continue
                        
                        if not in_list:
                            formatted_lines.append('<ul>')
                            in_list = True
                        content = line_stripped[2:]
                        
                        # Check if this is a portfolio allocation bullet (e.g., "25% SPY" or "**Aggressive Portfolio:**")
                        portfolio_header_match = re.search(r'\*\*(Conservative|Balanced|Aggressive)\s+Portfolio:\*\*', content, re.IGNORECASE)
                        if portfolio_header_match:
                            # This is a portfolio header - extract data but don't display
                            portfolio_type = portfolio_header_match.group(1)
                            if 'portfolio_allocations' not in st.session_state:
                                st.session_state.portfolio_allocations = {}
                            if portfolio_type not in st.session_state.portfolio_allocations:
                                st.session_state.portfolio_allocations[portfolio_type] = {}
                            # Store that we're in a portfolio section
                            if 'current_portfolio' not in st.session_state:
                                st.session_state.current_portfolio = portfolio_type
                            else:
                                st.session_state.current_portfolio = portfolio_type
                            # Don't display - skip adding to formatted_lines
                        elif 'current_portfolio' in st.session_state and st.session_state.current_portfolio:
                            # When in portfolio section, skip ALL bullet points (extract data but don't display)
                            # Check if this bullet contains a percentage allocation (e.g., "25% SPY")
                            allocation_match = re.search(r'(\d+(?:\.\d+)?)%\s+([A-Z]{2,5}(?:-USD)?)', content)
                            if allocation_match:
                                percentage = float(allocation_match.group(1))
                                ticker = allocation_match.group(2)
                                st.session_state.portfolio_allocations[st.session_state.current_portfolio][ticker] = percentage
                                # Also store in portfolio_charts for pie charts
                                if 'portfolio_charts' not in st.session_state:
                                    st.session_state.portfolio_charts = {}
                                if st.session_state.current_portfolio not in st.session_state.portfolio_charts:
                                    st.session_state.portfolio_charts[st.session_state.current_portfolio] = {}
                                st.session_state.portfolio_charts[st.session_state.current_portfolio][ticker] = percentage
                            # Don't display ANY bullet points in portfolio section - skip adding to formatted_lines
                            # This ensures only pie charts are shown, not lists
                        else:
                            # Regular bullet point processing
                            # Process bold text in list items first
                            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                            
                            # Process KPI patterns (e.g., "RSI: 30.33", "Beta: 1.107", "P/E Ratio: 36.64")
                            kpi_patterns = [
                                (r'<strong>RSI:</strong>\s*([0-9.]+)', 'RSI'),
                                (r'<strong>Beta:</strong>\s*([0-9.]+)', 'Beta'),
                                (r'<strong>P/E Ratio:</strong>\s*([0-9.]+)', 'P/E Ratio'),
                                (r'<strong>MACD:</strong>\s*([^<]+)', 'MACD'),
                                (r'<strong>Bollinger Bands:</strong>\s*([^<]+)', 'Bollinger Bands'),
                                (r'<strong>Current Price:</strong>\s*\$?([0-9.]+)', 'Price'),
                            ]
                            
                            for pattern, label in kpi_patterns:
                                content = re.sub(pattern, 
                                                lambda m: f'<span class="kpi-label">{label}:</span><span class="kpi-metric">{m.group(1)}</span>', 
                                                content)
                            
                            # Highlight stock tickers (avoid matching inside HTML tags)
                            parts = re.split(r'(<[^>]+>)', content)
                            processed_parts = []
                            for part in parts:
                                if part.startswith('<'):
                                    processed_parts.append(part)
                                else:
                                    # Only process parts that are not HTML tags
                                    processed_parts.append(re.sub(r'\b([A-Z]{2,5}(?:-USD)?)\b', 
                                                                r'<span class="stock-name" style="font-size: 1.2rem;">\1</span>', part))
                            content = ''.join(processed_parts)
                            formatted_lines.append(f'<li>{content}</li>')
                    
                    # Handle regular paragraphs
                    elif line_stripped:
                        # Skip ALL paragraphs in Portfolio Allocation Suggestions section
                        if skip_portfolio_section:
                            # Still extract data for pie charts, but don't display
                            content = line_stripped
                            
                            # Process bold text first for pattern matching
                            content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                            
                            # Process portfolio suggestions - extract data for pie charts (but don't display the text)
                            portfolio_match = re.search(r'<strong>(Conservative|Balanced|Aggressive) Portfolio:</strong>', content)
                            if portfolio_match:
                                portfolio_type = portfolio_match.group(1)
                                # Extract the rest of the content after the portfolio type
                                rest = content[portfolio_match.end():].strip()
                                
                                # Parse portfolio allocations (format: "50% SPY, 20% AAPL, ...")
                                allocations = {}
                                # Remove HTML tags from rest for parsing
                                rest_clean = re.sub(r'<[^>]+>', '', rest)
                                # Match patterns like "50% SPY" or "20% AAPL"
                                allocation_pattern = r'(\d+(?:\.\d+)?)%\s+([A-Z]{2,5}(?:-USD)?)'
                                matches = re.findall(allocation_pattern, rest_clean)
                                
                                for percentage, ticker in matches:
                                    allocations[ticker] = float(percentage)
                                
                                # Store portfolio data for pie chart generation
                                if 'portfolio_charts' not in st.session_state:
                                    st.session_state.portfolio_charts = {}
                                st.session_state.portfolio_charts[portfolio_type] = allocations
                            # Skip displaying - continue to next line
                            continue
                        
                        if in_list:
                            formatted_lines.append('</ul>')
                            in_list = False
                        
                        content = line_stripped
                        
                        # Process bold text first
                        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                        
                        # Process Buy/Hold/Sell recommendations (with bold)
                        content = re.sub(r'<strong>Buy:</strong>\s*([A-Z, -]+)', 
                                        r'<span class="recommendation-badge badge-buy">Buy</span> <strong>\1</strong>', content)
                        content = re.sub(r'<strong>Hold:</strong>\s*([A-Z, -]+)', 
                                        r'<span class="recommendation-badge badge-hold">Hold</span> <strong>\1</strong>', content)
                        content = re.sub(r'<strong>Sell:</strong>\s*([A-Z, -]+)', 
                                        r'<span class="recommendation-badge badge-sell">Sell</span> <strong>\1</strong>', content)
                        
                        # Process risk levels (with bold)
                        content = re.sub(r'<strong>High Risk:</strong>\s*([A-Z, -]+)', 
                                        r'<span class="risk-badge risk-high">High Risk</span> <strong>\1</strong>', content)
                        content = re.sub(r'<strong>Moderate Risk:</strong>\s*([A-Z, -]+)', 
                                        r'<span class="risk-badge risk-moderate">Moderate Risk</span> <strong>\1</strong>', content)
                        content = re.sub(r'<strong>Low Risk:</strong>\s*([A-Z, -]+)', 
                                        r'<span class="risk-badge risk-low">Low Risk</span> <strong>\1</strong>', content)
                        
                        # Process portfolio suggestions - extract data for pie charts (but don't display the text)
                        portfolio_match = re.search(r'<strong>(Conservative|Balanced|Aggressive) Portfolio:</strong>', content)
                        if portfolio_match:
                            portfolio_type = portfolio_match.group(1)
                            # Extract the rest of the content after the portfolio type
                            rest = content[portfolio_match.end():].strip()
                            
                            # Parse portfolio allocations (format: "50% SPY, 20% AAPL, ...")
                            allocations = {}
                            # Remove HTML tags from rest for parsing
                            rest_clean = re.sub(r'<[^>]+>', '', rest)
                            # Match patterns like "50% SPY" or "20% AAPL"
                            allocation_pattern = r'(\d+(?:\.\d+)?)%\s+([A-Z]{2,5}(?:-USD)?)'
                            matches = re.findall(allocation_pattern, rest_clean)
                            
                            for percentage, ticker in matches:
                                allocations[ticker] = float(percentage)
                            
                            # Store portfolio data for pie chart generation
                            if 'portfolio_charts' not in st.session_state:
                                st.session_state.portfolio_charts = {}
                            st.session_state.portfolio_charts[portfolio_type] = allocations
                            
                            # Don't display the portfolio suggestion text - we only want the charts
                            # Skip adding this to formatted_lines - data is already extracted above
                        else:
                            # Process KPI patterns in paragraphs
                            kpi_patterns = [
                                (r'<strong>RSI:</strong>\s*([0-9.]+)', 'RSI'),
                                (r'<strong>Beta:</strong>\s*([0-9.]+)', 'Beta'),
                                (r'<strong>P/E Ratio:</strong>\s*([0-9.]+)', 'P/E Ratio'),
                                (r'<strong>MACD:</strong>\s*([^<]+)', 'MACD'),
                                (r'<strong>Bollinger Bands:</strong>\s*([^<]+)', 'Bollinger Bands'),
                            ]
                            
                            for pattern, label in kpi_patterns:
                                content = re.sub(pattern, 
                                                lambda m: f'<span class="kpi-label">{label}:</span><span class="kpi-metric">{m.group(1)}</span>', 
                                                content)
                            
                            # Highlight stock tickers in paragraphs (avoid matching inside HTML tags)
                            parts = re.split(r'(<[^>]+>)', content)
                            processed_parts = []
                            for part in parts:
                                if part.startswith('<'):
                                    processed_parts.append(part)
                                else:
                                    # Only process parts that are not HTML tags - make stock names prominent
                                    processed_parts.append(re.sub(r'\b([A-Z]{2,5}(?:-USD)?)\b', 
                                                                r'<span class="stock-name" style="font-size: 1.2rem;">\1</span>', part))
                            content = ''.join(processed_parts)
                            formatted_lines.append(f'<p>{content}</p>')
                
                # Close any open tags
                if in_list:
                    formatted_lines.append('</ul>')
                if in_stock_card:
                    formatted_lines.append('</div>')
                
                # Hide the recommendations text - only show pie charts
                # recommendations_html = '\n'.join(formatted_lines)
                # 
                # st.markdown(f"""
                # <div class="ai-recommendations">
                #     {recommendations_html}
                # </div>
                # """, unsafe_allow_html=True)
                
                # Clear current_portfolio flag after processing
                if 'current_portfolio' in st.session_state:
                    del st.session_state.current_portfolio
                
                # Extract and display Overall Market Assessment
                # Try multiple patterns to catch different formats
                market_assessment_match = None
                patterns = [
                    r'(?:##\s*)?1\.\s*Overall\s+Market\s+Assessment[:\s]*(.*?)(?=(?:##\s*)?2\.|##\s*3\.|Buy:|Hold:|Sell:|$)',
                    r'Overall\s+Market\s+Assessment[:\s]*(.*?)(?=(?:##\s*)?2\.|##\s*3\.|Buy:|Hold:|Sell:|Stock-by-Stock|Portfolio|$)',
                    r'1\.\s*Overall.*?Assessment[:\s]*(.*?)(?=\d+\.|Buy:|Hold:|Sell:|$)',
                ]
                
                for pattern in patterns:
                    market_assessment_match = re.search(pattern, recommendations_text, re.DOTALL | re.IGNORECASE)
                    if market_assessment_match:
                        break
                
                if market_assessment_match:
                    market_assessment_text = market_assessment_match.group(1).strip()
                    # Remove all HTML tags first (before other cleanup)
                    market_assessment_text = re.sub(r'<[^>]+>', '', market_assessment_text)  # Remove all HTML tags
                    # Remove leading whitespace/indentation from each line
                    market_assessment_text = re.sub(r'^\s+', '', market_assessment_text, flags=re.MULTILINE)  # Remove leading whitespace from each line
                    # Clean up the text - remove extra whitespace and markdown formatting
                    market_assessment_text = re.sub(r'\n{3,}', '\n\n', market_assessment_text)
                    # Remove bullet points at start of lines but keep the content
                    market_assessment_text = re.sub(r'^\s*[-•*]\s+', '', market_assessment_text, flags=re.MULTILINE)
                    # Remove all markdown formatting (bold **, italic *, etc.)
                    market_assessment_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', market_assessment_text)  # Remove bold **text**
                    market_assessment_text = re.sub(r'\*([^*]+)\*', r'\1', market_assessment_text)  # Remove italic *text*
                    market_assessment_text = re.sub(r'\*\*', '', market_assessment_text)  # Remove any remaining **
                    market_assessment_text = re.sub(r'^\s*\*\s*', '', market_assessment_text, flags=re.MULTILINE)  # Remove leading * at start of lines
                    market_assessment_text = re.sub(r'\s+\*\s+', ' ', market_assessment_text)  # Remove standalone * in text
                    # Clean up any remaining HTML entities or fragments
                    market_assessment_text = re.sub(r'&[a-zA-Z]+;', '', market_assessment_text)  # Remove HTML entities if any
                    # Final cleanup - ensure text starts at the beginning
                    market_assessment_text = market_assessment_text.strip()
                    # Remove any remaining leading whitespace from the first line
                    if market_assessment_text:
                        market_assessment_text = market_assessment_text.lstrip()
                    
                    st.markdown("---")
                    st.markdown("""
                    <div style='margin: 2rem 0;'>
                        <h2 style='font-family: "Inter", sans-serif; font-weight: 600; 
                                  color: #1a1a2e; margin-bottom: 1.5rem;'>
                            📊 Overall Market Assessment
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Escape HTML to prevent rendering HTML tags as code (though we've already removed them)
                    escaped_text = html.escape(market_assessment_text)
                    st.markdown(f"""
                    <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 12px; 
                                border-left: 4px solid #667eea; margin-bottom: 2rem;'>
                        <p style='font-family: "Inter", sans-serif; font-size: 1rem; 
                                  color: #1a1a2e; line-height: 1.8; margin: 0; text-align: left;'>
                            {escaped_text}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display Buy/Hold/Sell Recommendations
                st.markdown("---")
                st.markdown("""
                <div style='margin: 2rem 0;'>
                    <h2 style='font-family: "Inter", sans-serif; font-weight: 600; 
                              color: #1a1a2e; margin-bottom: 1.5rem;'>
                        🎯 Buy/Hold/Sell Recommendations
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Parse Buy/Hold/Sell recommendations from main AI response
                buy_tickers = []
                hold_tickers = []
                sell_tickers = []
                
                # Get valid tickers from KPI data to validate extracted tickers
                valid_tickers = set(st.session_state.kpi_data.keys()) if st.session_state.kpi_data else set()
                
                if 'ai_recommendations' in st.session_state and st.session_state.ai_recommendations:
                    recommendations_text = st.session_state.ai_recommendations
                    
                    # Extract Buy recommendations - simple pattern matching
                    buy_match = re.search(r'Buy:\s*([^\n]+)', recommendations_text, re.IGNORECASE)
                    if buy_match:
                        buy_content = buy_match.group(1).strip()
                        if buy_content and buy_content.lower() not in ['none', 'n/a', '']:
                            # Split by comma and clean up
                            buy_tickers = [t.strip().upper() for t in buy_content.split(',')]
                            # Filter to only valid tickers from KPI data
                            buy_tickers = [t for t in buy_tickers if t in valid_tickers]
                            buy_tickers = list(dict.fromkeys(buy_tickers))  # Remove duplicates
                    
                    # Extract Hold recommendations
                    hold_match = re.search(r'Hold:\s*([^\n]+)', recommendations_text, re.IGNORECASE)
                    if hold_match:
                        hold_content = hold_match.group(1).strip()
                        if hold_content and hold_content.lower() not in ['none', 'n/a', '']:
                            # Split by comma and clean up
                            hold_tickers = [t.strip().upper() for t in hold_content.split(',')]
                            # Filter to only valid tickers from KPI data
                            hold_tickers = [t for t in hold_tickers if t in valid_tickers]
                            hold_tickers = list(dict.fromkeys(hold_tickers))  # Remove duplicates
                    
                    # Extract Sell recommendations
                    sell_match = re.search(r'Sell:\s*([^\n]+)', recommendations_text, re.IGNORECASE)
                    if sell_match:
                        sell_content = sell_match.group(1).strip()
                        if sell_content and sell_content.lower() not in ['none', 'n/a', '']:
                            # Split by comma and clean up
                            sell_tickers = [t.strip().upper() for t in sell_content.split(',')]
                            # Filter to only valid tickers from KPI data
                            sell_tickers = [t for t in sell_tickers if t in valid_tickers]
                            sell_tickers = list(dict.fromkeys(sell_tickers))  # Remove duplicates
                
                # Display recommendations with clean formatting
                buy_display = ", ".join(buy_tickers) if buy_tickers else "None"
                hold_display = ", ".join(hold_tickers) if hold_tickers else "None"
                sell_display = ", ".join(sell_tickers) if sell_tickers else "None"
                
                # Escape HTML in ticker displays to prevent XSS
                buy_display_escaped = html.escape(buy_display)
                hold_display_escaped = html.escape(hold_display)
                sell_display_escaped = html.escape(sell_display)
                
                # Render the recommendations without background container
                # Buy recommendation
                st.markdown(f"""
                    <div style='display: flex; align-items: center; margin-bottom: 1.5rem;'>
                        <span class="recommendation-badge badge-buy" style='margin-right: 1rem;'>Buy</span>
                        <span style='font-size: 1.2rem; font-weight: 500; color: #1a1a2e; font-family: "Inter", sans-serif;'>{buy_display_escaped}</span>
                    </div>
                """, unsafe_allow_html=True)
                    
                # Hold recommendation
                st.markdown(f"""
                    <div style='display: flex; align-items: center; margin-bottom: 1.5rem;'>
                        <span class="recommendation-badge badge-hold" style='margin-right: 1rem;'>Hold</span>
                        <span style='font-size: 1.2rem; font-weight: 500; color: #1a1a2e; font-family: "Inter", sans-serif;'>{hold_display_escaped}</span>
                    </div>
                """, unsafe_allow_html=True)
                    
                # Sell recommendation
                st.markdown(f"""
                    <div style='display: flex; align-items: center; margin-bottom: 2rem;'>
                        <span class="recommendation-badge badge-sell" style='margin-right: 1rem;'>Sell</span>
                        <span style='font-size: 1.2rem; font-weight: 500; color: #1a1a2e; font-family: "Inter", sans-serif;'>{sell_display_escaped}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display Risk Assessment (Tier List)
                st.markdown("---")
                st.markdown("""
                <div style='margin: 2rem 0;'>
                    <h2 style='font-family: "Inter", sans-serif; font-weight: 600; 
                              color: #1a1a2e; margin-bottom: 1.5rem;'>
                        ⚠️ Risk Assessment
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Parse Risk Assessment from main AI response
                high_risk_tickers = []
                moderate_risk_tickers = []
                low_risk_tickers = []
                risk_details = {}  # Dictionary to store detailed risk info: {ticker: description}
                
                if 'ai_recommendations' in st.session_state and st.session_state.ai_recommendations:
                    recommendations_text = st.session_state.ai_recommendations
                    
                    # Extract High Risk recommendations
                    high_risk_match = re.search(r'High Risk:\s*([^\n]+)', recommendations_text, re.IGNORECASE)
                    if high_risk_match:
                        high_risk_content = high_risk_match.group(1).strip()
                        if high_risk_content and high_risk_content.lower() not in ['none', 'n/a', '']:
                            # Split by comma and clean up
                            high_risk_tickers = [t.strip().upper() for t in high_risk_content.split(',')]
                            # Filter to only valid tickers from KPI data
                            high_risk_tickers = [t for t in high_risk_tickers if t in valid_tickers]
                            high_risk_tickers = list(dict.fromkeys(high_risk_tickers))  # Remove duplicates
                    
                    # Extract Moderate Risk recommendations
                    moderate_risk_match = re.search(r'Moderate Risk:\s*([^\n]+)', recommendations_text, re.IGNORECASE)
                    if moderate_risk_match:
                        moderate_risk_content = moderate_risk_match.group(1).strip()
                        if moderate_risk_content and moderate_risk_content.lower() not in ['none', 'n/a', '']:
                            # Split by comma and clean up
                            moderate_risk_tickers = [t.strip().upper() for t in moderate_risk_content.split(',')]
                            # Filter to only valid tickers from KPI data
                            moderate_risk_tickers = [t for t in moderate_risk_tickers if t in valid_tickers]
                            moderate_risk_tickers = list(dict.fromkeys(moderate_risk_tickers))  # Remove duplicates
                    
                    # Extract Low Risk recommendations
                    low_risk_match = re.search(r'Low Risk:\s*([^\n]+)', recommendations_text, re.IGNORECASE)
                    if low_risk_match:
                        low_risk_content = low_risk_match.group(1).strip()
                        if low_risk_content and low_risk_content.lower() not in ['none', 'n/a', '']:
                            # Split by comma and clean up
                            low_risk_tickers = [t.strip().upper() for t in low_risk_content.split(',')]
                            # Filter to only valid tickers from KPI data
                            low_risk_tickers = [t for t in low_risk_tickers if t in valid_tickers]
                            low_risk_tickers = list(dict.fromkeys(low_risk_tickers))  # Remove duplicates
                    
                    # Extract detailed risk descriptions (format: "TICKER: Description")
                    # Look for patterns like "AAPL: Moderate risk due to..."
                    risk_detail_pattern = r'([A-Z]{2,5}(?:-USD)?):\s*([^\n]+)'
                    risk_detail_matches = re.findall(risk_detail_pattern, recommendations_text)
                    for ticker, description in risk_detail_matches:
                        ticker_upper = ticker.strip().upper()
                        if ticker_upper in valid_tickers:
                            # Clean up the description
                            desc = description.strip()
                            # Remove any trailing periods if they're part of the format
                            desc = desc.rstrip('.')
                            risk_details[ticker_upper] = desc
                
                # Display risk assessment with clean formatting
                high_risk_display = ", ".join(high_risk_tickers) if high_risk_tickers else "None"
                moderate_risk_display = ", ".join(moderate_risk_tickers) if moderate_risk_tickers else "None"
                low_risk_display = ", ".join(low_risk_tickers) if low_risk_tickers else "None"
                
                # Escape HTML in ticker displays to prevent XSS
                high_risk_display_escaped = html.escape(high_risk_display)
                moderate_risk_display_escaped = html.escape(moderate_risk_display)
                low_risk_display_escaped = html.escape(low_risk_display)
                
                # Helper function to render clickable tickers with risk details
                def render_clickable_tickers(tickers, risk_level):
                    if not tickers or tickers == ["None"]:
                        return "None"
                    
                    ticker_elements = []
                    for ticker in tickers:
                        if ticker in risk_details:
                            # Create expander for ticker with detailed risk info
                            with st.expander(f"**{ticker}**", expanded=False):
                                st.markdown(f"""
                                <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; 
                                            border-left: 3px solid #667eea; margin-top: 0.5rem;'>
                                    <p style='font-family: "Inter", sans-serif; font-size: 0.95rem; 
                                              color: #1a1a2e; line-height: 1.6; margin: 0;'>
                                        <strong>{ticker}:</strong> {html.escape(risk_details[ticker])}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            ticker_elements.append(ticker)
                        else:
                            ticker_elements.append(ticker)
                    
                    # Display tickers as clickable elements
                    ticker_html = []
                    for ticker in tickers:
                        if ticker in risk_details:
                            # Make ticker clickable with a link-style appearance
                            ticker_html.append(f'<span style="cursor: pointer; text-decoration: underline; color: #667eea; font-weight: 600;" onclick="document.querySelector(\'[data-ticker=\'{ticker}\']\').click()">{ticker}</span>')
                        else:
                            ticker_html.append(ticker)
                    
                    return ", ".join(ticker_html)
                
                # #region agent log
                _log_write({"id": "log_risk_assessment_rendering_start", "timestamp": int(time.time() * 1000), "location": "app/main.py:2475", "message": "Starting risk assessment rendering", "data": {"lowRiskCount": len(low_risk_tickers), "moderateRiskCount": len(moderate_risk_tickers), "highRiskCount": len(high_risk_tickers), "hypothesisId": "A"}, "sessionId": "debug-session", "runId": "run1"})
                # #endregion
                
                # Add CSS for styling risk ticker buttons
                st.markdown("""
                <style>
                /* Risk Ticker Button Styling */
                button[data-testid="baseButton-secondary"] {
                    font-family: 'Inter', sans-serif !important;
                    font-size: 1.2rem !important;
                    font-weight: 500 !important;
                    border-radius: 8px !important;
                    transition: all 0.2s ease !important;
                    border: none !important;
                }
                
                button[data-testid="baseButton-secondary"]:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15) !important;
                    opacity: 0.9 !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <style>
                /* Risk Modal Styles */
                .risk-modal {
                    display: none;
                    position: fixed;
                    z-index: 10000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    overflow: auto;
                    background-color: rgba(0, 0, 0, 0.5);
                    animation: fadeIn 0.3s;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                
                .risk-modal-content {
                    background-color: #ffffff;
                    margin: 5% auto;
                    padding: 0;
                    border-radius: 16px;
                    width: 90%;
                    max-width: 600px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    animation: slideDown 0.3s;
                }
                
                @keyframes slideDown {
                    from {
                        transform: translateY(-50px);
                        opacity: 0;
                    }
                    to {
                        transform: translateY(0);
                        opacity: 1;
                    }
                }
                
                .risk-modal-header {
                    padding: 1.5rem 2rem;
                    border-bottom: 1px solid #e9ecef;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-radius: 16px 16px 0 0;
                }
                
                .risk-modal-header.low {
                    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                    color: white;
                }
                
                .risk-modal-header.moderate {
                    background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%);
                    color: #856404;
                }
                
                .risk-modal-header.high {
                    background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
                    color: white;
                }
                
                .risk-modal-title {
                    font-family: 'Inter', sans-serif;
                    font-size: 1.5rem;
                    font-weight: 700;
                    margin: 0;
                }
                
                .risk-modal-close {
                    color: inherit;
                    font-size: 2rem;
                    font-weight: bold;
                    cursor: pointer;
                    line-height: 1;
                    opacity: 0.8;
                    transition: opacity 0.2s;
                }
                
                .risk-modal-close:hover {
                    opacity: 1;
                }
                
                .risk-modal-body {
                    padding: 2rem;
                    font-family: 'Inter', sans-serif;
                    font-size: 1rem;
                    line-height: 1.8;
                    color: #1a1a2e;
                }
                
                .risk-modal-body strong {
                    color: #667eea;
                    font-weight: 600;
                }
                
                .risk-ticker-button {
                    cursor: pointer;
                    transition: all 0.2s;
                    border-radius: 8px;
                    padding: 0.5rem 1rem;
                    display: inline-block;
                    text-align: center;
                    font-size: 1.2rem;
                    font-weight: 500;
                    font-family: 'Inter', sans-serif;
                }
                
                .risk-ticker-button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }
                </style>
                
                <div id="riskModal" class="risk-modal">
                    <div class="risk-modal-content">
                        <div class="risk-modal-header" id="riskModalHeader">
                            <h2 class="risk-modal-title" id="riskModalTitle">Risk Details</h2>
                            <span class="risk-modal-close" id="riskModalClose">&times;</span>
                        </div>
                        <div class="risk-modal-body" id="riskModalBody">
                            <p id="riskModalText"></p>
                        </div>
                    </div>
                </div>
                
                <script>
                // Simple test to verify JavaScript is running - this should ALWAYS show
                try {
                    console.log('=== RISK MODAL SCRIPT LOADING ===');
                    console.log('Document ready state:', document.readyState);
                    console.log('Window object exists:', typeof window !== 'undefined');
                    console.log('Document object exists:', typeof document !== 'undefined');
                } catch(e) {
                    console.error('Error in test script:', e);
                }
                
                (function() {
                    try {
                        // #region agent log
                        console.log('[DEBUG] Risk color script starting');
                        console.log('[DEBUG] Document ready state:', document.readyState);
                        // #endregion
                    
                    // Wait for DOM to be ready
                    function applyRiskColors() {
                        // #region agent log
                        console.log('[DEBUG] applyRiskColors called');
                        // #endregion
                        
                        // Find all expanders and apply colors based on their container
                        const expanders = document.querySelectorAll('[data-testid="stExpander"]');
                        
                        // #region agent log
                        console.log('[DEBUG] Found expanders:', expanders.length);
                        // #endregion
                        
                        expanders.forEach((expander, index) => {
                            const header = expander.querySelector('.streamlit-expanderHeader');
                            
                            // #region agent log
                            console.log('[DEBUG] Expander', index, 'header found:', !!header);
                            // #endregion
                            
                            if (!header) return;
                            
                            // Check parent containers for risk level
                            let parent = expander.parentElement;
                            let riskLevel = null;
                            let foundContainer = null;
                            
                            // #region agent log
                            console.log('[DEBUG] Expander', index, 'starting parent traversal');
                            // #endregion
                            
                            // Look for risk level in parent containers
                            while (parent && parent !== document.body) {
                                // #region agent log
                                const hasLowClass = parent.classList.contains('risk-expander-low');
                                const hasModerateClass = parent.classList.contains('risk-expander-moderate');
                                const hasHighClass = parent.classList.contains('risk-expander-high');
                                const dataRisk = parent.getAttribute('data-risk-level');
                                const id = parent.id || '';
                                console.log('[DEBUG] Expander', index, 'parent check:', {
                                    tagName: parent.tagName,
                                    hasLowClass,
                                    hasModerateClass,
                                    hasHighClass,
                                    dataRisk,
                                    id: id.substring(0, 20)
                                });
                                // #endregion
                                
                                if (parent.classList.contains('risk-expander-low') || 
                                    parent.getAttribute('data-risk-level') === 'low' ||
                                    (parent.id && parent.id.startsWith('risk-low-'))) {
                                    riskLevel = 'low';
                                    foundContainer = parent;
                                    break;
                                } else if (parent.classList.contains('risk-expander-moderate') || 
                                          parent.getAttribute('data-risk-level') === 'moderate' ||
                                          (parent.id && parent.id.startsWith('risk-moderate-'))) {
                                    riskLevel = 'moderate';
                                    foundContainer = parent;
                                    break;
                                } else if (parent.classList.contains('risk-expander-high') || 
                                          parent.getAttribute('data-risk-level') === 'high' ||
                                          (parent.id && parent.id.startsWith('risk-high-'))) {
                                    riskLevel = 'high';
                                    foundContainer = parent;
                                    break;
                                }
                                parent = parent.parentElement;
                            }
                            
                            // #region agent log
                            console.log('[DEBUG] Expander', index, 'riskLevel:', riskLevel, 'foundContainer:', !!foundContainer);
                            // #endregion
                            
                            // Apply styles based on risk level
                            if (riskLevel === 'low') {
                                header.style.backgroundColor = '#11998e';
                                header.style.border = '1px solid #0d7a6b';
                                header.style.color = '#ffffff';
                                header.style.borderRadius = '8px';
                                header.style.padding = '0.5rem 1rem';
                                header.style.fontWeight = '600';
                                // #region agent log
                                console.log('[DEBUG] Applied LOW risk styles to expander', index);
                                // #endregion
                            } else if (riskLevel === 'moderate') {
                                header.style.backgroundColor = '#ffc107';
                                header.style.border = '1px solid #e0a800';
                                header.style.color = '#856404';
                                header.style.borderRadius = '8px';
                                header.style.padding = '0.5rem 1rem';
                                header.style.fontWeight = '600';
                                // #region agent log
                                console.log('[DEBUG] Applied MODERATE risk styles to expander', index);
                                // #endregion
                            } else if (riskLevel === 'high') {
                                header.style.backgroundColor = '#ee0979';
                                header.style.border = '1px solid #c40761';
                                header.style.color = '#ffffff';
                                header.style.borderRadius = '8px';
                                header.style.padding = '0.5rem 1rem';
                                header.style.fontWeight = '600';
                                // #region agent log
                                console.log('[DEBUG] Applied HIGH risk styles to expander', index);
                                // #endregion
                            } else {
                                // #region agent log
                                console.log('[DEBUG] No risk level found for expander', index, 'header computed style:', window.getComputedStyle(header).backgroundColor);
                                // #endregion
                            }
                        });
                    }
                    
                    // Run immediately and after a short delay to catch dynamically added elements
                    applyRiskColors();
                    setTimeout(applyRiskColors, 100);
                    setTimeout(applyRiskColors, 500);
                    setTimeout(applyRiskColors, 1000);
                    
                    // Also run when new content is added (MutationObserver)
                    const observer = new MutationObserver(function(mutations) {
                        // #region agent log
                        console.log('[DEBUG] DOM mutation detected, reapplying colors');
                        // #endregion
                        applyRiskColors();
                    });
                    observer.observe(document.body, { childList: true, subtree: true });
                    
                    // Modal functionality
                    const modal = document.getElementById('riskModal');
                    const modalTitle = document.getElementById('riskModalTitle');
                    const modalBody = document.getElementById('riskModalBody');
                    const modalHeader = document.getElementById('riskModalHeader');
                    const modalText = document.getElementById('riskModalText');
                    const closeBtn = document.getElementById('riskModalClose');
                    
                    function openRiskModal(ticker, details, riskLevel) {
                        modalTitle.textContent = ticker + ' - Risk Assessment';
                        modalText.innerHTML = '<strong>' + ticker + ':</strong> ' + details;
                        
                        // Set header color based on risk level
                        modalHeader.className = 'risk-modal-header ' + riskLevel;
                        
                        modal.style.display = 'block';
                        document.body.style.overflow = 'hidden';
                    }
                    
                    function closeRiskModal() {
                        modal.style.display = 'none';
                        document.body.style.overflow = 'auto';
                    }
                    
                    if (closeBtn) {
                        closeBtn.onclick = closeRiskModal;
                    }
                    window.onclick = function(event) {
                        if (event.target === modal) {
                            closeRiskModal();
                        }
                    };
                    
                    // Use event delegation - attach to document to catch all clicks
                    // This works even if buttons are added dynamically
                    function attachClickHandler() {
                        // Remove any existing listener first
                        document.removeEventListener('click', handleDocumentClick);
                        // Add new listener
                        document.addEventListener('click', handleDocumentClick, true); // Use capture phase
                        // #region agent log
                        console.log('[DEBUG] Click handler attached to document');
                        // #endregion
                    }
                    
                    function handleDocumentClick(e) {
                        // #region agent log
                        console.log('[DEBUG] Click detected! Target:', e.target.tagName, 'Classes:', e.target.className, 'Text:', e.target.textContent?.substring(0, 20));
                        // #endregion
                        
                        // Check if clicked element or any parent has the risk-ticker-button class
                        let element = e.target;
                        let button = null;
                        let depth = 0;
                        
                        while (element && element !== document.body && depth < 10) {
                            if (element.classList && element.classList.contains('risk-ticker-button')) {
                                button = element;
                                break;
                            }
                            element = element.parentElement;
                            depth++;
                        }
                        
                        if (button) {
                            // #region agent log
                            console.log('[DEBUG] Found risk ticker button! Element:', button.tagName, 'Ticker:', button.getAttribute('data-ticker'));
                            // #endregion
                            
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const ticker = button.getAttribute('data-ticker');
                            const details = button.getAttribute('data-details');
                            const riskLevel = button.getAttribute('data-risk-level');
                            
                            // #region agent log
                            console.log('[DEBUG] Risk ticker button clicked! Ticker:', ticker, 'RiskLevel:', riskLevel, 'Has details:', !!details);
                            // #endregion
                            
                            if (ticker && details && riskLevel) {
                                openRiskModal(ticker, details, riskLevel);
                            } else {
                                // #region agent log
                                console.log('[DEBUG] Missing attributes - ticker:', ticker, 'details:', !!details, 'riskLevel:', riskLevel);
                                // #endregion
                            }
                            return false;
                        }
                    }
                    
                    // Attach immediately
                    attachClickHandler();
                    
                    // Make ticker buttons clickable (legacy support)
                    function setupTickerButtons() {
                        // #region agent log
                        console.log('[DEBUG] setupTickerButtons called');
                        // #endregion
                        const tickerButtons = document.querySelectorAll('.risk-ticker-button');
                        
                        // #region agent log
                        console.log('[DEBUG] Found ticker buttons:', tickerButtons.length);
                        if (tickerButtons.length > 0) {
                            console.log('[DEBUG] First button:', tickerButtons[0].outerHTML.substring(0, 200));
                        }
                        // #endregion
                        
                        tickerButtons.forEach((button, index) => {
                            // #region agent log
                            console.log('[DEBUG] Processing button', index, 'has listener:', button.hasAttribute('data-listener'));
                            // #endregion
                            
                            // Ensure cursor style is set
                            button.style.cursor = 'pointer';
                            button.style.userSelect = 'none';
                            button.style.pointerEvents = 'auto';
                        });
                    }
                    
                    // Run setup after DOM is ready and when content loads
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', setupTickerButtons);
                    } else {
                        setupTickerButtons();
                    }
                    
                    setTimeout(setupTickerButtons, 100);
                    setTimeout(setupTickerButtons, 500);
                    setTimeout(setupTickerButtons, 1000);
                    setTimeout(setupTickerButtons, 2000);
                    
                    // Also setup when new content is added
                    const buttonObserver = new MutationObserver(function(mutations) {
                        // #region agent log
                        console.log('[DEBUG] DOM mutation detected, checking for buttons');
                        // #endregion
                        setupTickerButtons();
                    });
                    buttonObserver.observe(document.body, { childList: true, subtree: true });
                    
                    // NEW: Style Risk Assessment buttons based on data-risk-buttons wrapper divs
                    // This is more reliable than DOM traversal
                    function styleRiskAssessmentButtons() {
                        // Find all buttons and their risk level using data-risk-buttons wrapper
                        const riskLevels = ['low', 'moderate', 'high'];
                        
                        riskLevels.forEach(riskLevel => {
                            // Find the wrapper div with data-risk-buttons attribute
                            const wrapper = document.querySelector(`[data-risk-buttons="${riskLevel}"]`);
                            if (!wrapper) return;
                            
                            // Find all buttons within this wrapper
                            const buttons = wrapper.querySelectorAll('button[data-testid="baseButton-secondary"]');
                            
                            buttons.forEach(btn => {
                                // Apply styles based on risk level
                                if (riskLevel === 'low') {
                                    btn.style.setProperty('background-color', '#11998e', 'important');
                                    btn.style.setProperty('color', '#ffffff', 'important');
                                    btn.style.setProperty('font-size', '1.2rem', 'important');
                                    btn.style.setProperty('font-weight', '500', 'important');
                                    btn.style.setProperty('border', 'none', 'important');
                                } else if (riskLevel === 'moderate') {
                                    btn.style.setProperty('background-color', '#ffc107', 'important');
                                    btn.style.setProperty('color', '#856404', 'important');
                                    btn.style.setProperty('font-size', '1.2rem', 'important');
                                    btn.style.setProperty('font-weight', '500', 'important');
                                    btn.style.setProperty('border', 'none', 'important');
                                } else if (riskLevel === 'high') {
                                    btn.style.setProperty('background-color', '#ee0979', 'important');
                                    btn.style.setProperty('color', '#ffffff', 'important');
                                    btn.style.setProperty('font-size', '1.2rem', 'important');
                                    btn.style.setProperty('font-weight', '500', 'important');
                                    btn.style.setProperty('border', 'none', 'important');
                                }
                            });
                        });
                    }
                    
                    // Run styleRiskAssessmentButtons after DOM is ready
                    setTimeout(styleRiskAssessmentButtons, 200);
                    setTimeout(styleRiskAssessmentButtons, 500);
                    setTimeout(styleRiskAssessmentButtons, 1000);
                    setTimeout(styleRiskAssessmentButtons, 2000);
                    
                    // Also run when new content is added
                    const riskButtonObserver = new MutationObserver(function(mutations) {
                        styleRiskAssessmentButtons();
                    });
                    riskButtonObserver.observe(document.body, { childList: true, subtree: true });
                })();
                </script>
                """, unsafe_allow_html=True)
                
                # Render the risk assessment with clickable tickers using expanders
                # Low Risk (first)
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown("""
                    <div style='display: flex; align-items: center;' data-risk-section="low">
                        <span class="risk-badge risk-low" style='font-size: 0.875rem; padding: 0.5rem 1rem;'>Low Risk</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div data-risk-buttons="low">', unsafe_allow_html=True)
                    if low_risk_tickers:
                        # Display tickers inline, each as a clickable expander
                        ticker_cols = st.columns(len(low_risk_tickers))
                        for idx, ticker in enumerate(low_risk_tickers):
                            with ticker_cols[idx]:
                                if ticker in risk_details:
                                    # Use Streamlit button with session state to trigger modal
                                    button_key = f"risk_btn_low_{ticker}"
                                    
                                    if st.button(ticker, key=button_key, use_container_width=True, type="secondary"):
                                        st.session_state[f"show_modal_{ticker}"] = True
                                        st.rerun()
                                    
                                    
                                    # Show modal details if button was clicked
                                    if st.session_state.get(f"show_modal_{ticker}", False):
                                        st.markdown(f"""
                                        <div style='background: linear-gradient(135deg, rgba(17, 153, 142, 0.1) 0%, rgba(56, 239, 125, 0.1) 100%); 
                                                    padding: 1.5rem; border-radius: 12px; margin: 0.5rem 0; 
                                                    border-left: 4px solid #11998e;'>
                                            <h3 style='color: #11998e; margin-top: 0;'>{ticker} - Risk Assessment</h3>
                                            <p style='font-size: 1rem; line-height: 1.6; color: #1a1a2e;'>
                                                <strong>{ticker}:</strong> {html.escape(risk_details[ticker])}
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        # Add close button
                                        if st.button("Close", key=f"close_{ticker}"):
                                            st.session_state[f"show_modal_{ticker}"] = False
                                            st.rerun()
                                else:
                                    st.markdown(f'<div style="text-align: center; font-size: 1.2rem; font-weight: 500; color: #ffffff; background: #11998e; padding: 0.5rem 1rem; border-radius: 8px; font-family: \'Inter\', sans-serif;">{ticker}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="font-size: 1.2rem; font-weight: 500; color: #1a1a2e; font-family: \'Inter\', sans-serif;">None</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Moderate Risk (second)
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown("""
                    <div style='display: flex; align-items: center;' data-risk-section="moderate">
                        <span class="risk-badge risk-moderate" style='font-size: 0.875rem; padding: 0.5rem 1rem;'>Moderate Risk</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div data-risk-buttons="moderate">', unsafe_allow_html=True)
                    if moderate_risk_tickers:
                        # Display tickers in a centered grid with equal-size items and gaps between them
                        max_cols = min(len(moderate_risk_tickers), 8)
                        
                        # Split tickers into rows
                        rows = []
                        for i in range(0, len(moderate_risk_tickers), max_cols):
                            rows.append(moderate_risk_tickers[i:i + max_cols])
                        
                        # Display each row with gap between rows
                        for row_idx, row_tickers in enumerate(rows):
                            # Add gap between rows (except for the first row)
                            if row_idx > 0:
                                st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Create columns for this row
                            try:
                                ticker_cols = st.columns(max_cols, gap="medium")
                            except TypeError:
                                # Fallback for older Streamlit versions without 'gap' parameter
                                ticker_cols = st.columns(max_cols)
                            
                            # Start items from the left (no centering)
                            offset = 0
                            
                            for idx, ticker in enumerate(row_tickers):
                                col_index = offset + idx
                                with ticker_cols[col_index]:
                                    if ticker in risk_details:
                                        # Use Streamlit button with session state to trigger modal
                                        button_key = f"risk_btn_moderate_{ticker}"
                                        if st.button(ticker, key=button_key, use_container_width=True, type="secondary"):
                                            st.session_state[f"show_modal_{ticker}"] = True
                                            st.rerun()
                                        
                                        # Show modal details if button was clicked
                                        if st.session_state.get(f"show_modal_{ticker}", False):
                                            st.markdown(f"""
                                            <div style='background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%); 
                                                        padding: 1.5rem; border-radius: 12px; margin: 0.5rem 0; 
                                                        border-left: 4px solid #ffc107;'>
                                                <h3 style='color: #856404; margin-top: 0;'>{ticker} - Risk Assessment</h3>
                                                <p style='font-size: 1rem; line-height: 1.6; color: #1a1a2e;'>
                                                    <strong>{ticker}:</strong> {html.escape(risk_details[ticker])}
                                                </p>
                                            </div>
                                            """, unsafe_allow_html=True)
                                            # Add close button
                                            if st.button("Close", key=f"close_{ticker}"):
                                                st.session_state[f"show_modal_{ticker}"] = False
                                                st.rerun()
                                    else:
                                        st.markdown(f'<div style="text-align: center; font-size: 1.2rem; font-weight: 500; color: #ffffff; background: #ffc107; padding: 0.5rem 1rem; border-radius: 8px; font-family: \'Inter\', sans-serif;">{ticker}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="font-size: 1.2rem; font-weight: 500; color: #1a1a2e; font-family: \'Inter\', sans-serif;">None</span>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # High Risk (third)
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown("""
                    <div style='display: flex; align-items: center;' data-risk-section="high">
                        <span class="risk-badge risk-high" style='font-size: 0.875rem; padding: 0.5rem 1rem;'>High Risk</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div data-risk-buttons="high">', unsafe_allow_html=True)
                    if high_risk_tickers:
                        # Display tickers inline, each as a clickable expander
                        ticker_cols = st.columns(len(high_risk_tickers))
                        for idx, ticker in enumerate(high_risk_tickers):
                            with ticker_cols[idx]:
                                if ticker in risk_details:
                                    # Use Streamlit button with session state to trigger modal
                                    button_key = f"risk_btn_high_{ticker}"
                                    if st.button(ticker, key=button_key, use_container_width=True, type="secondary"):
                                        st.session_state[f"show_modal_{ticker}"] = True
                                        st.rerun()
                                    
                                    # Show modal details if button was clicked
                                    if st.session_state.get(f"show_modal_{ticker}", False):
                                        st.markdown(f"""
                                        <div style='background: linear-gradient(135deg, rgba(238, 9, 121, 0.1) 0%, rgba(255, 106, 0, 0.1) 100%); 
                                                    padding: 1.5rem; border-radius: 12px; margin: 0.5rem 0; 
                                                    border-left: 4px solid #ee0979;'>
                                            <h3 style='color: #ee0979; margin-top: 0;'>{ticker} - Risk Assessment</h3>
                                            <p style='font-size: 1rem; line-height: 1.6; color: #1a1a2e;'>
                                                <strong>{ticker}:</strong> {html.escape(risk_details[ticker])}
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        # Add close button
                                        if st.button("Close", key=f"close_{ticker}"):
                                            st.session_state[f"show_modal_{ticker}"] = False
                                            st.rerun()
                                else:
                                    st.markdown(f'<div style="text-align: center; font-size: 1.2rem; font-weight: 500; color: #ffffff; background: #ee0979; padding: 0.5rem 1rem; border-radius: 8px; font-family: \'Inter\', sans-serif;">{ticker}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="font-size: 1.2rem; font-weight: 500; color: #1a1a2e; font-family: \'Inter\', sans-serif;">None</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Add script to ensure buttons are clickable after all content is rendered
                st.markdown("""
                <script>
                (function() {
                    // Force setup of ticker buttons after all content is rendered
                    function forceSetupButtons() {
                        const tickerButtons = document.querySelectorAll('.risk-ticker-button');
                        console.log('[DEBUG] Force setup found buttons:', tickerButtons.length);
                        
                        tickerButtons.forEach((button, index) => {
                            if (!button.hasAttribute('data-listener')) {
                                button.setAttribute('data-listener', 'true');
                                const ticker = button.getAttribute('data-ticker');
                                const details = button.getAttribute('data-details');
                                const riskLevel = button.getAttribute('data-risk-level');
                                
                                console.log('[DEBUG] Force setup button', index, 'ticker:', ticker);
                                
                                button.onclick = function(e) {
                                    e.preventDefault();
                                    e.stopPropagation();
                                    console.log('[DEBUG] Force setup button clicked:', ticker);
                                    
                                    const modal = document.getElementById('riskModal');
                                    const modalTitle = document.getElementById('riskModalTitle');
                                    const modalText = document.getElementById('riskModalText');
                                    const modalHeader = document.getElementById('riskModalHeader');
                                    
                                    if (modal && modalTitle && modalText && modalHeader) {
                                        modalTitle.textContent = ticker + ' - Risk Assessment';
                                        modalText.innerHTML = '<strong>' + ticker + ':</strong> ' + details;
                                        modalHeader.className = 'risk-modal-header ' + riskLevel;
                                        modal.style.display = 'block';
                                        document.body.style.overflow = 'hidden';
                                    }
                                    return false;
                                };
                                
                                button.style.cursor = 'pointer';
                                button.style.userSelect = 'none';
                            }
                        });
                    }
                    
                    // Run multiple times to catch all render cycles
                    setTimeout(forceSetupButtons, 100);
                    setTimeout(forceSetupButtons, 500);
                    setTimeout(forceSetupButtons, 1000);
                    setTimeout(forceSetupButtons, 2000);
                    setTimeout(forceSetupButtons, 3000);
                    
                    // Also observe for changes
                    const observer = new MutationObserver(function() {
                        forceSetupButtons();
                    });
                    observer.observe(document.body, { childList: true, subtree: true });
                })();
                </script>
                """, unsafe_allow_html=True)
                
                # Display Stock-by-Stock Analysis table (moved after recommendations)
                if st.session_state.kpi_data:
                    st.markdown("---")
                    st.markdown("""
                    <div style='margin: 2rem 0;'>
                        <h2 style='font-family: "Inter", sans-serif; font-weight: 600; 
                                  color: #1a1a2e; margin-bottom: 1.5rem;'>
                            📊 Stock-by-Stock Analysis
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create Stock-by-Stock Analysis table with separate columns for each metric
                    stock_analysis_data = []
                    sorted_tickers = sorted(st.session_state.kpi_data.keys())
                    
                    for ticker in sorted_tickers:
                        kpis = st.session_state.kpi_data[ticker]
                        
                        row = {'Ticker': ticker}
                        
                        # RSI Column
                        rsi_value = kpis.get('RSI')
                        if rsi_value is not None:
                            rsi_display = f'{rsi_value:.2f}'
                            if rsi_value < 30:
                                rsi_status = "low, suggesting potential oversold conditions"
                            elif rsi_value > 70:
                                rsi_status = "high, indicating overbought conditions"
                            elif 45 <= rsi_value <= 55:
                                rsi_status = "neutral"
                            elif rsi_value > 50:
                                rsi_status = "above 50, indicating bullish momentum"
                            else:
                                rsi_status = "moderate"
                            row['RSI'] = f"RSI is {rsi_status} ({rsi_display})"
                        else:
                            row['RSI'] = "RSI is N/A"
                        
                        # Bollinger Bands Column
                        bb_data = kpis.get('Bollinger Bands')
                        if bb_data and isinstance(bb_data, dict):
                            current_price = bb_data.get('Current Price')
                            middle_band = bb_data.get('Middle Band')
                            if current_price is not None and middle_band is not None:
                                price_diff_pct = abs((current_price - middle_band) / middle_band) * 100
                                if price_diff_pct < 1:  # Within 1% of middle band
                                    bb_status = "near the middle Bollinger Band"
                                elif current_price > middle_band:
                                    bb_status = "above the middle Bollinger Band"
                                else:
                                    bb_status = "below the middle Bollinger Band, indicating potential undervaluation"
                                row['Bollinger Band'] = f"The current price is {bb_status}"
                            else:
                                row['Bollinger Band'] = "Bollinger Bands data is N/A"
                        else:
                            row['Bollinger Band'] = "Bollinger Bands data is N/A"
                        
                        # MACD Column
                        macd_data = kpis.get('MACD')
                        if macd_data and isinstance(macd_data, dict):
                            macd_value = macd_data.get('MACD')
                            signal_value = macd_data.get('Signal Line')
                            if macd_value is not None and signal_value is not None:
                                if macd_value > signal_value:
                                    macd_status = "above the signal line, suggesting bullish momentum"
                                else:
                                    macd_status = "below the signal line, indicating bearish momentum"
                                row['MACD'] = f"The MACD is {macd_status}"
                            elif macd_value is not None:
                                row['MACD'] = f"MACD is {macd_value:.4f}"
                            else:
                                row['MACD'] = "MACD data is N/A"
                        else:
                            row['MACD'] = "MACD data is N/A"
                        
                        # P/E Ratio Column
                        pe_value = kpis.get('P/E Ratio')
                        if pe_value is not None:
                            pe_display = f'{pe_value:.2f}'
                            # Add interpretation for P/E Ratio
                            if pe_value < 15:
                                pe_status = "low, suggesting potential undervaluation"
                            elif pe_value > 25:
                                pe_status = "high, suggesting potential overvaluation or high growth expected"
                            else:
                                pe_status = "moderate"
                            row['P/E Ratio'] = f"P/E Ratio is {pe_status} ({pe_display})"
                        else:
                            row['P/E Ratio'] = "P/E Ratio is N/A"
                        
                        stock_analysis_data.append(row)
                    
                    if stock_analysis_data:
                        stock_analysis_df = pd.DataFrame(stock_analysis_data)
                        # Reorder columns: Ticker, RSI, Bollinger Band, MACD, P/E Ratio
                        column_order = ['Ticker', 'RSI', 'Bollinger Band', 'MACD', 'P/E Ratio']
                        stock_analysis_df = stock_analysis_df[column_order]
                        
                        # Apply styling for text wrapping with auto-sizing
                        styled_df = stock_analysis_df.style.set_properties(**{
                            'white-space': 'normal',
                            'word-wrap': 'break-word',
                            'text-align': 'left',
                            'width': 'auto',
                            'max-width': 'none'
                        }).set_table_styles([
                            {
                                'selector': 'td',
                                'props': [
                                    ('white-space', 'normal'),
                                    ('word-wrap', 'break-word'),
                                    ('padding', '15px 10px'),
                                    ('vertical-align', 'top'),
                                    ('line-height', '1.6'),
                                    ('min-height', '60px'),
                                    ('width', 'auto'),
                                    ('max-width', 'none')
                                ]
                            },
                            {
                                'selector': 'th',
                                'props': [
                                    ('padding', '15px 10px'),
                                    ('white-space', 'normal'),
                                    ('word-wrap', 'break-word'),
                                    ('width', 'auto'),
                                    ('max-width', 'none')
                                ]
                            },
                            {
                                'selector': 'table',
                                'props': [
                                    ('table-layout', 'auto'),
                                    ('width', '100%')
                                ]
                            }
                        ])
                        
                        # Display the table with styling
                        st.dataframe(styled_df, use_container_width=True, height=400)
                        
                        # Add comprehensive CSS for automatic auto-sizing (especially for Bollinger Band column)
                        st.markdown("""
                        <style>
                        /* Force auto-sizing on all dataframe tables */
                        div[data-testid="stDataFrame"] table {
                            table-layout: auto !important;
                            width: 100% !important;
                        }
                        /* Remove any fixed column widths - critical for auto-sizing */
                        div[data-testid="stDataFrame"] colgroup,
                        div[data-testid="stDataFrame"] col {
                            display: none !important;
                            width: auto !important;
                        }
                        /* Auto-size all table cells - especially important for Bollinger Band column */
                        div[data-testid="stDataFrame"] td {
                            white-space: normal !important;
                            word-wrap: break-word !important;
                            padding: 15px 10px !important;
                            vertical-align: top !important;
                            line-height: 1.6 !important;
                            min-height: 60px !important;
                            height: auto !important;
                            width: auto !important;
                            max-width: none !important;
                            min-width: auto !important;
                        }
                        div[data-testid="stDataFrame"] th {
                            padding: 15px 10px !important;
                            white-space: normal !important;
                            word-wrap: break-word !important;
                            width: auto !important;
                            max-width: none !important;
                            min-width: auto !important;
                        }
                        div[data-testid="stDataFrame"] tr {
                            height: auto !important;
                            min-height: 60px !important;
                        }
                        /* Override any inline styles that might set fixed widths */
                        div[data-testid="stDataFrame"] td[style*="width"],
                        div[data-testid="stDataFrame"] th[style*="width"] {
                            width: auto !important;
                            min-width: auto !important;
                            max-width: none !important;
                        }
                        /* Specifically target Bollinger Band column for auto-sizing */
                        div[data-testid="stDataFrame"] td:nth-child(3),
                        div[data-testid="stDataFrame"] th:nth-child(3) {
                            width: auto !important;
                            min-width: auto !important;
                            max-width: none !important;
                            white-space: normal !important;
                            word-wrap: break-word !important;
                        }
                        /* Ensure all columns auto-size based on content */
                        div[data-testid="stDataFrame"] table td,
                        div[data-testid="stDataFrame"] table th {
                            width: auto !important;
                            min-width: fit-content !important;
                            max-width: none !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                
                # Merge portfolio_allocations into portfolio_charts if they exist
                if 'portfolio_allocations' in st.session_state and st.session_state.portfolio_allocations:
                    if 'portfolio_charts' not in st.session_state:
                        st.session_state.portfolio_charts = {}
                    # Merge the allocations
                    for portfolio_type, allocations in st.session_state.portfolio_allocations.items():
                        if allocations:  # Only add if there are allocations
                            st.session_state.portfolio_charts[portfolio_type] = allocations
                
                # Generate and display pie charts for portfolio allocations
                if 'portfolio_charts' in st.session_state and st.session_state.portfolio_charts:
                    st.markdown("---")
                    st.markdown("""
                    <div style='margin: 2rem 0;'>
                        <h2 style='font-family: "Inter", sans-serif; font-weight: 600; 
                                  color: #1a1a2e; margin-bottom: 1.5rem;'>
                            📊 Portfolio Allocation Charts
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create columns for portfolio charts (up to 3 columns)
                    num_portfolios = len(st.session_state.portfolio_charts)
                    portfolio_cols = st.columns(min(num_portfolios, 3))
                    
                    # Modern color palettes for each portfolio type
                    color_palettes = {
                        'Conservative': px.colors.qualitative.Pastel,
                        'Balanced': px.colors.qualitative.Set3,
                        'Aggressive': px.colors.qualitative.Bold
                    }
                    
                    for idx, (portfolio_type, allocations) in enumerate(st.session_state.portfolio_charts.items()):
                        if allocations and len(allocations) > 0:
                            with portfolio_cols[idx % len(portfolio_cols)]:
                                # Prepare data
                                labels = list(allocations.keys())
                                values = list(allocations.values())
                                
                                # Get color palette for this portfolio type
                                palette = color_palettes.get(portfolio_type, px.colors.qualitative.Pastel)
                                colors = [palette[i % len(palette)] for i in range(len(labels))]
                                
                                # Create interactive Plotly pie chart using plotly.express for simplicity
                                fig = px.pie(
                                    values=values,
                                    names=labels,
                                    title=f'{portfolio_type} Portfolio',
                                    color_discrete_sequence=colors,
                                    hole=0.3  # Creates a donut chart
                                )
                                
                                # Update traces for better styling
                                fig.update_traces(
                                    textposition='inside',
                                    textinfo='percent+label',
                                    textfont=dict(
                                        size=12,
                                        family='Inter',
                                        color='#1a1a2e'
                                    ),
                                    marker=dict(
                                        line=dict(color='#FFFFFF', width=2)
                                    ),
                                    hovertemplate='<b>%{label}</b><br>' +
                                                  'Allocation: %{percent}<br>' +
                                                  'Value: %{value}%<br>' +
                                                  '<extra></extra>',
                                    pull=[0.02] * len(labels)  # Slight separation
                                )
                                
                                # Update layout for modern styling
                                fig.update_layout(
                                    title={
                                        'text': f'{portfolio_type} Portfolio',
                                        'x': 0.5,
                                        'xanchor': 'center',
                                        'font': {
                                            'size': 18,
                                            'family': 'Inter',
                                            'color': '#667eea'
                                        }
                                    },
                                    showlegend=True,
                                    legend=dict(
                                        orientation="v",
                                        yanchor="middle",
                                        y=0.5,
                                        xanchor="left",
                                        x=1.05,
                                        font=dict(
                                            family='Inter',
                                            size=11,
                                            color='#1a1a2e'
                                        )
                                    ),
                                    height=500,
                                    margin=dict(l=20, r=20, t=60, b=20),
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)'
                                )
                                
                                # Display the chart
                                st.plotly_chart(fig, use_container_width=True)
                    
                    # Clear portfolio charts after display to avoid re-rendering on rerun
                    # But keep it for the current session
                    # del st.session_state.portfolio_charts
                
                # Manual refresh button (optional)
                if st.button("🔄 Regenerate Recommendations", type="secondary"):
                    # Increment regenerate counter to force cache invalidation
                    if 'ai_recommendations_regenerate_counter' not in st.session_state:
                        st.session_state.ai_recommendations_regenerate_counter = 0
                    st.session_state.ai_recommendations_regenerate_counter += 1
                    # Clear session state recommendations to force regeneration
                    if 'ai_recommendations' in st.session_state:
                        del st.session_state.ai_recommendations
                    if 'ai_recommendations_kpi_hash' in st.session_state:
                        del st.session_state.ai_recommendations_kpi_hash
                    st.rerun()

if __name__ == "__main__":
    # #region agent log
    try:
        _log_write({"id": "log_main_call_start", "timestamp": int(time.time() * 1000), "location": "app/main.py:2414", "message": "About to call main()", "data": {"hypothesisId": "E"}, "sessionId": "debug-session", "runId": "run1"})
        # #endregion
        main()
        # #region agent log
        _log_write({"id": "log_main_call_success", "timestamp": int(time.time() * 1000), "location": "app/main.py:2418", "message": "Main function completed successfully", "data": {"hypothesisId": "E"}, "sessionId": "debug-session", "runId": "run1"})
        # #endregion
    except Exception as e:
        # #region agent log
        _log_write({"id": "log_main_call_error", "timestamp": int(time.time() * 1000), "location": "app/main.py:2422", "message": "Error in main() execution", "data": {"error": str(e), "errorType": type(e).__name__, "hypothesisId": "E"}, "sessionId": "debug-session", "runId": "run1"})
        # #endregion
        raise
    # #endregion

