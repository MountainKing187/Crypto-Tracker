import os
import time
import requests
from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv

class CryptoPriceToMongoNoKey:
    def __init__(self, symbols):
        load_dotenv()
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("FALTA MONGODB_URI en el archivo .env")

        self.symbols = symbols
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.client = MongoClient(mongo_uri)
        self.db = self.client.crypto
        self.prices = self.db.prices

        print(f"Conexión MongoDB establecida.")
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

if __name__ == "__main__":
    symbols = ["bitcoin", "ethereum", "dogecoin"]
    app = CryptoPriceToMongoNoKey(symbols)
    app.run(interval_seconds=60)
