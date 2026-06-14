import logging
import os
import yfinance as yf
import httpx
import sys
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
from twelvedata import TDClient
import analysis_engine

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🚀 **Binary Options AI Trading Bot**\n\n"
        "I provide high-precision signals and AI analysis for Forex, Crypto, and Metals.\n\n"
        "📊 **Commands:**\n"
        "/price <ticker> - Get real-time price\n"
        "/analyze <ticker> - AI Market Analysis\n"
        "/signal <ticker> <timeframe> - Get Binary Option Signal (1m, 2m, 3m, 5m)\n\n"
        "💡 **Examples:**\n"
        "• Binary Signal: `/signal EUR/USD 1min`\n"
        "• Crypto Signal: `/signal BTC/USD 5min`\n"
        "• Gold Price: `/price GC=F`\n"
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
        price_info = fast_info.last_price
        if price_info is None:
             await update.message.reply_text(f"Could not find price for {ticker_symbol}.")
             return

        currency = getattr(fast_info, 'currency', 'USD')
        await update.message.reply_text(f"The current price of {ticker_symbol} is {price_info:.2f} {currency}")
    except Exception as e:
        await update.message.reply_text(f"Error fetching price: {str(e)}")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not TWELVEDATA_API_KEY:
        await update.message.reply_text("Twelve Data API Key is missing. Check your .env file.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /signal <ticker> [timeframe]\nExample: /signal EUR/USD 1min")
        return

    symbol = context.args[0].upper()
    interval = context.args[1] if len(context.args) > 1 else "1min"

    if interval not in ["1min", "2min", "3min", "5min", "15min", "30min", "45min", "1h"]:
        await update.message.reply_text("Invalid timeframe. Supported: 1min, 2min, 3min, 5min, etc.")
        return

    await update.message.reply_text(f"Generating signal for {symbol} on {interval} timeframe...")

    try:
        td = TDClient(apikey=TWELVEDATA_API_KEY)
        ts = td.time_series(symbol=symbol, interval=interval, outputsize=100)
        df = ts.as_pd()

        if df.empty:
            await update.message.reply_text("Could not fetch data for this symbol.")
            return

        # Prepare data for analysis_engine (it expects lowercase columns usually or specific names)
        df.columns = [c.lower() for c in df.columns]
        df = analysis_engine.calculate_indicators(df)
        supports, resistances = analysis_engine.detect_support_resistance(df)
        binary_call = analysis_engine.get_binary_signal(df)

        latest_price = df.iloc[-1]['close']

        response = (
            f"🎯 **SIGNAL: {symbol} ({interval})**\n"
            f"💰 Price: {latest_price:.5f}\n\n"
            f"💹 **Direction: {binary_call}**\n\n"
            f"🧱 Support: {', '.join([str(s) for s in supports])}\n"
            f"🚀 Resistance: {', '.join([str(r) for r in resistances])}\n"
            f"📈 RSI: {df.iloc[-1].get('RSI_14', 'N/A'):.2f}"
        )
        await update.message.reply_text(response, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Signal Error: {e}")
        await update.message.reply_text(f"Error generating signal: {e}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not DEEPSEEK_API_KEY:
        await update.message.reply_text("DeepSeek API Key is missing.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /analyze <ticker>")
        return

    symbol = context.args[0].upper()
    await update.message.reply_text(f"Analyzing {symbol}... please wait.")

    try:
        # Get data from Twelve Data for more accuracy if available, else yf
        if TWELVEDATA_API_KEY:
            td = TDClient(apikey=TWELVEDATA_API_KEY)
            ts = td.time_series(symbol=symbol, interval="5min", outputsize=50)
            df = ts.as_pd()
            data_source = "Twelve Data"
        else:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1d", interval="5m")
            data_source = "Yahoo Finance"

        if df.empty:
            await update.message.reply_text("Could not find data for analysis.")
            return

        # Technical context
        latest_price = df.iloc[-1]['Close'] if 'Close' in df.columns else df.iloc[-1]['close']

        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are an expert binary options analyst. Analyze the market data and provide a concise summary and binary option sentiment."},
                {"role": "user", "content": f"Symbol: {symbol}\nPrice: {latest_price}\nData from {data_source}:\n{df.tail(10).to_string()}"}
            ]
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30.0)

        if resp.status_code == 200:
            analysis = resp.json()['choices'][0]['message']['content']
            await update.message.reply_text(f"🤖 **AI Analysis for {symbol}:**\n\n{analysis}")
        else:
            await update.message.reply_text(f"AI Error: {resp.status_code}")

    except Exception as e:
        await update.message.reply_text(f"Analysis Error: {e}")

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN missing.")
        sys.exit(1)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('price', price))
    application.add_handler(CommandHandler('signal', signal))
    application.add_handler(CommandHandler('analyze', analyze))

    print("Binary Option Bot started...")
    application.run_polling()
