"""
Endpoints para análisis de conversaciones de WhatsApp
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.whatsapp_analyzer import whatsapp_analyzer
from services.super_agent import super_agent
from services.tag_persistence import tag_persistence_service
from models.conversation import Conversation, ConversationCreate
from core.db import get_session
from sqlmodel import Session, select
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


class WhatsAppAnalysisRequest(BaseModel):
    conversation_text: str
    customer_id: str


class WhatsAppAnalysisResponse(BaseModel):
    conversation_id: str
    analysis: Dict[str, Any]
    database_saved: bool
    super_agent_processed: bool


@router.post("/analyze", response_model=WhatsAppAnalysisResponse)
async def analyze_whatsapp_conversation(request: WhatsAppAnalysisRequest):
    """Analiza una conversación de WhatsApp y la guarda en la base de datos"""
    try:
        # 1. Analizar la conversación (SIN persistir tags aún)
        analysis_result = whatsapp_analyzer.analyze_conversation_text(
            request.conversation_text,
            request.customer_id
        )

        # 2. Guardar la conversación en la base de datos PRIMERO
        conversation_data = ConversationCreate(
            id=analysis_result["conversation_id"],
            customer_id=request.customer_id,
            category=analysis_result["category"],
            tags=analysis_result["insights"]["tags"],
            sentiment=analysis_result["sentiment"],
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        database_saved = False
        with get_session() as session:
            # Verificar si ya existe
            existing = session.exec(
                select(Conversation).where(
                    Conversation.id == conversation_data.id)
            ).first()

            if not existing:
                conversation = Conversation.from_orm(conversation_data)
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                database_saved = True
                print(
                    f"✅ Conversación guardada en BD con ID: {conversation.id}")
            else:
                database_saved = False
                print(
                    f"⚠️ Conversación ya existe en BD: {conversation_data.id}")

        # 3. AHORA persistir los tags (después de que la conversación existe)
        if database_saved:
            print(f"🔍 DEBUG: Persistiendo tags DESPUÉS de crear conversación...")
            try:
                # Extraer smart_tags del análisis
                smart_tags = []
                if "insights" in analysis_result and "tags" in analysis_result["insights"]:
                    # Convertir tags simples a formato smart_tags
                    for tag_name in analysis_result["insights"]["tags"]:
                        smart_tags.append({
                            "name": tag_name,
                            "category": analysis_result["category"],
                            "type": "llm_generated",
                            "confidence_score": 0.8,
                            "source": "llm_classification",
                            "weight": 0.8,
                            "context": request.conversation_text[:100],
                            "related_tags": []
                        })

                if smart_tags:
                    print(f"🔍 DEBUG: Persistiendo {len(smart_tags)} tags...")
                    from services.tag_persistence import tag_persistence_service
                    tags_persisted = tag_persistence_service.save_tags_to_database(
                        tags=smart_tags,
                        conversation_id=analysis_result["conversation_id"],
                        customer_id=request.customer_id,
                        category=analysis_result["category"]
                    )

                    if tags_persisted:
                        print(
                            f"✅ Tags persistidos exitosamente: {len(smart_tags)} tags")
                    else:
                        print(f"❌ Tags NO se persistieron")
                else:
                    print(f"⚠️ No hay tags para persistir")

            except Exception as e:
                import traceback
                print(f"❌ Error persistiendo tags: {e}")
                print(f"🔍 Traceback: {traceback.format_exc()}")

        # 4. Procesar con el Super Agente
        try:
            super_agent_result = super_agent.process_conversation(
                conversation_data)
            super_agent_processed = True
        except Exception as e:
            print(f"Error en Super Agente: {e}")
            super_agent_processed = False

        return WhatsAppAnalysisResponse(
            conversation_id=analysis_result["conversation_id"],
            analysis=analysis_result,
            database_saved=database_saved,
            super_agent_processed=super_agent_processed
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error analyzing WhatsApp: {str(e)}")


@router.post("/test-tags")
async def test_tags_persistence():
    """Endpoint de prueba para verificar la persistencia de tags"""
    try:
        from services.tag_persistence import tag_persistence_service

        print(f"🧪 DEBUG: Iniciando prueba de persistencia de tags...")
        result = tag_persistence_service.test_persistence()

        if result:
            return {
                "success": True,
                "message": "Prueba de persistencia de tags EXITOSA",
                "details": "Los tags se guardaron correctamente en la BD"
            }
        else:
            return {
                "success": False,
                "message": "Prueba de persistencia de tags FALLÓ",
                "details": "Los tags NO se guardaron en la BD"
            }

    except Exception as e:
        import traceback
        print(f"❌ ERROR en endpoint de prueba: {e}")
        print(f"🔍 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error en prueba de tags: {str(e)}")


@router.get("/conversations")
async def get_conversations():
    """Obtiene todas las conversaciones guardadas en la BD"""
    try:
        with get_session() as session:
            conversations = session.exec(select(Conversation)).all()
            return {
                "success": True,
                "conversations": [
                    {
                        "id": str(conv.id),
                        "customer_profile_id": str(conv.customer_profile_id) if conv.customer_profile_id else None,
                        "category": conv.category,
                        "tags": conv.tags,
                        "sentiment": conv.sentiment,
                        "status": conv.status,
                        "created_at": conv.created_at.isoformat() if conv.created_at else None
                    }
                    for conv in conversations
                ]
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting conversations: {str(e)}")


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Obtiene una conversación específica"""
    try:
        with get_session() as session:
            conversation = session.exec(
                select(Conversation).where(Conversation.id == conversation_id)
            ).first()

            if not conversation:
                raise HTTPException(
                    status_code=404, detail="Conversation not found")

            return {
                "success": True,
                "conversation": {
                    "id": str(conversation.id),
                    "customer_profile_id": str(conversation.customer_profile_id) if conversation.customer_profile_id else None,
                    "category": conversation.category,
                    "tags": conversation.tags,
                    "sentiment": conversation.sentiment,
                    "status": conversation.status,
                    "created_at": conversation.created_at.isoformat() if conversation.created_at else None
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting conversation: {str(e)}")


@router.post("/upload")
async def upload_whatsapp_file(
    file: UploadFile = File(...),
    customer_id: str = Form(...)
):
    """Sube y analiza un archivo de conversación de WhatsApp"""
    try:
        content = await file.read()
        conversation_text = content.decode("utf-8")

        # Analizar y guardar
        result = await analyze_whatsapp_conversation(
            WhatsAppAnalysisRequest(
                conversation_text=conversation_text,
                customer_id=customer_id
            )
        )

        return {
            "success": True,
            "message": "Archivo procesado y guardado exitosamente",
            "result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/tags")
async def get_all_tags():
    """Obtiene todos los tags guardados en la BD"""
    try:
        tags = tag_persistence_service.get_all_tags()
        return {
            "success": True,
            "total_tags": len(tags),
            "tags": tags
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting tags: {str(e)}")


@router.get("/tags/conversation/{conversation_id}")
async def get_conversation_tags(conversation_id: str):
    """Obtiene los tags de una conversación específica"""
    try:
        tags = tag_persistence_service.get_tags_by_conversation(
            conversation_id)
        return {
            "success": True,
            "conversation_id": conversation_id,
            "total_tags": len(tags),
            "tags": tags
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting conversation tags: {str(e)}")


@router.get("/learning-status")
async def get_learning_status():
    """Obtiene el estado del sistema de aprendizaje"""
    try:
        from services.super_agent import super_agent
        from services.agents import available_agents

        # Estado del Super Agente
        super_agent_status = super_agent.get_system_status()

        # Estado de agentes individuales
        agents_status = {}
        for agent_type, agent in available_agents.items():
            agents_status[agent_type] = agent.get_learning_summary()

        # Estado general del aprendizaje
        learning_status = {
            "super_agent": super_agent_status,
            "individual_agents": agents_status,
            "total_learning_agents": len(available_agents),
            "system_learning_active": True,
            "timestamp": datetime.now().isoformat()
        }

        return {
            "success": True,
            "learning_status": learning_status
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@router.post("/force-learning")
async def force_system_learning():
    """Fuerza un ciclo de aprendizaje del sistema"""
    try:
        from services.super_agent import super_agent

        # Forzar ciclo de aprendizaje
        learning_result = super_agent._run_optimization_cycle()

        return {
            "success": True,
            "message": "Ciclo de aprendizaje forzado exitosamente",
            "learning_result": learning_result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@router.get("/super-agent-learnings")
async def get_super_agent_learnings():
    """Obtiene todos los aprendizajes del Super Agente desde la base de datos"""
    try:
        from core.db import get_session
        from models.agent import AgentLearning as AgentLearningModel
        from sqlmodel import select

        with get_session() as session:
            # Buscar todos los aprendizajes del Super Agente
            learnings = session.exec(
                select(AgentLearningModel)
                .where(AgentLearningModel.agent_type == "super_agent")
                .order_by(AgentLearningModel.created_at.desc())
            ).all()

            learning_data = []
            for learning in learnings:
                learning_data.append({
                    "id": learning.id,
                    "agent_type": learning.agent_type,
                    "learning_type": learning.learning_type,
                    "content": learning.content,
                    "confidence_score": learning.confidence_score,
                    "category": learning.category,
                    "metadata": learning.metadata,
                    "created_at": learning.created_at.isoformat() if learning.created_at else None
                })

            return {
                "success": True,
                "total_learnings": len(learning_data),
                "learnings": learning_data,
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        import traceback
        print(f"❌ Error obteniendo aprendizajes del Super Agente: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Verifica el webhook de WhatsApp Business API"""
    try:
        from services.whatsapp_api import whatsapp_api_service

        if hub_mode and hub_verify_token and hub_challenge:
            # Verificación del webhook
            verification_result = whatsapp_api_service.verify_webhook(
                hub_mode, hub_verify_token, hub_challenge)

            if verification_result:
                logger.info("✅ Webhook de WhatsApp verificado correctamente")
                return int(verification_result)
            else:
                logger.warning("❌ Verificación de webhook fallida")
                raise HTTPException(
                    status_code=403, detail="Verification failed")
        else:
            # Parámetros de verificación faltantes
            raise HTTPException(
                status_code=400, detail="Missing verification parameters")

    except Exception as e:
        logger.error(f"❌ Error verificando webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Webhook para recibir mensajes de WhatsApp Business API"""
    try:
        # Obtener el cuerpo del request
        body = await request.json()

        # Verificar si es un mensaje de WhatsApp
        if "entry" in body and "changes" in body["entry"][0]:
            changes = body["entry"][0]["changes"]

            for change in changes:
                if change.get("value") and "messages" in change["value"]:
                    messages = change["value"]["messages"]

                    for message in messages:
                        # Procesar cada mensaje
                        await process_whatsapp_message(message)

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Error en webhook de WhatsApp: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_whatsapp_message(message: dict):
    """Procesa un mensaje individual de WhatsApp"""
    try:
        # Extraer información del mensaje
        phone_number = message.get("from")
        message_text = message.get("text", {}).get("body", "")
        message_id = message.get("id")
        timestamp = message.get("timestamp")

        logger.info(
            f"📱 Mensaje WhatsApp recibido: {phone_number} - {message_text[:50]}...")

        # Crear objeto de conversación
        conversation = Conversation(
            id=str(uuid.uuid4()),
            customer_id=phone_number,  # Usar número de teléfono como ID
            content=message_text,
            source="whatsapp",
            timestamp=datetime.fromtimestamp(int(timestamp)),
            category=None,  # Se determinará automáticamente
            sentiment=None,  # Se determinará automáticamente
            tags=[]
        )

        # Procesar con el SuperAgente
        learning_outcome = super_agent.process_conversation(conversation)

        # Generar respuesta automática
        response = await generate_whatsapp_response(conversation, learning_outcome)

        # Enviar respuesta por WhatsApp
        from services.whatsapp_api import whatsapp_api_service
        whatsapp_api_service.send_text_message(phone_number, response)

        logger.info(f"✅ Mensaje procesado y respondido: {message_id}")

    except Exception as e:
        logger.error(f"❌ Error procesando mensaje WhatsApp: {e}")


async def generate_whatsapp_response(conversation: Conversation, learning_outcome: dict) -> str:
    """Genera una respuesta automática para WhatsApp basada en el aprendizaje"""
    try:
        # Determinar el tipo de respuesta basándose en la categoría
        category = conversation.category or "general"

        if category == "ventas":
            return "¡Hola! Gracias por tu consulta sobre ventas. Nuestro equipo especializado te atenderá en breve. 🛍️"
        elif category == "soporte":
            return "¡Hola! Entiendo que necesitas soporte técnico. Nuestro equipo de asistencia te ayudará pronto. 🔧"
        elif category == "reclamo":
            return "¡Hola! Lamento que hayas tenido una experiencia negativa. Nuestro equipo de atención al cliente se pondrá en contacto contigo. 📞"
        else:
            return "¡Hola! Gracias por contactarnos. Nuestro equipo te atenderá en breve. 😊"

    except Exception as e:
        logger.error(f"❌ Error generando respuesta WhatsApp: {e}")
        return "¡Hola! Gracias por contactarnos. Te responderemos pronto. 😊"


async def send_whatsapp_message(phone_number: str, message: str):
    """Envía un mensaje por WhatsApp Business API"""
    try:
        # Aquí iría la lógica para enviar por WhatsApp Business API
        # Por ahora, solo logueamos
        logger.info(
            f"📤 Enviando mensaje WhatsApp a {phone_number}: {message[:50]}...")

        # TODO: Implementar envío real por WhatsApp Business API
        # Ejemplo de implementación:
        # whatsapp_api.send_message(phone_number, message)

    except Exception as e:
        logger.error(f"❌ Error enviando mensaje WhatsApp: {e}")


@router.post("/send-message")
async def send_whatsapp_message_endpoint(
    phone_number: str,
    message: str
):
    """Envía un mensaje de WhatsApp manualmente"""
    try:
        from services.whatsapp_api import whatsapp_api_service

        success = whatsapp_api_service.send_text_message(phone_number, message)

        if success:
            return {
                "success": True,
                "message": "Mensaje enviado exitosamente",
                "phone_number": phone_number,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error enviando mensaje WhatsApp"
            )

    except Exception as e:
        logger.error(f"❌ Error enviando mensaje: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-template")
async def send_template_message_endpoint(
    phone_number: str,
    template_name: str,
    language_code: str = "es",
    components: list = None
):
    """Envía un mensaje de plantilla por WhatsApp"""
    try:
        from services.whatsapp_api import whatsapp_api_service

        success = whatsapp_api_service.send_template_message(
            phone_number, template_name, language_code, components
        )

        if success:
            return {
                "success": True,
                "message": "Plantilla enviada exitosamente",
                "phone_number": phone_number,
                "template": template_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error enviando plantilla WhatsApp"
            )

    except Exception as e:
        logger.error(f"❌ Error enviando plantilla: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-interactive")
async def send_interactive_message_endpoint(
    phone_number: str,
    message: str,
    buttons: list
):
    """Envía un mensaje interactivo con botones por WhatsApp"""
    try:
        from services.whatsapp_api import whatsapp_api_service

        success = whatsapp_api_service.send_interactive_message(
            phone_number, message, buttons
        )

        if success:
            return {
                "success": True,
                "message": "Mensaje interactivo enviado exitosamente",
                "phone_number": phone_number,
                "buttons": buttons,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error enviando mensaje interactivo WhatsApp"
            )

    except Exception as e:
        logger.error(f"❌ Error enviando mensaje interactivo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/message-status/{message_id}")
async def get_message_status_endpoint(message_id: str):
    """Obtiene el estado de un mensaje enviado"""
    try:
        from services.whatsapp_api import whatsapp_api_service

        status = whatsapp_api_service.get_message_status(message_id)

        if status:
            return {
                "success": True,
                "message_id": message_id,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="Estado del mensaje no encontrado"
            )

    except Exception as e:
        logger.error(f"❌ Error obteniendo estado del mensaje: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-status")
async def get_whatsapp_service_status():
    """Obtiene el estado del servicio de WhatsApp"""
    try:
        from services.whatsapp_api import whatsapp_api_service

        # Verificar configuración
        config_status = {
            "base_url": whatsapp_api_service.base_url,
            "phone_number_id": bool(whatsapp_api_service.phone_number_id),
            "access_token": bool(whatsapp_api_service.access_token),
            "verify_token": whatsapp_api_service.verify_token
        }

        return {
            "success": True,
            "service": "WhatsApp Business API",
            "status": "active" if all(config_status.values()) else "incomplete_config",
            "configuration": config_status,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error obteniendo estado del servicio: {e}")
        raise HTTPException(status_code=500, detail=str(e))
