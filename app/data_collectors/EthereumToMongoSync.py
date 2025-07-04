import os
from time import sleep
from web3 import Web3, LegacyWebSocketProvider
from pymongo import MongoClient
from dotenv import load_dotenv

class EthereumToMongoSync:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ALCHEMY_API_KEY")
        mongo_uri = os.getenv("MONGODB_URI")

        if not api_key or not mongo_uri:
            raise ValueError("Falta ALCHEMY_API_KEY o MONGODB_URI en el .env")

        self.w3 = Web3(LegacyWebSocketProvider(f"wss://eth-mainnet.g.alchemy.com/v2/{api_key}"))
        if not self.w3.is_connected():
            raise ConnectionError("No se pudo conectar a Ethereum WebSocket")

        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client.ethereum
        self.blocks = self.db.blocks
        self.transactions = self.db.transactions

    def save_block_and_transactions(self, block_number):
        block = self.w3.eth.get_block(block_number, full_transactions=True)
    
        block_data = {
            "blockNumber": block.number,
            "hash": block.hash.hex(),
            "timestamp": block.timestamp,
            "miner": block.miner,
            "transactions": [tx.hash.hex() for tx in block.transactions]
        }
    
        self.blocks.update_one({"blockNumber": block.number}, {"$set": block_data}, upsert=True)
    
        for tx in block.transactions:
            value_eth = str(Web3.from_wei(tx.value, "ether"))
    
            tx_data = {
                "hash": tx.hash.hex(),
                "blockNumber": block.number,
                "from": tx["from"],
                "to": tx.to,
                "value": value_eth,
                "asset": "ETH",
                "timestamp": block.timestamp
            }
            self.transactions.update_one({"hash": tx.hash.hex()}, {"$set": tx_data}, upsert=True)
    
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

                sleep(5)

            except Exception as e:
                print(f"Error: {e}")
                sleep(10)

if __name__ == "__main__":
    eth_to_mongo = EthereumToMongoSync()
    eth_to_mongo.run()
