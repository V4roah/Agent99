"""
Agent 99 - Modelos del Sistema
==============================

Este módulo define las clases y estructuras de datos principales usando SQLModel
El orden de las importaciones es importante para la creación de las tablas en la base de datos
Las tablas se crean en el orden en que se importan sus modelos
Las tablas con claves foráneas deben importarse después de las tablas que referencian
"""

# Modelos base (sin dependencias)
from .customer import CustomerProfile, CustomerProfileCreate, CustomerProfileUpdate, CustomerProfileRead
from .product import ProductInventory, ProductInventoryCreate, ProductInventoryUpdate, ProductInventoryRead

# Modelos con dependencias (después de los base)
from .conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationRead
from .intent import ConversationIntent, ConversationIntentCreate, ConversationIntentUpdate, ConversationIntentRead
from .agent import AgentLearning, AgentLearningCreate, AgentLearningUpdate, AgentLearningRead
from .metric import AgentMetrics, AgentMetricsCreate, AgentMetricsUpdate, AgentMetricsRead
from .workflow import WorkflowExecution, WorkflowExecutionCreate, WorkflowExecutionUpdate, WorkflowExecutionRead

# Modelos de servicios (dataclasses)
from .whatsapp import WhatsAppMessage, WhatsAppConversation
from .vector import VectorItem
from .agent_models import AgentAction, AgentMemory

# Modelos de tags
from .tag import Tag, TagUsage, TagCategory, TagCreate, TagUpdate, TagRead, TagUsageCreate, TagUsageRead

__all__ = [
    # Customer models
    'CustomerProfile', 'CustomerProfileCreate', 'CustomerProfileUpdate', 'CustomerProfileRead',

    # Product models
    'ProductInventory', 'ProductInventoryCreate', 'ProductInventoryUpdate', 'ProductInventoryRead',

    # Conversation models
    'Conversation', 'ConversationCreate', 'ConversationUpdate', 'ConversationRead',

    # Intent models
    'ConversationIntent', 'ConversationIntentCreate', 'ConversationIntentUpdate', 'ConversationIntentRead',

    # Agent models
    'AgentLearning', 'AgentLearningCreate', 'AgentLearningUpdate', 'AgentLearningRead',

    # Metric models
    'AgentMetrics', 'AgentMetricsCreate', 'AgentMetricsUpdate', 'AgentMetricsRead',

    # Workflow models
    'WorkflowExecution', 'WorkflowExecutionCreate', 'WorkflowExecutionUpdate', 'WorkflowExecutionRead',

    # WhatsApp models
    'WhatsAppMessage', 'WhatsAppConversation',

    # Vector models
    'VectorItem',

    # Agent action models
    'AgentAction', 'AgentMemory',

    # Tag models
    'Tag', 'TagUsage', 'TagCategory', 'TagCreate', 'TagUpdate', 'TagRead', 'TagUsageCreate', 'TagUsageRead'
]
