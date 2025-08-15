"""
Endpoints para análisis de conversaciones de WhatsApp
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
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
