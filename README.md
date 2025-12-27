# Genesis Alpha 📈

A comprehensive Streamlit application for stock analysis and portfolio optimization powered by Generative AI.

## Features

- **🤖 GenAI-Powered Ticker Extraction**: Automatically extract stock tickers from asset names using OpenAI
- **📊 Key Performance Indicators (KPIs)**: Calculate RSI, Bollinger Bands, P/E Ratio, Beta, and MACD
- **📈 Technical Indicators Visualization**: Interactive charts for all major technical indicators
- **💼 Portfolio Optimization**: 
  - Black-Litterman model optimization
  - Risk Parity optimization
- **🤖 AI Recommendations**: Get AI-powered investment recommendations based on KPI analysis

## Installation

1. Clone or download this repository

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)

2. Configure your API key using one of these methods (in order of priority):
   - **Environment variable** (recommended):
     ```bash
     # Windows (PowerShell)
     $env:OPENAI_API_KEY="your-api-key-here"
     
     # Windows (CMD)
     set OPENAI_API_KEY=your-api-key-here
     
     # Linux/Mac
     export OPENAI_API_KEY="your-api-key-here"
     ```
   - **`.env` file** (create from `.env.example`):
     ```bash
     cp .env.example .env
     # Then edit .env and add your API key
     ```
   - **`api_key.txt` file** (for backward compatibility):
     ```bash
     echo "your-api-key-here" > api_key.txt
     ```

**⚠️ Important**: Never commit your API key to the repository. The `.gitignore` file is configured to exclude sensitive files.

## Usage

Run the Streamlit app:

```bash
streamlit run app/main.py
```

The app will open in your default web browser at `http://localhost:8501`

## Project Structure

```
.
├── app/
│   └── main.py              # Main Streamlit application
├── utils/
│   ├── llm_utils.py         # LLM initialization and response functions
│   ├── date_utils.py         # Date calculation utilities
│   ├── kpi_calculator.py    # KPI calculation functions
│   ├── portfolio_optimizer.py  # Portfolio optimization functions
│   └── visualizations.py    # Chart generation functions
├── config/
│   └── settings.py          # Configuration settings
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## How to Use

1. **Enter API Key**: Input your OpenAI API key in the sidebar
2. **Select Assets**: Enter asset names (e.g., "Apple (AAPL)") or use the default list
3. **Extract Tickers**: Click "Extract Tickers with GenAI" to automatically parse ticker symbols
4. **Configure Settings**: Adjust years of historical data and risk-free rates
5. **Analyze**: 
   - View KPIs in the "KPIs & Analysis" tab
   - Generate technical indicator charts in the "Technical Indicators" tab
   - Optimize your portfolio in the "Portfolio Optimization" tab
   - Get AI recommendations in the "AI Recommendations" tab

## Features Explained

### RSI (Relative Strength Index)
- Values above 70 indicate overbought conditions
- Values below 30 indicate oversold conditions

### Bollinger Bands
- Upper and lower bands indicate volatility
- Price touching upper band = potentially overbought
- Price touching lower band = potentially oversold

### P/E Ratio
- Measures stock price relative to earnings
- High P/E = potentially overvalued or high growth expected
- Low P/E = potentially undervalued

### Beta
- Measures volatility relative to market
- Beta > 1 = more volatile than market
- Beta < 1 = less volatile than market

### MACD
- Trend-following momentum indicator
- MACD crossing above signal = bullish signal
- MACD crossing below signal = bearish signal

### Portfolio Optimization
- **Black-Litterman**: Incorporates market views and equilibrium returns for personalized portfolio optimization
- **Risk Parity**: Balances risk contribution across all assets for more stable portfolios

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for fetching stock data

## License

This project is for educational purposes.

## Disclaimer

This application is for educational and informational purposes only. It does not constitute financial advice. Always consult with a qualified financial advisor before making investment decisions.
