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
        "/analyze <ticker> <provider> - AI Market Analysis (deepseek, gemini, groq, openrouter)\n"
        "/signal <ticker> <timeframe> - Get Binary Option Signal (1min, 5min)\n\n"
        "💡 **Examples:**\n"
        "• Binary Signal: `/signal EUR/USD 1min`\n"
        "• AI Analysis: `/analyze BTC/USD gemini`\n"
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
        await update.message.reply_text("Twelve Data API Key is missing.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /signal <ticker> [timeframe]")
        return

    symbol = context.args[0].upper()
    interval = context.args[1] if len(context.args) > 1 else "1min"

    await update.message.reply_text(f"Generating signal for {symbol} on {interval}...")

    try:
        td = TDClient(apikey=TWELVEDATA_API_KEY)
        ts = td.time_series(symbol=symbol, interval=interval, outputsize=100)
        df = ts.as_pd()

        if df.empty:
            await update.message.reply_text("Could not fetch data.")
            return

        # Correct data ordering: newest last
        df = df.iloc[::-1]

        df.columns = [c.lower() for c in df.columns]
        df = analysis_engine.calculate_indicators(df)
        supports, resistances = analysis_engine.detect_support_resistance(df)
        binary_call = analysis_engine.get_binary_signal(df)

        response = (
            f"🎯 **SIGNAL: {symbol} ({interval})**\n"
            f"💰 Price: {df.iloc[-1]['close']:.5f}\n\n"
            f"💹 **Direction: {binary_call}**\n\n"
            f"🧱 Support: {', '.join([str(s) for s in supports])}\n"
            f"🚀 Resistance: {', '.join([str(r) for r in resistances])}\n"
        )
        await update.message.reply_text(response, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"Signal Error: {e}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /analyze <ticker> [provider]")
        return

    symbol = context.args[0].upper()
    provider = context.args[1].lower() if len(context.args) > 1 else "deepseek"

    await update.message.reply_text(f"Analyzing {symbol} using {provider}... please wait.")

    try:
        # Get data
        if TWELVEDATA_API_KEY:
            td = TDClient(apikey=TWELVEDATA_API_KEY)
            ts = td.time_series(symbol=symbol, interval="5min", outputsize=20)
            df = ts.as_pd()
            df = df.iloc[::-1] # Ascending order
        else:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="1d", interval="5m")

        if df.empty:
            await update.message.reply_text("Could not find data for analysis.")
            return

        market_data = df.tail(10).to_string()
        prompt = f"Analyze the following 5-minute market data for {symbol} and provide a Binary Options trading recommendation (CALL/PUT/NEUTRAL):\n{market_data}"

        analysis = "Provider not configured or unavailable."

        if provider == "deepseek" and DEEPSEEK_API_KEY:
            headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
            async with httpx.AsyncClient() as client:
                resp = await client.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30.0)
            if resp.status_code == 200:
                analysis = resp.json()['choices'][0]['message']['content']

        elif provider == "gemini" and GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            # Run blocking call in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: model.generate_content(prompt))
            analysis = response.text

        elif provider == "groq" and GROQ_API_KEY:
            client = AsyncGroq(api_key=GROQ_API_KEY)
            chat_completion = await client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="mixtral-8x7b-32768",
            )
            analysis = chat_completion.choices[0].message.content

        elif provider == "openrouter" and OPENROUTER_API_KEY:
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "openai/gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}]}
            async with httpx.AsyncClient() as client:
                resp = await client.post(OPENROUTER_API_URL, headers=headers, json=data, timeout=30.0)
            if resp.status_code == 200:
                analysis = resp.json()['choices'][0]['message']['content']

        await update.message.reply_text(f"🤖 **{provider.upper()} Analysis for {symbol}:**\n\n{analysis}")

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

    print("Final Binary Option Bot started...")
    application.run_polling()
