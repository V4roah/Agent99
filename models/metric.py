"""
Modelo de Métricas de Agentes
=============================

Almacena métricas y rendimiento de los agentes
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class AgentMetricsBase(SQLModel):
    """Clase base para métricas de agentes"""
    agent_type: str = Field(description="Tipo de agente (sales, support, complaint)")
    metric_name: str = Field(description="Nombre de la métrica")
    metric_value: float = Field(description="Valor de la métrica")
    metric_unit: Optional[str] = Field(default=None, description="Unidad de la métrica")
    category: Optional[str] = Field(default=None, description="Categoría de la métrica")
    subcategory: Optional[str] = Field(default=None, description="Subcategoría de la métrica")


class AgentMetrics(AgentMetricsBase, table=True):
    """Modelo principal de métricas de agentes"""
    __tablename__ = "agent_metrics"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(COLOMBIA_TZ))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(COLOMBIA_TZ))
    recorded_at: datetime = Field(description="Fecha y hora de la métrica")

    def __repr__(self):
        return f"<AgentMetrics(id={self.id}, agent={self.agent_type})>"


class AgentMetricsCreate(AgentMetricsBase):
    """Modelo para crear métricas de agentes"""
    recorded_at: datetime


class AgentMetricsUpdate(SQLModel):
    """Modelo para actualizar métricas de agentes"""
    agent_type: Optional[str] = Field(default=None)
    metric_name: Optional[str] = Field(default=None)
    metric_value: Optional[float] = Field(default=None)
    metric_unit: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    subcategory: Optional[str] = Field(default=None)


class AgentMetricsRead(AgentMetricsBase):
    """Modelo para leer métricas de agentes"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    recorded_at: datetime
