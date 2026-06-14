# Telegram AI Trading Bot

A Telegram bot that provides real-time stock prices and AI-powered market analysis using DeepSeek.

## Features

- `/start`: Welcome message and list of commands.
- `/price <ticker>`: Get the current price of an asset.
- `/analyze <ticker>`: Get AI-powered sentiment and analysis for an asset.

## Asset Examples

- **Bitcoin (USD)**: `/price BTC-USD`
- **Forex (EUR/USD)**: `/price EURUSD=X`
- **Gold (Futures)**: `/price GC=F`
- **Stocks (Apple)**: `/price AAPL`

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your API keys:
   - `TELEGRAM_BOT_TOKEN`: Get this from [@BotFather](https://t.me/BotFather) on Telegram.
   - `DEEPSEEK_API_KEY`: Get this from the DeepSeek API portal.

3. **Run the Bot**:
   ```bash
   python trading_bot.py
   ```

## Development

The bot uses:
- `python-telegram-bot` for the Telegram interface (asynchronous).
- `yfinance` for fetching market data.
- `httpx` for asynchronous requests to the DeepSeek API.
- `python-dotenv` for managing environment variables.
