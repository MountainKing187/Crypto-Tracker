from app.ia_agent import NotificationService, GeminiAgent
import time

class AnalisisHandler:
    def run(self, interval_seconds=3600):
        print(f"Iniciando analisis ...")
        NotificationService.send_notification_to_all("Actualizacion de analisis", "Se ha actualizado el analisis con IA")
        GeminiAgent.analizar_datos_gemini()
        time.sleep(interval_seconds)
         
