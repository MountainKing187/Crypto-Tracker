import time
from app.ia_agent.notification_service import NotificationService
from app.ia_agent.gemini_agent import GeminiAgent

class AnalisisHandler:
    def run(self, interval_seconds=600):
        print(f"Iniciando analisis ...")
        while True:
            servicioNotificacion = NotificationService()
            servicioNotificacion.send_notification_to_all("Actualizacion de analisis", "Se ha actualizado el analisis con IA")
            AgenteIA = GeminiAgent()
            AgenteIA.analizar_datos_gemini()
            time.sleep(interval_seconds)
         
