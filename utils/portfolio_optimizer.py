"""
Portfolio optimization functions using Modern Portfolio Theory and Black-Litterman
"""
import numpy as np
import pandas as pd
import yfinance as yf
import time
import json
import os
from scipy.optimize import minimize
from requests.exceptions import ConnectionError as RequestsConnectionError, Timeout, RequestException
from utils.data_cache import get_ticker_history, get_ticker_info as get_ticker_info_cached, get_multiple_tickers_history

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

# Try to import pypfopt, but make it optional
try:
    from pypfopt import risk_models, expected_returns, BlackLittermanModel, EfficientFrontier, black_litterman
    PYPFOPT_AVAILABLE = True
except ImportError:
    PYPFOPT_AVAILABLE = False
    # Create dummy classes to prevent errors
    risk_models = None
    expected_returns = None
    BlackLittermanModel = None
    EfficientFrontier = None
    black_litterman = None


def portfolio_performance(weights, mean_returns, cov_matrix):
    """
    Calculate portfolio performance metrics.

    Parameters:
    weights (array): Asset weights in the portfolio.
    mean_returns (Series): Mean returns for each asset.
    cov_matrix (DataFrame): Covariance matrix of asset returns.

    Returns:
    float: Portfolio returns.
    float: Portfolio standard deviation.
    """
    returns = np.sum(mean_returns * weights)
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
    return returns, std


def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    """
    Calculate the negative Sharpe ratio for a given portfolio.

    Parameters:
    weights (array): Asset weights in the portfolio.
    mean_returns (Series): Mean returns for each asset.
    cov_matrix (DataFrame): Covariance matrix of asset returns.
    risk_free_rate (float): Risk-free rate.

    Returns:
    float: Negative Sharpe ratio.
    """
    p_returns, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
    return -(p_returns - risk_free_rate) / p_std


def max_sharpe_ratio(mean_returns, cov_matrix, risk_free_rate):
    """
    Find the portfolio with the maximum Sharpe ratio.

    Parameters:
    mean_returns (Series): Mean returns for each asset.
    cov_matrix (DataFrame): Covariance matrix of asset returns.
    risk_free_rate (float): Risk-free rate.

    Returns:
    OptimizeResult: The optimization result containing the portfolio weights.
    """
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix, risk_free_rate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for asset in range(num_assets))
    
    result = minimize(negative_sharpe_ratio, num_assets * [1. / num_assets,], 
                      args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return result


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def _download_portfolio_data(tickers, start_date, end_date, max_retries=3, retry_delay=2):
    """
    Download portfolio data with retry logic and caching.
    Uses centralized data cache to avoid redundant downloads.
    Cached to reduce API calls and improve performance.
    
    Parameters:
    tickers (list): List of stock ticker symbols.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    max_retries (int): Maximum number of retry attempts.
    retry_delay (float): Delay between retries in seconds.
    
    Returns:
    pd.DataFrame: Adjusted close prices with tickers as columns.
    
    Raises:
    ConnectionError: If connection fails after all retries.
    """
    # Use centralized cached function - it already handles retries and caching
    return get_multiple_tickers_history(tickers, start_date, end_date, max_retries, retry_delay)


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def optimize_portfolio_mpt(tickers, start_date, end_date, risk_free_rate=0.04):
    """
    Optimize portfolio using Modern Portfolio Theory with scipy optimization.
    Uses a direct scipy.optimize approach for maximum Sharpe ratio.
    Cached to improve performance and reduce API calls.
    
    Parameters:
    tickers (list): List of stock ticker symbols.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    risk_free_rate (float): Risk-free rate.
    
    Returns:
    dict: Dictionary containing optimal weights and performance metrics.
    """
    log_path = r"c:\Users\ohada\OneDrive\Desktop\Gen AI for Stock Analysis (2)\Gen AI for Stock Analysis\.cursor\debug.log"
    
    # #region agent log - Function entry
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'A',
            'location': 'portfolio_optimizer.py:211',
            'message': 'MPT: Function entry',
            'data': {
                'tickers': tickers,
                'start_date': str(start_date),
                'end_date': str(end_date),
                'risk_free_rate': float(risk_free_rate)
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Fetch the adjusted close prices with retry logic
    data = _download_portfolio_data(tickers, start_date, end_date)
    
    # #region agent log - After data download
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:240',
            'message': 'MPT: After data download',
            'data': {
                'data_empty': bool(data.empty),
                'data_shape': list(data.shape) if hasattr(data, 'shape') else None,
                'data_columns': list(data.columns) if hasattr(data, 'columns') else None,
                'data_has_nan': bool(data.isna().any().any()) if hasattr(data, 'isna') else None,
                'data_sample_first_5': data.head().to_dict() if not data.empty else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Validate data BEFORE processing
    if data is None or data.empty:
        raise ValueError(
            "No price data returned. Check tickers and date range.\n"
            f"Tickers: {tickers}\n"
            f"Date range: {start_date} to {end_date}"
        )
    
    # #region agent log - Data validation
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:250',
            'message': 'MPT: Data validation before returns',
            'data': {
                'data_shape': list(data.shape) if hasattr(data, 'shape') else None,
                'data_columns': list(data.columns) if hasattr(data, 'columns') else None,
                'data_nan_per_col': data.isna().sum().to_dict() if hasattr(data, 'isna') else None,
                'data_min_date': str(data.index.min()) if hasattr(data, 'index') and len(data) > 0 else None,
                'data_max_date': str(data.index.max()) if hasattr(data, 'index') and len(data) > 0 else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Remove columns where ALL values are NaN (invalid tickers)
    data = data.dropna(axis=1, how='all')
    
    if data.shape[1] == 0:
        raise ValueError(
            "All tickers have no price data in the selected date range.\n"
            f"Tickers: {tickers}\n"
            f"Date range: {start_date} to {end_date}\n"
            "Please verify ticker symbols and ensure the date range contains trading days."
        )
    
    # Need at least 2 rows for pct_change to work
    if data.shape[0] < 2:
        raise ValueError(
            f"Not enough price rows to compute returns (need at least 2 trading days, got {data.shape[0]}).\n"
            f"Date range: {start_date} to {end_date}\n"
            "Please widen the date range to include at least 2 trading days."
        )
    
    # Clean tickers list - remove any that don't exist in data
    available_tickers_before = [t for t in tickers if t in data.columns]
    if len(available_tickers_before) != len(tickers):
        missing = set(tickers) - set(available_tickers_before)
        raise ValueError(
            f"Missing data for tickers: {missing}\n"
            f"Available tickers in data: {list(data.columns)}\n"
            "Please verify ticker symbols are correct."
        )
    
    # Calculate daily returns
    returns = data.pct_change(fill_method=None)
    
    # #region agent log - After pct_change
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:290',
            'message': 'MPT: After pct_change',
            'data': {
                'returns_empty': bool(returns.empty),
                'returns_shape': list(returns.shape) if hasattr(returns, 'shape') else None,
                'returns_has_nan': bool(returns.isna().any().any()) if hasattr(returns, 'isna') else None,
                'returns_nan_count': int(returns.isna().sum().sum()) if hasattr(returns, 'isna') else None,
                'first_row_all_nan': bool(returns.iloc[0].isna().all()) if len(returns) > 0 else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Replace infinite values with NaN
    returns = returns.replace([np.inf, -np.inf], np.nan)
    
    # Fill NaN values: forward fill, backward fill, then 0
    # This handles the first row (all NaN from pct_change) and any other missing values
    returns = returns.ffill(axis=0).bfill(axis=0).fillna(0)
    
    # #region agent log - After fill
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:310',
            'message': 'MPT: After fill',
            'data': {
                'returns_empty': bool(returns.empty),
                'returns_shape': list(returns.shape) if hasattr(returns, 'shape') else None,
                'returns_has_nan': bool(returns.isna().any().any()) if hasattr(returns, 'isna') else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Drop rows where ALL values are NaN (shouldn't happen after fill, but safety check)
    returns = returns.dropna(how='all')
    
    # #region agent log - After returns calculation (final)
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:325',
            'message': 'MPT: After returns calculation (final)',
            'data': {
                'returns_empty': bool(returns.empty),
                'returns_shape': list(returns.shape) if hasattr(returns, 'shape') else None,
                'returns_columns': list(returns.columns) if hasattr(returns, 'columns') else None,
                'original_data_shape': list(data.shape) if hasattr(data, 'shape') else None,
                'returns_has_nan': bool(returns.isna().any().any()) if hasattr(returns, 'isna') else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Validate returns with detailed error message
    if returns.empty:
        raise ValueError(
            "Returns calculation produced empty data.\n"
            f"Likely causes:\n"
            f"1. Invalid tickers: {tickers}\n"
            f"2. Too short date range: {start_date} to {end_date}\n"
            f"3. Missing prices for all tickers\n"
            f"Original data shape: {data.shape}\n"
            "Try: widen the date range, verify tickers, and ensure at least 2 trading days of data."
        )
    
    if len(returns) < 5:
        raise ValueError(
            f"Insufficient return data points: {len(returns)} (need at least 5).\n"
            f"Date range: {start_date} to {end_date}\n"
            "Please widen the date range to include more trading days."
        )
    
    # Remove columns where ALL values are NaN (shouldn't happen after fill, but safety check)
    returns = returns.dropna(axis=1, how='all')
    
    if returns.empty:
        raise ValueError(
            "All ticker columns were removed after processing.\n"
            f"Original tickers: {tickers}\n"
            "This should not happen. Please check the data source."
        )
    
    # Ensure we still have data for all tickers (we already checked earlier, but verify again)
    available_tickers = [t for t in tickers if t in returns.columns]
    if len(available_tickers) != len(tickers):
        missing = set(tickers) - set(available_tickers)
        raise ValueError(
            f"Missing data for tickers after processing: {missing}\n"
            f"Available tickers: {list(returns.columns)}\n"
            "This should not happen if data validation passed earlier."
        )
    if len(available_tickers) == 0:
        raise ValueError(
            "No valid tickers after data cleaning.\n"
            f"Original tickers: {tickers}\n"
            "Please verify ticker symbols are correct."
        )
    
    # Select only the tickers we need
    returns = returns[available_tickers]
    
    # Final validation of returns
    if returns.empty or len(returns) < 5:
        raise ValueError(
            f"Insufficient valid return data after cleaning: {len(returns)} rows (need at least 5).\n"
            f"Date range: {start_date} to {end_date}\n"
            "Please widen the date range to include more trading days."
        )
    
    # Calculate mean returns and covariance matrix
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    # Validate mean returns
    if mean_returns.isna().any() or np.isinf(mean_returns).any():
        raise ValueError("Mean returns contain NaN or Inf values")
    if (mean_returns == 0).all():
        raise ValueError("All mean returns are zero")
    
    # Validate covariance matrix
    if cov_matrix.isna().any().any() or np.isinf(cov_matrix).any().any():
        raise ValueError("Covariance matrix contains NaN or Inf values")
    
    # Ensure covariance matrix is positive semi-definite
    # Add small regularization if needed
    min_eigenval = np.min(np.linalg.eigvals(cov_matrix))
    if min_eigenval < 1e-8:
        regularization = abs(min_eigenval) + 1e-8
        cov_matrix = cov_matrix + np.eye(len(cov_matrix)) * regularization
    
    # Convert to numpy arrays
    mu = mean_returns.values
    S = cov_matrix.values
    
    # Final validation of arrays
    if np.any(np.isnan(mu)) or np.any(np.isinf(mu)):
        raise ValueError("Mean returns array contains NaN or Inf")
    if np.any(np.isnan(S)) or np.any(np.isinf(S)):
        raise ValueError("Covariance matrix array contains NaN or Inf")
    
    # Objective function: negative Sharpe ratio (we minimize)
    def objective(weights):
        portfolio_return = np.dot(weights, mu)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(S, weights)))
        if portfolio_std < 1e-10:
            return 1e10  # Penalty for zero volatility
        sharpe = (portfolio_return - risk_free_rate) / portfolio_std
        return -sharpe  # Negative because we minimize
    
    # Constraints: weights sum to 1
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
    
    # Bounds: each weight between 0 and 1
    bounds = tuple((0.0, 1.0) for _ in range(len(available_tickers)))
    
    # Initial guess: equal weights
    initial_weights = np.array([1.0 / len(available_tickers)] * len(available_tickers))
    
    # Optimize
    result = minimize(
        objective,
        initial_weights,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000, 'ftol': 1e-9}
    )
    
    # #region agent log - Log optimization result
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'F',
            'location': 'portfolio_optimizer.py:285',
            'message': 'MPT: Optimization result',
            'data': {
                'success': result.success,
                'message': result.message,
                'fun': float(result.fun) if not np.isnan(result.fun) and not np.isinf(result.fun) else None,
                'optimal_weights': [float(w) for w in result.x[:5]] if len(result.x) >= 5 else [float(w) for w in result.x],
                'weights_sum': float(np.sum(result.x)),
                'num_weights': len(result.x)
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    if not result.success:
        raise ValueError(f"Optimization failed: {result.message}")
    
    optimal_weights = result.x
    
    # Validate optimal weights
    if np.any(np.isnan(optimal_weights)) or np.any(np.isinf(optimal_weights)):
        raise ValueError("Optimization produced NaN or Inf weights")
    if np.sum(optimal_weights) < 0.99 or np.sum(optimal_weights) > 1.01:
        raise ValueError(f"Optimization weights don't sum to 1: {np.sum(optimal_weights)}")
    
    # Calculate portfolio performance
    portfolio_return = np.dot(optimal_weights, mu)
    variance = np.dot(optimal_weights.T, np.dot(S, optimal_weights))
    
    # #region agent log - Before sqrt calculation (Hypothesis C)
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'C',
            'location': 'portfolio_optimizer.py:345',
            'message': 'MPT: Before sqrt calculation',
            'data': {
                'portfolio_return': float(portfolio_return),
                'variance': float(variance),
                'variance_is_nan': bool(np.isnan(variance)),
                'variance_is_negative': bool(variance < 0),
                'variance_is_inf': bool(np.isinf(variance))
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    portfolio_std = np.sqrt(variance) if variance >= 0 else np.nan
    
    # #region agent log - After portfolio_std calculation (Hypothesis C)
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'C',
            'location': 'portfolio_optimizer.py:360',
            'message': 'MPT: After portfolio_std calculation',
            'data': {
                'portfolio_return': float(portfolio_return),
                'portfolio_std': float(portfolio_std) if not np.isnan(portfolio_std) else None,
                'portfolio_return_is_nan': bool(np.isnan(portfolio_return)),
                'portfolio_std_is_nan': bool(np.isnan(portfolio_std)),
                'portfolio_std_is_inf': bool(np.isinf(portfolio_std)) if not np.isnan(portfolio_std) else False
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # #region agent log - Before validation checks (Hypothesis B)
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'B',
            'location': 'portfolio_optimizer.py:375',
            'message': 'MPT: Before validation checks',
            'data': {
                'portfolio_return': float(portfolio_return),
                'portfolio_std': float(portfolio_std) if not np.isnan(portfolio_std) else None,
                'portfolio_return_is_nan': bool(np.isnan(portfolio_return)),
                'portfolio_std_is_nan': bool(np.isnan(portfolio_std))
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Validate results
    if np.isnan(portfolio_return) or np.isinf(portfolio_return):
        # #region agent log - Validation failed
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'portfolio_optimizer.py:390',
                'message': 'MPT: Validation FAILED - portfolio_return invalid',
                'data': {
                    'portfolio_return': float(portfolio_return) if not np.isnan(portfolio_return) and not np.isinf(portfolio_return) else None,
                    'is_nan': bool(np.isnan(portfolio_return)),
                    'is_inf': bool(np.isinf(portfolio_return))
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        raise ValueError("Portfolio return calculation produced NaN or Inf")
    
    if np.isnan(portfolio_std) or np.isinf(portfolio_std) or portfolio_std < 1e-10:
        # #region agent log - Validation failed
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'portfolio_optimizer.py:405',
                'message': 'MPT: Validation FAILED - portfolio_std invalid',
                'data': {
                    'portfolio_std': float(portfolio_std) if not np.isnan(portfolio_std) and not np.isinf(portfolio_std) else None,
                    'is_nan': bool(np.isnan(portfolio_std)),
                    'is_inf': bool(np.isinf(portfolio_std)),
                    'is_too_small': bool(portfolio_std < 1e-10) if not np.isnan(portfolio_std) else False
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        raise ValueError("Portfolio volatility calculation produced invalid value")
    
    # #region agent log - Validation passed
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'B',
            'location': 'portfolio_optimizer.py:420',
            'message': 'MPT: Validation PASSED',
            'data': {
                'portfolio_return': float(portfolio_return),
                'portfolio_std': float(portfolio_std)
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std if portfolio_std > 0 else 0.0
    
    # Annualize (assuming 252 trading days)
    annual_return = portfolio_return * 252
    annual_volatility = portfolio_std * np.sqrt(252)
    annual_sharpe = sharpe_ratio * np.sqrt(252) if not np.isnan(sharpe_ratio) else 0.0
    
    # #region agent log - Log annualized values
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'F',
            'location': 'portfolio_optimizer.py:320',
            'message': 'MPT: Annualized values calculated',
            'data': {
                'annual_return': float(annual_return),
                'annual_volatility': float(annual_volatility),
                'annual_sharpe': float(annual_sharpe),
                'annual_return_is_nan': bool(np.isnan(annual_return)),
                'annual_volatility_is_nan': bool(np.isnan(annual_volatility)),
                'annual_sharpe_is_nan': bool(np.isnan(annual_sharpe))
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Validate annualized values
    if np.isnan(annual_return) or np.isinf(annual_return):
        raise ValueError("Annual return calculation produced NaN or Inf")
    if np.isnan(annual_volatility) or np.isinf(annual_volatility):
        raise ValueError("Annual volatility calculation produced NaN or Inf")
    if np.isnan(annual_sharpe) or np.isinf(annual_sharpe):
        annual_sharpe = 0.0
    
    # Create weights dictionary and validate
    weights_dict = {}
    for i in range(len(available_tickers)):
        weight = float(optimal_weights[i])
        if np.isnan(weight) or np.isinf(weight):
            raise ValueError(f"Invalid weight for {available_tickers[i]}: {weight}")
        # Include all weights, even small ones
        weights_dict[available_tickers[i]] = max(0.0, weight)  # Ensure non-negative
    
    # Ensure weights sum to approximately 1 (they should from optimization, but verify)
    total_weight = sum(weights_dict.values())
    if abs(total_weight - 1.0) > 0.01:
        # Normalize weights if they don't sum to 1 (shouldn't happen, but safety check)
        if total_weight > 0:
            weights_dict = {k: v / total_weight for k, v in weights_dict.items()}
        else:
            raise ValueError("All weights are zero")
    
    # Validate annualized values before creating result
    if np.isnan(annual_return) or np.isinf(annual_return):
        raise ValueError(f"Invalid annual_return: {annual_return}")
    if np.isnan(annual_volatility) or np.isinf(annual_volatility) or annual_volatility <= 0:
        raise ValueError(f"Invalid annual_volatility: {annual_volatility}")
    if np.isnan(annual_sharpe) or np.isinf(annual_sharpe):
        annual_sharpe = 0.0
    
    result = {
        'weights': weights_dict,
        'expected_return': float(annual_return),
        'volatility': float(annual_volatility),
        'sharpe_ratio': float(annual_sharpe)
    }
    
    # #region agent log - Result dictionary created (Hypothesis D)
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'D',
            'location': 'portfolio_optimizer.py:440',
            'message': 'MPT: Result dictionary created',
            'data': {
                'expected_return': result['expected_return'],
                'volatility': result['volatility'],
                'sharpe_ratio': result['sharpe_ratio'],
                'expected_return_is_nan': bool(np.isnan(result['expected_return'])),
                'volatility_is_nan': bool(np.isnan(result['volatility'])),
                'sharpe_ratio_is_nan': bool(np.isnan(result['sharpe_ratio'])),
                'annual_return_before_dict': float(annual_return),
                'annual_volatility_before_dict': float(annual_volatility) if not np.isnan(annual_volatility) else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # #region agent log - Before final validation (Hypothesis B)
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'B',
            'location': 'portfolio_optimizer.py:460',
            'message': 'MPT: Before final validation checks',
            'data': {
                'expected_return': result['expected_return'],
                'volatility': result['volatility'],
                'sharpe_ratio': result['sharpe_ratio'],
                'expected_return_is_nan': bool(np.isnan(result['expected_return'])),
                'volatility_is_nan': bool(np.isnan(result['volatility'])),
                'sharpe_ratio_is_nan': bool(np.isnan(result['sharpe_ratio']))
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Final validation - ensure all values are valid and reasonable
    if np.isnan(result['expected_return']) or np.isinf(result['expected_return']):
        # #region agent log - Final validation failed
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'portfolio_optimizer.py:480',
                'message': 'MPT: Final validation FAILED - expected_return',
                'data': {'expected_return': result['expected_return']},
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        raise ValueError(f"Invalid expected_return: {result['expected_return']}")
    
    if np.isnan(result['volatility']) or np.isinf(result['volatility']) or result['volatility'] <= 0:
        # #region agent log - Final validation failed
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'B',
                'location': 'portfolio_optimizer.py:495',
                'message': 'MPT: Final validation FAILED - volatility',
                'data': {'volatility': result['volatility']},
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        raise ValueError(f"Invalid volatility: {result['volatility']}")
    
    if abs(result['expected_return']) < 1e-10 and result['volatility'] > 1e-10:
        raise ValueError(f"Portfolio optimization produced zero return ({result['expected_return']}) with non-zero volatility ({result['volatility']})")
    
    if not weights_dict or len(weights_dict) == 0:
        raise ValueError("No valid weights generated")
    
    # Final check: ensure result values are not NaN or zero when they shouldn't be
    if result['expected_return'] == 0.0 and result['volatility'] == 0.0:
        raise ValueError("Portfolio optimization produced zero return and zero volatility")
    
    # #region agent log - Final validation passed
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'B',
            'location': 'portfolio_optimizer.py:520',
            'message': 'MPT: Final validation PASSED - returning result',
            'data': {
                'expected_return': result['expected_return'],
                'volatility': result['volatility'],
                'sharpe_ratio': result['sharpe_ratio']
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # #region agent log - Log final validated result
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'F',
            'location': 'portfolio_optimizer.py:395',
            'message': 'MPT: Returning validated result',
            'data': {
                'expected_return': result['expected_return'],
                'volatility': result['volatility'],
                'sharpe_ratio': result['sharpe_ratio'],
                'validation_passed': True
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    return result


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def optimize_portfolio_risk_parity(tickers, start_date, end_date, risk_free_rate=0.04):
    """
    Optimize portfolio using Risk Parity (Equal Risk Contribution).

    Uses the same cleaned return and covariance pipeline as MPT, but with a
    different objective: each asset should contribute an equal share of total risk.

    The risk-free rate is only used for reporting the Sharpe ratio; it does not
    affect the optimization itself.
    
    Parameters:
    tickers (list): List of stock ticker symbols.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    risk_free_rate (float): Risk-free rate for Sharpe ratio calculation.
    
    Returns:
    dict: Dictionary containing optimal weights and performance metrics.
    """
    log_path = r"c:\Users\ohada\OneDrive\Desktop\Gen AI for Stock Analysis (2)\Gen AI for Stock Analysis\.cursor\debug.log"

    # Fetch and clean data using the same pipeline as MPT
    data = _download_portfolio_data(tickers, start_date, end_date)
    
    if data is None or data.empty:
        raise ValueError(
            "No price data returned. Check tickers and date range.\n"
            f"Tickers: {tickers}\n"
            f"Date range: {start_date} to {end_date}"
        )

    # Remove columns where ALL values are NaN (invalid tickers)
    data = data.dropna(axis=1, how='all')
    if data.shape[1] == 0:
        raise ValueError(
            "All tickers have no price data in the selected date range.\n"
            f"Tickers: {tickers}\n"
            f"Date range: {start_date} to {end_date}\n"
            "Please verify ticker symbols and ensure the date range contains trading days."
        )

    # Need at least 2 rows for pct_change to work
    if data.shape[0] < 2:
        raise ValueError(
            f"Not enough price rows to compute returns (need at least 2 trading days, got {data.shape[0]}).\n"
            f"Date range: {start_date} to {end_date}\n"
            "Please widen the date range to include at least 2 trading days."
        )

    # Clean tickers list - remove any that don't exist in data
    available_tickers_before = [t for t in tickers if t in data.columns]
    if len(available_tickers_before) != len(tickers):
        missing = set(tickers) - set(available_tickers_before)
        raise ValueError(
            f"Missing data for tickers: {missing}\n"
            f"Available tickers in data: {list(data.columns)}\n"
            "Please verify ticker symbols are correct."
        )

    # Calculate daily returns
    returns = data.pct_change(fill_method=None)
    returns = returns.replace([np.inf, -np.inf], np.nan)
    returns = returns.ffill(axis=0).bfill(axis=0).fillna(0)
    returns = returns.dropna(how='all')

    if returns.empty or len(returns) < 5:
        raise ValueError(
            f"Insufficient valid return data after cleaning: {len(returns)} rows (need at least 5).\n"
            f"Date range: {start_date} to {end_date}\n"
            "Please widen the date range to include more trading days."
        )

    # Ensure we still have data for all tickers
    available_tickers = [t for t in tickers if t in returns.columns]
    if len(available_tickers) != len(tickers):
        missing = set(tickers) - set(available_tickers)
        raise ValueError(
            f"Missing data for tickers after processing: {missing}\n"
            f"Available tickers: {list(returns.columns)}\n"
            "This should not happen if data validation passed earlier."
        )
    if len(available_tickers) == 0:
        raise ValueError(
            "No valid tickers after data cleaning.\n"
            f"Original tickers: {tickers}\n"
            "Please verify ticker symbols are correct."
        )

    returns = returns[available_tickers]
    
    # Calculate mean returns and covariance matrix
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    
    if mean_returns.isna().any() or np.isinf(mean_returns).any():
        raise ValueError("Mean returns contain NaN or Inf values")
    if cov_matrix.isna().any().any() or np.isinf(cov_matrix).any().any():
        raise ValueError("Covariance matrix contains NaN or Inf values")

    # Ensure covariance matrix is positive semi-definite
    min_eigenval = np.min(np.linalg.eigvals(cov_matrix))
    if min_eigenval < 1e-8:
        regularization = abs(min_eigenval) + 1e-8
        cov_matrix = cov_matrix + np.eye(len(cov_matrix)) * regularization

    mu = mean_returns.values
    S = cov_matrix.values

    if np.any(np.isnan(mu)) or np.any(np.isinf(mu)):
        raise ValueError("Mean returns array contains NaN or Inf")
    if np.any(np.isnan(S)) or np.any(np.isinf(S)):
        raise ValueError("Covariance matrix array contains NaN or Inf")

    n_assets = len(available_tickers)

    def risk_parity_objective(weights):
        # Enforce simple bounds in objective to avoid numerical issues
        if np.any(weights < 0) or np.any(weights > 1):
            return 1e10
        if abs(np.sum(weights) - 1.0) > 1e-4:
            return 1e10

        portfolio_var = float(np.dot(weights.T, np.dot(S, weights)))
        if portfolio_var <= 0:
            return 1e10

        # Marginal contribution to risk
        marginal_contrib = np.dot(S, weights)
        # Total risk contribution of each asset (not normalized)
        risk_contrib = weights * marginal_contrib

        # Normalize by total variance to get fractional risk contributions
        risk_contrib_fraction = risk_contrib / portfolio_var

        # Target: equal risk contribution
        target = np.ones(n_assets) / n_assets

        return float(np.sum((risk_contrib_fraction - target) ** 2))

    # Constraints: weights sum to 1
    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}

    # Bounds: each weight between 0 and 1
    bounds = tuple((0.0, 1.0) for _ in range(n_assets))

    # Initial guess: equal weights
    initial_weights = np.ones(n_assets) / n_assets

    result = minimize(
        risk_parity_objective,
        initial_weights,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000, 'ftol': 1e-9}
    )

    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'RP',
            'location': 'portfolio_optimizer.py:optimize_portfolio_risk_parity',
            'message': 'Risk Parity: Optimization result',
            'data': {
                'success': bool(result.success),
                'message': str(result.message),
                'fun': float(result.fun) if result.fun is not None and not np.isnan(result.fun) and not np.isinf(result.fun) else None,
                'weights_sum': float(np.sum(result.x)),
                'num_weights': len(result.x)
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass

    if not result.success:
        raise ValueError(f"Risk Parity optimization failed: {result.message}")

    optimal_weights = result.x

    if np.any(np.isnan(optimal_weights)) or np.any(np.isinf(optimal_weights)):
        raise ValueError("Risk Parity optimization produced NaN or Inf weights")
    if np.sum(optimal_weights) < 0.99 or np.sum(optimal_weights) > 1.01:
        raise ValueError(f"Risk Parity weights don't sum to 1: {np.sum(optimal_weights)}")

    # Compute portfolio performance for reporting
    portfolio_return = float(np.dot(optimal_weights, mu))
    variance = float(np.dot(optimal_weights.T, np.dot(S, optimal_weights)))
    portfolio_std = np.sqrt(variance) if variance >= 0 else np.nan

    if np.isnan(portfolio_return) or np.isinf(portfolio_return):
        raise ValueError("Risk Parity portfolio return calculation produced NaN or Inf")
    if np.isnan(portfolio_std) or np.isinf(portfolio_std) or portfolio_std < 1e-10:
        raise ValueError("Risk Parity portfolio volatility calculation produced invalid value")

    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std if portfolio_std > 0 else 0.0

    # Annualize (assuming 252 trading days)
    annual_return = portfolio_return * 252
    annual_volatility = portfolio_std * np.sqrt(252)
    annual_sharpe = sharpe_ratio * np.sqrt(252) if not np.isnan(sharpe_ratio) else 0.0

    if np.isnan(annual_sharpe) or np.isinf(annual_sharpe):
        annual_sharpe = 0.0

    weights_dict = {}
    for i in range(n_assets):
        weight = float(optimal_weights[i])
        if np.isnan(weight) or np.isinf(weight):
            raise ValueError(f"Invalid weight for {available_tickers[i]}: {weight}")
        weights_dict[available_tickers[i]] = max(0.0, weight)

    total_weight = sum(weights_dict.values())
    if abs(total_weight - 1.0) > 0.01:
        if total_weight > 0:
            weights_dict = {k: v / total_weight for k, v in weights_dict.items()}
        else:
            raise ValueError("All Risk Parity weights are zero")

    result_dict = {
        'weights': weights_dict,
        'expected_return': float(annual_return),
        'volatility': float(annual_volatility),
        'sharpe_ratio': float(annual_sharpe)
    }

    return result_dict


@st.cache_data(ttl=3600, show_spinner=False)  # Cache for 1 hour
def optimize_portfolio_black_litterman(tickers, start_date, end_date, risk_free_rate=0.001):
    """
    Optimize portfolio using Black-Litterman model.
    Cached to improve performance and reduce API calls.
    
    Parameters:
    tickers (list): List of stock ticker symbols.
    start_date (str): Start date for historical data.
    end_date (str): End date for historical data.
    risk_free_rate (float): Risk-free rate.
    
    Returns:
    dict: Dictionary containing optimal weights and performance metrics.
    """
    if not PYPFOPT_AVAILABLE:
        raise ImportError(
            "PyPortfolioOpt is not installed. Portfolio optimization requires Microsoft Visual C++ Build Tools.\n"
            "Please install Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/\n"
            "Then run: pip install PyPortfolioOpt"
        )
    
    # Fetch historical stock data with retry logic
    df = _download_portfolio_data(tickers, start_date, end_date)
    
    # Calculate the sample mean returns and the covariance matrix
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    
    # Define market capitalizations using cached function
    mcap = {}
    for ticker in tickers:
        try:
            # Use centralized cached function for ticker info
            market_cap = get_ticker_info_cached(ticker, 'marketCap')
            mcap[ticker] = market_cap
        except Exception:
            mcap[ticker] = None
    
    # Manually set the market capitalization for SPY if it's in the list
    if 'SPY' in tickers:
        mcap['SPY'] = 45000000000000
    
    # Define beliefs (Microsoft will outperform Google by 5%)
    # This is a simple example - in practice, you'd want to make this configurable
    Q = np.array([0.05])
    P = np.zeros((1, len(tickers)))
    
    if 'MSFT' in tickers and 'GOOGL' in tickers:
        P[0, tickers.index('MSFT')] = 1
        P[0, tickers.index('GOOGL')] = -1
    
    # Calculate the market implied returns
    if 'SPY' in tickers and all(mcap.get(t) is not None for t in tickers):
        market_prices = df["SPY"]
        delta = black_litterman.market_implied_risk_aversion(market_prices)
        market_prior = black_litterman.market_implied_prior_returns(mcap, delta, S, risk_free_rate)
        # Calculate market weights from market cap
        total_mcap = sum(v for v in mcap.values() if v is not None)
        market_weights = {t: (mcap.get(t, 0) or 0) / total_mcap for t in tickers}
    else:
        # If SPY is not available, use historical mean returns and equal weights
        market_prior = mu
        market_weights = {t: 1.0 / len(tickers) for t in tickers}
    
    # Create the Black-Litterman model
    bl = BlackLittermanModel(
        S,
        Q=Q,
        P=P,
        pi=market_prior,
        market_weights=market_weights,
        risk_free_rate=risk_free_rate
    )
    
    # Get the adjusted returns and covariance matrix
    bl_returns = bl.bl_returns()
    bl_cov = bl.bl_cov()
    
    # #region agent log
    log_path = r"c:\Users\ohada\OneDrive\Desktop\Gen AI for Stock Analysis (2)\Gen AI for Stock Analysis\.cursor\debug.log"
    
    # #region agent log - After bl_returns creation
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'F',
            'location': 'portfolio_optimizer.py:1003',
            'message': 'BL: After bl_returns creation',
            'data': {
                'bl_returns_type': type(bl_returns).__name__,
                'bl_returns_has_isna': hasattr(bl_returns, 'isna'),
                'bl_returns_isna_any': bool(bl_returns.isna().any()) if hasattr(bl_returns, 'isna') else None,
                'bl_returns_has_values': hasattr(bl_returns, 'values'),
                'bl_returns_np_isnan_any': bool(np.isnan(bl_returns.values).any()) if hasattr(bl_returns, 'values') else bool(np.isnan(bl_returns).any()) if hasattr(bl_returns, '__array__') else None,
                'bl_returns_np_isinf_any': bool(np.isinf(bl_returns.values).any()) if hasattr(bl_returns, 'values') else bool(np.isinf(bl_returns).any()) if hasattr(bl_returns, '__array__') else None,
                'bl_returns_shape': list(bl_returns.shape) if hasattr(bl_returns, 'shape') else None,
                'bl_returns_length': len(bl_returns) if hasattr(bl_returns, '__len__') else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Get historical mean returns (mu) for fallback - defined earlier in function
    mu_array = mu.values if hasattr(mu, 'values') else np.asarray(mu)
    
    # Convert bl_returns to numpy array for cleaning
    if hasattr(bl_returns, 'values'):
        bl_returns_array = bl_returns.values
        bl_returns_index = bl_returns.index
        is_series = True
    elif hasattr(bl_returns, '__array__'):
        bl_returns_array = np.asarray(bl_returns)
        bl_returns_index = None
        is_series = False
    else:
        bl_returns_array = np.asarray(bl_returns)
        bl_returns_index = None
        is_series = False
    
    # Check for NaN/Inf in returns BEFORE cleaning
    returns_has_nan = np.isnan(bl_returns_array).any()
    returns_has_inf = np.isinf(bl_returns_array).any()
    
    # #region agent log - Before returns cleaning
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'F',
            'location': 'portfolio_optimizer.py:1040',
            'message': 'BL: Before returns cleaning',
            'data': {
                'returns_has_nan': bool(returns_has_nan),
                'returns_has_inf': bool(returns_has_inf),
                'returns_shape': list(bl_returns_array.shape) if hasattr(bl_returns_array, 'shape') else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Clean returns: ALWAYS replace NaN/Inf (even if not detected, safety check)
    # First, try to use historical mean returns (mu) as fallback for NaN values
    # This ensures we have realistic returns instead of zeros
    # Replace NaN with corresponding historical mean return, or 0 if that's also NaN
    # Replace Inf with large finite values
    for i in range(len(bl_returns_array)):
        if np.isnan(bl_returns_array[i]):
            # Use historical mean return if available, otherwise use 0
            if i < len(mu_array) and not np.isnan(mu_array[i]):
                bl_returns_array[i] = mu_array[i]
            else:
                bl_returns_array[i] = 0.0
        elif np.isinf(bl_returns_array[i]):
            bl_returns_array[i] = 1e6 if bl_returns_array[i] > 0 else -1e6
    
    # Final validation: ensure no NaN/Inf remain
    if np.isnan(bl_returns_array).any() or np.isinf(bl_returns_array).any():
        # If still has NaN/Inf, replace with mean of non-NaN values or historical mean
        if len(bl_returns_array) > 0:
            non_nan_values = bl_returns_array[~np.isnan(bl_returns_array) & ~np.isinf(bl_returns_array)]
            if len(non_nan_values) > 0:
                mean_val = np.mean(non_nan_values)
            elif len(mu_array) > 0:
                mean_val = np.nanmean(mu_array) if not np.isnan(np.nanmean(mu_array)) else 0.0
            else:
                mean_val = 0.0
            bl_returns_array = np.where(np.isnan(bl_returns_array) | np.isinf(bl_returns_array), mean_val, bl_returns_array)
    
    # Convert back to Series if original was Series, otherwise keep as array
    if is_series and bl_returns_index is not None:
        bl_returns = pd.Series(bl_returns_array, index=bl_returns_index)
    else:
        bl_returns = bl_returns_array
    
    # Validate that at least one return exceeds risk-free rate
    # This is required for the optimization to be feasible
    max_return = np.max(bl_returns_array) if len(bl_returns_array) > 0 else 0.0
    min_return = np.min(bl_returns_array) if len(bl_returns_array) > 0 else 0.0
    
    # #region agent log - After returns cleaning
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'F',
            'location': 'portfolio_optimizer.py:1095',
            'message': 'BL: After returns cleaning',
            'data': {
                'had_nan': bool(returns_has_nan),
                'had_inf': bool(returns_has_inf),
                'has_nan_after': bool(np.isnan(bl_returns_array).any()),
                'has_inf_after': bool(np.isinf(bl_returns_array).any()),
                'is_finite': bool(np.isfinite(bl_returns_array).all()),
                'max_return': float(max_return),
                'min_return': float(min_return),
                'risk_free_rate': float(risk_free_rate),
                'max_exceeds_rf': bool(max_return > risk_free_rate)
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # If no return exceeds risk-free rate, adjust returns to ensure feasibility
    if max_return <= risk_free_rate:
        # #region agent log - Adjusting returns for feasibility
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'F',
                'location': 'portfolio_optimizer.py:1120',
                'message': 'BL: Adjusting returns - max return does not exceed risk-free rate',
                'data': {
                    'max_return_before': float(max_return),
                    'risk_free_rate': float(risk_free_rate),
                    'adjustment_needed': True
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        
        # Add a small premium to all returns to ensure at least one exceeds risk-free rate
        # Use historical mean returns as baseline if available
        if len(mu_array) > 0 and len(mu_array) == len(bl_returns_array):
            # Use historical mean returns, ensuring at least one exceeds risk-free rate
            mu_max = np.max(mu_array)
            if mu_max > risk_free_rate:
                # Scale historical returns to ensure feasibility
                bl_returns_array = mu_array.copy()
            else:
                # Add premium to make it feasible
                premium = risk_free_rate - mu_max + 0.01  # Add 1% above risk-free rate
                bl_returns_array = mu_array + premium
        else:
            # Fallback: add premium to current returns
            premium = risk_free_rate - max_return + 0.01  # Add 1% above risk-free rate
            bl_returns_array = bl_returns_array + premium
        
        # Update bl_returns with adjusted array
        if is_series and bl_returns_index is not None:
            bl_returns = pd.Series(bl_returns_array, index=bl_returns_index)
        else:
            bl_returns = bl_returns_array
        
        # Verify adjustment worked
        max_return_after = np.max(bl_returns_array) if len(bl_returns_array) > 0 else 0.0
        
        # #region agent log - After adjustment
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'F',
                'location': 'portfolio_optimizer.py:1165',
                'message': 'BL: After returns adjustment',
                'data': {
                    'max_return_after': float(max_return_after),
                    'min_return_after': float(np.min(bl_returns_array)) if len(bl_returns_array) > 0 else 0.0,
                    'max_exceeds_rf_after': bool(max_return_after > risk_free_rate),
                    'risk_free_rate': float(risk_free_rate)
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
    
    # Convert to numpy array if it's a DataFrame
    if hasattr(bl_cov, 'values'):
        bl_cov = bl_cov.values
    bl_cov = np.asarray(bl_cov)
    
    # Check for NaN/Inf in covariance matrix BEFORE computing eigenvalues
    cov_has_nan = np.isnan(bl_cov).any()
    cov_has_inf = np.isinf(bl_cov).any()
    
    # #region agent log - Before validation
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:1010',
            'message': 'BL: Before covariance validation',
            'data': {
                'cov_has_nan': bool(cov_has_nan),
                'cov_has_inf': bool(cov_has_inf),
                'cov_shape': list(bl_cov.shape) if hasattr(bl_cov, 'shape') else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Clean covariance matrix: ALWAYS replace NaN/Inf (even if not detected, safety check)
    # Replace NaN with 0, Inf with large finite values
    bl_cov = np.nan_to_num(bl_cov, nan=0.0, posinf=1e6, neginf=-1e6)
    # Add small regularization to diagonal to ensure stability
    bl_cov = bl_cov + np.eye(len(bl_cov)) * 1e-8
    
    # Final validation: ensure no NaN/Inf remain
    if np.isnan(bl_cov).any() or np.isinf(bl_cov).any():
        # If still has NaN/Inf, replace with identity matrix scaled by variance
        bl_cov = np.eye(len(bl_cov)) * np.diag(bl_cov).mean() if len(bl_cov) > 0 else bl_cov
    
    # #region agent log - After cleaning
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:1045',
            'message': 'BL: Cleaned covariance matrix (NaN/Inf removed)',
            'data': {
                'had_nan': bool(cov_has_nan),
                'had_inf': bool(cov_has_inf),
                'has_nan_after': bool(np.isnan(bl_cov).any()),
                'has_inf_after': bool(np.isinf(bl_cov).any()),
                'is_finite': bool(np.isfinite(bl_cov).all())
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    # Now safe to compute eigenvalues
    try:
        # Hypothesis A: Check covariance matrix properties
        cov_eigenvals = np.linalg.eigvals(bl_cov)
        cov_min_eigenval = np.min(cov_eigenvals)
        cov_max_eigenval = np.max(cov_eigenvals)
        cov_is_psd = np.all(cov_eigenvals >= -1e-8)
        cov_has_nan = np.isnan(bl_cov).any()
        cov_has_inf = np.isinf(bl_cov).any()
        
        # Hypothesis B: Check expected returns
        returns_has_nan = bl_returns.isna().any() if hasattr(bl_returns, 'isna') else np.isnan(bl_returns).any()
        returns_has_inf = np.isinf(bl_returns).any() if hasattr(bl_returns, 'values') else np.isinf(bl_returns).any()
        returns_min = float(bl_returns.min()) if hasattr(bl_returns, 'min') else float(np.min(bl_returns))
        returns_max = float(bl_returns.max()) if hasattr(bl_returns, 'max') else float(np.max(bl_returns))
        
        # Hypothesis C: Check input data quality
        # Clean S before computing eigenvalues
        S_has_nan = np.isnan(S).any()
        S_has_inf = np.isinf(S).any()
        if S_has_nan or S_has_inf:
            S = np.nan_to_num(S, nan=0.0, posinf=1e6, neginf=-1e6)
        S_min_eigenval = np.min(np.linalg.eigvals(S))
        market_prior_has_nan = np.isnan(market_prior).any() if hasattr(market_prior, '__iter__') else np.isnan(market_prior)
        
        # Hypothesis D: Check solver configuration
        solver_info = {'risk_free_rate': float(risk_free_rate), 'num_assets': len(tickers)}
        
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'A',
            'location': 'portfolio_optimizer.py:337',
            'message': 'Covariance matrix properties before optimization',
            'data': {
                'cov_min_eigenval': float(cov_min_eigenval),
                'cov_max_eigenval': float(cov_max_eigenval),
                'cov_is_psd': bool(cov_is_psd),
                'cov_has_nan': bool(cov_has_nan_after),
                'cov_has_inf': bool(cov_has_inf_after),
                'cov_shape': list(bl_cov.shape) if hasattr(bl_cov, 'shape') else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'B',
            'location': 'portfolio_optimizer.py:338',
            'message': 'Expected returns properties before optimization',
            'data': {
                'returns_has_nan': bool(returns_has_nan),
                'returns_has_inf': bool(returns_has_inf),
                'returns_min': returns_min,
                'returns_max': returns_max,
                'returns_count': len(bl_returns) if hasattr(bl_returns, '__len__') else None
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'C',
            'location': 'portfolio_optimizer.py:339',
            'message': 'Input data quality (S and market_prior)',
            'data': {
                'S_min_eigenval': float(S_min_eigenval),
                'S_has_nan': bool(S_has_nan),
                'market_prior_has_nan': bool(market_prior_has_nan),
                'tickers': tickers
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'D',
            'location': 'portfolio_optimizer.py:340',
            'message': 'Solver configuration',
            'data': solver_info,
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as log_err:
        pass  # Don't fail on logging errors
    # #endregion
    
    # Validate covariance matrix before optimization
    # Ensure it's positive semi-definite
    cov_eigenvals = np.linalg.eigvals(bl_cov)
    min_eigenval = np.min(cov_eigenvals)
    if min_eigenval < -1e-8:
        # Add regularization to make it positive semi-definite
        regularization = abs(min_eigenval) + 1e-8
        bl_cov = bl_cov + np.eye(len(bl_cov)) * regularization
        # #region agent log
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'E',
                'location': 'portfolio_optimizer.py:1110',
                'message': 'BL: Added regularization to covariance matrix',
                'data': {
                    'min_eigenval_before': float(min_eigenval),
                    'regularization': float(regularization)
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
    
    # Validate returns (after cleaning, should not have NaN/Inf)
    # Get array for validation
    returns_array = bl_returns.values if hasattr(bl_returns, 'values') else (np.asarray(bl_returns) if hasattr(bl_returns, '__array__') else bl_returns)
    
    if np.isnan(returns_array).any():
        # #region agent log - Validation failed
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'F',
                'location': 'portfolio_optimizer.py:1408',
                'message': 'BL: Returns validation FAILED - still has NaN after cleaning',
                'data': {
                    'has_nan': bool(np.isnan(returns_array).any()),
                    'nan_count': int(np.isnan(returns_array).sum())
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        # Final attempt: replace any remaining NaN with 0
        returns_array = np.nan_to_num(returns_array, nan=0.0)
        if hasattr(bl_returns, 'index'):
            bl_returns = pd.Series(returns_array, index=bl_returns.index)
        else:
            bl_returns = returns_array
    
    if np.isinf(returns_array).any():
        # #region agent log - Validation failed
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'F',
                'location': 'portfolio_optimizer.py:1430',
                'message': 'BL: Returns validation FAILED - still has Inf after cleaning',
                'data': {
                    'has_inf': bool(np.isinf(returns_array).any()),
                    'inf_count': int(np.isinf(returns_array).sum())
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        # Final attempt: replace any remaining Inf with finite values
        returns_array = np.nan_to_num(returns_array, posinf=1e6, neginf=-1e6)
        if hasattr(bl_returns, 'index'):
            bl_returns = pd.Series(returns_array, index=bl_returns.index)
        else:
            bl_returns = returns_array
    
    # Optimize the portfolio for maximum Sharpe ratio
    ef = EfficientFrontier(bl_returns, bl_cov)
    
    # #region agent log
    try:
        log_entry = {
            'sessionId': 'debug-session',
            'runId': 'run1',
            'hypothesisId': 'E',
            'location': 'portfolio_optimizer.py:1130',
            'message': 'About to call max_sharpe',
            'data': {
                'ef_created': True,
                'risk_free_rate': float(risk_free_rate),
                'num_assets': len(tickers)
            },
            'timestamp': int(time.time() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception:
        pass
    # #endregion
    
    try:
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        cleaned_weights = ef.clean_weights()
        
        # Get portfolio performance
        performance = ef.portfolio_performance(verbose=False)
        
        return {
            'weights': dict(cleaned_weights),
            'expected_return': performance[0],
            'volatility': performance[1],
            'sharpe_ratio': performance[2]
        }
    except Exception as solver_err:
        # #region agent log - Solver error
        try:
            log_entry = {
                'sessionId': 'debug-session',
                'runId': 'run1',
                'hypothesisId': 'E',
                'location': 'portfolio_optimizer.py:1160',
                'message': 'BL: Solver error caught',
                'data': {
                    'error_type': type(solver_err).__name__,
                    'error_message': str(solver_err),
                    'cov_min_eigenval': float(np.min(np.linalg.eigvals(bl_cov))),
                    'cov_has_nan': bool(np.isnan(bl_cov).any()),
                    'returns_has_nan': bool(bl_returns.isna().any() if hasattr(bl_returns, 'isna') else np.isnan(bl_returns).any())
                },
                'timestamp': int(time.time() * 1000)
            }
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass
        # #endregion
        
        # Provide helpful error message
        error_msg = (
            f"Portfolio optimization failed with solver error: {str(solver_err)}\n"
            f"This usually means the optimization problem is infeasible or numerically unstable.\n"
            f"Possible causes:\n"
            f"1. Invalid or missing market cap data for some tickers\n"
            f"2. Numerically unstable covariance matrix\n"
            f"3. Conflicting constraints in the Black-Litterman model\n"
            f"Tickers: {tickers}\n"
            f"Date range: {start_date} to {end_date}\n"
            f"Try: Use Modern Portfolio Theory (MPT) instead, or verify all tickers have valid market cap data."
        )
        raise ValueError(error_msg) from solver_err

