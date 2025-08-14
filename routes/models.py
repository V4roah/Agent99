from fastapi import APIRouter, HTTPException
from services.llm import llm_service

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/ollama")
def list_ollama_models():
    """Lista los modelos disponibles en Ollama"""
    try:
        models = llm_service.list_models()
        return {"models": models, "current_model": llm_service.model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@router.post("/ollama/switch")
def switch_ollama_model(model_name: str):
    """Cambia el modelo de Ollama"""
    try:
        success = llm_service.switch_model(model_name)
        if success:
            return {"message": f"Modelo cambiado a {model_name}", "current_model": llm_service.model_name}
        else:
            raise HTTPException(status_code=400, detail=f"Modelo {model_name} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error switching model: {str(e)}")
