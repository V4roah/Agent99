from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    """Endpoint de salud del sistema"""
    return {"status": "ok", "version": "2.0.0", "services": ["scraping", "classification", "llm", "whatsapp", "agents"]}


@router.get("/")
def root():
    """Endpoint raíz con información del sistema"""
    return {
        "message": "Agent99 - Sistema Inteligente para Pequeñas Empresas",
        "version": "2.0.0",
        "endpoints": {
            "health": "/health",
            "models": "/models/ollama",
            "classification": "/classify",
            "scraping": "/scrape",
            "llm": "/llm/generate",
            "whatsapp": "/whatsapp/analyze",
            "agents": "/agents/process",
            "vector_search": "/vector/search"
        }
    }
