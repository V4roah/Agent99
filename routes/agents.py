from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.agents import agent_manager
from models.whatsapp import WhatsAppConversation, WhatsAppMessage
from datetime import datetime

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentProcessBody(BaseModel):
    conversation_text: str
    customer_name: str
    context: Optional[str] = ""


@router.post("/process")
def process_with_agents(body: AgentProcessBody):
    """Procesa una conversación usando el sistema de agentes"""
    try:
        # Crear una conversación temporal para el procesamiento
        # Crear mensaje temporal
        temp_message = WhatsAppMessage(
            timestamp=datetime.now(),
            sender=body.customer_name,
            content=body.conversation_text
        )

        # Crear conversación temporal
        temp_conversation = WhatsAppConversation(
            id="temp_" + str(datetime.now().timestamp()),
            customer_phone="",
            customer_name=body.customer_name,
            messages=[temp_message],
            start_date=datetime.now(),
            last_activity=datetime.now()
        )

        # Procesar con agentes
        result = agent_manager.route_WhatsAppConversation(temp_conversation)

        return {
            "conversation_id": temp_conversation.id,
            "agent_result": result,
            "suggested_response": result.get("response", "")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing with agents: {str(e)}")


@router.get("/performance")
def get_agent_performance():
    """Obtiene métricas de rendimiento de todos los agentes"""
    try:
        performance = agent_manager.get_agent_performance()
        return {"agent_performance": performance}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting agent performance: {str(e)}")
