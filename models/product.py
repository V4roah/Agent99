"""
Modelo de Inventario de Productos
=================================

Almacena información de productos del inventario
Siguiendo la estructura de milla99-backend con SQLModel
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


class ProductInventoryBase(SQLModel):
    """Clase base para inventario de productos"""
    name: str = Field(description="Nombre del producto")
    description: Optional[str] = Field(
        default=None, description="Descripción del producto")
    category: Optional[str] = Field(
        default=None, description="Categoría del producto")
    price: Optional[Decimal] = Field(
        default=None, description="Precio del producto")
    stock_quantity: int = Field(
        default=0, description="Cantidad disponible en stock")


class ProductInventory(ProductInventoryBase, table=True):
    """Modelo principal de inventario de productos"""
    __tablename__ = "product_inventory"

    # Identificación
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Timestamps
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(COLOMBIA_TZ))


class ProductInventoryCreate(ProductInventoryBase):
    """Modelo para crear productos en el inventario"""
    pass


class ProductInventoryUpdate(SQLModel):
    """Modelo para actualizar productos en el inventario"""
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    price: Optional[Decimal] = Field(default=None)
    stock_quantity: Optional[int] = Field(default=None)


class ProductInventoryRead(ProductInventoryBase):
    """Modelo para leer productos del inventario"""
    id: UUID
    last_updated: datetime
    created_at: datetime
