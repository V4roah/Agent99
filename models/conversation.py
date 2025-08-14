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
import json

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class ConversationBase(SQLModel):
    """Clase base para conversaciones"""
    category: Optional[str] = Field(
        default=None, description="Categoría de la conversación")
    tags_json: Optional[str] = Field(
        default=None, description="Tags generados por ML (JSON)")
    sentiment: Optional[str] = Field(
        default=None, description="Sentimiento de la conversación")
    status: str = Field(
        default="active", description="Estado de la conversación")
    message_count: int = Field(
        default=0, description="Número total de mensajes")
    duration_hours: Optional[float] = Field(
        default=None, description="Duración en horas")
    avg_response_time_minutes: Optional[float] = Field(
        default=None, description="Tiempo promedio de respuesta")
    avg_message_length: Optional[float] = Field(
        default=None, description="Longitud promedio de mensajes")

    @property
    def tags(self) -> List[str]:
        """Obtiene la lista de tags desde JSON"""
        if self.tags_json:
            try:
                return json.loads(self.tags_json)
            except:
                return []
        return []

    @tags.setter
    def tags(self, value: List[str]):
        """Establece la lista de tags como JSON"""
        if value:
            self.tags_json = json.dumps(value)
        else:
            self.tags_json = None


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
        return f"<Conversation(id={self.id}, customer_profile_id={self.customer_profile_id})>"


class ConversationCreate(SQLModel):
    """Modelo para crear conversaciones"""
    id: Optional[UUID] = None
    customer_id: str
    customer_profile_id: Optional[UUID] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    sentiment: Optional[str] = None
    status: str = "active"
    message_count: int = 0
    duration_hours: Optional[float] = None
    avg_response_time_minutes: Optional[float] = None
    avg_message_length: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConversationUpdate(SQLModel):
    """Modelo para actualizar conversaciones"""
    customer_id: Optional[str] = Field(default=None)
    customer_profile_id: Optional[UUID] = Field(default=None)
    category: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    sentiment: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    message_count: Optional[int] = Field(default=None)
    duration_hours: Optional[float] = Field(default=None)
    avg_response_time_minutes: Optional[float] = Field(default=None)
    avg_message_length: Optional[float] = Field(default=None)


class ConversationRead(SQLModel):
    """Modelo para leer conversaciones"""
    id: UUID
    customer_id: str
    customer_profile_id: Optional[UUID]
    category: Optional[str]
    tags: List[str]
    sentiment: Optional[str]
    status: str
    message_count: int
    duration_hours: Optional[float]
    avg_response_time_minutes: Optional[float]
    avg_message_length: Optional[float]
    created_at: datetime
    updated_at: datetime
