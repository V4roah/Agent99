"""
Modelos para WhatsApp y análisis de conversaciones
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WhatsAppMessage:
    timestamp: datetime
    sender: str
    content: str
    message_type: str = "text"  # text, image, audio, document, etc.
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class WhatsAppConversation:
    id: str
    customer_phone: str
    customer_name: str
    messages: List[WhatsAppMessage]
    start_date: datetime
    last_activity: datetime
    status: str = "active"  # active, closed, pending
    category: Optional[str] = None
    tags: List[str] = None
    sentiment: Optional[str] = None
