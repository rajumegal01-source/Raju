#!/bin/bash

echo "🚀 Starting Termux Setup for Binary Option AI Bot..."

# Update system
echo "📦 Updating packages..."
pkg update -y && pkg upgrade -y

# Install dependencies
echo "🛠 Installing Python and Build Tools..."
pkg install python git clang make -y

# Install python requirements
echo "🐍 Installing Python libraries..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with 'nano .env' to add your API keys."
fi

echo "✨ Setup Complete!"
echo "To start the bot, run: python trading_bot.py"
