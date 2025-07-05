import time
from app import socketio
from web3 import Web3, LegacyWebSocketProvider
from app.utils import config_loader, mongo_handler
from datetime import datetime

class EthereumToMongoSync:
    def __init__(self):
        # Cargar configuración centralizada
        self.config = config_loader.load_config()
        
        # Verificar que tenemos la clave de Alchemy
        if not self.config.ALCHEMY_API_KEY:
            raise ValueError("Falta ALCHEMY_API_KEY en la configuración")
        
        # Inicializar Web3 con WebSocket de Alchemy
        ws_url = f"wss://eth-mainnet.g.alchemy.com/v2/{self.config.ALCHEMY_API_KEY}"
        self.w3 = Web3(LegacyWebSocketProvider(ws_url))
        if not self.w3.is_connected():
            raise ConnectionError("No se pudo conectar a Ethereum WebSocket")
        
        # Inicializar MongoDB usando MongoHandler
        self.mongo = mongo_handler.MongoHandler()
        self.mongo.client = self.mongo.create_client(self.config.MONGODB_URI)
        self.mongo.db = self.mongo.client[self.config.MONGO_DB_NAME]
        
        # Colecciones
        self.blocks = self.mongo.db.blocks
        self.transactions = self.mongo.db.transactions

        print("Conexión a Ethereum y MongoDB establecida.")
        print(f"Base de datos: {self.config.MONGO_DB_NAME}")

    def save_block_and_transactions(self, block_number):
        block = self.w3.eth.get_block(block_number, full_transactions=True)
        
        # Convertir timestamp a datetime UTC
        block_timestamp = datetime.utcfromtimestamp(block.timestamp)
        
        block_data = {
            "blockNumber": block.number,
            "hash": block.hash.hex(),
            "timestamp": block_timestamp,
            "miner": block.miner,
            "transactions": [tx.hash.hex() for tx in block.transactions]
        }
        
        # Actualizar o insertar el bloque
        self.blocks.update_one(
            {"blockNumber": block.number}, 
            {"$set": block_data}, 
            upsert=True
        )

        block_data['timestamp'] = block_timestamp.isoformat()
        socketio.emit('new_block', block_data)
        
        # Guardar cada transacción
        for tx in block.transactions:
            value_eth = str(Web3.from_wei(tx.value, "ether"))
            
            tx_data = {
                "hash": tx.hash.hex(),
                "blockNumber": block.number,
                "from": tx.get("from", ""),  # Usamos get por si acaso no existe
                "to": tx.to,
                "value": value_eth,
                "asset": "ETH",
                "timestamp": block_timestamp
            }
            self.transactions.update_one(
                {"hash": tx.hash.hex()}, 
                {"$set": tx_data}, 
                upsert=True
            )
        
        print(f"Guardado bloque {block.number} con {len(block.transactions)} transacciones.")

    def run(self):
        print("Escuchando nuevos bloques...")
        block_filter = self.w3.eth.filter('latest')

        while True:
            try:
                new_blocks = block_filter.get_new_entries()
                for block_hash in new_blocks:
                    block = self.w3.eth.get_block(block_hash.hex())
                    self.save_block_and_transactions(block.number)

                time.sleep(5)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    sync = EthereumToMongoSync()
    sync.run()
