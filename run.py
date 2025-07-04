from app import create_app
from app.data_collectors import crypto_price_to_mongo, ethereum_to_mongo_sync
import threading

app = create_app()
symbols = ["bitcoin", "ethereum", "dogecoin"]

def run_data_collectors():
    # Iniciar recolectores en hilos separados
    crypto_thread = threading.Thread(target=crypto_price_to_mongo.run, args=(symbols,))
    eth_thread = threading.Thread(target=ethereum_to_mongo_sync.run)
    
    crypto_thread.daemon = True
    eth_thread.daemon = True
    
    crypto_thread.start()
    eth_thread.start()

if __name__ == '__main__':
    run_data_collectors()
    app.run(host='0.0.0.0', port=8081, use_reloader=False)
