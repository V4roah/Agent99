"""
Modelo de Aprendizaje de Agentes
================================

Almacena aprendizajes y patrones de los agentes
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class AgentLearningBase(SQLModel):
    """Clase base para aprendizajes de agentes"""
    agent_type: str = Field(description="Tipo de agente (sales, support, complaint)")
    learning_type: str = Field(description="Tipo de aprendizaje")
    content: str = Field(description="Contenido del aprendizaje")
    confidence_score: float = Field(description="Puntuación de confianza (0-1)")
    category: Optional[str] = Field(default=None, description="Categoría del aprendizaje")
    subcategory: Optional[str] = Field(default=None, description="Subcategoría del aprendizaje")


class AgentLearning(AgentLearningBase, table=True):
    """Modelo principal de aprendizajes de agentes"""
    __tablename__ = "agent_learnings"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(COLOMBIA_TZ))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(COLOMBIA_TZ))
    last_used: Optional[datetime] = Field(default=None, description="Última vez que se usó")

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
