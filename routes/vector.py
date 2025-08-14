from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from services.vector_store import vector_store, VectorItem
import uuid

router = APIRouter(prefix="/vector", tags=["vector"])

class VectorSearchBody(BaseModel):
    query: str
    k: int = 5

@router.post("/search")
def vector_search(body: VectorSearchBody):
    """Busca en el vector store"""
    try:
        results = vector_store.search(body.query, body.k)
        return {"query": body.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching vector store: {str(e)}")

@router.post("/add")
def add_to_vector_store(text: str, metadata: Dict[str, Any]):
    """Añade un item al vector store"""
    try:
        item = VectorItem(
            id=str(uuid.uuid4()),
            text=text,
            metadata=metadata
        )
        
        item_id = vector_store.add_item(item)
        vector_store.save_index()
        
        return {"item_id": item_id, "message": "Item añadido al vector store"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding to vector store: {str(e)}")

@router.get("/stats")
def get_vector_store_stats():
    """Obtiene estadísticas del vector store"""
    try:
        return {
            "total_items": len(vector_store.items),
            "dimension": vector_store.dimension,
            "model_name": vector_store.model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting vector store stats: {str(e)}")
