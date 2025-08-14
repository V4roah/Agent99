"""
Modelos para el almacenamiento de vectores
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class VectorItem:
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
