"""
Endpoints para el Super Agente - Cerebro Central del Sistema
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.super_agent import super_agent
from models.conversation import Conversation

router = APIRouter(prefix="/super-agent", tags=["super-agent"])


class ConversationRequest(BaseModel):
    conversation_id: str
    customer_id: str
    category: str
    tags: List[str] = []
    content: str


@router.post("/process")
async def process_conversation_with_super_agent(request: ConversationRequest):
    """Procesa una conversación usando el Super Agente"""
    try:
        # Crear objeto de conversación
        conversation = Conversation(
            id=request.conversation_id,
            customer_id=request.customer_id,
            category=request.category,
            tags=request.tags,
            content=request.content
        )

        # Procesar con Super Agente
        result = super_agent.process_conversation(conversation)

        return {
            "success": True,
            "conversation_id": request.conversation_id,
            "super_agent_result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando con Super Agente: {str(e)}"
        )


@router.get("/status")
async def get_super_agent_status():
    """Obtiene el estado completo del Super Agente"""
    try:
        status = super_agent.get_system_status()

        return {
            "success": True,
            "status": status
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado: {str(e)}"
        )


@router.get("/insights")
async def get_business_insights():
    """Obtiene insights de negocio del Super Agente"""
    try:
        insights = super_agent.get_business_insights()

        return {
            "success": True,
            "insights": insights
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo insights: {str(e)}"
        )


@router.post("/optimize")
async def trigger_optimization_cycle():
    """Dispara manualmente un ciclo de optimización"""
    try:
        # Ejecutar ciclo de optimización
        super_agent._run_optimization_cycle()

        return {
            "success": True,
            "message": "Ciclo de optimización ejecutado manualmente",
            "optimization_count": super_agent.optimization_count
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando optimización: {str(e)}"
        )


@router.get("/memory")
async def get_global_memory():
    """Obtiene la memoria global del Super Agente"""
    try:
        memory = super_agent.global_memory

        return {
            "success": True,
            "memory": memory
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo memoria: {str(e)}"
        )


@router.get("/metrics")
async def get_aggregated_metrics():
    """Obtiene métricas agregadas del sistema"""
    try:
        metrics = super_agent.aggregated_metrics

        return {
            "success": True,
            "metrics": metrics
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo métricas: {str(e)}"
        )


@router.get("/learning-cycles")
async def get_learning_cycles():
    """Obtiene el historial de ciclos de aprendizaje"""
    try:
        cycles = super_agent.global_memory["learning_cycles"]

        return {
            "success": True,
            "total_cycles": len(cycles),
            "cycles": cycles
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo ciclos de aprendizaje: {str(e)}"
        )


@router.get("/optimization-history")
async def get_optimization_history():
    """Obtiene el historial de optimizaciones"""
    try:
        history = super_agent.global_memory["optimization_history"]

        return {
            "success": True,
            "total_optimizations": len(history),
            "history": history
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial de optimizaciones: {str(e)}"
        )


@router.post("/reset-memory")
async def reset_global_memory():
    """Resetea la memoria global del Super Agente (solo para desarrollo)"""
    try:
        # Resetear memoria
        super_agent.global_memory = {
            "customer_patterns": {},
            "conversation_trends": {},
            "agent_performance": {},
            "business_insights": {},
            "learning_cycles": [],
            "optimization_history": []
        }

        # Resetear métricas
        super_agent.aggregated_metrics = {
            "total_conversations": 0,
            "success_rate": 0.0,
            "average_response_time": 0.0,
            "customer_satisfaction": 0.0,
            "conversion_rate": 0.0
        }

        return {
            "success": True,
            "message": "Memoria global reseteada",
            "timestamp": super_agent.creation_date.isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reseteando memoria: {str(e)}"
        )
