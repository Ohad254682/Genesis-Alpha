"""
KPI calculation functions for stock analysis
"""
import yfinance as yf
import pandas as pd
import numpy as np
import time
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout, RequestException
from utils.data_cache import get_ticker_history, get_ticker_info as get_ticker_info_cached, get_multiple_tickers_history as get_multiple_tickers_history_cached

# Try to import streamlit for caching (optional - if not available, caching won't work)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create a dummy decorator if streamlit is not available
    def cache_data(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    st = type('obj', (object,), {'cache_data': cache_data})()


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def calculate_kpis(tickers, start_date, end_date):
    """
    Calculate KPIs for a list of stocks over a given time period.
    Uses get_multiple_tickers_history_cached() to download all tickers at once for better performance.
    Cached to improve performance and reduce API calls.

    Parameters:
    tickers (list): A list of stock ticker symbols.
    start_date (str): The start date for the analysis.
    end_date (str): The end date for the analysis.

    Returns:
    dict: A dictionary containing the KPIs for each stock.
    """
    kpi_data = {}
    
    # Download all tickers at once using get_multiple_tickers_history_cached()
    # This is more efficient than downloading each ticker separately
    try:
        all_data = get_multiple_tickers_history_cached(tickers, start_date, end_date)
    except (RequestsConnectionError, Timeout, RequestException) as e:
        error_msg = (
            f"Connection error downloading data: {str(e)}\n"
            "Please check your internet connection or VPN settings."
        )
        print(error_msg)
        raise RequestsConnectionError(error_msg) from e
    except Exception as e:
        error_msg = f"Error downloading data: {str(e)}"
        print(error_msg)
        raise Exception(error_msg) from e
    
    if all_data.empty:
        return kpi_data
    
    # Process each ticker from the combined DataFrame
    for ticker in tickers:
        try:
            # Skip if ticker not in the downloaded data
            if ticker not in all_data.columns:
                continue
            
            # Get the Close prices for this ticker (as a Series)
            data_series = all_data[ticker].dropna()
            
            if data_series.empty or len(data_series) < 14:
                continue
                
            kpi_data[ticker] = {}

            # Calculate RSI
            delta = data_series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            kpi_data[ticker]['RSI'] = rsi.iloc[-1] if not rsi.empty else None

            # Calculate Bollinger Bands
            middle_band = data_series.rolling(window=20).mean()
            upper_band = middle_band + 2 * data_series.rolling(window=20).std()
            lower_band = middle_band - 2 * data_series.rolling(window=20).std()
            kpi_data[ticker]['Bollinger Bands'] = {
                'Middle Band': middle_band.iloc[-1] if not middle_band.empty else None,
                'Upper Band': upper_band.iloc[-1] if not upper_band.empty else None,
                'Lower Band': lower_band.iloc[-1] if not lower_band.empty else None,
                'Current Price': data_series.iloc[-1] if not data_series.empty else None
            }

            # Calculate P/E Ratio - use cached ticker info function
            # EPS (Earnings Per Share) represents the company's profit per share.
            # Formula: EPS = Net Income / Number of Outstanding Shares
            # Example:
            # If a company earned $100M and has 50M shares outstanding:
            # EPS = 100 / 50 = 2
            # This value is commonly used to calculate the P/E ratio (Price / EPS).
            try:
                eps = get_ticker_info_cached(ticker, 'trailingEps')
                if eps and eps != 0:
                    pe_ratio = data_series.iloc[-1] / eps
                    kpi_data[ticker]['P/E Ratio'] = pe_ratio
                else:
                    kpi_data[ticker]['P/E Ratio'] = None
            except Exception:
                kpi_data[ticker]['P/E Ratio'] = None

            # Calculate Beta - use cached ticker info function
            try:
                beta = get_ticker_info_cached(ticker, 'beta')
                kpi_data[ticker]['Beta'] = beta
            except Exception:
                kpi_data[ticker]['Beta'] = None

            # Calculate MACD
            ema_12 = data_series.ewm(span=12, adjust=False).mean()
            ema_26 = data_series.ewm(span=26, adjust=False).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9, adjust=False).mean()
            kpi_data[ticker]['MACD'] = {
                'MACD': macd.iloc[-1] if not macd.empty else None,
                'Signal Line': signal.iloc[-1] if not signal.empty else None
            }
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    return kpi_data


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_beta_values(tickers, start_date, end_date):
    """
    Get beta values for a list of tickers.
    Cached to improve performance and reduce API calls.
    
    Parameters:
    tickers (list): List of stock ticker symbols.
    start_date (str): Start date for analysis.
    end_date (str): End date for analysis.
    
    Returns:
    dict: Dictionary of ticker to beta value mappings.
    """
    betas = {}
    for ticker in tickers:
        try:
            # Use centralized cached function for ticker info
            beta = get_ticker_info_cached(ticker, 'beta')
            if beta is not None:
                betas[ticker] = beta
        except Exception:
            continue
    return betas

