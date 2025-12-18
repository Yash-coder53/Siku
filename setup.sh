#!/bin/bash

# SIKU TAGALL BOT - Setup Script

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
echo "║            SIKU TAGALL BOT - Setup                 ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}[!] Warning: Running as root is not recommended${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python
echo -e "${BLUE}[*] Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python3 is not installed!${NC}"
    echo "Please install Python 3.8 or higher:"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "macOS: brew install python"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc) -eq 1 ]] 2>/dev/null; then
    echo -e "${RED}[!] Python 3.8 or higher is required!${NC}"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi
echo -e "${GREEN}[+] Python $PYTHON_VERSION detected${NC}"

# Create directories
echo -e "${BLUE}[*] Creating directories...${NC}"
mkdir -p data backups
echo -e "${GREEN}[+] Created data/ and backups/ directories${NC}"

# Create virtual environment
echo -e "${BLUE}[*] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}[+] Virtual environment created${NC}"
else
    echo -e "${YELLOW}[!] Virtual environment already exists${NC}"
fi

# Activate virtual environment and install requirements
echo -e "${BLUE}[*] Installing requirements...${NC}"
source venv/bin/activate
pip install --upgrade pip setuptools wheel > /dev/null 2>&1

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}[+] Requirements installed${NC}"
else
    echo -e "${YELLOW}[!] requirements.txt not found, creating default...${NC}"
    cat > requirements.txt << 'EOL'
telethon==1.34.0
psutil==5.9.6
colorama==0.4.6
python-dotenv==1.0.0
aiofiles==23.2.1
EOL
    pip install -r requirements.txt
    echo -e "${GREEN}[+] Default requirements installed${NC}"
fi

# Create default configuration files
echo -e "${BLUE}[*] Creating configuration files...${NC}"

# bot_settings.json
if [ ! -f "bot_settings.json" ]; then
    cat > bot_settings.json << 'EOL'
{
  "api_id": 0,
  "api_hash": "your_api_hash_here",
  "bot_token": "your_bot_token_here",
  "owner_id": 0,
  "session_name": "siku_tagall_bot.session",
  "connection_retries": 10,
  "retry_delay": 3,
  "max_message_length": 4096,
  "auto_save_interval": 60,
  "siku_cooldown": 10,
  "max_siku_messages": 500,
  "siku_max_length": 1000,
  "raid_max_users": 100,
  "raid_min_delay": 0.3,
  "raid_max_delay": 3.0,
  "raid_max_sessions_per_user": 5,
  "raid_max_messages_per_session": 200,
  "raid_cooldown": 60,
  "raid_default_count": 20,
  "tagall_cooldown": 120,
  "tagall_max_users": 200,
  "tagall_message_templates": [
    "🚨 Attention everyone!",
    "📢 Announcement for all members!",
    "👋 Hey everyone, listen up!",
    "🎯 Important message for all!",
    "🔔 Notification for all members!"
  ],
  "default_siku_gm": [
    "Good morning! ☀️ Rise and shine!",
    "Morning! 🌄 Hope you have a great day ahead!",
    "Good morning sunshine! 🌞",
    "Wakey wakey! 🌅 It's a new day!",
    "Morning vibes! 🌤 Have an amazing day!",
    "Good morning! 🌻 May your day be filled with joy!",
    "🌅 Morning everyone! Time to conquer the day!",
    "☕ Good morning! Coffee's ready!",
    "🌞 Good morning! Let's make today amazing!",
    "🌄 Rise and grind! Good morning!"
  ],
  "default_siku_gn": [
    "Good night! 🌙 Sleep well!",
    "Night night! 🌌 Sweet dreams!",
    "Good night! 🌠 Rest peacefully!",
    "Sleep tight! 🌃 Don't let the bed bugs bite!",
    "Good night! 🌜 May you have peaceful dreams!",
    "Night! 🌉 See you in the morning!",
    "🌙 Time to rest! Good night everyone!",
    "✨ Sweet dreams! Good night!",
    "🌠 Good night! Rest well for tomorrow!",
    "🌌 Night night! Sleep tight!"
  ]
}
EOL
    echo -e "${YELLOW}[!] Created bot_settings.json - Please edit with your credentials!${NC}"
else
    echo -e "${GREEN}[+] bot_settings.json already exists${NC}"
fi

# Create empty data files
echo -e "${BLUE}[*] Creating data files...${NC}"
for file in main_data siku_data raid_data; do
    if [ ! -f "data/${file}.json" ]; then
        echo "{}" > "data/${file}.json"
        echo -e "${GREEN}[+] Created data/${file}.json${NC}"
    fi
done

# Make scripts executable
echo -e "${BLUE}[*] Making scripts executable...${NC}"
chmod +x start.sh stop.sh restart.bsh update.sh setup.sh 2>/dev/null || true
echo -e "${GREEN}[+] Scripts are now executable${NC}"

# Test installation
echo -e "${BLUE}[*] Testing installation...${NC}"
source venv/bin/activate
python3 -c "
try:
    import telethon
    print(f'✅ Telethon version: {telethon.__version__}')
    import psutil
    print(f'✅ Psutil installed')
    print('✅ All dependencies installed successfully!')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════╗"
echo "║        Setup Completed Successfully!               ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Next steps:${NC}"
echo "1. ${YELLOW}Edit bot_settings.json${NC} with your credentials:"
echo "   • Get api_id and api_hash from: https://my.telegram.org"
echo "   • Get bot_token from: @BotFather on Telegram"
echo "   • Set owner_id to your Telegram user ID"
echo ""
echo "2. ${YELLOW}Activate virtual environment:${NC}"
echo "   source venv/bin/activate"
echo ""
echo "3. ${YELLOW}Start the bot:${NC}"
echo "   ./start.sh"
echo ""
echo "4. ${YELLOW}Check logs:${NC}"
echo "   tail -f bot.log"
echo ""
echo "5. ${YELLOW}Stop the bot:${NC}"
echo "   ./stop.sh"
echo ""
echo "6. ${YELLOW}Restart the bot:${NC}"
echo "   ./restart.bsh"
echo ""

read -p "Do you want to start the bot now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[*] Starting bot...${NC}"
    ./start.sh
fi

echo ""
echo -e "${CYAN}Thank you for installing SIKU TAGALL BOT!${NC}"
echo -e "${CYAN}For support, check the documentation.${NC}"
