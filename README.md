# Binary Option AI Trading Bot

A high-performance Telegram bot for Binary Options (Forex, Crypto, Gold) with multi-AI analysis. Optimized for speed and reliability.

## Features

- **Multi-AI Analysis**: DeepSeek, Gemini, Groq, and OpenRouter.
- **Precision Signals**: CALL/PUT signals for 1m, 2m, 3m, and 5m timeframes.
- **Advanced Indicators**: RSI, Bollinger Bands, and EMA crossover.
- **Speed Optimized**: Caching and parallel data fetching.

## Commands

- `/start`: Help and command list.
- `/price <ticker>`: Real-time price.
- `/signal <ticker> <timeframe>`: Binary Option signal.
- `/analyze <ticker> <provider>`: AI Analysis.

## Setup (PC/Server)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure**: Copy `.env.example` to `.env` and add keys.
3. **Run**: `python trading_bot.py`

## Termux Setup Guide (Mobile)

To run this bot on your Android phone using Termux, follow these steps:

1. **Install Termux** from F-Droid (not Play Store).
2. **Update Packages**:
   ```bash
   pkg update && pkg upgrade
   ```
3. **Install Python & Git**:
   ```bash
   pkg install python git clang make
   ```
4. **Clone the Bot**:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```
5. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
6. **Setup Environment**:
   ```bash
   cp .env.example .env
   nano .env
   ```
   (Paste your keys and press `Ctrl+O`, `Enter`, `Ctrl+X`)
7. **Run the Bot**:
   ```bash
   python trading_bot.py
   ```

## Binary Options Strategy

The bot utilizes a combined strategy:
1. **Mean Reversion**: Bollinger Bands.
2. **Momentum**: RSI.
3. **Price Action**: Support and Resistance.
4. **Trend**: EMA 9/21 Crossovers.
