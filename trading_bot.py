import logging
import os
import yfinance as yf
import httpx
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "👋 Welcome to the Trading AI Bot!\n\n"
        "I can provide real-time prices and AI-powered analysis for various assets.\n\n"
        "📊 **Commands:**\n"
        "/price <ticker> - Get real-time price\n"
        "/analyze <ticker> - AI Market Analysis\n\n"
        "💡 **Examples:**\n"
        "• Stocks: `/price AAPL`\n"
        "• Bitcoin: `/price BTC-USD`\n"
        "• Forex: `/price EURUSD=X`\n"
        "• Gold: `/price GC=F` (Gold Futures)\n"
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

        # Accessing as attribute because FastInfo is not subscriptable in latest yfinance
        price_info = fast_info.last_price
        if price_info is None:
             await update.message.reply_text(f"Could not find price for {ticker_symbol}. Please check the ticker.")
             return

        currency = getattr(fast_info, 'currency', 'USD')
        await update.message.reply_text(f"The current price of {ticker_symbol} is {price_info:.2f} {currency}")
    except Exception as e:
        logging.error(f"Error fetching price for {ticker_symbol}: {e}")
        await update.message.reply_text(f"Could not fetch price for {ticker_symbol}. Error: {str(e)}")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not DEEPSEEK_API_KEY:
        await update.message.reply_text("AI Analysis is currently unavailable (API key not configured).")
        return

    if not context.args:
        await update.message.reply_text("Please provide a ticker symbol. Usage: /analyze BTC-USD")
        return

    ticker_symbol = context.args[0].upper()
    await update.message.reply_text(f"Analyzing {ticker_symbol}... please wait.")

    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1mo")
        if hist.empty:
            await update.message.reply_text(f"Could not find historical data for {ticker_symbol}.")
            return

        fast_info = ticker.fast_info
        current_price = fast_info.last_price

        # Try to get some info, handle potential empty info
        try:
            info = ticker.info
        except Exception:
            info = {}

        analysis_context = f"""
        Ticker: {ticker_symbol}
        Current Price: {current_price}
        Asset Info: {info.get('longName', ticker_symbol)}
        Recent Price History (1 month):
        {hist[['Close', 'Volume']].tail(5).to_string()}
        """

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a professional financial analyst. Provide a brief analysis and trading sentiment (Bullish/Bearish/Neutral) based on the provided data."},
                {"role": "user", "content": f"Analyze the following data:\n{analysis_context}"}
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30.0)

        if response.status_code == 200:
            analysis = response.json()['choices'][0]['message']['content']
            await update.message.reply_text(f"AI Analysis for {ticker_symbol}:\n\n{analysis}")
        else:
            await update.message.reply_text(f"Error from AI service: {response.status_code}")

    except Exception as e:
        logging.error(f"Error analyzing {ticker_symbol}: {e}")
        await update.message.reply_text(f"An error occurred during analysis: {e}")

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment or .env file.")
        sys.exit(1)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('price', price))
    application.add_handler(CommandHandler('analyze', analyze))

    print("Bot started...")
    application.run_polling()
