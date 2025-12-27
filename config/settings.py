"""
Configuration settings for the application
"""
import os
from pathlib import Path

# Default settings
DEFAULT_YEARS = 2
DEFAULT_RISK_FREE_RATE_MPT = 0.04
DEFAULT_RISK_FREE_RATE_BL = 0.001

# Default assets list
DEFAULT_ASSETS = [
    "Apple (AAPL)",
    "Amazon (AMZN)",
    "Alphabet (GOOGL)",
    "Meta (META)",
    "Microsoft (MSFT)",
    "Nvidia (NVDA)",
    "S&P 500 index (SPY)",
    "Tesla (TSLA)"
]

# Get API key from multiple sources (priority order):
# 1. Environment variable
# 2. .env file in project root
# 3. api_key.txt file in project root (for backward compatibility)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Try to load from .env file if not in environment
if not OPENAI_API_KEY:
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('OPENAI_API_KEY='):
                        OPENAI_API_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass

# Try to load from api_key.txt file if still not found
if not OPENAI_API_KEY:
    api_key_file = Path(__file__).parent.parent / "api_key.txt"
    if api_key_file.exists():
        try:
            with open(api_key_file, 'r') as f:
                OPENAI_API_KEY = f.read().strip()
        except Exception:
            pass

