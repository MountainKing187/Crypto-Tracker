import firebase_admin
from firebase_admin import credentials, messaging
from pymongo import MongoClient
from app.utils import config_loader, mongo_handler

class NotificationService:

    def __init__(self):
        # Cargar configuración centralizada
        self.config = config_loader.load_config()
        
        # Configurar Firebase
        self.firebase_cred = credentials.Certificate(self.config.FIREBASE_CRED_PATH)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(self.firebase_cred)


        # Inicializar MongoDB usando MongoHandler
        self.mongo = mongo_handler.MongoHandler()
        self.mongo.client = self.mongo.create_client(self.config.MONGODB_URI)
        self.mongo.db = self.mongo.client[self.config.MONGO_DB_NAME]
        
        # Colecciones
        self.devices_collection = self.mongo.db.devices_collection

    def get_device_tokens(self):
        """Obtiene todos los tokens FCM registrados en MongoDB"""
        try:
            tokens = [doc['token'] for doc in self.devices_collection.find({}, {'token': 1})]
            print(f"Obtenidos {len(tokens)} tokens de dispositivos")
            return tokens
        except Exception as e:
            print(f"Error al obtener tokens: {str(e)}")
            return []

    def send_notification_to_all(self, title, body):
        """
        Envía una notificación a todos los dispositivos registrados
        
        :param title: Título de la notificación
        :param body: Cuerpo del mensaje
        """
        tokens = self.get_device_tokens()
        if not tokens:
            print("No hay tokens disponibles para enviar notificaciones")
            return
        
        try:
            # Crear mensaje multicast (para múltiples dispositivos)
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                tokens=tokens
            )
            
            # Enviar y procesar respuesta
            response = messaging.send_multicast(message)
            print(f"Notificación enviada. Éxitos: {response.success_count}, Fallos: {response.failure_count}")
            
            # Manejar tokens inválidos
            if response.failure_count > 0:
                self.handle_failed_tokens(response.responses, tokens)
                
        except Exception as e:
            print(f"Error al enviar notificación: {str(e)}")

    def handle_failed_tokens(self, responses, tokens):
        """Elimina tokens inválidos de la base de datos"""
        invalid_tokens = []
        for i, resp in enumerate(responses):
            if not resp.success:
                invalid_tokens.append(tokens[i])
                print(f"Token inválido detectado: {tokens[i]} - {resp.exception}")
        
        if invalid_tokens:
            try:
                result = self.devices_collection.delete_many({'token': {'$in': invalid_tokens}})
                print(f"Tokens inválidos eliminados: {result.deleted_count}")
            except Exception as e:
                print(f"Error al eliminar tokens inválidos: {str(e)}")
