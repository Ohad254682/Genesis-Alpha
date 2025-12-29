"""
Centralized data caching for yfinance downloads.
This module provides cached functions to avoid redundant API calls.
"""
import yfinance as yf
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout, RequestException

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
def get_ticker_history(ticker, start_date, end_date, max_retries=3, retry_delay=2):
    """
    Download historical stock data for a single ticker with caching.
    This is the central function that all other modules should use to avoid redundant downloads.
    
    Parameters:
    ticker (str): Stock ticker symbol.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    max_retries (int): Maximum number of retry attempts.
    retry_delay (float): Delay between retries in seconds.
    
    Returns:
    pd.DataFrame: Historical stock data with all columns (Open, High, Low, Close, Adj Close, Volume).
    
    Raises:
    ConnectionError: If connection fails after all retries.
    """
    # Validate dates
    if not start_date or not end_date:
        raise ValueError("Start date and end date must be provided.")
    
    # Ensure dates are strings in correct format
    start_str = str(start_date) if isinstance(start_date, str) else start_date.strftime('%Y-%m-%d')
    end_str = str(end_date) if isinstance(end_date, str) else end_date.strftime('%Y-%m-%d')
    
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            
            # Download history with explicit parameters
            try:
                hist = stock.history(start=start_str, end=end_str, auto_adjust=True)
            except Exception as hist_err:
                # Try without auto_adjust if that fails
                try:
                    hist = stock.history(start=start_str, end=end_str)
                except Exception as e2:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    raise Exception(f"Failed to download history: {str(hist_err)}. Retry failed: {str(e2)}") from e2
            
            if hist.empty:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise ValueError(f"No data downloaded for {ticker} in date range {start_str} to {end_str}")
            
            # Return full DataFrame with all columns
            return hist
            
        except (RequestsConnectionError, Timeout, RequestException) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            else:
                raise ConnectionError(
                    f"Failed to download data for {ticker} after {max_retries} attempts. "
                    f"Please check your internet connection or VPN. Error: {str(e)}"
                ) from e
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                raise Exception(f"Error downloading data for {ticker}: {str(e)}") from e


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_ticker_info(ticker, field=None):
    """
    Get ticker info (company name, market cap, etc.) with caching.
    
    Parameters:
    ticker (str): Stock ticker symbol.
    field (str, optional): Specific field to retrieve (e.g., 'longName', 'marketCap').
                           If None, returns entire info dict.
    
    Returns:
    dict or str: Ticker info dict or specific field value.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if field:
            return info.get(field)
        return info
    except Exception as e:
        # Return None if info retrieval fails
        return None


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def get_multiple_tickers_history(tickers, start_date, end_date, max_retries=3, retry_delay=2):
    """
    Download historical stock data for multiple tickers with caching.
    Uses get_ticker_history internally to leverage the cache.
    
    Parameters:
    tickers (list): List of stock ticker symbols.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    max_retries (int): Maximum number of retry attempts per ticker.
    retry_delay (float): Delay between retries in seconds.
    
    Returns:
    pd.DataFrame: Historical stock data with tickers as columns (Adj Close or Close).
    """
    # Validate dates
    if not start_date or not end_date:
        raise ValueError("Start date and end date must be provided.")
    
    # Helper function to download a single ticker
    def _download_single_ticker(ticker):
        """Download and process a single ticker"""
        try:
            # Use the cached function to get full history
            hist = get_ticker_history(ticker, start_date, end_date, max_retries, retry_delay)
            
            # Get Adj Close, fallback to Close if not available
            if 'Close' in hist.columns:
                ticker_data = hist['Close'].copy()
            elif 'Adj Close' in hist.columns:
                ticker_data = hist['Adj Close'].copy()
            else:
                raise ValueError(f"No 'Close' or 'Adj Close' column found for {ticker}")

            if ticker_data is not None and len(ticker_data) > 0:
                return ticker, ticker_data
            else:
                return ticker, None
        except Exception as e:
            # Log error but continue with other tickers
            print(f"Warning: Failed to download data for {ticker}: {str(e)}")
            return ticker, None
    
    # Download all tickers in parallel using ThreadPoolExecutor
    # This is much faster than sequential downloads
    all_data = {}
    max_workers = min(5, len(tickers))  # Limit to 5 concurrent downloads to avoid overwhelming the API
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_ticker = {
            executor.submit(_download_single_ticker, ticker): ticker 
            for ticker in tickers
        }
        
        # Process results as they complete
        for future in as_completed(future_to_ticker):
            ticker, ticker_data = future.result()
            if ticker_data is not None:
                all_data[ticker] = ticker_data
    
    if not all_data:
        raise ValueError("No data downloaded for any ticker")
    
    # Combine all tickers into a single DataFrame
#     אחרי to_numeric:
#             AAPL     TSLA
# 2025-01-01  185.10  245.00
# 2025-01-02  187.30  250.20
# 2025-01-03   NaN    248.70
# 2025-01-04  188.00   NaN
    try:
        result_df = pd.DataFrame(all_data)
        # Ensure all columns are numeric
        for col in result_df.columns:
            result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
        # Drop any rows with all NaN values
        result_df = result_df.dropna(how='all')
        # Sort by index (date)
        result_df = result_df.sort_index()
    except Exception as e:
        raise Exception(f"Error combining ticker data: {str(e)}") from e
    
    if result_df.empty:
        raise ValueError("Combined data is empty after processing")
    
    return result_df

