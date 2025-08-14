from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.llm import llm_service

router = APIRouter(prefix="/llm", tags=["llm"])

class LLMGenerateBody(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7

class WhatsAppAnalysisBody(BaseModel):
    conversation_text: str

@router.post("/generate")
def generate_text(body: LLMGenerateBody):
    """Genera texto usando el LLM local"""
    try:
        response = llm_service.generate(
            body.prompt, 
            body.system_prompt, 
            body.temperature
        )
        return {"generated_text": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")

@router.post("/classify")
def classify_with_llm(body: WhatsAppAnalysisBody):
    """Clasifica texto usando LLM"""
    try:
        categories = ["ventas", "soporte", "reclamo", "consulta", "otro"]
        classification = llm_service.classify_conversation(body.conversation_text, categories)
        return {"classification": classification}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying with LLM: {str(e)}")

@router.post("/extract-entities")
def extract_entities(body: WhatsAppAnalysisBody):
    """Extrae entidades del texto usando LLM"""
    try:
        entities = llm_service.extract_entities(body.conversation_text)
        return {"entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting entities: {str(e)}")
