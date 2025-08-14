from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from services.whatsapp_analyzer import whatsapp_analyzer

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

class WhatsAppAnalysisBody(BaseModel):
    conversation_text: str

@router.post("/analyze")
def analyze_whatsapp(body: WhatsAppAnalysisBody):
    """Analiza una conversación de WhatsApp"""
    try:
        # Parsear la conversación
        conversations = whatsapp_analyzer.parse_whatsapp_export(body.conversation_text)
        
        if not conversations:
            return {"message": "No se encontraron conversaciones válidas", "conversations": []}
        
        # Analizar la primera conversación
        conversation = conversations[0]
        analysis = whatsapp_analyzer.analyze_conversation(conversation)
        
        return {
            "conversation_id": conversation.id,
            "analysis": analysis,
            "insights": whatsapp_analyzer.get_conversation_insights(conversation)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing WhatsApp: {str(e)}")

@router.post("/upload")
async def upload_whatsapp_export(file: UploadFile = File(...)):
    """Sube y analiza un archivo de export de WhatsApp"""
    try:
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Solo se aceptan archivos .txt")
        
        content = await file.read()
        conversation_text = content.decode('utf-8')
        
        # Analizar conversaciones
        conversations = whatsapp_analyzer.parse_whatsapp_export(conversation_text)
        
        if not conversations:
            return {"message": "No se encontraron conversaciones válidas", "conversations": []}
        
        # Analizar todas las conversaciones
        results = []
        for conversation in conversations:
            analysis = whatsapp_analyzer.analyze_conversation(conversation)
            insights = whatsapp_analyzer.get_conversation_insights(conversation)
            
            results.append({
                "conversation_id": conversation.id,
                "customer_name": conversation.customer_name,
                "analysis": analysis,
                "insights": insights
            })
        
        return {
            "total_conversations": len(conversations),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/conversations")
def get_conversations():
    """Obtiene todas las conversaciones analizadas"""
    try:
        conversations = list(whatsapp_analyzer.conversations.values())
        return {
            "total": len(conversations),
            "conversations": [
                {
                    "id": conv.id,
                    "customer_name": conv.customer_name,
                    "category": conv.category,
                    "sentiment": conv.sentiment,
                    "message_count": len(conv.messages),
                    "start_date": conv.start_date.isoformat(),
                    "last_activity": conv.last_activity.isoformat()
                }
                for conv in conversations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversations: {str(e)}")
