from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    
    # API Configuration
    API_URL = "https://api.invincibleocean.com/invincible/mobile-identity"
    SECRET_KEY = os.getenv("SECRET_KEY")
    CLIENT_ID = os.getenv("CLIENT_ID")
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/mobile_uan_bot")
    
    # Owner ID (can add/remove sudos)
    OWNER_ID = int(os.getenv("OWNER_ID"))
    
    # Default sudo limit
    DEFAULT_SUDO_LIMIT = 50

config = Config()



