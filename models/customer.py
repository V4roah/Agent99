"""
Modelo de Perfiles de Clientes
==============================

Almacena información completa de clientes y sus patrones de interacción
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class CustomerProfileBase(SQLModel):
    """Clase base para perfiles de clientes"""
    name: str = Field(description="Nombre completo del cliente")
    email: Optional[str] = Field(default=None, description="Email del cliente")
    phone: Optional[str] = Field(
        default=None, description="Teléfono del cliente")

    # Métricas
    total_conversations: int = Field(default=0)


class CustomerProfile(CustomerProfileBase, table=True):
    """Modelo principal de perfil de cliente"""
    __tablename__ = "customer_profiles"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Timestamps
    last_interaction: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))

    # Relaciones
    conversations: List["Conversation"] = Relationship(
        back_populates="customer_profile")

    def __repr__(self):
        return f"<CustomerProfile(id={self.id}, name={self.name})>"

    def to_dict(self):
        """Convertir modelo a diccionario"""
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'total_conversations': self.total_conversations,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def update_interaction_count(self):
        """Actualizar contador de conversaciones"""
        self.total_conversations += 1
        self.last_interaction = datetime.now(COLOMBIA_TZ)

    def is_recurring_customer(self) -> bool:
        """Verificar si es un cliente recurrente"""
        return self.total_conversations > 1

    def get_phone_without_formatting(self) -> Optional[str]:
        """Obtener teléfono sin formato para comparaciones"""
        if self.phone:
            return self.phone.replace('+', '').replace('-', '').replace(' ', '')
        return None


class CustomerProfileCreate(CustomerProfileBase):
    """Modelo para crear perfiles de clientes"""
    pass


class CustomerProfileUpdate(SQLModel):
    """Modelo para actualizar perfiles de clientes"""
    name: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)


class CustomerProfileRead(CustomerProfileBase):
    """Modelo para leer perfiles de clientes"""
    id: UUID
    last_interaction: Optional[datetime]
    created_at: datetime
    updated_at: datetime
