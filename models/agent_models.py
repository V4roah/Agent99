"""
Modelos para los agentes del sistema
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentAction:
    agent_id: str
    action_type: str  # classify, respond, escalate, learn
    timestamp: datetime
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentMemory:
    agent_id: str
    conversation_id: str
    key_insights: List[str]
    successful_patterns: List[str]
    failed_patterns: List[str]
    customer_preferences: Dict[str, Any]
    last_updated: datetime
