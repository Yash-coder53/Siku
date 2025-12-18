#!/bin/bash

# SIKU TAGALL BOT - Start Script

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════╗"
echo "║            SIKU TAGALL BOT - Starting              ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if already running
if pgrep -f "python3 main.py" > /dev/null || pgrep -f "python main.py" > /dev/null; then
    echo -e "${YELLOW}[!] Bot is already running!${NC}"
    echo -e "Use ${BLUE}./stop.sh${NC} to stop it first."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python3 is not installed!${NC}"
    exit 1
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}[+] Virtual environment activated${NC}"
else
    echo -e "${YELLOW}[!] Virtual environment not found${NC}"
    echo -e "Run ${BLUE}./setup.sh${NC} first to set up the environment."
    exit 1
fi

# Check requirements
echo -e "${BLUE}[*] Checking requirements...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}[+] Requirements checked${NC}"

# Check configuration
if [ ! -f "bot_settings.json" ]; then
    echo -e "${RED}[!] bot_settings.json not found!${NC}"
    echo "Run ./setup.sh first to create configuration files."
    exit 1
fi

# Check if credentials are set
if grep -q "your_api_hash_here\|your_bot_token_here\|123456" bot_settings.json; then
    echo -e "${YELLOW}[!] Warning: Default API credentials detected${NC}"
    echo "Please edit bot_settings.json with your actual credentials"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Set Python path
export PYTHONPATH=$PWD:$PYTHONPATH

# Run the bot
echo -e "${BLUE}[*] Starting SIKU TAGALL BOT...${NC}"
echo -e "${GREEN}[+] Bot started successfully!${NC}"
echo -e "${YELLOW}[*] Press Ctrl+C to stop${NC}"
echo -e "${YELLOW}[*] Check bot.log for logs${NC}"
echo ""

# Create log directory if not exists
mkdir -p logs

# Run the bot
python3 main.py

# Handle exit
echo ""
echo -e "${BLUE}[*] Bot stopped${NC}"

# Deactivate virtual environment
deactivate 2>/dev/null
echo -e "${GREEN}[+] Virtual environment deactivated${NC}"

echo -e "${CYAN}Goodbye!${NC}"
