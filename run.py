from app import create_app
from app.ia_agent.analisis_handler import AnalisisHandler
from app.data_collectors.CryptoPriceToMongo import CryptoPriceToMongo
from app.data_collectors.EthereumToMongoSync import EthereumToMongoSync
import threading

app = create_app()

def run_data_collectors():
    symbols = ["bitcoin", "ethereum", "dogecoin"]
    
    # Instanciar ambos recolectores
    crypto_collector = CryptoPriceToMongo(symbols)
    eth_sync = EthereumToMongoSync()
    an_han = AnalisisHandler()
    
    
    # Iniciar recolectores en hilos separados
    crypto_thread = threading.Thread(
        target=crypto_collector.run,
        kwargs={'interval_seconds': 60}
    )
    
    eth_thread = threading.Thread(
        target=eth_sync.run
    )

    an_thread = threading.Thread(
        target=an_han.run 
    )
    
    crypto_thread.daemon = True
    eth_thread.daemon = True
    an_thread.daemon = True

        
    crypto_thread.start()
    eth_thread.start()
    an_thread.start()

if __name__ == '__main__':
    run_data_collectors()
    app.run(host='0.0.0.0', port=8081, use_reloader=False, debug=True)
