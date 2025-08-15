"""
Servicio de Integración con WhatsApp Business API
================================================

Maneja la comunicación bidireccional con WhatsApp Business API
"""
import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class WhatsAppAPIService:
    """Servicio para interactuar con WhatsApp Business API"""
    
    def __init__(self):
        # Configuración de WhatsApp Business API
        self.base_url = os.getenv("WHATSAPP_API_URL", "https://graph.facebook.com/v18.0")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "agent99_verify_token")
        
        if not all([self.phone_number_id, self.access_token]):
            logger.warning("⚠️ Configuración de WhatsApp Business API incompleta")
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verifica el webhook de WhatsApp"""
        try:
            if mode == "subscribe" and token == self.verify_token:
                logger.info("✅ Webhook de WhatsApp verificado correctamente")
                return challenge
            else:
                logger.warning("❌ Verificación de webhook fallida")
                return None
        except Exception as e:
            logger.error(f"❌ Error verificando webhook: {e}")
            return None
    
    def send_text_message(self, phone_number: str, message: str) -> bool:
        """Envía un mensaje de texto por WhatsApp"""
        try:
            if not all([self.phone_number_id, self.access_token]):
                logger.error("❌ Configuración de WhatsApp incompleta")
                return False
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Mensaje WhatsApp enviado a {phone_number}")
                return True
            else:
                logger.error(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje WhatsApp: {e}")
            return False
    
    def send_template_message(self, phone_number: str, template_name: str, 
                            language_code: str = "es", components: list = None) -> bool:
        """Envía un mensaje de plantilla por WhatsApp"""
        try:
            if not all([self.phone_number_id, self.access_token]):
                logger.error("❌ Configuración de WhatsApp incompleta")
                return False
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code}
                }
            }
            
            if components:
                data["template"]["components"] = components
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Plantilla WhatsApp enviada a {phone_number}")
                return True
            else:
                logger.error(f"❌ Error enviando plantilla: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error enviando plantilla WhatsApp: {e}")
            return False
    
    def send_interactive_message(self, phone_number: str, message: str, 
                               buttons: list) -> bool:
        """Envía un mensaje interactivo con botones por WhatsApp"""
        try:
            if not all([self.phone_number_id, self.access_token]):
                logger.error("❌ Configuración de WhatsApp incompleta")
                return False
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Crear botones interactivos
            button_components = []
            for i, button in enumerate(buttons[:3]):  # Máximo 3 botones
                button_components.append({
                    "type": "button",
                    "sub_type": "quick_reply",
                    "index": i,
                    "parameters": [{"type": "text", "text": button}]
                })
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message},
                    "action": {"buttons": button_components}
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Mensaje interactivo WhatsApp enviado a {phone_number}")
                return True
            else:
                logger.error(f"❌ Error enviando mensaje interactivo: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje interactivo WhatsApp: {e}")
            return False
    
    def get_message_status(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de un mensaje enviado"""
        try:
            if not all([self.phone_number_id, self.access_token]):
                logger.error("❌ Configuración de WhatsApp incompleta")
                return None
            
            url = f"{self.base_url}/{message_id}"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Error obteniendo estado: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado del mensaje: {e}")
            return None

# Instancia global del servicio
whatsapp_api_service = WhatsAppAPIService()
