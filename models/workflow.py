"""
Modelo de Ejecución de Flujos de Trabajo
=========================================

Almacena ejecuciones de flujos de trabajo automatizados
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class WorkflowExecutionBase(SQLModel):
    """Clase base para ejecuciones de flujos de trabajo"""
    workflow_name: str = Field(description="Nombre del flujo de trabajo")
    workflow_type: str = Field(description="Tipo de flujo de trabajo")
    status: str = Field(description="Estado de la ejecución")
    trigger_type: Optional[str] = Field(
        default=None, description="Tipo de disparador")
    priority: Optional[str] = Field(
        default=None, description="Prioridad del flujo")


class WorkflowExecution(WorkflowExecutionBase, table=True):
    """Modelo principal de ejecuciones de flujos de trabajo"""
    __tablename__ = "workflow_executions"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Timestamps
    started_at: datetime = Field(description="Fecha y hora de inicio")
    completed_at: Optional[datetime] = Field(
        default=None, description="Fecha y hora de finalización")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))

    def __repr__(self):
        return f"<WorkflowExecution(id={self.id}, workflow={self.workflow_name})>"


class WorkflowExecutionCreate(WorkflowExecutionBase):
    """Modelo para crear ejecuciones de flujos de trabajo"""
    started_at: datetime


class WorkflowExecutionUpdate(SQLModel):
    """Modelo para actualizar ejecuciones de flujos de trabajo"""
    workflow_name: Optional[str] = Field(default=None)
    workflow_type: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    trigger_type: Optional[str] = Field(default=None)
    priority: Optional[str] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


class WorkflowExecutionRead(WorkflowExecutionBase):
    """Modelo para leer ejecuciones de flujos de trabajo"""
    id: UUID
    started_at: datetime
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
