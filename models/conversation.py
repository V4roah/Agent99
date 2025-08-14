"""
Modelo de Conversaciones
========================

Almacena conversaciones de WhatsApp analizadas
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class ConversationBase(SQLModel):
    """Clase base para conversaciones"""
    conversation_id: str = Field(description="ID único de la conversación")
    customer_name: str = Field(description="Nombre del cliente")
    phone_number: str = Field(description="Número de teléfono del cliente")
    conversation_text: str = Field(
        description="Texto completo de la conversación")
    message_count: int = Field(description="Número total de mensajes")
    conversation_date: datetime = Field(description="Fecha de la conversación")
    intent_classified: Optional[str] = Field(
        default=None, description="Intención clasificada")
    sentiment_score: Optional[float] = Field(
        default=None, description="Puntuación de sentimiento")
    priority_level: Optional[str] = Field(
        default=None, description="Nivel de prioridad")


class Conversation(ConversationBase, table=True):
    """Modelo principal de conversaciones"""
    __tablename__ = "conversations"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Clave foránea para CustomerProfile
    customer_profile_id: Optional[UUID] = Field(
        default=None, foreign_key="customer_profiles.id")

    # Relaciones
    customer_profile: Optional["CustomerProfile"] = Relationship(
        back_populates="conversations")
    intents: List["ConversationIntent"] = Relationship(
        back_populates="conversation")

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))

    def __repr__(self):
        return f"<Conversation(id={self.id}, customer={self.customer_name})>"


class ConversationCreate(ConversationBase):
    """Modelo para crear conversaciones"""
    customer_profile_id: Optional[UUID] = None


class ConversationUpdate(SQLModel):
    """Modelo para actualizar conversaciones"""
    conversation_id: Optional[str] = Field(default=None)
    customer_name: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    conversation_text: Optional[str] = Field(default=None)
    message_count: Optional[int] = Field(default=None)
    conversation_date: Optional[datetime] = Field(default=None)
    intent_classified: Optional[str] = Field(default=None)
    sentiment_score: Optional[float] = Field(default=None)
    priority_level: Optional[str] = Field(default=None)
    customer_profile_id: Optional[UUID] = Field(default=None)


class ConversationRead(ConversationBase):
    """Modelo para leer conversaciones"""
    id: UUID
    customer_profile_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
