# 🤖 SIKU TAGALL BOT

A powerful, feature-rich Telegram bot with Siku (Good Morning/Good Night) messages, RAID mass messaging system, and TagAll functionality.

![Version](https://img.shields.io/badge/Version-3.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Telethon](https://img.shields.io/badge/Telethon-1.34.0-red)

## ✨ Features

### 🌟 **SIKU System**
- **Good Morning Messages**: Random GM messages with `/siku gm`
- **Good Night Messages**: Random GN messages with `/siku gn`
- **Custom Messages**: Add your own messages with `/siku add`
- **Message Management**: List, delete, and track your messages
- **Statistics**: Track most popular messages and usage

### ⚡ **RAID System**
- **Mass Messaging**: Send messages to multiple users
- **Custom Templates**: Use variables like `{user}`, `{count}`, `{total}`
- **Session Management**: Start, stop, pause, and resume raids
- **Progress Tracking**: Real-time status and progress monitoring
- **Cooldown System**: Prevent spam with configurable cooldowns

### 🏷️ **TAGALL System**
- **Mention All**: Tag all members in a group
- **Custom Messages**: Add custom text before mentions
- **Smart Mentioning**: Automatically handles large groups
- **Cooldown Protection**: Prevent abuse with cooldowns

### 🛠️ **Administration**
- **User Management**: Add/remove sudo users, authorized users
- **Chat Management**: Control which chats can use the bot
- **Global Bans**: Ban users from using the bot globally
- **Settings**: Configurable bot settings

### 📊 **Statistics**
- **Bot Statistics**: Uptime, messages processed, commands executed
- **SIKU Statistics**: Message counts, usage, top messages
- **RAID Statistics**: Sessions, messages sent, top users
- **TAGALL Statistics**: Usage statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))
- Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

1. **Clone/Download the bot:**
```bash
git clone <repository-url>
cd SIKU_TAGALL_BOT
```

2. **Run the setup script:**
```bash
chmod +x setup.sh
./setup.sh
```

3. **Configure the bot:**
   Edit `bot_settings.json` and add your:
   - `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org)
   - `bot_token` from [@BotFather](https://t.me/BotFather)
   - `owner_id` (your Telegram user ID)

4. **Start the bot:**
```bash
./start.sh
```

## 📁 Project Structure

```
SIKU_TAGALL_BOT/
├── main.py                 # Main bot file
├── bot_settings.json       # Configuration file
├── requirements.txt        # Python dependencies
├── setup.sh               # Installation script
├── start.sh               # Start script
├── stop.sh                # Stop script
├── restart.bsh            # Restart script
├── update.sh              # Update script
├── bot.log                # Log file (auto-generated)
├── README.md              # This file
├── data/                  # Data storage
│   ├── main_data.json     # Main bot data
│   ├── siku_data.json     # Siku messages
│   └── raid_data.json     # RAID sessions
└── venv/                  # Virtual environment
```

## 🎯 Commands Reference

### Basic Commands
- `/start` - Start the bot and show welcome message
- `/help` - Show complete command list
- `/ping` - Check bot latency
- `/id` - Get user and chat ID information
- `/stats` - Show bot statistics

### Siku Commands
- `/siku gm` - Send random good morning message
- `/siku gn` - Send random good night message
- `/siku custom` - Send random custom message
- `/siku addgm <text>` - Add good morning message
- `/siku addgn <text>` - Add good night message
- `/siku add <text>` - Add custom message
- `/siku list` - List your messages
- `/siku delete <id>` - Delete your message
- `/siku stats` - Show Siku statistics
- `/siku top` - Show top messages

### RAID Commands
- `/raid start <name> <message>` - Start a raid session
- `/raid stop <id>` - Stop a raid session
- `/raid pause <id>` - Pause a raid session
- `/raid resume <id>` - Resume a raid session
- `/raid status <id>` - Check raid status
- `/raid list` - List your active raids
- `/raid stats` - Show raid statistics
- `/raid help` - RAID help guide

### TagAll Commands
- `/tagall [message]` - Tag all members with optional message
- `/tagall stats` - Show TagAll statistics
- `/tagall help` - TagAll help guide

### Admin Commands
- `/addsudo <user_id>` - Add sudo user (admin)
- `/delsudo <user_id>` - Remove sudo user
- `/listsudo` - List all sudo users
- `/addchat <chat_id>` - Add allowed chat
- `/removechat <chat_id>` - Remove chat
- `/listchats` - List allowed chats
- `/auth <user_id>` - Authorize user
- `/unauth <user_id>` - Unauthorize user
- `/gban <user_id>` - Global ban user
- `/ungban <user_id>` - Remove global ban

## ⚙️ Configuration

### bot_settings.json
```json
{
  "api_id": 123456,
  "api_hash": "your_api_hash_here",
  "bot_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
  "owner_id": 0,
  
  "siku_cooldown": 10,
  "max_siku_messages": 500,
  
  "raid_max_users": 100,
  "raid_min_delay": 0.3,
  "raid_max_delay": 3.0,
  "raid_max_messages_per_session": 200,
  
  "tagall_cooldown": 120,
  "tagall_max_users": 200,
  
  "default_siku_gm": ["Good morning! ☀️", "Morning! 🌄"],
  "default_siku_gn": ["Good night! 🌙", "Night night! 🌌"]
}
```

### Key Configuration Options
- **`siku_cooldown`**: Seconds between Siku commands (default: 10)
- **`raid_min_delay`**: Minimum delay between RAID messages (default: 0.3)
- **`raid_max_delay`**: Maximum delay between RAID messages (default: 3.0)
- **`tagall_cooldown`**: Seconds between TagAll commands (default: 120)

## 🔧 Management Scripts

### Setup Script (`./setup.sh`)
- Checks Python version
- Creates virtual environment
- Installs dependencies
- Creates configuration files
- Sets up directory structure

### Start Script (`./start.sh`)
- Checks if bot is already running
- Activates virtual environment
- Checks requirements
- Starts the bot
- Handles graceful shutdown

### Stop Script (`./stop.sh`)
- Finds bot processes
- Sends stop signal
- Force kills if necessary
- Verifies bot is stopped

### Restart Script (`./restart.bsh`)
- Stops the bot
- Waits for cleanup
- Starts the bot again

### Update Script (`./update.sh`)
- Creates backup
- Updates from Git (if available)
- Updates dependencies
- Checks configuration

## 📊 Statistics Tracking

The bot tracks:
- **Total messages processed**
- **Total commands executed**
- **SIKU messages sent**
- **RAID messages sent**
- **TAGALL messages sent**
- **User activity**
- **Message popularity**

## 🛡️ Safety Features

1. **Cooldown System**: Prevents spam and abuse
2. **Rate Limiting**: Protects against Telegram API limits
3. **User Authorization**: Controls who can use which features
4. **Chat Restrictions**: Limits bot usage to authorized chats
5. **Error Handling**: Graceful error recovery
6. **Flood Wait Handling**: Automatically handles Telegram flood errors
7. **Session Management**: Proper cleanup of old sessions

## 🚨 Important Notes

### Rate Limits
- Telegram has strict rate limits
- The bot includes flood wait handling
- Use reasonable delays in RAID messages
- Respect group rules and user preferences

### Legal Compliance
- Use the bot responsibly
- Respect Telegram's Terms of Service
- Don't spam or harass users
- Get permission before using in groups

### Best Practices
1. **Test in small groups first**
2. **Use appropriate delays** (≥ 0.5s for RAID)
3. **Monitor bot logs** regularly
4. **Keep backups** of important data
5. **Update regularly** for security fixes

## 🔍 Troubleshooting

### Common Issues

1. **Bot won't start**
   - Check Python version (≥ 3.8 required)
   - Verify API credentials in `bot_settings.json`
   - Check `bot.log` for error messages
   - Ensure internet connection

2. **Can't connect to Telegram**
   - Check API credentials
   - Verify internet connection
   - Check if Telegram is blocked in your region
   - Try increasing `connection_retries`

3. **Commands not working**
   - Check if you're authorized to use the bot
   - Verify you're in an allowed chat
   - Check cooldown status
   - Look for errors in `bot.log`

4. **High memory usage**
   - The bot automatically cleans old sessions
   - Check for memory leaks in logs
   - Consider reducing `max_siku_messages`

### Logs
- Logs are saved to `bot.log`
- Use `tail -f bot.log` to monitor in real-time
- Log level can be adjusted in `main.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup
```bash
# Clone the repository
git clone <repository-url>

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black flake8 pytest
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings to functions
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This bot is for educational and legitimate purposes only. The developers are not responsible for any misuse of this software. Users are responsible for complying with Telegram's Terms of Service and all applicable laws.

## 🙏 Acknowledgments

- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram client library
- All contributors and testers
- The Telegram community

## 📞 Support

For support, feature requests, or bug reports:
1. Check the `bot.log` for errors
2. Review this README for troubleshooting
3. Open an issue on GitHub
4. Contact the maintainers

---

**Made with ❤️ for the Telegram community**

> **Note**: Always respect users' privacy and follow Telegram's guidelines when using this bot.
