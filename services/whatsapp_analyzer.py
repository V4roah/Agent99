import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from services.llm import llm_service

from services.vector_store import vector_store
from services.tag_persistence import tag_persistence_service
from models.whatsapp import WhatsAppMessage, WhatsAppConversation
import uuid


class WhatsAppAnalyzer:
    def __init__(self):

        self.conversations: Dict[str, WhatsAppConversation] = {}

    def parse_whatsapp_export(self, export_text: str) -> List[WhatsAppConversation]:
        """Parsea un export de WhatsApp y extrae conversaciones"""
        conversations = []

        # Patrón común de export de WhatsApp
        # [DD/MM/YYYY, HH:MM:SS] Nombre: Mensaje
        pattern = r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.+?): (.+)'

        current_conversation = None
        current_messages = []

        lines = export_text.split('\n')

        for line in lines:
            match = re.match(pattern, line.strip())
            if match:
                date_str, time_str, sender, content = match.groups()

                # Parsear fecha y hora
                try:
                    timestamp = datetime.strptime(
                        f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                except ValueError:
                    continue

                # Crear mensaje
                message = WhatsAppMessage(
                    timestamp=timestamp,
                    sender=sender,
                    content=content
                )

                # Si es un nuevo cliente o la conversación es muy antigua, crear nueva
                if (current_conversation is None or
                    sender != current_conversation.customer_name or
                        timestamp - current_conversation.last_activity > timedelta(hours=24)):

                    # Guardar conversación anterior si existe
                    if current_conversation:
                        current_conversation.messages = current_messages
                        conversations.append(current_conversation)

                    # Crear nueva conversación
                    conversation_id = str(uuid.uuid4())

                    current_conversation = WhatsAppConversation(
                        id=conversation_id,
                        customer_phone="",  # Se puede extraer del nombre si hay patrón
                        customer_name=sender,
                        messages=[],
                        start_date=timestamp,
                        last_activity=timestamp
                    )
                    current_messages = []

                current_messages.append(message)
                current_conversation.last_activity = timestamp

        # Agregar última conversación
        if current_conversation:
            current_conversation.messages = current_messages
            conversations.append(current_conversation)

        return conversations

    def analyze_conversation(self, conversation: WhatsAppConversation) -> Dict[str, Any]:
        """Analiza una conversación completa usando LLM"""

        # Preparar texto de la conversación
        conversation_text = "\n".join([
            f"[{msg.timestamp.strftime('%H:%M')}] {msg.sender}: {msg.content}"
            for msg in conversation.messages
        ])

        # Clasificar conversación
        categories = ["ventas", "soporte", "reclamo", "consulta", "otro"]
        classification = llm_service.classify_conversation(
            conversation_text, categories)

        # Extraer entidades
        entities = llm_service.extract_entities(conversation_text)

        # Actualizar conversación
        conversation.category = classification.get("category", "otro")

        # Generar etiquetas inteligentes usando el nuevo servicio
        from services.smart_tagging import smart_tagging_service
        smart_tags = smart_tagging_service.generate_smart_tags(
            text=conversation_text,
            category=conversation.category,
            max_tags=8
        )

        # Extraer solo los nombres de las etiquetas para compatibilidad
        conversation.tags = [tag["name"] for tag in smart_tags]
        conversation.sentiment = classification.get("sentiment", "neutral")

        # Guardar en vector store para búsquedas futuras

        from models.vector import VectorItem
        vector_item = VectorItem(
            id=conversation.id,
            text=conversation_text,
            metadata={
                "type": "whatsapp_conversation",
                "customer_name": conversation.customer_name,
                "category": conversation.category,
                "sentiment": conversation.sentiment,
                "tags": conversation.tags,

                "smart_tags": smart_tags,  # Incluir etiquetas inteligentes completas
                "start_date": conversation.start_date.isoformat(),
                "message_count": len(conversation.messages)
            }
        )
        vector_store.add_item(vector_item)

        return {
            "conversation_id": conversation.id,
            "classification": classification,
            "entities": entities,

            "vector_id": vector_item.id,
            "total_messages": len(conversation.messages),
            "duration_hours": (conversation.last_activity - conversation.start_date).total_seconds() / 3600,
            "customer_name": conversation.customer_name,
            "category": conversation.category,

            "sentiment": conversation.sentiment,
            "insights": {
                "total_messages": len(conversation.messages),
                "duration_hours": (conversation.last_activity - conversation.start_date).total_seconds() / 3600,
                "avg_response_time_minutes": 0,
                "avg_message_length": sum(len(msg.content) for msg in conversation.messages) / len(conversation.messages) if conversation.messages else 0,
                "category": conversation.category,
                "sentiment": conversation.sentiment,
                "tags": conversation.tags
            }
        }

    def analyze_conversation_text(self, conversation_text: str, customer_id: str) -> Dict[str, Any]:
        """Analiza texto de conversación directamente y crea la conversación internamente"""

        # Crear una conversación temporal para análisis
        conversation_id = str(uuid.uuid4())
        temp_conversation = WhatsAppConversation(
            id=conversation_id,
            customer_phone="",
            customer_name="Cliente",
            messages=[],
            start_date=datetime.now(),
            last_activity=datetime.now()
        )

        # Clasificar conversación
        categories = ["ventas", "soporte", "reclamo", "consulta", "otro"]
        classification = llm_service.classify_conversation(
            conversation_text, categories)

        # Extraer entidades
        entities = llm_service.extract_entities(conversation_text)

        # Actualizar conversación
        temp_conversation.category = classification.get("category", "otro")

        # Generar etiquetas inteligentes usando el nuevo servicio
        from services.smart_tagging import smart_tagging_service
        print(f"🔍 DEBUG: Generando tags para texto: '{conversation_text}'")
        print(f"🔍 DEBUG: Categoría: {temp_conversation.category}")

        try:
            smart_tags = smart_tagging_service.generate_smart_tags(
                text=conversation_text,
                category=temp_conversation.category,
                max_tags=8
            )
            print(
                f"🔍 DEBUG: Tags generados por smart_tagging: {len(smart_tags)} tags")
            print(f"🔍 DEBUG: smart_tags contenido: {smart_tags}")
        except Exception as e:
            import traceback
            print(f"❌ ERROR en smart_tagging_service.generate_smart_tags: {e}")
            print(f"🔍 Traceback completo: {traceback.format_exc()}")
            smart_tags = []

        # Si no se generaron tags inteligentes, usar los del LLM
        if not smart_tags and "tags" in classification:
            llm_tags = classification["tags"]
            smart_tags = [
                {
                    "name": tag,
                    "category": temp_conversation.category,
                    "type": "llm_generated",
                    "confidence": 0.8,
                    "source": "llm_classification",
                    "weight": 0.8,
                    "context": conversation_text[:100],
                    "related_tags": []
                }
                for tag in llm_tags
            ]
            print(f"🔄 Usando tags del LLM: {llm_tags}")

        # Extraer solo los nombres de las etiquetas para compatibilidad
        temp_conversation.tags = [tag["name"] for tag in smart_tags]
        print(
            f"🔍 DEBUG: Tags asignados a temp_conversation: {temp_conversation.tags}")
        print(f"🔍 DEBUG: smart_tags original: {smart_tags}")
        temp_conversation.sentiment = classification.get(
            "sentiment", "neutral")

        # Guardar en vector store para búsquedas futuras
        from models.vector import VectorItem
        vector_item = VectorItem(
            id=temp_conversation.id,
            text=conversation_text,
            metadata={
                "category": temp_conversation.category,
                "sentiment": temp_conversation.sentiment,
                "tags": temp_conversation.tags,
                "customer_id": customer_id
            }
        )
        vector_store.add_item(vector_item)

        # 🔴 COMENTADO: La persistencia de tags ahora se hace desde la ruta
        # después de crear la conversación en la BD
        # PERSISTIR TAGS EN LA BASE DE DATOS
        # print(f"🔍 DEBUG: Intentando persistir {len(smart_tags)} tags...")
        # print(f"🔍 DEBUG: conversation_id: {temp_conversation.id}")
        # print(f"🔍 DEBUG: customer_id: {customer_id}")
        # print(f"🔍 DEBUG: category: {temp_conversation.category}")

        # try:
        #     result = tag_persistence_service.save_tags_to_database(
        #         tags=smart_tags,
        #         conversation_id=temp_conversation.id,
        #         customer_id=customer_id,
        #         category=temp_conversation.category
        #     )
        #     print(f"🔍 DEBUG: Resultado de persistencia: {result}")
        #     if result:
        #         print(
        #             f"✅ Tags persistidos en BD: {len(smart_tags)} tags guardados")
        #     else:
        #         print(f"❌ Tags NO se persistieron en BD")
        # except Exception as e:
        #     import traceback
        #     print(f"❌ Error persistiendo tags en BD: {e}")
        #     print(f"🔍 Traceback: {traceback.format_exc()}")

        print(
            f"🔍 DEBUG: Tags en insights del return: {temp_conversation.tags}")
        return {
            "conversation_id": temp_conversation.id,
            "classification": classification,
            "entities": entities,
            "vector_id": vector_item.id,
            "total_messages": 0,
            "duration_hours": 0,
            "customer_name": "Cliente",
            "category": temp_conversation.category,
            "sentiment": temp_conversation.sentiment,
            "insights": {
                "total_messages": 0,
                "duration_hours": 0,
                "avg_response_time_minutes": 0,
                "avg_message_length": len(conversation_text),
                "category": temp_conversation.category,
                "sentiment": temp_conversation.sentiment,
                "tags": temp_conversation.tags
            }
        }

    def search_similar_conversations(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Busca conversaciones similares usando vector store"""
        return vector_store.search(query, k)

    def generate_response_suggestion(self, conversation: WhatsAppConversation, context: str = "") -> str:
        """Genera sugerencias de respuesta basadas en el contexto"""

        # Determinar tipo de respuesta según categoría
        if conversation.category == "ventas":

            response_type = "sales_response"
        elif conversation.category == "reclamo":

            response_type = "complaint_response"
        elif conversation.category == "soporte":

            response_type = "support_response"
        else:
            response_type = "general_response"

        # Buscar conversaciones similares para contexto
            similar = self.search_similar_conversations(context, 3)

        # Preparar contexto de conversación
        conversation_text = "\n".join([
            f"{msg.sender}: {msg.content}"
            for msg in conversation.messages[-5:]  # Últimos 5 mensajes
        ])

        # Generar respuesta usando LLM
        response = llm_service.generate_response(
            conversation_text,
            context,

            response_type
        )

        return response

    def get_conversation_insights(self, conversation: WhatsAppConversation) -> Dict[str, Any]:
        """Obtiene insights detallados de una conversación"""

        # Análisis temporal
        message_times = [msg.timestamp for msg in conversation.messages]

        if message_times:
            time_diffs = [
                (message_times[i] - message_times[i-1]).total_seconds() / 60
                for i in range(1, len(message_times))
            ]
            avg_response_time = sum(time_diffs) / \
                len(time_diffs) if time_diffs else 0
        else:
            avg_response_time = 0

        # Análisis de contenido

        total_chars = sum(len(msg.content) for msg in conversation.messages)
        avg_message_length = total_chars / \
            len(conversation.messages) if conversation.messages else 0

        return {
            "conversation_id": conversation.id,

            "insights": {
                "total_messages": len(conversation.messages),

                "duration_hours": round((conversation.last_activity - conversation.start_date).total_seconds() / 3600, 2),
                "avg_response_time_minutes": round(avg_response_time, 2),
                "avg_message_length": round(avg_message_length, 2),
                "category": conversation.category,
                "sentiment": conversation.sentiment,
                "tags": conversation.tags

            }
        }

    def save_conversations(self, filepath: str):
        """Guarda las conversaciones en un archivo JSON"""
        import json

        data = []
        for conv in self.conversations.values():
            conv_data = {
                "id": conv.id,

                "customer_name": conv.customer_name,
                "customer_phone": conv.customer_phone,
                "start_date": conv.start_date.isoformat(),
                "last_activity": conv.last_activity.isoformat(),
                "status": conv.status,
                "category": conv.category,
                "tags": conv.tags,
                "sentiment": conv.sentiment,

                "messages": [
                    {
                        "timestamp": msg.timestamp.isoformat(),
                        "sender": msg.sender,
                        "content": msg.content,
                        "message_type": msg.message_type
                    }
                    for msg in conv.messages
                ]
            }
            data.append(conv_data)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_conversations(self, filepath: str):
        """Carga conversaciones desde un archivo JSON"""
        import json

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for conv_data in data:
            messages = []
            for msg_data in conv_data["messages"]:
                message = WhatsAppMessage(
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    sender=msg_data["sender"],
                    content=msg_data["content"],
                    message_type=msg_data.get("message_type", "text")
                )
                messages.append(message)

            conversation = WhatsAppConversation(
                id=conv_data["id"],
                customer_phone=conv_data["customer_phone"],
                customer_name=conv_data["customer_name"],
                messages=messages,
                start_date=datetime.fromisoformat(conv_data["start_date"]),
                last_activity=datetime.fromisoformat(
                    conv_data["last_activity"]),
                status=conv_data.get("status", "active"),
                category=conv_data.get("category"),
                tags=conv_data.get("tags", []),
                sentiment=conv_data.get("sentiment")
            )

            self.conversations[conversation.id] = conversation


# Instancia global del analizador
whatsapp_analyzer = WhatsAppAnalyzer()
