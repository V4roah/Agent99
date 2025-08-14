"""
Endpoints para el sistema de tagging inteligente
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.smart_tagging import smart_tagging_service

router = APIRouter(prefix="/tagging", tags=["tagging"])


class TaggingRequest(BaseModel):
    text: str
    category: Optional[str] = None
    max_tags: Optional[int] = 8


class TagSuggestionRequest(BaseModel):
    partial_tag: str
    category: Optional[str] = None


@router.post("/generate")
async def generate_smart_tags(request: TaggingRequest):
    """Genera etiquetas inteligentes para un texto"""
    try:
        tags = smart_tagging_service.generate_smart_tags(
            text=request.text,
            category=request.category,
            max_tags=request.max_tags
        )
        
        return {
            "success": True,
            "text": request.text,
            "category": request.category,
            "tags_generated": len(tags),
            "tags": tags
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error generando etiquetas: {str(e)}"
        )


@router.post("/suggest")
async def suggest_tags(request: TagSuggestionRequest):
    """Sugiere etiquetas basadas en entrada parcial"""
    try:
        suggestions = smart_tagging_service.suggest_tags(
            partial_tag=request.partial_tag,
            category=request.category
        )
        
        return {
            "success": True,
            "partial_tag": request.partial_tag,
            "category": request.category,
            "suggestions_count": len(suggestions),
            "suggestions": suggestions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error sugiriendo etiquetas: {str(e)}"
        )


@router.get("/statistics")
async def get_tag_statistics():
    """Obtiene estadísticas del sistema de etiquetas"""
    try:
        stats = smart_tagging_service.get_tag_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.get("/categories")
async def get_tag_categories():
    """Obtiene todas las categorías de etiquetas disponibles"""
    try:
        categories = smart_tagging_service.predefined_tags
        
        return {
            "success": True,
            "categories_count": len(categories),
            "categories": categories
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error obteniendo categorías: {str(e)}"
        )


@router.get("/tags/{category}")
async def get_tags_by_category(category: str):
    """Obtiene todas las etiquetas de una categoría específica"""
    try:
        if category not in smart_tagging_service.predefined_tags:
            raise HTTPException(
                status_code=404, 
                detail=f"Categoría '{category}' no encontrada"
            )
        
        tags = smart_tagging_service.predefined_tags[category]
        
        return {
            "success": True,
            "category": category,
            "tags_count": len(tags),
            "tags": tags
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error obteniendo etiquetas: {str(e)}"
        )


@router.get("/search")
async def search_tags(
    query: str = Query(..., description="Texto para buscar etiquetas"),
    category: Optional[str] = Query(None, description="Categoría específica"),
    max_results: int = Query(10, description="Máximo número de resultados")
):
    """Busca etiquetas que coincidan con una consulta"""
    try:
        # Generar etiquetas para la consulta
        tags = smart_tagging_service.generate_smart_tags(
            text=query,
            category=category,
            max_tags=max_results
        )
        
        return {
            "success": True,
            "query": query,
            "category": category,
            "results_count": len(tags),
            "results": tags
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error buscando etiquetas: {str(e)}"
        )
