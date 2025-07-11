from datetime import datetime, timedelta
import time
from app.utils import config_loader, mongo_handler
import os
import google.generativeai as genai

class GeminiAgent:

    def __init__(self):
        # Cargar configuración centralizada
        self.config = config_loader.load_config()

        if not self.config.GEMINI_API_KEY:
            raise ValueError("La API Key de Gemini no está configurada")
        
        # Inicializar MongoDB usando MongoHandler
        self.mongo = mongo_handler.MongoHandler()
        self.mongo.client = self.mongo.create_client(self.config.MONGODB_URI)
        self.mongo.db = self.mongo.client[self.config.MONGO_DB_NAME]
        
        # Colecciones
        self.price_history = self.mongo.db.price_history
        self.aiprompt = self.mongo.db.aiprompt

    def analizar_datos_gemini(self):

        # Configurar Gemini
        genai.configure(api_key= self.config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Calcular timestamp de hace dos horas
        hora_actual = datetime.utcnow()
        hace_dos_horas = hora_actual - timedelta(hours=2)
        
        try:
                        
            # Consultar registros de hace dos horas
            query = {
                "timestamp": {"$gte": hace_dos_horas}
            }

            registros = list(self.price_history.find(query))

            print(f"Registros encontrados: {len(registros)}")

            # Preparar datos para el prompt conjunto
            resumen_monedas = []
            simbolos = set()
            precio_promedio = 0
            min_precio = float('inf')
            max_precio = float('-inf')
            
            for registro in registros:
                symbol = registro['symbol']
                price = registro['price']
                timestamp = registro['timestamp']
                
                resumen_monedas.append(f"- {symbol.upper()}: ${price:.2f}")
                simbolos.add(symbol)
                precio_promedio += price
                min_precio = min(min_precio, price)
                max_precio = max(max_precio, price)
            
            if (len(registros)!= 0):
                precio_promedio /= len(registros)
                resumen_monedas = "\n".join(resumen_monedas)
                
                # Construir prompt para análisis conjunto
                prompt = f"""
                Quiero que analises brevemente y en texto puro los siguientes precios de criptomonedas registrados hace aproximadamente dos horas ({hace_dos_horas.strftime('%Y-%m-%d %H:%M')} UTC teniendo en cuenta que la hora actual es ({hora_actual.strftime('%Y-%m-%d %H:%M')}):

                {resumen_monedas}

                Proporciona un análisis que incluya:
                1. Tendencia general del mercado 
                2. Monedas con comportamiento destacado (mayores ganancias/pérdidas)
                3. Perspectiva a corto plazo (próximas 24 horas)
                4. Nivel de riesgo general del mercado (Bajo/Medio/Alto)

                Contexto adicional:
                - Precio promedio: ${precio_promedio:.2f}
                - Rango de precios: ${min_precio:.2f} - ${max_precio:.2f}
                - Total de monedas analizadas: {len(registros)}
                """
                
                # Enviar solicitud a Gemini
                response = model.generate_content(prompt)
                analisis = response.text.strip()
                
                # Crear documento para insertar
                documento_analisis = {
                    "fecha_analisis": datetime.utcnow(),
                    "rango_temporal": {
                        "inicio": hace_dos_horas
                    },
                    "prompt_utilizado": prompt,
                    "analisis_gemini": analisis,
                    "monedas_analizadas": list(simbolos),
                    "total_monedas": len(registros),
                    "precio_promedio": precio_promedio,
                    "precio_minimo": min_precio,
                    "precio_maximo": max_precio,
                    "metadata": {
                        "fuente": "CoinGecko",
                        "tipo_analisis": "conjunto"
                    }
                }
                
                # Insertar en colección destino
                self.aiprompt.insert_one(documento_analisis)
                print(f"Análisis conjunto guardado. Monedas analizadas: {len(simbolos)}")
                print(f"Hora actual: {hora_actual.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("No hay nada que analizar")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

