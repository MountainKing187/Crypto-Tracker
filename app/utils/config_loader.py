import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()  # Cargar variables de entorno desde .env
    
    class Config:
        MONGODB_URI = os.getenv('MONGODB_URI')
        MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'crypto_data')
        ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')
        
        @property
        def ETHEREUM_NODE_WS(self):
            if self.ALCHEMY_API_KEY:
                return f"wss://eth-mainnet.g.alchemy.com/v2/{self.ALCHEMY_API_KEY}"
            return None
    
    return Config()
