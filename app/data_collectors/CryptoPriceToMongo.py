import time
import requests
from app import socketio
from datetime import datetime, timezone
from app.utils import config_loader, mongo_handler

class CryptoPriceToMongo:
    def __init__(self, symbols):
        # Cargar configuración desde el config_loader centralizado
        self.config = config_loader.load_config()
        
        # Obtener instancia de MongoHandler
        self.mongo = mongo_handler.MongoHandler()
        
        # Configurar MongoDB
        self.mongo.client = self.mongo.create_client(self.config.MONGODB_URI)
        self.mongo.db = self.mongo.client[self.config.MONGO_DB_NAME]
        self.prices = self.mongo.db['price_history']

        self.symbols = symbols
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"

        print(f"Conexión MongoDB establecida. DB: {self.config.MONGO_DB_NAME}")
        print(f"Criptos configuradas: {', '.join(self.symbols)}")

    def get_prices(self, currency="usd"):
        params = {
            "ids": ",".join(self.symbols),
            "vs_currencies": currency
        }

        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error al obtener precios desde CoinGecko: {e}")
            return None

    def save_prices(self):
        data = self.get_prices()
        if not data:
            return
        
        print("")
        now = datetime.now(timezone.utc)
        for symbol in self.symbols:
            if symbol in data:
                price = data[symbol].get("usd")
                if price is not None:
                    record = {
                        "symbol": symbol,
                        "price": price,
                        "timestamp": now,
                        "source": "CoinGecko"
                    }
                    self.prices.insert_one(record)
                    try:
                        if symbol == 'ethereum':
                            socketio.emit('new_price_ethereum', {
                                'symbol': symbol,
                                'price': price,
                                'timestamp': now.isoformat()
                            })
                        elif symbol == 'dogecoin':
                            socketio.emit('new_price_dogecoin', {
                                'symbol': symbol,
                                'price': price,
                                'timestamp': now.isoformat()
                            })
                        elif symbol == 'bitcoin':
                            socketio.emit('new_price_bitcoin', {
                                'symbol': symbol,
                                'price': price,
                                'timestamp': now.isoformat()
                            })
                    except Exception as e:
                        print(f"Error emitiendo evento para {symbol}: {str(e)}")
                    print(f"Guardado: {symbol} -> ${price}")
                else:
                    print(f"Precio USD no encontrado para: {symbol}")
            else:
                print(f"No se encontró precio para: {symbol}")
        print("")

    def run(self, interval_seconds=60):
        print(f"Iniciando recolección cada {interval_seconds} segundos...")
        while True:
            self.save_prices()
            time.sleep(interval_seconds)
