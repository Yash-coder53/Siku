#!/usr/bin/env python3
"""
SIKU TAGALL BOT - Advanced Telegram Bot with Siku & RAID Features
Author: Auto Generated
Version: 3.0.0
Bot Name: SIKU TAGALL BOT
"""

import os
import sys
import json
import logging
import asyncio
import signal
import time
import random
import string
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import (
    ConnectionError as TelethonConnectionError,
    FloodWaitError,
    AuthKeyError,
    SessionPasswordNeededError,
    ChatAdminRequiredError,
    UserNotParticipantError,
    ChannelPrivateError
)
from telethon.tl.types import (
    Message,
    User,
    Chat,
    Channel,
    PeerUser,
    PeerChat,
    PeerChannel,
    InputPeerUser,
    InputPeerChat,
    InputPeerChannel
)
from telethon.tl.functions.channels import (
    GetParticipantsRequest,
    GetFullChannelRequest
)
from telethon.tl.types import (
    ChannelParticipantsRecent,
    ChannelParticipantsSearch
)
from telethon.tl.functions.messages import GetFullChatRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG_DIR = Path("data")
CONFIG_DIR.mkdir(exist_ok=True)

class RaidStatus(Enum):
    """RAID Session Status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

@dataclass
class RaidSession:
    """RAID Session data class"""
    id: str
    name: str
    creator_id: int
    creator_name: str
    chat_id: int
    chat_title: str
    target_users: List[int]
    message_template: str
    delay_between_messages: float
    total_messages: int
    messages_sent: int = 0
    status: str = RaidStatus.ACTIVE.value
    created_at: str = ""
    last_action: str = ""
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class SikuMessage:
    """Siku message data class"""
    id: str
    text: str
    type: str  # 'gm', 'gn', or 'custom'
    author_id: int
    author_name: str
    created_at: str
    uses: int = 0
    last_used: Optional[str] = None
    likes: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

@dataclass
class BotConfig:
    """Bot configuration data class"""
    api_id: int = 0
    api_hash: str = ""
    bot_token: str = ""
    owner_id: int = 0
    session_name: str = "siku_tagall_bot.session"
    connection_retries: int = 10
    retry_delay: int = 3
    max_message_length: int = 4096
    auto_save_interval: int = 60  # seconds
    
    # Siku commands settings
    siku_cooldown: int = 10  # seconds between siku commands
    max_siku_messages: int = 500  # maximum stored siku messages
    siku_max_length: int = 1000  # maximum siku message length
    
    # RAID settings
    raid_max_users: int = 100  # maximum users per raid
    raid_min_delay: float = 0.3  # minimum delay between messages
    raid_max_delay: float = 3.0  # maximum delay between messages
    raid_max_sessions_per_user: int = 5  # maximum concurrent raid sessions per user
    raid_max_messages_per_session: int = 200  # maximum messages per raid session
    raid_cooldown: int = 60  # seconds between raid commands
    raid_default_count: int = 20  # default number of raid messages
    
    # TagAll settings
    tagall_cooldown: int = 120  # seconds between tagall commands
    tagall_max_users: int = 200  # maximum users to tag
    tagall_message_templates: List[str] = field(default_factory=lambda: [
        "🚨 Attention everyone!",
        "📢 Announcement for all members!",
        "👋 Hey everyone, listen up!",
        "🎯 Important message for all!",
        "🔔 Notification for all members!"
    ])
    
    # Default messages
    default_siku_gm: List[str] = field(default_factory=lambda: [
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
    ])
    
    default_siku_gn: List[str] = field(default_factory=lambda: [
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
    ])
    
    @classmethod
    def from_file(cls, filename: str = "bot_settings.json") -> 'BotConfig':
        """Load configuration from file"""
        try:
            if Path(filename).exists():
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return cls(**data)
        except Exception as e:
            logger.error(f"Error loading config from {filename}: {e}")
        return cls()

@dataclass
class BotData:
    """Bot data storage"""
    allowed_chats: List[int] = field(default_factory=list)
    sudo_users: List[int] = field(default_factory=list)
    gban_users: List[int] = field(default_factory=list)
    authorized_users: Dict[int, List[int]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    
    # Siku messages storage
    siku_gm_messages: Dict[str, SikuMessage] = field(default_factory=dict)
    siku_gn_messages: Dict[str, SikuMessage] = field(default_factory=dict)
    siku_custom_messages: Dict[str, SikuMessage] = field(default_factory=dict)
    
    # Cooldown tracking
    siku_cooldowns: Dict[int, float] = field(default_factory=dict)
    tagall_cooldowns: Dict[int, float] = field(default_factory=dict)
    
    # RAID sessions storage
    raid_sessions: Dict[str, RaidSession] = field(default_factory=dict)
    raid_cooldowns: Dict[int, float] = field(default_factory=dict)
    
    # Statistics
    total_messages_processed: int = 0
    total_commands_executed: int = 0
    siku_messages_sent: int = 0
    raid_messages_sent: int = 0
    tagall_messages_sent: int = 0
    
    def save_to_file(self, filename: str):
        """Save data to file"""
        try:
            data_dict = {
                'allowed_chats': self.allowed_chats,
                'sudo_users': self.sudo_users,
                'gban_users': self.gban_users,
                'authorized_users': self.authorized_users,
                'settings': self.settings,
                'siku_gm_messages': {k: v.to_dict() for k, v in self.siku_gm_messages.items()},
                'siku_gn_messages': {k: v.to_dict() for k, v in self.siku_gn_messages.items()},
                'siku_custom_messages': {k: v.to_dict() for k, v in self.siku_custom_messages.items()},
                'siku_cooldowns': self.siku_cooldowns,
                'tagall_cooldowns': self.tagall_cooldowns,
                'raid_sessions': {k: v.to_dict() for k, v in self.raid_sessions.items()},
                'raid_cooldowns': self.raid_cooldowns,
                'total_messages_processed': self.total_messages_processed,
                'total_commands_executed': self.total_commands_executed,
                'siku_messages_sent': self.siku_messages_sent,
                'raid_messages_sent': self.raid_messages_sent,
                'tagall_messages_sent': self.tagall_messages_sent
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'BotData':
        """Load data from file"""
        try:
            if Path(filename).exists():
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                bot_data = cls()
                
                # Load basic lists/dicts
                for key in ['allowed_chats', 'sudo_users', 'gban_users', 'authorized_users', 
                          'settings', 'siku_cooldowns', 'tagall_cooldowns', 'raid_cooldowns']:
                    if key in data:
                        setattr(bot_data, key, data[key])
                
                # Load Siku messages
                for msg_type in ['siku_gm_messages', 'siku_gn_messages', 'siku_custom_messages']:
                    if msg_type in data:
                        msg_dict = {}
                        for msg_id, msg_data in data[msg_type].items():
                            msg_dict[msg_id] = SikuMessage(**msg_data)
                        setattr(bot_data, msg_type, msg_dict)
                
                # Load RAID sessions
                if 'raid_sessions' in data:
                    raid_dict = {}
                    for session_id, session_data in data['raid_sessions'].items():
                        raid_dict[session_id] = RaidSession(**session_data)
                    bot_data.raid_sessions = raid_dict
                
                # Load statistics
                for stat in ['total_messages_processed', 'total_commands_executed', 
                           'siku_messages_sent', 'raid_messages_sent', 'tagall_messages_sent']:
                    if stat in data:
                        setattr(bot_data, stat, data[stat])
                
                return bot_data
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
        return cls()

class SikuTagAllBot:
    """Main bot class for SIKU TAGALL BOT"""
    
    def __init__(self):
        self.config = BotConfig()
        self.data = BotData()
        self.client: Optional[TelegramClient] = None
        self.is_running = False
        self.start_time = datetime.now()
        self.bot_info: Optional[User] = None
        self.connected = False
        
        # Active tasks
        self.active_raid_tasks: Dict[str, asyncio.Task] = {}
        
        # Load configuration
        self.load_configuration()
        
        # Initialize default messages
        self.initialize_default_messages()
    
    def initialize_default_messages(self):
        """Initialize default siku messages if empty"""
        # Check and add default GM messages
        if not self.data.siku_gm_messages:
            for i, text in enumerate(self.config.default_siku_gm):
                msg_id = f"default_gm_{i}"
                self.data.siku_gm_messages[msg_id] = SikuMessage(
                    id=msg_id,
                    text=text,
                    type="gm",
                    author_id=0,
                    author_name="System",
                    created_at=datetime.now().isoformat(),
                    uses=0,
                    likes=0
                )
        
        # Check and add default GN messages
        if not self.data.siku_gn_messages:
            for i, text in enumerate(self.config.default_siku_gn):
                msg_id = f"default_gn_{i}"
                self.data.siku_gn_messages[msg_id] = SikuMessage(
                    id=msg_id,
                    text=text,
                    type="gn",
                    author_id=0,
                    author_name="System",
                    created_at=datetime.now().isoformat(),
                    uses=0,
                    likes=0
                )
    
    def load_configuration(self):
        """Load all configuration files"""
        logger.info("=" * 70)
        logger.info("SIKU TAGALL BOT - Loading Configuration...")
        logger.info("=" * 70)
        
        # Load main config
        self.config = BotConfig.from_file("bot_settings.json")
        
        # Check for required configuration
        if not self.config.api_id or not self.config.api_hash or not self.config.bot_token:
            logger.error("❌ Missing API credentials in bot_settings.json!")
            logger.info("Please edit bot_settings.json with your credentials:")
            logger.info("1. Get api_id and api_hash from: https://my.telegram.org")
            logger.info("2. Get bot_token from: @BotFather on Telegram")
            logger.info("3. Set owner_id to your Telegram user ID")
        
        # Load data files
        data_files = {
            'main_data': 'data/main_data.json',
            'siku_data': 'data/siku_data.json',
            'raid_data': 'data/raid_data.json'
        }
        
        for name, filepath in data_files.items():
            if Path(filepath).exists():
                data = BotData.load_from_file(filepath)
                
                if name == 'main_data':
                    # Merge main data
                    for attr in ['allowed_chats', 'sudo_users', 'gban_users', 
                               'authorized_users', 'settings', 'siku_cooldowns',
                               'tagall_cooldowns', 'raid_cooldowns']:
                        if hasattr(data, attr):
                            setattr(self.data, attr, getattr(data, attr))
                    
                    # Load statistics
                    for stat in ['total_messages_processed', 'total_commands_executed',
                               'siku_messages_sent', 'raid_messages_sent', 'tagall_messages_sent']:
                        if hasattr(data, stat):
                            setattr(self.data, stat, getattr(data, stat))
                
                elif name == 'siku_data':
                    # Merge Siku data
                    for msg_type in ['siku_gm_messages', 'siku_gn_messages', 'siku_custom_messages']:
                        if hasattr(data, msg_type):
                            # Preserve existing messages, add new ones
                            existing = getattr(self.data, msg_type)
                            new_messages = getattr(data, msg_type)
                            existing.update(new_messages)
                
                elif name == 'raid_data':
                    # Merge RAID data
                    if hasattr(data, 'raid_sessions'):
                        self.data.raid_sessions.update(data.raid_sessions)
        
        # Log loaded data
        logger.info(f"✅ Loaded {len(self.data.allowed_chats)} allowed chats")
        logger.info(f"✅ Loaded {len(self.data.sudo_users)} sudo users")
        logger.info(f"✅ Loaded {len(self.data.gban_users)} GBAN users")
        logger.info(f"✅ Loaded {len(self.data.authorized_users)} authorized chats")
        
        siku_gm = len(self.data.siku_gm_messages)
        siku_gn = len(self.data.siku_gn_messages)
        siku_custom = len(self.data.siku_custom_messages)
        logger.info(f"✅ Loaded {siku_gm} GM, {siku_gn} GN, {siku_custom} custom Siku messages")
        
        active_raids = len([s for s in self.data.raid_sessions.values() if s.status == RaidStatus.ACTIVE.value])
        total_raids = len(self.data.raid_sessions)
        logger.info(f"✅ Loaded {total_raids} RAID sessions ({active_raids} active)")
        
        logger.info("=" * 70)
        logger.info("Configuration loaded successfully!")
        logger.info("=" * 70)
    
    def save_configuration(self):
        """Save all configuration files"""
        try:
            logger.info("💾 Saving configuration...")
            
            # Save main data
            main_data = BotData()
            for attr in ['allowed_chats', 'sudo_users', 'gban_users', 'authorized_users', 
                        'settings', 'siku_cooldowns', 'tagall_cooldowns', 'raid_cooldowns',
                        'total_messages_processed', 'total_commands_executed',
                        'siku_messages_sent', 'raid_messages_sent', 'tagall_messages_sent']:
                setattr(main_data, attr, getattr(self.data, attr))
            
            if main_data.save_to_file("data/main_data.json"):
                logger.info("✅ Saved main data")
            
            # Save Siku data
            siku_data = BotData()
            siku_data.siku_gm_messages = self.data.siku_gm_messages
            siku_data.siku_gn_messages = self.data.siku_gn_messages
            siku_data.siku_custom_messages = self.data.siku_custom_messages
            
            if siku_data.save_to_file("data/siku_data.json"):
                total_siku = (len(self.data.siku_gm_messages) + 
                            len(self.data.siku_gn_messages) + 
                            len(self.data.siku_custom_messages))
                logger.info(f"✅ Saved {total_siku} Siku messages")
            
            # Save RAID data
            raid_data = BotData()
            raid_data.raid_sessions = self.data.raid_sessions
            
            if raid_data.save_to_file("data/raid_data.json"):
                active_raids = len([s for s in self.data.raid_sessions.values() if s.status == RaidStatus.ACTIVE.value])
                logger.info(f"✅ Saved {len(self.data.raid_sessions)} RAID sessions ({active_raids} active)")
            
            logger.info("💾 All configuration saved successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving configuration: {e}")
            return False
    
    def generate_id(self, length: int = 10) -> str:
        """Generate a unique ID"""
        chars = string.ascii_lowercase + string.digits
        while True:
            new_id = ''.join(random.choices(chars, k=length))
            # Check if ID doesn't exist in any storage
            if (new_id not in self.data.siku_gm_messages and
                new_id not in self.data.siku_gn_messages and
                new_id not in self.data.siku_custom_messages and
                new_id not in self.data.raid_sessions):
                return new_id
    
    # ========== SIKU METHODS ==========
    
    def check_siku_cooldown(self, user_id: int) -> Tuple[bool, float]:
        """Check if user is on cooldown for siku commands"""
        if user_id in self.data.siku_cooldowns:
            last_used = self.data.siku_cooldowns[user_id]
            elapsed = time.time() - last_used
            if elapsed < self.config.siku_cooldown:
                return False, self.config.siku_cooldown - elapsed
        return True, 0
    
    def set_siku_cooldown(self, user_id: int):
        """Set cooldown for user's siku commands"""
        self.data.siku_cooldowns[user_id] = time.time()
    
    def get_random_siku_message(self, msg_type: str) -> Optional[SikuMessage]:
        """Get a random siku message of specified type"""
        if msg_type == 'gm':
            messages = list(self.data.siku_gm_messages.values())
        elif msg_type == 'gn':
            messages = list(self.data.siku_gn_messages.values())
        elif msg_type == 'custom':
            messages = list(self.data.siku_custom_messages.values())
        else:
            return None
        
        if not messages:
            return None
        
        # Weighted random selection (less used messages have higher chance)
        weights = [1 / (msg.uses + 1) for msg in messages]
        selected = random.choices(messages, weights=weights, k=1)[0]
        
        # Update usage stats
        selected.uses += 1
        selected.last_used = datetime.now().isoformat()
        
        return selected
    
    def add_siku_message(self, text: str, msg_type: str, user_id: int, user_name: str) -> Optional[SikuMessage]:
        """Add a new siku message"""
        if len(text) > self.config.siku_max_length:
            return None
        
        # Generate unique ID
        msg_id = self.generate_id(8)
        
        # Create message
        siku_msg = SikuMessage(
            id=msg_id,
            text=text,
            type=msg_type,
            author_id=user_id,
            author_name=user_name,
            created_at=datetime.now().isoformat(),
            uses=0,
            likes=0
        )
        
        # Store based on type
        if msg_type == 'gm':
            self.data.siku_gm_messages[msg_id] = siku_msg
        elif msg_type == 'gn':
            self.data.siku_gn_messages[msg_id] = siku_msg
        elif msg_type == 'custom':
            self.data.siku_custom_messages[msg_id] = siku_msg
        else:
            return None
        
        return siku_msg
    
    # ========== RAID METHODS ==========
    
    def check_raid_cooldown(self, user_id: int) -> Tuple[bool, float]:
        """Check if user is on cooldown for raid commands"""
        if user_id in self.data.raid_cooldowns:
            last_used = self.data.raid_cooldowns[user_id]
            elapsed = time.time() - last_used
            if elapsed < self.config.raid_cooldown:
                return False, self.config.raid_cooldown - elapsed
        return True, 0
    
    def set_raid_cooldown(self, user_id: int):
        """Set cooldown for user's raid commands"""
        self.data.raid_cooldowns[user_id] = time.time()
    
    def get_user_active_raid_sessions(self, user_id: int) -> List[RaidSession]:
        """Get active raid sessions for a user"""
        return [session for session in self.data.raid_sessions.values()
                if session.creator_id == user_id and session.status == RaidStatus.ACTIVE.value]
    
    def create_raid_session(self, user_id: int, user_name: str, chat_id: int,
                           chat_title: str, name: str, target_users: List[int],
                           message_template: str, delay: float = 1.0,
                           total_messages: int = None) -> Optional[RaidSession]:
        """Create a new raid session"""
        # Check cooldown
        can_raid, wait_time = self.check_raid_cooldown(user_id)
        if not can_raid:
            return None
        
        # Check maximum concurrent sessions
        active_sessions = self.get_user_active_raid_sessions(user_id)
        if len(active_sessions) >= self.config.raid_max_sessions_per_user:
            return None
        
        # Set defaults
        if total_messages is None:
            total_messages = self.config.raid_default_count
        
        # Validate parameters
        if len(target_users) > self.config.raid_max_users:
            target_users = target_users[:self.config.raid_max_users]
        
        if delay < self.config.raid_min_delay:
            delay = self.config.raid_min_delay
        elif delay > self.config.raid_max_delay:
            delay = self.config.raid_max_delay
        
        if total_messages > self.config.raid_max_messages_per_session:
            total_messages = self.config.raid_max_messages_per_session
        
        # Generate session ID
        session_id = self.generate_id(12)
        
        # Create session
        session = RaidSession(
            id=session_id,
            name=name,
            creator_id=user_id,
            creator_name=user_name,
            chat_id=chat_id,
            chat_title=chat_title,
            target_users=target_users,
            message_template=message_template,
            delay_between_messages=delay,
            total_messages=total_messages,
            status=RaidStatus.ACTIVE.value,
            created_at=datetime.now().isoformat(),
            last_action=datetime.now().isoformat(),
            started_at=datetime.now().isoformat()
        )
        
        # Store session
        self.data.raid_sessions[session_id] = session
        
        # Set cooldown
        self.set_raid_cooldown(user_id)
        
        return session
    
    async def execute_raid(self, session_id: str):
        """Execute a raid session"""
        if session_id not in self.data.raid_sessions:
            return
        
        session = self.data.raid_sessions[session_id]
        
        try:
            logger.info(f"⚡ Starting RAID session: {session_id}")
            
            for i in range(session.total_messages):
                # Check if session is still active
                if (session_id not in self.data.raid_sessions or 
                    session.status != RaidStatus.ACTIVE.value):
                    break
                
                # Select random user
                if session.target_users:
                    target_id = random.choice(session.target_users)
                    
                    # Format message
                    message = session.message_template
                    message = message.replace("{user}", f"👤 User {target_id}")
                    message = message.replace("{count}", str(i + 1))
                    message = message.replace("{total}", str(session.total_messages))
                    message = message.replace("{session}", session.name)
                    
                    # Send message
                    try:
                        await self.client.send_message(
                            entity=session.chat_id,
                            message=message,
                            parse_mode='html',
                            silent=True
                        )
                        session.messages_sent += 1
                        session.last_action = datetime.now().isoformat()
                        
                        # Update statistics
                        self.data.raid_messages_sent += 1
                        self.data.total_messages_processed += 1
                        
                        # Log every 10 messages
                        if (i + 1) % 10 == 0:
                            logger.info(f"⚡ RAID {session_id}: Sent {i+1}/{session.total_messages} messages")
                    
                    except FloodWaitError as e:
                        logger.warning(f"⚡ RAID {session_id}: Flood wait for {e.seconds} seconds")
                        await asyncio.sleep(e.seconds)
                        continue
                    except Exception as e:
                        logger.error(f"⚡ RAID {session_id}: Error sending message: {e}")
                        continue
                
                # Delay between messages
                await asyncio.sleep(session.delay_between_messages)
            
            # Mark as completed
            if session_id in self.data.raid_sessions and session.status == RaidStatus.ACTIVE.value:
                session.status = RaidStatus.COMPLETED.value
                session.ended_at = datetime.now().isoformat()
                logger.info(f"✅ RAID session completed: {session_id}")
        
        except asyncio.CancelledError:
            logger.info(f"🛑 RAID session cancelled: {session_id}")
            if session_id in self.data.raid_sessions:
                session.status = RaidStatus.CANCELLED.value
                session.ended_at = datetime.now().isoformat()
        
        except Exception as e:
            logger.error(f"❌ RAID session error {session_id}: {e}")
            if session_id in self.data.raid_sessions:
                session.status = RaidStatus.ERROR.value
                session.ended_at = datetime.now().isoformat()
        
        finally:
            # Clean up task
            if session_id in self.active_raid_tasks:
                del self.active_raid_tasks[session_id]
            
            # Save configuration
            self.save_configuration()
    
    def stop_raid_session(self, session_id: str, user_id: int) -> bool:
        """Stop a raid session"""
        if session_id not in self.data.raid_sessions:
            return False
        
        session = self.data.raid_sessions[session_id]
        
        # Check permissions
        if (session.creator_id != user_id and 
            user_id not in self.data.sudo_users and 
            user_id != self.config.owner_id):
            return False
        
        # Update session
        session.status = RaidStatus.CANCELLED.value
        session.ended_at = datetime.now().isoformat()
        session.last_action = datetime.now().isoformat()
        
        # Cancel task if running
        if session_id in self.active_raid_tasks:
            self.active_raid_tasks[session_id].cancel()
        
        return True
    
    # ========== TAGALL METHODS ==========
    
    def check_tagall_cooldown(self, user_id: int) -> Tuple[bool, float]:
        """Check if user is on cooldown for tagall commands"""
        if user_id in self.data.tagall_cooldowns:
            last_used = self.data.tagall_cooldowns[user_id]
            elapsed = time.time() - last_used
            if elapsed < self.config.tagall_cooldown:
                return False, self.config.tagall_cooldown - elapsed
        return True, 0
    
    def set_tagall_cooldown(self, user_id: int):
        """Set cooldown for user's tagall commands"""
        self.data.tagall_cooldowns[user_id] = time.time()
    
    async def get_chat_members(self, chat_id: int, limit: int = None) -> List[User]:
        """Get chat members"""
        try:
            if limit is None:
                limit = self.config.tagall_max_users
            
            participants = []
            async for user in self.client.iter_participants(chat_id, limit=limit):
                if not user.bot and not user.deleted:
                    participants.append(user)
            
            return participants
        
        except (ChatAdminRequiredError, ChannelPrivateError, UserNotParticipantError) as e:
            logger.error(f"❌ Cannot get chat members: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error getting chat members: {e}")
            return []
    
    async def send_tagall(self, chat_id: int, message: str = None, 
                         user_id: int = None, user_name: str = None) -> Tuple[bool, str]:
        """Send tagall message to all chat members"""
        try:
            # Get chat members
            members = await self.get_chat_members(chat_id, self.config.tagall_max_users)
            
            if not members:
                return False, "No members found in this chat"
            
            if len(members) > self.config.tagall_max_users:
                members = members[:self.config.tagall_max_users]
            
            # Prepare message
            if message is None:
                message = random.choice(self.config.tagall_message_templates)
            
            # Create mentions
            mentions = []
            for member in members:
                if member.username:
                    mentions.append(f"@{member.username}")
                else:
                    mentions.append(f"[{member.first_name or ''}](tg://user?id={member.id})")
            
            # Split mentions if too many
            max_mentions_per_message = 20
            if len(mentions) > max_mentions_per_message:
                mention_chunks = [mentions[i:i + max_mentions_per_message] 
                                for i in range(0, len(mentions), max_mentions_per_message)]
                
                for i, chunk in enumerate(mention_chunks):
                    chunk_message = f"{message}\n\n" + " ".join(chunk)
                    await self.client.send_message(
                        chat_id,
                        chunk_message,
                        parse_mode='markdown'
                    )
                    await asyncio.sleep(1)  # Delay between chunks
            else:
                full_message = f"{message}\n\n" + " ".join(mentions)
                await self.client.send_message(
                    chat_id,
                    full_message,
                    parse_mode='markdown'
                )
            
            # Update statistics
            self.data.tagall_messages_sent += 1
            self.data.total_messages_processed += 1
            
            # Set cooldown
            if user_id:
                self.set_tagall_cooldown(user_id)
            
            return True, f"Tagged {len(members)} members successfully!"
        
        except FloodWaitError as e:
            logger.warning(f"⏳ TagAll flood wait: {e.seconds} seconds")
            return False, f"Flood wait: Please try again in {e.seconds} seconds"
        except Exception as e:
            logger.error(f"❌ TagAll error: {e}")
            return False, f"Error: {str(e)}"
    
    # ========== BOT CORE METHODS ==========
    
    async def initialize_client(self):
        """Initialize Telegram client"""
        try:
            if not self.config.api_id or not self.config.api_hash:
                logger.error("❌ Missing API credentials!")
                return False
            
            self.client = TelegramClient(
                session=self.config.session_name,
                api_id=self.config.api_id,
                api_hash=self.config.api_hash,
                device_model="SIKU TAGALL BOT",
                system_version="Python 3.10",
                app_version="3.0.0",
                lang_code="en",
                system_lang_code="en",
                connection_retries=self.config.connection_retries,
                retry_delay=self.config.retry_delay
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing client: {e}")
            return False
    
    async def connect_to_telegram(self):
        """Connect to Telegram with retry logic"""
        if not self.client:
            logger.error("❌ Client not initialized!")
            return False
        
        max_attempts = self.config.connection_retries
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"🔗 Connection attempt {attempt}/{max_attempts}...")
                
                await self.client.connect()
                
                # Test connection
                if not await self.client.is_user_authorized():
                    logger.info("🔐 Bot not authorized, signing in...")
                    if self.config.bot_token:
                        await self.client.start(bot_token=self.config.bot_token)
                    else:
                        logger.error("❌ No bot token provided!")
                        return False
                
                # Get bot info
                self.bot_info = await self.client.get_me()
                logger.info(f"✅ Connected as @{self.bot_info.username} (ID: {self.bot_info.id})")
                
                self.connected = True
                return True
                
            except AuthKeyError:
                logger.error("🔑 Auth key error. Removing session file...")
                if os.path.exists(self.config.session_name):
                    os.remove(self.config.session_name)
                logger.info("🔄 Please restart the bot")
                return False
                
            except SessionPasswordNeededError:
                logger.error("🔐 Two-factor authentication required!")
                return False
                
            except (TelethonConnectionError, OSError, ConnectionError) as e:
                logger.warning(f"❌ Connection attempt {attempt} failed: {e}")
                
                if attempt < max_attempts:
                    wait_time = min(self.config.retry_delay ** attempt, 30)
                    logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to connect after {max_attempts} attempts")
                    return False
        
        return False
    
    def setup_event_handlers(self):
        """Set up all event handlers"""
        
        # ========== START COMMAND ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/start$'))
        async def start_handler(event):
            """Handle /start command"""
            self.data.total_messages_processed += 1
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                chat = await event.get_chat()
                
                welcome_message = f"""
🤖 **SIKU TAGALL BOT v3.0.0**

👤 **Your Info:**
• Name: {sender.first_name or ''} {sender.last_name or ''}
• ID: `{sender.id}`
• Username: @{sender.username or 'N/A'}

💬 **Chat Info:**
• Type: {'Private' if event.is_private else 'Group'}
• ID: `{event.chat_id}`
• Title: {getattr(chat, 'title', 'Private Chat')}

🌟 **SIKU Commands:**
/siku gm - Send random good morning
/siku gn - Send random good night
/siku addgm <text> - Add GM message
/siku addgn <text> - Add GN message
/siku add <text> - Add custom message
/siku list - List your messages
/siku delete <id> - Delete message
/siku stats - Siku statistics

⚡ **RAID Commands:**
/raid start <name> <message> - Start raid
/raid stop <id> - Stop raid
/raid status <id> - Check status
/raid list - Your raids
/raid stats - Raid statistics

🏷️ **TAGALL Commands:**
/tagall [message] - Tag all members
/tagall stats - TagAll statistics

🛠️ **Admin Commands:**
/addsudo <id> - Add admin
/addchat <id> - Add allowed chat
/auth <id> - Authorize user

📊 **Stats:**
/stats - Bot statistics
/ping - Check latency
/id - Get detailed ID
/help - Full command list

⚙️ **Uptime:** {str(datetime.now() - self.start_time).split('.')[0]}
"""
                
                buttons = [
                    [Button.inline("🌅 Siku GM", b"siku_gm"),
                     Button.inline("🌃 Siku GN", b"siku_gn")],
                    [Button.inline("⚡ Start RAID", b"raid_start"),
                     Button.inline("🏷️ TagAll", b"tagall_now")],
                    [Button.inline("📊 Stats", b"show_stats"),
                     Button.inline("🆔 Get ID", b"get_id")]
                ]
                
                await event.respond(welcome_message, buttons=buttons)
                logger.info(f"👋 Sent welcome to {sender.id} in chat {event.chat_id}")
                
            except Exception as e:
                logger.error(f"❌ Error in start handler: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        # ========== HELP COMMAND ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/help$'))
        async def help_handler(event):
            """Handle /help command"""
            self.data.total_commands_executed += 1
            
            help_text = f"""
📚 **SIKU TAGALL BOT - Complete Command List**

🤖 **Basic Commands:**
/start - Start the bot
/help - Show this help
/ping - Check bot latency
/id - Get user & chat ID
/stats - Bot statistics

🌟 **SIKU System (Good Morning/Night):**
/siku gm - Random good morning message
/siku gn - Random good night message
/siku custom - Random custom message
/siku addgm <text> - Add GM message
/siku addgn <text> - Add GN message
/siku add <text> - Add custom message
/siku list - List your messages
/siku delete <id> - Delete message
/siku stats - Siku statistics
/siku top - Top messages

⚡ **RAID System (Mass Messaging):**
/raid start <name> <message> - Start raid
/raid stop <id> - Stop raid
/raid pause <id> - Pause raid
/raid resume <id> - Resume raid
/raid status <id> - Check status
/raid list - Your active raids
/raid stats - Raid statistics
/raid help - Detailed RAID help

🏷️ **TAGALL System (Mention All):**
/tagall [message] - Tag all members
/tagall stats - TagAll statistics
/tagall help - TagAll help

🛠️ **Administration:**
/addsudo <user_id> - Add sudo user
/delsudo <user_id> - Remove sudo user
/listsudo - List sudo users
/addchat <chat_id> - Add allowed chat
/removechat <chat_id> - Remove chat
/listchats - List allowed chats
/auth <user_id> - Authorize user
/unauth <user_id> - Unauthorize user
/gban <user_id> - Global ban
/ungban <user_id> - Remove ban

⚙️ **Settings:**
/settings - Bot settings
/setwelcome <text> - Set welcome
/setrules <text> - Set rules

📊 **Statistics:**
/stats - Full statistics
/siku stats - Siku statistics
/raid stats - Raid statistics
/tagall stats - TagAll statistics

🔧 **Maintenance:**
/backup - Backup data
/restart - Restart bot
/update - Update bot

📝 **Note:** Use /help <command> for specific help.
Example: /help siku
"""
            
            await event.respond(help_text)
        
        # ========== SIKU COMMANDS ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/siku gm$'))
        async def siku_gm_handler(event):
            """Handle /siku gm command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                
                # Check cooldown
                can_send, wait_time = self.check_siku_cooldown(sender.id)
                if not can_send:
                    await event.respond(f"⏳ Please wait {wait_time:.1f}s before next Siku command!")
                    return
                
                # Get random message
                siku_msg = self.get_random_siku_message('gm')
                
                if not siku_msg:
                    await event.respond("❌ No GM messages available!")
                    return
                
                # Send message
                response = f"🌅 **{siku_msg.text}**\n\n"
                response += f"📊 Used {siku_msg.uses} times"
                if siku_msg.author_id != 0:
                    response += f"\n👤 By {siku_msg.author_name}"
                response += f"\n❤️ {siku_msg.likes} likes"
                
                await event.respond(response)
                
                # Update stats and cooldown
                self.data.siku_messages_sent += 1
                self.set_siku_cooldown(sender.id)
                
                logger.info(f"🌅 Sent Siku GM to {sender.id}")
                
            except Exception as e:
                logger.error(f"❌ Siku GM error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/siku gn$'))
        async def siku_gn_handler(event):
            """Handle /siku gn command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                
                # Check cooldown
                can_send, wait_time = self.check_siku_cooldown(sender.id)
                if not can_send:
                    await event.respond(f"⏳ Please wait {wait_time:.1f}s before next Siku command!")
                    return
                
                # Get random message
                siku_msg = self.get_random_siku_message('gn')
                
                if not siku_msg:
                    await event.respond("❌ No GN messages available!")
                    return
                
                # Send message
                response = f"🌃 **{siku_msg.text}**\n\n"
                response += f"📊 Used {siku_msg.uses} times"
                if siku_msg.author_id != 0:
                    response += f"\n👤 By {siku_msg.author_name}"
                response += f"\n❤️ {siku_msg.likes} likes"
                
                await event.respond(response)
                
                # Update stats and cooldown
                self.data.siku_messages_sent += 1
                self.set_siku_cooldown(sender.id)
                
                logger.info(f"🌃 Sent Siku GN to {sender.id}")
                
            except Exception as e:
                logger.error(f"❌ Siku GN error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/siku addgm (.+)$'))
        async def siku_addgm_handler(event):
            """Handle /siku addgm command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                text = event.pattern_match.group(1).strip()
                
                if len(text) > self.config.siku_max_length:
                    await event.respond(f"❌ Message too long! Max {self.config.siku_max_length} chars")
                    return
                
                # Add message
                siku_msg = self.add_siku_message(
                    text=text,
                    msg_type='gm',
                    user_id=sender.id,
                    user_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip() or f"User{sender.id}"
                )
                
                if not siku_msg:
                    await event.respond("❌ Failed to add message!")
                    return
                
                await event.respond(
                    f"✅ **GM Message Added!**\n\n"
                    f"📝 {text}\n"
                    f"🆔 ID: `{siku_msg.id}`\n"
                    f"👤 By: {siku_msg.author_name}\n"
                    f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"Use `/siku gm` to send random GM messages!"
                )
                
                logger.info(f"➕ Added GM message by {sender.id}")
                
            except Exception as e:
                logger.error(f"❌ Siku addgm error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/siku addgn (.+)$'))
        async def siku_addgn_handler(event):
            """Handle /siku addgn command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                text = event.pattern_match.group(1).strip()
                
                if len(text) > self.config.siku_max_length:
                    await event.respond(f"❌ Message too long! Max {self.config.siku_max_length} chars")
                    return
                
                # Add message
                siku_msg = self.add_siku_message(
                    text=text,
                    msg_type='gn',
                    user_id=sender.id,
                    user_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip() or f"User{sender.id}"
                )
                
                if not siku_msg:
                    await event.respond("❌ Failed to add message!")
                    return
                
                await event.respond(
                    f"✅ **GN Message Added!**\n\n"
                    f"📝 {text}\n"
                    f"🆔 ID: `{siku_msg.id}`\n"
                    f"👤 By: {siku_msg.author_name}\n"
                    f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"Use `/siku gn` to send random GN messages!"
                )
                
                logger.info(f"➕ Added GN message by {sender.id}")
                
            except Exception as e:
                logger.error(f"❌ Siku addgn error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/siku add (.+)$'))
        async def siku_add_handler(event):
            """Handle /siku add command (custom)"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                text = event.pattern_match.group(1).strip()
                
                if len(text) > self.config.siku_max_length:
                    await event.respond(f"❌ Message too long! Max {self.config.siku_max_length} chars")
                    return
                
                # Add message
                siku_msg = self.add_siku_message(
                    text=text,
                    msg_type='custom',
                    user_id=sender.id,
                    user_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip() or f"User{sender.id}"
                )
                
                if not siku_msg:
                    await event.respond("❌ Failed to add message!")
                    return
                
                await event.respond(
                    f"✅ **Custom Message Added!**\n\n"
                    f"📝 {text}\n"
                    f"🆔 ID: `{siku_msg.id}`\n"
                    f"👤 By: {siku_msg.author_name}\n"
                    f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"Use `/siku custom` to send random custom messages!"
                )
                
                logger.info(f"➕ Added custom message by {sender.id}")
                
            except Exception as e:
                logger.error(f"❌ Siku add error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/siku list$'))
        async def siku_list_handler(event):
            """Handle /siku list command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                
                # Get user's messages
                user_gm = [msg for msg in self.data.siku_gm_messages.values() 
                          if msg.author_id == sender.id]
                user_gn = [msg for msg in self.data.siku_gn_messages.values() 
                          if msg.author_id == sender.id]
                user_custom = [msg for msg in self.data.siku_custom_messages.values() 
                             if msg.author_id == sender.id]
                
                if not user_gm and not user_gn and not user_custom:
                    await event.respond(
                        "📭 You haven't added any Siku messages yet!\n\n"
                        "Use:\n"
                        "• `/siku addgm <text>` - Add good morning\n"
                        "• `/siku addgn <text>` - Add good night\n"
                        "• `/siku add <text>` - Add custom message"
                    )
                    return
                
                response = "📋 **Your Siku Messages**\n\n"
                
                if user_gm:
                    response += f"🌅 **Good Morning ({len(user_gm)}):**\n"
                    for msg in user_gm[:3]:
                        response += f"• `{msg.id}`: {msg.text[:40]}...\n"
                    if len(user_gm) > 3:
                        response += f"• ... and {len(user_gm) - 3} more\n"
                    response += "\n"
                
                if user_gn:
                    response += f"🌃 **Good Night ({len(user_gn)}):**\n"
                    for msg in user_gn[:3]:
                        response += f"• `{msg.id}`: {msg.text[:40]}...\n"
                    if len(user_gn) > 3:
                        response += f"• ... and {len(user_gn) - 3} more\n"
                    response += "\n"
                
                if user_custom:
                    response += f"💬 **Custom ({len(user_custom)}):**\n"
                    for msg in user_custom[:3]:
                        response += f"• `{msg.id}`: {msg.text[:40]}...\n"
                    if len(user_custom) > 3:
                        response += f"• ... and {len(user_custom) - 3} more\n"
                
                response += f"\n📊 **Total:** {len(user_gm) + len(user_gn) + len(user_custom)} messages"
                response += f"\n🗑️ Delete with: `/siku delete <id>`"
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"❌ Siku list error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/siku stats$'))
        async def siku_stats_handler(event):
            """Handle /siku stats command"""
            self.data.total_commands_executed += 1
            
            try:
                total_gm = len(self.data.siku_gm_messages)
                total_gn = len(self.data.siku_gn_messages)
                total_custom = len(self.data.siku_custom_messages)
                total_all = total_gm + total_gn + total_custom
                
                # Calculate usage
                gm_uses = sum(msg.uses for msg in self.data.siku_gm_messages.values())
                gn_uses = sum(msg.uses for msg in self.data.siku_gn_messages.values())
                custom_uses = sum(msg.uses for msg in self.data.siku_custom_messages.values())
                total_uses = gm_uses + gn_uses + custom_uses
                
                # Most popular
                top_gm = sorted(self.data.siku_gm_messages.values(), key=lambda x: x.uses, reverse=True)[:3]
                top_gn = sorted(self.data.siku_gn_messages.values(), key=lambda x: x.uses, reverse=True)[:3]
                top_custom = sorted(self.data.siku_custom_messages.values(), key=lambda x: x.uses, reverse=True)[:3]
                
                response = f"""
📊 **Siku Statistics**

📈 **Totals:**
• GM Messages: {total_gm}
• GN Messages: {total_gn}
• Custom Messages: {total_custom}
• **Total Messages:** {total_all}

🎯 **Usage:**
• GM Sent: {gm_uses} times
• GN Sent: {gn_uses} times
• Custom Sent: {custom_uses} times
• **Total Sent:** {total_uses} times

🏆 **Top Messages:**

🌅 **Top GM:**
"""
                
                for i, msg in enumerate(top_gm, 1):
                    response += f"{i}. {msg.uses} uses - {msg.text[:30]}...\n"
                
                response += "\n🌃 **Top GN:**\n"
                for i, msg in enumerate(top_gn, 1):
                    response += f"{i}. {msg.uses} uses - {msg.text[:30]}...\n"
                
                response += "\n💬 **Top Custom:**\n"
                for i, msg in enumerate(top_custom, 1):
                    response += f"{i}. {msg.uses} uses - {msg.text[:30]}...\n"
                
                response += f"\n⏳ **Cooldown:** {self.config.siku_cooldown}s"
                response += f"\n📏 **Max Length:** {self.config.siku_max_length} chars"
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"❌ Siku stats error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        # ========== RAID COMMANDS ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/raid help$'))
        async def raid_help_handler(event):
            """Handle /raid help command"""
            self.data.total_commands_executed += 1
            
            help_text = f"""
⚡ **RAID System Help**

**Commands:**
/raid start <name> <message> - Start new raid
/raid stop <id> - Stop raid session
/raid status <id> - Check raid status
/raid list - Your active raids
/raid stats - Raid statistics

**Parameters:**
• name: Session name (no spaces)
• message: Message template
• delay: Delay between messages (default: 1.0s)
• count: Number of messages (default: {self.config.raid_default_count})

**Message Templates:**
Use {{user}} for target mention
Use {{count}} for message number
Use {{total}} for total messages
Use {{session}} for session name

**Examples:**
/raid start test "Hello {{user}}!"
/raid start alert "Message {{count}} of {{total}}"

**Limits:**
• Max users: {self.config.raid_max_users}
• Max messages: {self.config.raid_max_messages_per_session}
• Min delay: {self.config.raid_min_delay}s
• Max delay: {self.config.raid_max_delay}s
• Cooldown: {self.config.raid_cooldown}s

**⚠️ Warning:**
Use responsibly! Follow Telegram rules.
"""
            
            await event.respond(help_text)
        
        @self.client.on(events.NewMessage(pattern='(?i)/raid start (.+?) (.+)$'))
        async def raid_start_handler(event):
            """Handle /raid start command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                chat = await event.get_chat()
                
                # Check authorization
                if (event.chat_id not in self.data.allowed_chats and 
                    sender.id not in self.data.sudo_users and
                    sender.id != self.config.owner_id):
                    await event.respond("❌ You are not authorized to use RAID!")
                    return
                
                # Parse parameters
                params = event.pattern_match.group(1).strip()
                message = event.pattern_match.group(2).strip()
                
                # Extract name and optional parameters
                parts = params.split()
                name = parts[0] if parts else "raid"
                
                # Parse optional parameters
                delay = 1.0
                count = self.config.raid_default_count
                
                for part in parts[1:]:
                    if part.startswith("delay="):
                        try:
                            delay = float(part.split("=")[1])
                        except:
                            pass
                    elif part.startswith("count="):
                        try:
                            count = int(part.split("=")[1])
                        except:
                            pass
                
                # Get target users (all non-bot users in chat)
                members = await self.get_chat_members(event.chat_id, self.config.raid_max_users)
                target_users = [user.id for user in members]
                
                if not target_users:
                    await event.respond("❌ No users found to target!")
                    return
                
                # Create raid session
                session = self.create_raid_session(
                    user_id=sender.id,
                    user_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip() or f"User{sender.id}",
                    chat_id=event.chat_id,
                    chat_title=getattr(chat, 'title', 'Private Chat'),
                    name=name,
                    target_users=target_users,
                    message_template=message,
                    delay=delay,
                    total_messages=count
                )
                
                if not session:
                    await event.respond("❌ Failed to create raid session! Check cooldown or limits.")
                    return
                
                # Start execution
                task = asyncio.create_task(self.execute_raid(session.id))
                self.active_raid_tasks[session.id] = task
                
                response = f"""
⚡ **RAID Session Started!**

📛 **Name:** {session.name}
🆔 **ID:** `{session.id}`
💬 **Chat:** {session.chat_title}
👥 **Targets:** {len(session.target_users)} users
📨 **Messages:** {session.total_messages} total
⏱️ **Delay:** {session.delay_between_messages}s
📝 **Template:** {session.message_template[:50]}...

✅ **Status:** Active
📅 **Started:** {datetime.now().strftime('%H:%M:%S')}

**Commands:**
• `/raid stop {session.id}` - Stop this raid
• `/raid status {session.id}` - Check status
"""
                
                await event.respond(response)
                logger.info(f"⚡ Started RAID session {session.id} by {sender.id}")
                
            except Exception as e:
                logger.error(f"❌ RAID start error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/raid stop (\w+)$'))
        async def raid_stop_handler(event):
            """Handle /raid stop command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                session_id = event.pattern_match.group(1).strip()
                
                if self.stop_raid_session(session_id, sender.id):
                    await event.respond(f"✅ **RAID Stopped!**\n🆔 ID: `{session_id}`")
                    logger.info(f"🛑 Stopped RAID session {session_id} by {sender.id}")
                else:
                    await event.respond(f"❌ RAID session `{session_id}` not found or no permission!")
                
            except Exception as e:
                logger.error(f"❌ RAID stop error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/raid status (\w+)$'))
        async def raid_status_handler(event):
            """Handle /raid status command"""
            self.data.total_commands_executed += 1
            
            try:
                session_id = event.pattern_match.group(1).strip()
                
                if session_id not in self.data.raid_sessions:
                    await event.respond(f"❌ RAID session `{session_id}` not found!")
                    return
                
                session = self.data.raid_sessions[session_id]
                created = datetime.fromisoformat(session.created_at)
                
                progress = (session.messages_sent / session.total_messages * 100) if session.total_messages > 0 else 0
                
                response = f"""
📊 **RAID Session Status**

📛 **Name:** {session.name}
🆔 **ID:** `{session.id}`
👤 **Creator:** {session.creator_name}
💬 **Chat:** {session.chat_title}
📈 **Status:** {session.status.upper()}
🔄 **Active:** {'✅ Yes' if session.status == RaidStatus.ACTIVE.value else '❌ No'}

📨 **Progress:** {session.messages_sent}/{session.total_messages} messages
📊 **Completion:** {progress:.1f}%
👥 **Targets:** {len(session.target_users)} users
⏱️ **Delay:** {session.delay_between_messages}s

📅 **Created:** {created.strftime('%Y-%m-%d %H:%M:%S')}
⏰ **Last Action:** {datetime.fromisoformat(session.last_action).strftime('%H:%M:%S')}

📝 **Template:** {session.message_template[:100]}...
"""
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"❌ RAID status error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/raid stats$'))
        async def raid_stats_handler(event):
            """Handle /raid stats command"""
            self.data.total_commands_executed += 1
            
            try:
                total_sessions = len(self.data.raid_sessions)
                active_sessions = len([s for s in self.data.raid_sessions.values() 
                                      if s.status == RaidStatus.ACTIVE.value])
                completed_sessions = len([s for s in self.data.raid_sessions.values() 
                                         if s.status == RaidStatus.COMPLETED.value])
                
                total_messages = sum(s.messages_sent for s in self.data.raid_sessions.values())
                active_tasks = len(self.active_raid_tasks)
                
                # Top users
                user_stats = {}
                for session in self.data.raid_sessions.values():
                    if session.creator_id not in user_stats:
                        user_stats[session.creator_id] = {
                            'name': session.creator_name,
                            'sessions': 0,
                            'messages': 0
                        }
                    user_stats[session.creator_id]['sessions'] += 1
                    user_stats[session.creator_id]['messages'] += session.messages_sent
                
                top_users = sorted(user_stats.items(), key=lambda x: x[1]['messages'], reverse=True)[:5]
                
                response = f"""
📊 **RAID Statistics**

📈 **Overview:**
• Total Sessions: {total_sessions}
• Active Sessions: {active_sessions}
• Completed Sessions: {completed_sessions}
• Total Messages Sent: {total_messages}
• Active Tasks: {active_tasks}

⚙️ **Limits:**
• Max Users: {self.config.raid_max_users}
• Max Messages: {self.config.raid_max_messages_per_session}
• Max Sessions/User: {self.config.raid_max_sessions_per_user}
• Cooldown: {self.config.raid_cooldown}s

🏆 **Top Users (by messages):**
"""
                
                for i, (user_id, stats) in enumerate(top_users, 1):
                    response += f"{i}. {stats['name']}: {stats['messages']} messages ({stats['sessions']} sessions)\n"
                
                if not top_users:
                    response += "No RAID activity yet.\n"
                
                response += f"\n📅 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"❌ RAID stats error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        # ========== TAGALL COMMANDS ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/tagall(?: (.+))?$'))
        async def tagall_handler(event):
            """Handle /tagall command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                chat = await event.get_chat()
                
                # Check if group
                if event.is_private:
                    await event.respond("❌ TagAll works only in groups/channels!")
                    return
                
                # Check authorization
                if (event.chat_id not in self.data.allowed_chats and 
                    sender.id not in self.data.sudo_users and
                    sender.id != self.config.owner_id):
                    await event.respond("❌ You are not authorized to use TagAll!")
                    return
                
                # Check cooldown
                can_tag, wait_time = self.check_tagall_cooldown(sender.id)
                if not can_tag:
                    await event.respond(f"⏳ Please wait {wait_time:.1f}s before next TagAll!")
                    return
                
                # Get message text
                message_text = event.pattern_match.group(1)
                
                # Send initial response
                processing_msg = await event.respond("🏷️ Tagging all members... Please wait!")
                
                # Execute tagall
                success, result = await self.send_tagall(
                    chat_id=event.chat_id,
                    message=message_text,
                    user_id=sender.id,
                    user_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip()
                )
                
                # Update processing message
                if success:
                    await processing_msg.edit(f"✅ {result}")
                    logger.info(f"🏷️ TagAll completed by {sender.id} in {event.chat_id}")
                else:
                    await processing_msg.edit(f"❌ {result}")
                
            except FloodWaitError as e:
                await event.respond(f"⏳ Flood wait: Please try again in {e.seconds} seconds")
            except Exception as e:
                logger.error(f"❌ TagAll error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        @self.client.on(events.NewMessage(pattern='(?i)/tagall stats$'))
        async def tagall_stats_handler(event):
            """Handle /tagall stats command"""
            self.data.total_commands_executed += 1
            
            try:
                response = f"""
🏷️ **TagAll Statistics**

📊 **Usage:**
• Total TagAlls Sent: {self.data.tagall_messages_sent}
• Cooldown: {self.config.tagall_cooldown} seconds
• Max Users: {self.config.tagall_max_users}

📝 **Default Messages:**
"""
                
                for i, msg in enumerate(self.config.tagall_message_templates[:5], 1):
                    response += f"{i}. {msg}\n"
                
                response += f"\n📅 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"❌ TagAll stats error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        # ========== STATISTICS COMMAND ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/stats$'))
        async def stats_handler(event):
            """Handle /stats command"""
            self.data.total_commands_executed += 1
            
            try:
                uptime = datetime.now() - self.start_time
                days = uptime.days
                hours, remainder = divmod(uptime.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                # Bot info
                bot_name = f"@{self.bot_info.username}" if self.bot_info else "Unknown"
                bot_id = self.bot_info.id if self.bot_info else "Unknown"
                
                # Siku stats
                total_siku = (len(self.data.siku_gm_messages) + 
                            len(self.data.siku_gn_messages) + 
                            len(self.data.siku_custom_messages))
                
                # RAID stats
                active_raids = len([s for s in self.data.raid_sessions.values() 
                                   if s.status == RaidStatus.ACTIVE.value])
                
                response = f"""
📊 **SIKU TAGALL BOT - Statistics**

🤖 **Bot Info:**
• Name: {bot_name}
• ID: {bot_id}
• Version: 3.0.0
• Uptime: {days}d {hours}h {minutes}m {seconds}s

📈 **Overall Statistics:**
• Messages Processed: {self.data.total_messages_processed}
• Commands Executed: {self.data.total_commands_executed}
• Connected: {'✅ Yes' if self.connected else '❌ No'}

🌟 **SIKU System:**
• Total Messages: {total_siku}
• GM Messages: {len(self.data.siku_gm_messages)}
• GN Messages: {len(self.data.siku_gn_messages)}
• Custom Messages: {len(self.data.siku_custom_messages)}
• Siku Messages Sent: {self.data.siku_messages_sent}

⚡ **RAID System:**
• Total Sessions: {len(self.data.raid_sessions)}
• Active Sessions: {active_raids}
• RAID Messages Sent: {self.data.raid_messages_sent}

🏷️ **TagAll System:**
• TagAll Messages Sent: {self.data.tagall_messages_sent}

👥 **User Management:**
• Allowed Chats: {len(self.data.allowed_chats)}
• Sudo Users: {len(self.data.sudo_users)}
• GBAN Users: {len(self.data.gban_users)}
• Authorized Chats: {len(self.data.authorized_users)}

⚙️ **System Info:**
• Python: {sys.version.split()[0]}
• Platform: {sys.platform}
• Memory Usage: {self.get_memory_usage():.1f} MB

📅 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"❌ Stats error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        # ========== PING COMMAND ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/ping$'))
        async def ping_handler(event):
            """Handle /ping command"""
            self.data.total_commands_executed += 1
            
            try:
                start_time = time.time()
                msg = await event.respond('🏓 Pong!')
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                
                await msg.edit(f'🏓 **Pong!**\n⏱ **Latency:** `{latency:.2f}ms`')
                
            except Exception as e:
                logger.error(f"❌ Ping error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        # ========== ID COMMAND ==========
        
        @self.client.on(events.NewMessage(pattern='(?i)/id$'))
        async def id_handler(event):
            """Handle /id command"""
            self.data.total_commands_executed += 1
            
            try:
                sender = await event.get_sender()
                chat = await event.get_chat()
                
                # Get chat info
                chat_type = "Private"
                members_count = "N/A"
                
                if not event.is_private:
                    chat_type = "Group" if not hasattr(chat, 'broadcast') else "Channel"
                    if hasattr(chat, 'participants_count'):
                        members_count = chat.participants_count
                    elif hasattr(chat, 'broadcast'):
                        members_count = "Broadcast"
                
                response = f"""
🆔 **ID Information**

👤 **User Info:**
• Full Name: {sender.first_name or ''} {sender.last_name or ''}
• User ID: `{sender.id}`
• Username: @{sender.username or 'N/A'}
• Bot: {'✅ Yes' if sender.bot else '❌ No'}
• Verified: {'✅ Yes' if getattr(sender, 'verified', False) else '❌ No'}

💬 **Chat Info:**
• Chat ID: `{event.chat_id}`
• Type: {chat_type}
• Title: {getattr(chat, 'title', 'Private Chat')}
• Members: {members_count}
• Username: @{getattr(chat, 'username', 'N/A')}

📊 **Quick Stats:**
• Messages: {self.data.total_messages_processed}
• Commands: {self.data.total_commands_executed}
• Uptime: {str(datetime.now() - self.start_time).split('.')[0]}
"""
                
                await event.respond(response)
                
            except Exception as e:
                logger.error(f"❌ ID error: {e}")
                await event.respond(f"❌ Error: {str(e)[:100]}")
        
        # ========== INLINE BUTTONS ==========
        
        @self.client.on(events.CallbackQuery)
        async def callback_handler(event):
            """Handle inline button clicks"""
            try:
                data = event.data.decode('utf-8')
                sender = await event.get_sender()
                
                if data == "siku_gm":
                    siku_msg = self.get_random_siku_message('gm')
                    if siku_msg:
                        await event.answer(f"🌅 {siku_msg.text}", alert=True)
                    else:
                        await event.answer("No GM messages available!", alert=True)
                
                elif data == "siku_gn":
                    siku_msg = self.get_random_siku_message('gn')
                    if siku_msg:
                        await event.answer(f"🌃 {siku_msg.text}", alert=True)
                    else:
                        await event.answer("No GN messages available!", alert=True)
                
                elif data == "raid_start":
                    await event.answer("Use /raid start <name> <message>", alert=False)
                
                elif data == "tagall_now":
                    await event.answer("Use /tagall [message]", alert=False)
                
                elif data == "show_stats":
                    uptime = datetime.now() - self.start_time
                    stats = f"""
📊 Quick Stats:
• Uptime: {str(uptime).split('.')[0]}
• Messages: {self.data.total_messages_processed}
• Commands: {self.data.total_commands_executed}
• Siku Sent: {self.data.siku_messages_sent}
• RAID Sent: {self.data.raid_messages_sent}
• TagAll Sent: {self.data.tagall_messages_sent}
"""
                    await event.answer(stats, alert=True)
                
                elif data == "get_id":
                    await event.answer(f"Your ID: {sender.id}", alert=True)
                
                else:
                    await event.answer("Button clicked!", alert=False)
                
            except Exception as e:
                logger.error(f"❌ Callback error: {e}")
                await event.answer("Error!", alert=False)
        
        logger.info("✅ Event handlers set up successfully!")
        logger.info(f"📊 Loaded {len(self.data.siku_gm_messages)} GM, {len(self.data.siku_gn_messages)} GN messages")
        logger.info(f"📊 Loaded {len(self.data.raid_sessions)} RAID sessions")
        
    def get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    async def cleanup_old_sessions(self):
        """Clean up old RAID sessions"""
        try:
            cutoff_time = datetime.now() - timedelta(days=1)
            to_remove = []
            
            for session_id, session in self.data.raid_sessions.items():
                if session.status in [RaidStatus.COMPLETED.value, RaidStatus.CANCELLED.value, RaidStatus.ERROR.value]:
                    created = datetime.fromisoformat(session.created_at)
                    if created < cutoff_time:
                        to_remove.append(session_id)
            
            for session_id in to_remove:
                if session_id in self.data.raid_sessions:
                    del self.data.raid_sessions[session_id]
                
                if session_id in self.active_raid_tasks:
                    del self.active_raid_tasks[session_id]
            
            if to_remove:
                logger.info(f"🧹 Cleaned up {len(to_remove)} old RAID sessions")
        
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
    
    async def auto_save_task(self):
        """Auto-save task that runs periodically"""
        while self.is_running:
            await asyncio.sleep(self.config.auto_save_interval)
            try:
                self.save_configuration()
                logger.debug("💾 Auto-saved configuration")
            except Exception as e:
                logger.error(f"❌ Auto-save error: {e}")
    
    async def cleanup_task(self):
        """Cleanup task that runs periodically"""
        while self.is_running:
            await asyncio.sleep(3600)  # Run every hour
            try:
                await self.cleanup_old_sessions()
                logger.debug("🧹 Cleanup task completed")
            except Exception as e:
                logger.error(f"❌ Cleanup task error: {e}")
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("=" * 70)
            logger.info("🤖 STARTING SIKU TAGALL BOT v3.0.0")
            logger.info("=" * 70)
            
            # Initialize client
            if not await self.initialize_client():
                logger.error("❌ Failed to initialize client!")
                return False
            
            # Connect to Telegram
            logger.info("🔗 Connecting to Telegram...")
            if not await self.connect_to_telegram():
                logger.error("❌ Failed to connect to Telegram!")
                return False
            
            # Set up event handlers
            logger.info("⚙️ Setting up event handlers...")
            self.setup_event_handlers()
            
            # Start maintenance tasks
            self.is_running = True
            asyncio.create_task(self.auto_save_task())
            asyncio.create_task(self.cleanup_task())
            
            # Resume active RAID sessions
            active_sessions = [s for s in self.data.raid_sessions.values() 
                             if s.status == RaidStatus.ACTIVE.value]
            for session in active_sessions:
                task = asyncio.create_task(self.execute_raid(session.id))
                self.active_raid_tasks[session.id] = task
                logger.info(f"⚡ Resumed RAID session: {session.id}")
            
            # Set up signal handlers
            loop = asyncio.get_event_loop()
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
            
            logger.info("=" * 70)
            logger.info("✅ BOT IS NOW RUNNING!")
            logger.info("✅ Press Ctrl+C to stop")
            logger.info("=" * 70)
            
            # Send startup notification to owner
            if self.config.owner_id and self.client:
                try:
                    await self.client.send_message(
                        self.config.owner_id,
                        f"🤖 **SIKU TAGALL BOT Started!**\n"
                        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"⏰ Uptime: Just started\n"
                        f"📊 Version: 3.0.0\n\n"
                        f"✅ Bot is now running!"
                    )
                except:
                    pass
            
            # Keep the bot running
            await self.client.run_until_disconnected()
            
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
            return True
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot gracefully"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        logger.info("🛑 Shutting down bot...")
        
        # Stop all active RAID tasks
        for session_id, task in list(self.active_raid_tasks.items()):
            if not task.done():
                task.cancel()
                logger.info(f"🛑 Cancelled RAID task: {session_id}")
        
        # Save final configuration
        self.save_configuration()
        
        # Disconnect client
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            logger.info("🔌 Disconnected from Telegram")
        
        logger.info("=" * 70)
        logger.info("✅ Bot shutdown complete!")
        logger.info("=" * 70)

async def main():
    """Main entry point"""
    bot = SikuTagAllBot()
    
    try:
        success = await bot.start()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8 or higher is required!")
        sys.exit(1)
    
    # Create data directory
    CONFIG_DIR.mkdir(exist_ok=True)
    
    # Run the bot
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
