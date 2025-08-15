"""
Modelo de Aprendizaje de Agentes
================================

Almacena aprendizajes y patrones de los agentes
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID, uuid4
import pytz
from sqlalchemy import JSON, Column

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class AgentLearningBase(SQLModel):
    """Clase base para aprendizajes de agentes"""
    agent_type: str = Field(
        description="Tipo de agente (sales, support, complaint)")
    learning_type: str = Field(description="Tipo de aprendizaje")
    content: str = Field(description="Contenido del aprendizaje")
    confidence_score: float = Field(
        description="Puntuación de confianza (0-1)")
    category: Optional[str] = Field(
        default=None, description="Categoría del aprendizaje")
    subcategory: Optional[str] = Field(
        default=None, description="Subcategoría del aprendizaje")


class AgentLearning(AgentLearningBase, table=True):
    """Modelo principal de aprendizajes de agentes"""
    __tablename__ = "agent_learnings"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))
    last_used: Optional[datetime] = Field(
        default=None, description="Última vez que se usó")

    def __repr__(self):
        return f"<AgentLearning(id={self.id}, agent={self.agent_type})>"


class AgentLearningCreate(AgentLearningBase):
    """Modelo para crear aprendizajes de agentes"""
    pass


class AgentLearningUpdate(SQLModel):
    """Modelo para actualizar aprendizajes de agentes"""
    agent_type: Optional[str] = Field(default=None)
    learning_type: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    confidence_score: Optional[float] = Field(default=None)
    category: Optional[str] = Field(default=None)
    subcategory: Optional[str] = Field(default=None)


class AgentLearningRead(AgentLearningBase):
    """Modelo para leer aprendizajes de agentes"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime]


class SuperAgentModel(SQLModel, table=True):
    """Modelo para el Super Agente en la base de datos"""
    __tablename__ = "super_agents"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(description="Nombre del Super Agente")
    version: str = Field(description="Versión del Super Agente")

    # Estado del sistema
    status: str = Field(default="active", description="Estado del agente")
    is_learning: bool = Field(
        default=False, description="Si está en modo aprendizaje")

    # Métricas del sistema
    total_conversations_processed: int = Field(
        default=0, description="Total de conversaciones procesadas")
    total_learnings_generated: int = Field(
        default=0, description="Total de aprendizajes generados")
    success_rate: float = Field(
        default=0.0, description="Tasa de éxito del agente")

    # Configuración de aprendizaje
    learning_threshold: float = Field(
        default=0.7, description="Umbral de confianza para aprendizaje")
    optimization_frequency_hours: int = Field(
        default=24, description="Frecuencia de optimización en horas")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(
        COLOMBIA_TZ), description="Fecha de creación")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(
        COLOMBIA_TZ), description="Fecha de última actualización")
    last_learning_cycle: Optional[datetime] = Field(
        default=None, description="Último ciclo de aprendizaje")
    last_optimization: Optional[datetime] = Field(
        default=None, description="Última optimización")
    agent_metadata: Optional[Any] = Field(
        default=None, sa_column=Column(JSON), description="Metadatos del agente")

    def __repr__(self):
        return f"<SuperAgent(id={self.id}, name={self.name}, version={self.version})>"


class SuperAgentCreate(SQLModel):
    """Modelo para crear un Super Agente"""
    name: str
    version: str
    learning_threshold: float = 0.7
    optimization_frequency_hours: int = 24


class SuperAgentUpdate(SQLModel):
    """Modelo para actualizar un Super Agente"""
    status: Optional[str] = None
    is_learning: Optional[bool] = None
    total_conversations_processed: Optional[int] = None
    total_learnings_generated: Optional[int] = None
    success_rate: Optional[float] = None
    learning_threshold: Optional[float] = None
    optimization_frequency_hours: Optional[int] = None
    last_optimization: Optional[datetime] = None
    last_learning_cycle: Optional[datetime] = None
    agent_metadata: Optional[Any] = Field(default=None, sa_column=Column(JSON))
