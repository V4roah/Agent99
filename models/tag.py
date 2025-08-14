"""
Modelo para gestión de tags en la base de datos
"""
from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel
import json


class Tag(SQLModel, table=True):
    """Modelo de tag individual"""
    __tablename__ = "tags"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    category: str = Field(index=True)
    tag_type: str = Field(default="keyword")  # keyword, semantic, ml_generated
    confidence_score: float = Field(default=0.0)
    source: str = Field(default="smart_tagging")  # smart_tagging, manual, llm
    weight: float = Field(default=1.0)
    context: Optional[str] = Field(default=None)
    related_tags_json: Optional[str] = Field(
        default=None)  # JSON string para List[str]
    usage_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def related_tags(self) -> List[str]:
        """Obtiene la lista de tags relacionados desde JSON"""
        if self.related_tags_json:
            try:
                return json.loads(self.related_tags_json)
            except:
                return []
        return []

    @related_tags.setter
    def related_tags(self, value: List[str]):
        """Establece la lista de tags relacionados como JSON"""
        if value:
            self.related_tags_json = json.dumps(value)
        else:
            self.related_tags_json = None


class TagUsage(SQLModel, table=True):
    """Modelo para rastrear uso de tags en conversaciones"""
    __tablename__ = "tag_usage"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", index=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    customer_id: Optional[UUID] = Field(
        default=None, foreign_key="customer_profiles.id", index=True)
    usage_context: Optional[str] = Field(default=None)
    confidence_score: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.now)


class TagCategory(SQLModel, table=True):
    """Modelo para categorías de tags"""
    __tablename__ = "tag_categories"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = Field(default=None)
    parent_category: Optional[str] = Field(default=None)
    color: Optional[str] = Field(default="#007bff")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)


# Modelos Pydantic para API
class TagCreate(BaseModel):
    name: str
    category: str
    tag_type: str = "keyword"
    confidence_score: float = 0.0
    source: str = "smart_tagging"
    weight: float = 1.0
    context: Optional[str] = None
    related_tags: Optional[List[str]] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    tag_type: Optional[str] = None
    confidence_score: Optional[float] = None
    source: Optional[str] = None
    weight: Optional[float] = None
    context: Optional[str] = None
    related_tags: Optional[List[str]] = None


class TagRead(BaseModel):
    id: UUID
    name: str
    category: str
    tag_type: str
    confidence_score: float
    source: str
    weight: float
    context: Optional[str]
    related_tags: List[str]
    usage_count: int
    created_at: datetime
    updated_at: datetime


class TagUsageCreate(BaseModel):
    tag_id: UUID
    conversation_id: UUID
    customer_id: Optional[UUID] = None
    usage_context: Optional[str] = None
    confidence_score: float = 0.0


class TagUsageRead(BaseModel):
    id: UUID
    tag_id: UUID
    conversation_id: UUID
    customer_id: Optional[UUID]
    usage_context: Optional[str]
    confidence_score: float
    created_at: datetime
