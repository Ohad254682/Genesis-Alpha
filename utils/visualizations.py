"""
Visualization functions for stock analysis
"""
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import numpy as np


def plot_rsi(data, ticker):
    """
    Plot the Relative Strength Index (RSI) for a given stock.

    Parameters:
    data (DataFrame): The stock data.
    ticker (str): The stock ticker symbol.

    Returns:
    matplotlib.figure.Figure: The figure object.
    """
    window = 14
    
    # Ensure we have Close column
    if 'Close' not in data.columns:
        raise ValueError(f"Missing 'Close' column in data for {ticker}")
    
    # Check if we have enough data
    if len(data) < window:
        raise ValueError(f"Not enough data points for RSI calculation. Need at least {window}, got {len(data)}")
    
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Remove NaN values
    rsi = rsi.dropna()
    
    if len(rsi) == 0:
        raise ValueError("RSI calculation resulted in no valid data points")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rsi.index, rsi.values, label='RSI', color='purple')
    ax.axhline(70, color='red', linestyle='--', label='Overbought (70)')
    ax.axhline(30, color='green', linestyle='--', label='Oversold (30)')
    ax.set_title(f'RSI of {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('RSI')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def plot_bollinger_bands(data, ticker):
    """
    Plot the Bollinger Bands for a given stock.

    Parameters:
    data (DataFrame): The stock data.
    ticker (str): The stock ticker symbol.

    Returns:
    matplotlib.figure.Figure: The figure object.
    """
    window = 20
    
    # Ensure we have Close column
    if 'Close' not in data.columns:
        raise ValueError(f"Missing 'Close' column in data for {ticker}")
    
    # Check if we have enough data
    if len(data) < window:
        raise ValueError(f"Not enough data points for Bollinger Bands. Need at least {window}, got {len(data)}")
    
    # Create a copy to avoid modifying original
    plot_data = data.copy()
    plot_data['Middle Band'] = plot_data['Close'].rolling(window=window).mean()
    plot_data['Upper Band'] = plot_data['Middle Band'] + 2 * plot_data['Close'].rolling(window=window).std()
    plot_data['Lower Band'] = plot_data['Middle Band'] - 2 * plot_data['Close'].rolling(window=window).std()
    
    # Remove NaN values
    plot_data = plot_data.dropna()
    
    if len(plot_data) == 0:
        raise ValueError("Bollinger Bands calculation resulted in no valid data points")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(plot_data.index, plot_data['Close'].values, label='Closing Price', color='black')
    ax.plot(plot_data.index, plot_data['Middle Band'].values, label='Middle Band', color='blue')
    ax.plot(plot_data.index, plot_data['Upper Band'].values, label='Upper Band', color='red')
    ax.plot(plot_data.index, plot_data['Lower Band'].values, label='Lower Band', color='green')
    ax.fill_between(plot_data.index, plot_data['Upper Band'].values, plot_data['Lower Band'].values, alpha=0.2, color='gray')
    ax.set_title(f'Bollinger Bands of {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def plot_pe_ratios(data, ticker, eps):
    """
    Plot the Price-to-Earnings (P/E) ratio for a given stock.

    Parameters:
    data (DataFrame): The stock data.
    ticker (str): The stock ticker symbol.
    eps (float): The earnings per share of the stock.

    Returns:
    matplotlib.figure.Figure: The figure object or None if EPS is invalid.
    """
    if eps is None or eps == 0:
        return None
    
    pe_ratio = data['Close'] / eps
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index, pe_ratio, label=f'{ticker} PE Ratio', color='blue')
    ax.set_title(f'PE Ratio of {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('PE Ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def plot_beta_comparison(betas):
    """
    Plot a bar chart comparing beta values of the given stock tickers.

    Parameters:
    betas (dict): Dictionary of ticker to beta value mappings.

    Returns:
    matplotlib.figure.Figure: The figure object.
    """
    if not betas:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(betas.keys(), betas.values(), color='blue', alpha=0.7)
    ax.axhline(1, color='red', linestyle='--', label='Market Beta (1.0)')
    ax.set_title('Beta Comparison of Selected Stocks')
    ax.set_xlabel('Ticker')
    ax.set_ylabel('Beta')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig


def plot_macd(data, ticker):
    """
    Plot the Moving Average Convergence Divergence (MACD) for a given stock.

    Parameters:
    data (DataFrame): The stock data.
    ticker (str): The stock ticker symbol.

    Returns:
    matplotlib.figure.Figure: The figure object.
    """
    # Ensure we have Close column
    if 'Close' not in data.columns:
        raise ValueError(f"Missing 'Close' column in data for {ticker}")
    
    # Check if we have enough data
    if len(data) < 26:
        raise ValueError(f"Not enough data points for MACD. Need at least 26, got {len(data)}")
    
    ema_12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    
    # Remove NaN values
    valid_idx = ~(macd.isna() | signal.isna())
    if valid_idx.sum() == 0:
        raise ValueError("MACD calculation resulted in no valid data points")
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(data.index[valid_idx], macd[valid_idx].values, label=f'{ticker} MACD', color='blue')
    ax.plot(data.index[valid_idx], signal[valid_idx].values, label=f'{ticker} Signal Line', color='red')
    ax.bar(data.index[valid_idx], histogram[valid_idx].values, label='Histogram', alpha=0.3, color='gray')
    ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax.set_title(f'MACD and Signal Line of {ticker}')
    ax.set_xlabel('Date')
    ax.set_ylabel('MACD')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

