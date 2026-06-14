import logging
import os
import yfinance as yf
import httpx
import sys
import pandas as pd
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
from twelvedata import TDClient
import analysis_engine
import google.generativeai as genai
from groq import AsyncGroq

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Cache for ticker info to improve speed
info_cache = {}

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def get_ticker_info(ticker_symbol):
    """Cached and non-blocking ticker info retrieval."""
    if ticker_symbol in info_cache:
        return info_cache[ticker_symbol]

    try:
        ticker = yf.Ticker(ticker_symbol)
        # Running ticker.info in executor because it is slow and blocking
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: ticker.info)
        info_cache[ticker_symbol] = info
        return info
    except Exception as e:
        logging.error(f"Error fetching info for {ticker_symbol}: {e}")
        return {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🚀 **Binary Options AI Trading Bot (Optimized)**\n\n"
        "I provide high-precision signals and AI analysis for Forex, Crypto, and Metals.\n\n"
        "📊 **Commands:**\n"
        "/price <ticker> - Get real-time price\n"
        "/analyze <ticker> <provider> - AI Market Analysis\n"
        "/signal <ticker> <timeframe> - Get Binary Option Signal (1m, 2m, 3m, 5m)\n\n"
        "💡 **Examples:**\n"
        "• Binary Signal: `/signal EUR/USD 1min`\n"
        "• AI Analysis: `/analyze BTC/USD gemini`\n"
    )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text,
        parse_mode='Markdown'
    )

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a ticker symbol. Usage: /price BTC-USD")
        return

    ticker_symbol = context.args[0].upper()
    try:
        ticker = yf.Ticker(ticker_symbol)
        fast_info = ticker.fast_info
        price_val = fast_info.last_price
        if price_val is None:
             await update.message.reply_text(f"Could not find price for {ticker_symbol}.")
             return

        currency = getattr(fast_info, 'currency', 'USD')
        await update.message.reply_text(f"💰 **{ticker_symbol}**: {price_val:.5f} {currency}", parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /signal <ticker> [timeframe]")
        return

    symbol = context.args[0].upper()
    interval = context.args[1] if len(context.args) > 1 else "1min"

    # Map intervals for yfinance/twelvedata compatibility
    td_interval = interval
    if interval == "2m": td_interval = "2min"
    if interval == "3m": td_interval = "3min"
    if interval == "5m": td_interval = "5min"
    if interval == "1m": td_interval = "1min"

    await update.message.reply_text(f"🔍 Generating signal for {symbol} ({td_interval})...")

    try:
        df = pd.DataFrame()
        # Prefer Twelve Data for intraday
        if TWELVEDATA_API_KEY:
            try:
                td = TDClient(apikey=TWELVEDATA_API_KEY)
                ts = td.time_series(symbol=symbol, interval=td_interval, outputsize=100)
                df = ts.as_pd()
                if not df.empty:
                    df = df.iloc[::-1] # Newest last
            except Exception as e:
                logging.warning(f"TwelveData failed for {symbol}: {e}")

        # Fallback to yfinance
        if df.empty:
            yf_interval = "1m"
            if "2" in td_interval: yf_interval = "2m"
            if "5" in td_interval: yf_interval = "5m"

            ticker = yf.Ticker(symbol.replace("/", ""))
            df = ticker.history(period="1d", interval=yf_interval)

        if df.empty:
            await update.message.reply_text("❌ Could not fetch data for signal.")
            return

        df.columns = [c.lower() for c in df.columns]
        df = analysis_engine.calculate_indicators(df)
        supports, resistances = analysis_engine.detect_support_resistance(df)
        binary_call = analysis_engine.get_binary_signal(df)

        response = (
            f"🎯 **SIGNAL: {symbol} ({td_interval})**\n"
            f"💵 Price: {df.iloc[-1]['close']:.5f}\n\n"
            f"💹 **Direction: {binary_call}**\n\n"
            f"🧱 Support: {', '.join([f'{s:.5f}' for s in supports])}\n"
            f"🚀 Resistance: {', '.join([f'{r:.5f}' for r in resistances])}\n"
        )
        await update.message.reply_text(response, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Signal Error: {e}")
        await update.message.reply_text(f"⚠️ Signal Error: {e}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /analyze <ticker> [provider]")
        return

    symbol = context.args[0].upper()
    provider = context.args[1].lower() if len(context.args) > 1 else "deepseek"

    await update.message.reply_text(f"🤖 Analyzing {symbol} via {provider}... This may take a moment.")

    try:
        # Fetch data and info in parallel to save time
        data_task = None
        if TWELVEDATA_API_KEY:
            td = TDClient(apikey=TWELVEDATA_API_KEY)
            ts = td.time_series(symbol=symbol, interval="5min", outputsize=20)
            data_task = asyncio.to_thread(ts.as_pd)
        else:
            ticker = yf.Ticker(symbol)
            data_task = asyncio.to_thread(ticker.history, period="1d", interval="5m")

        info_task = get_ticker_info(symbol)

        df, info = await asyncio.gather(data_task, info_task)

        if df.empty:
            await update.message.reply_text("❌ No data available for analysis.")
            return

        market_data = df.tail(10).to_string()
        company_name = info.get('longName', symbol)
        summary = info.get('longBusinessSummary', 'No summary available.')[:300]

        prompt = f"Expert Analysis for {company_name} ({symbol}):\n{summary}\n\nRecent 5min Data:\n{market_data}\n\nProvide a Binary Options recommendation (CALL/PUT/NEUTRAL) and brief reasoning."

        analysis = "Provider not configured."

        async with httpx.AsyncClient() as client:
            if provider == "deepseek" and DEEPSEEK_API_KEY:
                resp = await client.post(DEEPSEEK_API_URL,
                    headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                    json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]},
                    timeout=40.0)
                if resp.status_code == 200:
                    analysis = resp.json()['choices'][0]['message']['content']

            elif provider == "gemini" and GEMINI_API_KEY:
                genai.configure(api_key=GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-pro')
                response = await asyncio.to_thread(model.generate_content, prompt)
                analysis = response.text

            elif provider == "groq" and GROQ_API_KEY:
                groq_client = AsyncGroq(api_key=GROQ_API_KEY)
                chat_completion = await groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="mixtral-8x7b-32768",
                )
                analysis = chat_completion.choices[0].message.content

            elif provider == "openrouter" and OPENROUTER_API_KEY:
                resp = await client.post(OPENROUTER_API_URL,
                    headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
                    json={"model": "openai/gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]},
                    timeout=40.0)
                if resp.status_code == 200:
                    analysis = resp.json()['choices'][0]['message']['content']

        await update.message.reply_text(f"📊 **{provider.upper()} Analysis:**\n\n{analysis}", parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"⚠️ Analysis Error: {e}")

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN missing.")
        sys.exit(1)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('price', price))
    application.add_handler(CommandHandler('signal', signal))
    application.add_handler(CommandHandler('analyze', analyze))

    print("Optimized Binary Option Bot is running...")
    application.run_polling()
