"""
Modelo de Intenciones de Conversación
====================================

Almacena intenciones extraídas de conversaciones
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class ConversationIntentBase(SQLModel):
    """Clase base para intenciones de conversación"""
    intent_type: str = Field(description="Tipo de intención detectada")
    confidence_score: float = Field(description="Puntuación de confianza (0-1)")
    intent_description: Optional[str] = Field(default=None, description="Descripción de la intención")
    category: Optional[str] = Field(default=None, description="Categoría de la intención")
    subcategory: Optional[str] = Field(default=None, description="Subcategoría de la intención")


class ConversationIntent(ConversationIntentBase, table=True):
    """Modelo principal de intenciones de conversación"""
    __tablename__ = "conversation_intents"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id")

    # Relaciones
    conversation: "Conversation" = Relationship(back_populates="intents")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(COLOMBIA_TZ))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(COLOMBIA_TZ))

    def __repr__(self):
        return f"<ConversationIntent(id={self.id}, type={self.intent_type})>"


class ConversationIntentCreate(ConversationIntentBase):
    """Modelo para crear intenciones de conversación"""
    conversation_id: UUID


class ConversationIntentUpdate(SQLModel):
    """Modelo para actualizar intenciones de conversación"""
    intent_type: Optional[str] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None)
    intent_description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    subcategory: Optional[str] = Field(default=None)


class ConversationIntentRead(ConversationIntentBase):
    """Modelo para leer intenciones de conversación"""
    id: UUID
    conversation_id: UUID
    created_at: datetime
    updated_at: datetime
