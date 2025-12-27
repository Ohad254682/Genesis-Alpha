"""
KPI calculation functions for stock analysis
"""
import yfinance as yf
import pandas as pd
import numpy as np
import time
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout, RequestException
from utils.data_cache import get_ticker_history, get_ticker_info as get_ticker_info_cached

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


def _download_with_retry(ticker, start_date, end_date, max_retries=3, retry_delay=2):
    """
    Download stock data with retry logic for handling connection errors.
    Uses centralized data cache to avoid redundant downloads.
    
    Parameters:
    ticker (str): Stock ticker symbol.
    start_date (str): Start date for the analysis.
    end_date (str): End date for the analysis.
    max_retries (int): Maximum number of retry attempts.
    retry_delay (float): Delay between retries in seconds.
    
    Returns:
    pd.DataFrame: Historical stock data.
    
    Raises:
    ConnectionError: If connection fails after all retries.
    """
    # Use centralized cached function - it already has retry logic built in
    try:
        data = get_ticker_history(ticker, start_date, end_date, max_retries, retry_delay)
        return data
    except Exception as e:
        # Re-raise as ConnectionError for compatibility
        raise ConnectionError(
            f"Failed to download data for {ticker}: {str(e)}"
        ) from e


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def calculate_kpis(tickers, start_date, end_date):
    """
    Calculate KPIs for a list of stocks over a given time period.
    Cached to improve performance and reduce API calls.

    Parameters:
    tickers (list): A list of stock ticker symbols.
    start_date (str): The start date for the analysis.
    end_date (str): The end date for the analysis.

    Returns:
    dict: A dictionary containing the KPIs for each stock.
    """
    kpi_data = {}
    for ticker in tickers:
        try:
            # Download historical stock data with retry logic (uses cached function)
            data = _download_with_retry(ticker, start_date, end_date)
            
            if data.empty:
                continue
                
            kpi_data[ticker] = {}

            # Calculate RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            kpi_data[ticker]['RSI'] = rsi.iloc[-1] if not rsi.empty else None

            # Calculate Bollinger Bands
            middle_band = data['Close'].rolling(window=20).mean()
            upper_band = middle_band + 2 * data['Close'].rolling(window=20).std()
            lower_band = middle_band - 2 * data['Close'].rolling(window=20).std()
            kpi_data[ticker]['Bollinger Bands'] = {
                'Middle Band': middle_band.iloc[-1] if not middle_band.empty else None,
                'Upper Band': upper_band.iloc[-1] if not upper_band.empty else None,
                'Lower Band': lower_band.iloc[-1] if not lower_band.empty else None,
                'Current Price': data['Close'].iloc[-1] if not data.empty else None
            }

            # Calculate P/E Ratio - use cached ticker info function
            try:
                eps = get_ticker_info_cached(ticker, 'trailingEps')
                if eps and eps != 0:
                    pe_ratio = data['Close'].iloc[-1] / eps
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
            ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
            ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
            macd = ema_12 - ema_26
            signal = macd.ewm(span=9, adjust=False).mean()
            kpi_data[ticker]['MACD'] = {
                'MACD': macd.iloc[-1] if not macd.empty else None,
                'Signal Line': signal.iloc[-1] if not signal.empty else None
            }
            
        except (RequestsConnectionError, Timeout, RequestException) as e:
            error_msg = (
                f"Connection error processing {ticker}: {str(e)}\n"
                "Please check your internet connection or VPN settings."
            )
            print(error_msg)
            # Re-raise connection errors so they can be handled by the UI
            raise RequestsConnectionError(error_msg) from e
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

