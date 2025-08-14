"""
Servicio de Tagging Inteligente usando Machine Learning
"""
from typing import List, Dict, Any, Optional, Tuple
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import re
from collections import Counter
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartTaggingService:
    """Servicio inteligente de etiquetado usando ML"""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        self.embedding_model = embedding_model
        self.encoder = None
        self.tfidf_vectorizer = None
        self.tag_clusters = {}
        self.predefined_tags = self._load_predefined_tags()
        self.tag_synonyms = self._load_tag_synonyms()

        # Inicializar modelos
        self._initialize_models()

    def _initialize_models(self):
        """Inicializa los modelos de ML"""
        try:
            # Inicializar encoder de embeddings
            self.encoder = SentenceTransformer(self.embedding_model)
            logger.info(f"✅ Encoder inicializado: {self.embedding_model}")

            # Inicializar vectorizador TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            logger.info("✅ TF-IDF vectorizador inicializado")

        except Exception as e:
            logger.error(f"❌ Error inicializando modelos: {e}")
            self.encoder = None
            self.tfidf_vectorizer = None

    def _load_predefined_tags(self) -> Dict[str, List[str]]:
        """Carga etiquetas predefinidas por categoría"""
        return {
            "ventas": [
                "compra", "producto", "precio", "oferta", "descuento", "cotización",
                "características", "garantía", "entrega", "pago", "financiamiento",
                "comparación", "recomendación", "stock", "disponibilidad"
            ],
            "soporte": [
                "problema", "error", "falla", "ayuda", "solución", "técnico",
                "configuración", "instalación", "actualización", "manual", "tutorial",
                "compatibilidad", "rendimiento", "optimización", "backup"
            ],
            "quejas": [
                "reclamo", "insatisfacción", "problema", "reembolso", "devolución",
                "calidad", "servicio", "atención", "tiempo", "espera", "cancelación",
                "facturación", "cobro", "garantía", "daño"
            ],
            "consulta": [
                "información", "duda", "pregunta", "ayuda", "orientación",
                "horarios", "ubicación", "contacto", "políticas", "procedimientos",
                "documentación", "requisitos", "proceso", "estado"
            ],
            "producto": [
                "especificaciones", "características", "funcionalidades", "beneficios",
                "aplicaciones", "casos_uso", "alternativas", "versiones", "actualizaciones",
                "compatibilidad", "requisitos", "instalación", "configuración"
            ]
        }

    def _load_tag_synonyms(self) -> Dict[str, List[str]]:
        """Carga sinónimos de etiquetas"""
        return {
            "compra": ["buy", "purchase", "adquirir", "obtener"],
            "producto": ["item", "artículo", "merchandise", "goods"],
            "precio": ["cost", "valor", "tarifa", "costo"],
            "problema": ["issue", "trouble", "inconveniente", "dificultad"],
            "ayuda": ["help", "assistance", "soporte", "apoyo"],
            "solución": ["solution", "fix", "resolución", "remedio"],
            "reclamo": ["complaint", "claim", "queja", "protesta"],
            "información": ["info", "data", "datos", "detalles"]
        }

    def generate_smart_tags(self, text: str, category: str = None,
                            max_tags: int = 8) -> List[Dict[str, Any]]:
        """Genera etiquetas inteligentes para un texto"""
        try:
            # 1. Extraer etiquetas basadas en palabras clave
            keyword_tags = self._extract_keyword_tags(text)

            # 2. Generar etiquetas semánticas
            semantic_tags = self._generate_semantic_tags(text, max_tags // 2)

            # 3. Combinar y priorizar etiquetas
            all_tags = keyword_tags + semantic_tags
            prioritized_tags = self._prioritize_tags(
                all_tags, category, max_tags)

            # 4. Agregar metadatos
            enhanced_tags = self._enhance_tags(prioritized_tags, text)

            logger.info(
                f"✅ Generadas {len(enhanced_tags)} etiquetas inteligentes")
            return enhanced_tags

        except Exception as e:
            logger.error(f"❌ Error generando etiquetas: {e}")
            return self._fallback_tags(category, max_tags)

    def _extract_keyword_tags(self, text: str) -> List[Dict[str, Any]]:
        """Extrae etiquetas basadas en palabras clave"""
        tags = []
        text_lower = text.lower()

        # Buscar etiquetas predefinidas en el texto
        for category, category_tags in self.predefined_tags.items():
            for tag in category_tags:
                if tag.lower() in text_lower:
                    tags.append({
                        "name": tag,
                        "category": category,
                        "type": "keyword",
                        "confidence": 0.8,
                        "source": "predefined"
                    })

        # Buscar sinónimos
        for tag, synonyms in self.tag_synonyms.items():
            for synonym in synonyms:
                if synonym.lower() in text_lower:
                    tags.append({
                        "name": tag,
                        "category": self._get_tag_category(tag),
                        "type": "synonym",
                        "confidence": 0.7,
                        "source": "synonym_match"
                    })
                    break

        return tags

    def _generate_semantic_tags(self, text: str, max_tags: int) -> List[Dict[str, Any]]:
        """Genera etiquetas usando embeddings semánticos"""
        if not self.encoder:
            return []

        try:
            # Generar embedding del texto
            text_embedding = self.encoder.encode([text])[0]

            # Comparar con embeddings de etiquetas predefinidas
            semantic_tags = []

            for category, category_tags in self.predefined_tags.items():
                for tag in category_tags:
                    tag_embedding = self.encoder.encode([tag])[0]
                    similarity = cosine_similarity(
                        [text_embedding], [tag_embedding]
                    )[0][0]

                    if similarity > 0.3:  # Umbral de similitud
                        semantic_tags.append({
                            "name": tag,
                            "category": category,
                            "type": "semantic",
                            "confidence": float(similarity),
                            "source": "semantic_analysis"
                        })

            # Ordenar por confianza y limitar
            semantic_tags.sort(key=lambda x: x["confidence"], reverse=True)
            return semantic_tags[:max_tags]

        except Exception as e:
            logger.error(f"❌ Error en análisis semántico: {e}")
            return []

    def _prioritize_tags(self, tags: List[Dict[str, Any]],
                         category: str = None, max_tags: int = 8) -> List[Dict[str, Any]]:
        """Prioriza y filtra etiquetas"""
        if not tags:
            return []

        # Agrupar por nombre para evitar duplicados
        unique_tags = {}
        for tag in tags:
            tag_name = tag["name"].lower()
            if tag_name not in unique_tags:
                unique_tags[tag_name] = tag
            else:
                # Mantener la versión con mayor confianza
                if tag["confidence"] > unique_tags[tag_name]["confidence"]:
                    unique_tags[tag_name] = tag

        # Convertir de vuelta a lista
        unique_tags_list = list(unique_tags.values())

        # Priorizar etiquetas de la categoría específica
        if category:
            category_tags = [
                t for t in unique_tags_list if t["category"] == category]
            other_tags = [
                t for t in unique_tags_list if t["category"] != category]

            # Ordenar por confianza
            category_tags.sort(key=lambda x: x["confidence"], reverse=True)
            other_tags.sort(key=lambda x: x["confidence"], reverse=True)

            # Combinar priorizando la categoría
            prioritized = category_tags + other_tags
        else:
            # Ordenar solo por confianza
            prioritized = sorted(unique_tags_list,
                                 key=lambda x: x["confidence"], reverse=True)

        return prioritized[:max_tags]

    def _enhance_tags(self, tags: List[Dict[str, Any]],
                      text: str) -> List[Dict[str, Any]]:
        """Mejora las etiquetas con metadatos adicionales"""
        enhanced_tags = []

        for tag in tags:
            enhanced_tag = tag.copy()

            # Agregar metadatos adicionales
            enhanced_tag["weight"] = self._calculate_tag_weight(tag, text)
            enhanced_tag["context"] = self._extract_tag_context(
                tag["name"], text)
            enhanced_tag["related_tags"] = self._find_related_tags(tag)

            enhanced_tags.append(enhanced_tag)

        return enhanced_tags

    def _calculate_tag_weight(self, tag: Dict[str, Any], text: str) -> float:
        """Calcula el peso de una etiqueta basado en el contexto"""
        base_weight = tag["confidence"]

        # Aumentar peso si aparece múltiples veces
        text_lower = text.lower()
        tag_lower = tag["name"].lower()
        frequency = text_lower.count(tag_lower)

        if frequency > 1:
            base_weight += min(0.2, frequency * 0.05)

        # Aumentar peso si es de la categoría principal del texto
        if tag["type"] == "keyword":
            base_weight += 0.1

        return min(1.0, base_weight)

    def _extract_tag_context(self, tag_name: str, text: str) -> str:
        """Extrae el contexto alrededor de una etiqueta"""
        try:
            # Buscar la etiqueta en el texto
            tag_lower = tag_name.lower()
            text_lower = text.lower()

            if tag_lower in text_lower:
                start_idx = text_lower.find(tag_lower)
                end_idx = start_idx + len(tag_name)

                # Extraer contexto (50 caracteres antes y después)
                context_start = max(0, start_idx - 50)
                context_end = min(len(text), end_idx + 50)

                context = text[context_start:context_end]
                return context.strip()

            return ""

        except Exception as e:
            logger.error(f"❌ Error extrayendo contexto: {e}")
            return ""

    def _find_related_tags(self, tag: Dict[str, Any]) -> List[str]:
        """Encuentra etiquetas relacionadas"""
        related = []

        # Buscar en la misma categoría
        category = tag["category"]
        if category in self.predefined_tags:
            category_tags = self.predefined_tags[category]
            # Agregar hasta 3 etiquetas relacionadas
            for related_tag in category_tags[:3]:
                if related_tag != tag["name"]:
                    related.append(related_tag)

        return related

    def _get_tag_category(self, tag_name: str) -> str:
        """Obtiene la categoría de una etiqueta"""
        for category, tags in self.predefined_tags.items():
            if tag_name in tags:
                return category
        return "general"

    def _fallback_tags(self, category: str = None, max_tags: int = 5) -> List[Dict[str, Any]]:
        """Etiquetas de respaldo si falla el análisis"""
        if category and category in self.predefined_tags:
            tags = self.predefined_tags[category][:max_tags]
        else:
            # Etiquetas generales
            tags = ["consulta", "información", "ayuda", "general"]

        return [
            {
                "name": tag,
                "category": category or "general",
                "type": "fallback",
                "confidence": 0.5,
                "source": "fallback_system",
                "weight": 0.5,
                "context": "",
                "related_tags": []
            }
            for tag in tags
        ]

    def suggest_tags(self, partial_tag: str, category: str = None) -> List[Dict[str, Any]]:
        """Sugiere etiquetas basadas en entrada parcial"""
        suggestions = []
        partial_lower = partial_tag.lower()

        # Buscar en etiquetas predefinidas
        for cat, tags in self.predefined_tags.items():
            if category and cat != category:
                continue

            for tag in tags:
                if partial_lower in tag.lower():
                    suggestions.append({
                        "name": tag,
                        "category": cat,
                        "type": "suggestion",
                        "confidence": 0.9,
                        "source": "tag_suggestion"
                    })

        # Ordenar por relevancia
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        return suggestions[:10]

    def get_tag_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de etiquetas"""
        stats = {
            "total_categories": len(self.predefined_tags),
            "total_tags": sum(len(tags) for tags in self.predefined_tags.values()),
            "categories": {}
        }

        for category, tags in self.predefined_tags.items():
            stats["categories"][category] = {
                "tag_count": len(tags),
                "tags": tags
            }

        return stats


# Instancia global del servicio de tagging
smart_tagging_service = SmartTaggingService()
