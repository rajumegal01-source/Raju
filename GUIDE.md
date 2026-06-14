# 🚀 Step-by-Step Guide: Telegram AI Trading Bot

This guide will walk you through setting up and using your Binary Options AI Trading Bot from scratch.

---

## 🛠 Step 1: Get Your API Keys

You need several keys to make the bot fully functional:

1.  **Telegram Bot Token**:
    *   Open Telegram and search for **@BotFather**.
    *   Send `/newbot` and follow the instructions.
    *   Copy the **API Token** provided.
2.  **Twelve Data (Market Data)**:
    *   Go to [twelvedata.com](https://twelvedata.com/) and sign up for a free account.
    *   Copy your **API Key** from the dashboard. This is needed for Forex and 1-minute data.
3.  **AI Providers (Pick at least one)**:
    *   **DeepSeek**: [platform.deepseek.com](https://platform.deepseek.com/)
    *   **Gemini**: [aistudio.google.com](https://aistudio.google.com/)
    *   **Groq**: [console.groq.com](https://console.groq.com/)
    *   **OpenRouter**: [openrouter.ai](https://openrouter.ai/)

---

## 📱 Step 2: Installation on Termux (Mobile)

1.  **Install Termux** from F-Droid.
2.  **Run the automated setup**:
    ```bash
    pkg update && pkg upgrade
    pkg install python git clang make -y
    git clone <your-repo-url>
    cd <your-repo-name>
    pip install -r requirements.txt
    ```
3.  **Configure API Keys**:
    ```bash
    cp .env.example .env
    nano .env
    ```
    *Replace the placeholders with your actual keys.*

---

## 💻 Step 3: Installation on PC (Windows/Mac/Linux)

1.  **Install Python 3.10+**.
2.  **Clone the project** and open a terminal in the folder.
3.  **Install requirements**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create `.env` file** and add your keys.

---

## 🤖 Step 4: Running and Using the Bot

1.  **Start the bot**:
    ```bash
    python trading_bot.py
    ```
2.  **Open Telegram** and find your bot.
3.  **Use the commands**:

### 📊 Get Real-Time Price
> `/price BTC-USD`
> `/price EURUSD=X` (Forex)
> `/price GC=F` (Gold)

### 🎯 Get Binary Option Signal
> `/signal EUR/USD 1min`
> `/signal BTC/USD 5min`
*Generates a CALL or PUT recommendation based on RSI, Bollinger Bands, and EMA.*

### 🤖 Get AI Market Analysis
> `/analyze AAPL deepseek`
> `/analyze BTC/USD gemini`
*Uses advanced AI models to provide professional market sentiment.*

---

## 💡 Pro Tips
*   **Forex Tickers**: Use `EUR/USD` for signals (TwelveData) and `EURUSD=X` for prices (Yahoo).
*   **Timeframes**: Use `1min`, `5min`, `15min`, `1h`.
*   **AI Choice**: `groq` and `gemini` are usually the fastest for quick analysis.
