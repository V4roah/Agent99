"""
Servicio de Gestión de Agentes con Sistema de Aprendizaje Individual
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from models.agent import AgentLearning, AgentLearningCreate
from core.db import get_session
from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class BaseAgent:
    """Clase base para todos los agentes con capacidades de aprendizaje"""

    def __init__(self, agent_type: str, name: str):
        self.agent_type = agent_type
        self.name = name
        self.learning_history = []
        self.performance_metrics = {}
        self.specialization_areas = []

        logger.info(
            f"🤖 Agente {self.name} ({self.agent_type}) inicializado con capacidades de aprendizaje")

    def learn_from_conversation(self, conversation: Dict[str, Any], outcome: Dict[str, Any]) -> Dict[str, Any]:
        """Aprende de una conversación específica"""
        try:
            learning_outcome = {
                "agent_type": self.agent_type,
                "conversation_id": conversation.get("id"),
                "learning_timestamp": datetime.now().isoformat(),
                "patterns_identified": [],
                "improvements_suggested": [],
                "confidence_adjustments": [],
                "specialization_updates": []
            }

            # 1. Identificar patrones en la conversación
            patterns = self._identify_conversation_patterns(
                conversation, outcome)
            learning_outcome["patterns_identified"] = patterns

            # 2. Generar sugerencias de mejora
            improvements = self._generate_improvement_suggestions(
                conversation, outcome, patterns)
            learning_outcome["improvements_suggested"] = improvements

            # 3. Ajustar niveles de confianza
            confidence_adjustments = self._adjust_confidence_levels(
                outcome, patterns)
            learning_outcome["confidence_adjustments"] = confidence_adjustments

            # 4. Actualizar áreas de especialización
            specialization_updates = self._update_specialization_areas(
                conversation, outcome)
            learning_outcome["specialization_updates"] = specialization_updates

            # 5. Guardar aprendizaje en BD
            self._save_learning_to_db(learning_outcome)

            # 6. Actualizar memoria local del agente
            self._update_local_memory(learning_outcome)

            logger.info(
                f"🧠 Agente {self.name} aprendió de conversación {conversation.get('id')}")
            return learning_outcome

        except Exception as e:
            logger.error(f"❌ Error en aprendizaje del agente {self.name}: {e}")
            return {"error": str(e)}

    def _identify_conversation_patterns(self, conversation: Dict[str, Any], outcome: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica patrones en la conversación para aprendizaje"""
        patterns = []

        try:
            # Patrón 1: Categoría de conversación
            if conversation.get("category"):
                patterns.append({
                    "type": "category_pattern",
                    "pattern": f"Conversación de categoría: {conversation['category']}",
                    "strength": 0.8,
                    "frequency": 1
                })

            # Patrón 2: Tags utilizados
            if conversation.get("tags"):
                for tag in conversation["tags"][:3]:  # Top 3 tags
                    patterns.append({
                        "type": "tag_pattern",
                        "pattern": f"Tag utilizado: {tag}",
                        "strength": 0.7,
                        "frequency": 1
                    })

            # Patrón 3: Sentimiento del cliente
            if conversation.get("sentiment"):
                patterns.append({
                    "type": "sentiment_pattern",
                    "pattern": f"Sentimiento del cliente: {conversation['sentiment']}",
                    "strength": 0.6,
                    "frequency": 1
                })

            # Patrón 4: Resultado del procesamiento
            if outcome.get("success_rate"):
                success_pattern = "exitoso" if outcome["success_rate"] > 0.7 else "problemático"
                patterns.append({
                    "type": "outcome_pattern",
                    "pattern": f"Conversación {success_pattern}",
                    "strength": 0.9,
                    "frequency": 1
                })

        except Exception as e:
            logger.error(f"❌ Error identificando patrones: {e}")

        return patterns

    def _generate_improvement_suggestions(self, conversation: Dict[str, Any],
                                        outcome: Dict[str, Any],
                                        patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Genera sugerencias de mejora basándose en patrones identificados"""
        suggestions = []

        try:
            # Sugerencia 1: Basada en éxito de la conversación
            if outcome.get("success_rate", 0) < 0.7:
                suggestions.append({
                    "type": "performance_improvement",
                    "suggestion": "Mejorar tiempo de respuesta para conversaciones problemáticas",
                    "priority": "high",
                    "confidence": 0.8
                })

            # Sugerencia 2: Basada en categoría
            if conversation.get("category") == "soporte":
                suggestions.append({
                    "type": "specialization_improvement",
                    "suggestion": "Profundizar en conocimientos técnicos de soporte",
                    "priority": "medium",
                    "confidence": 0.7
                })

            # Sugerencia 3: Basada en tags
            if conversation.get("tags") and "error" in conversation["tags"]:
                suggestions.append({
                    "type": "knowledge_improvement",
                    "suggestion": "Ampliar base de conocimientos sobre resolución de errores",
                    "priority": "high",
                    "confidence": 0.9
                })

        except Exception as e:
            logger.error(f"❌ Error generando sugerencias: {e}")

        return suggestions

    def _adjust_confidence_levels(self, outcome: Dict[str, Any], patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ajusta niveles de confianza basándose en resultados"""
        adjustments = []

        try:
            # Ajuste 1: Basado en éxito de la conversación
            success_rate = outcome.get("success_rate", 0.5)
            if success_rate > 0.8:
                adjustments.append({
                    "type": "confidence_increase",
                    "reason": "Conversación exitosa",
                    "adjustment": 0.1,
                    "new_confidence": min(1.0, 0.8 + 0.1)
                })
            elif success_rate < 0.5:
                adjustments.append({
                    "type": "confidence_decrease",
                    "reason": "Conversación problemática",
                    "adjustment": -0.1,
                    "new_confidence": max(0.1, 0.8 - 0.1)
                })

        except Exception as e:
            logger.error(f"❌ Error ajustando niveles de confianza: {e}")

        return adjustments

    def _update_specialization_areas(self, conversation: Dict[str, Any], outcome: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Actualiza áreas de especialización del agente"""
        updates = []

        try:
            # Actualización 1: Basada en categoría exitosa
            if outcome.get("success_rate", 0) > 0.8:
                category = conversation.get("category")
                if category and category not in self.specialization_areas:
                    self.specialization_areas.append(category)
                    updates.append({
                        "type": "specialization_added",
                        "area": category,
                        "reason": "Alto éxito en conversaciones de esta categoría",
                        "confidence": 0.8
                    })

            # Actualización 2: Basada en tags exitosos
            if conversation.get("tags") and outcome.get("success_rate", 0) > 0.7:
                for tag in conversation["tags"][:2]:  # Top 2 tags
                    if tag not in self.specialization_areas:
                        self.specialization_areas.append(tag)
                        updates.append({
                            "type": "specialization_added",
                            "area": tag,
                            "reason": "Éxito en conversaciones con este tag",
                            "confidence": 0.7
                        })

        except Exception as e:
            logger.error(f"❌ Error actualizando áreas de especialización: {e}")

        return updates

    def _save_learning_to_db(self, learning_outcome: Dict[str, Any]):
        """Guarda el aprendizaje del agente en la base de datos"""
        try:
            with get_session() as session:
                # Guardar patrón principal de aprendizaje
                learning = AgentLearning(
                    agent_type=self.agent_type,
                    learning_type="agent_learning",
                    content=f"Agente {self.name} aprendió de conversación {learning_outcome.get('conversation_id')}",
                    confidence_score=0.8,
                    category="agent_learning",
                    metadata={
                        "patterns_identified": len(learning_outcome.get("patterns_identified", [])),
                        "improvements_suggested": len(learning_outcome.get("improvements_suggested", [])),
                        "confidence_adjustments": len(learning_outcome.get("confidence_adjustments", [])),
                        "specialization_updates": len(learning_outcome.get("specialization_updates", []))
                    }
                )

                session.add(learning)
                session.commit()

                logger.info(
                    f"💾 Aprendizaje del agente {self.name} guardado en BD")

        except Exception as e:
            logger.error(f"❌ Error guardando aprendizaje en BD: {e}")

    def _update_local_memory(self, learning_outcome: Dict[str, Any]):
        """Actualiza la memoria local del agente"""
        try:
            # Agregar a historial de aprendizaje
            self.learning_history.append({
                "timestamp": datetime.now().isoformat(),
                "conversation_id": learning_outcome.get("conversation_id"),
                "patterns": learning_outcome.get("patterns_identified", []),
                "improvements": learning_outcome.get("improvements_suggested", []),
                "confidence_adjustments": learning_outcome.get("confidence_adjustments", [])
            })

            # Mantener solo los últimos 100 aprendizajes
            if len(self.learning_history) > 100:
                self.learning_history = self.learning_history[-100:]

            # Actualizar métricas de rendimiento
            self._update_performance_metrics(learning_outcome)

        except Exception as e:
            logger.error(f"❌ Error actualizando memoria local: {e}")

    def _update_performance_metrics(self, learning_outcome: Dict[str, Any]):
        """Actualiza métricas de rendimiento del agente"""
        try:
            conversation_id = learning_outcome.get("conversation_id")
            if conversation_id:
                # Métrica: Tasa de aprendizaje
                if "learning_rate" not in self.performance_metrics:
                    self.performance_metrics["learning_rate"] = 0.0

                # Métrica: Patrones identificados
                if "patterns_identified" not in self.performance_metrics:
                    self.performance_metrics["patterns_identified"] = 0
                self.performance_metrics["patterns_identified"] += len(
                    learning_outcome.get("patterns_identified", []))

                # Métrica: Mejoras sugeridas
                if "improvements_suggested" not in self.performance_metrics:
                    self.performance_metrics["improvements_suggested"] = 0
                self.performance_metrics["improvements_suggested"] += len(
                    learning_outcome.get("improvements_suggested", []))

        except Exception as e:
            logger.error(f"❌ Error actualizando métricas de rendimiento: {e}")

    def get_learning_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen del aprendizaje del agente"""
        return {
            "agent_type": self.agent_type,
            "name": self.name,
            "total_learnings": len(self.learning_history),
            "specialization_areas": self.specialization_areas,
            "performance_metrics": self.performance_metrics,
            "recent_learnings": self.learning_history[-5:] if self.learning_history else [],
            "learning_timestamp": datetime.now().isoformat()
        }


class SalesAgent(BaseAgent):
    """Agente especializado en ventas con aprendizaje específico"""

    def __init__(self):
        super().__init__("sales", "Agente de Ventas")
        self.specialization_areas = [
            "ventas", "productos", "cotizaciones", "objeciones"]
        self.sales_metrics = {
            "conversion_rate": 0.0,
            "average_deal_size": 0.0,
            "sales_cycle_length": 0.0
        }

    def learn_from_sales_conversation(self, conversation: Dict[str, Any], outcome: Dict[str, Any]):
        """Aprende específicamente de conversaciones de ventas"""
        # Llamar al método base de aprendizaje
        learning_outcome = self.learn_from_conversation(conversation, outcome)

        # Aprendizaje específico de ventas
        if outcome.get("conversion", False):
            self._learn_from_successful_sale(conversation, outcome)
        else:
            self._learn_from_failed_sale(conversation, outcome)

        return learning_outcome

    def _learn_from_successful_sale(self, conversation: Dict[str, Any], outcome: Dict[str, Any]):
        """Aprende de ventas exitosas"""
        # Implementar lógica específica de aprendizaje de ventas exitosas
        pass

    def _learn_from_failed_sale(self, conversation: Dict[str, Any], outcome: Dict[str, Any]):
        """Aprende de ventas fallidas"""
        # Implementar lógica específica de aprendizaje de ventas fallidas
        pass


class SupportAgent(BaseAgent):
    """Agente especializado en soporte técnico con aprendizaje específico"""

    def __init__(self):
        super().__init__("support", "Agente de Soporte")
        self.specialization_areas = ["soporte",
            "técnico", "problemas", "soluciones"]
        self.support_metrics = {
            "resolution_time": 0.0,
            "first_call_resolution": 0.0,
            "customer_satisfaction": 0.0
        }

    def learn_from_support_conversation(self, conversation: Dict[str, Any], outcome: Dict[str, Any]):
        """Aprende específicamente de conversaciones de soporte"""
        # Llamar al método base de aprendizaje
        learning_outcome = self.learn_from_conversation(conversation, outcome)

        # Aprendizaje específico de soporte
        if outcome.get("resolved", False):
            self._learn_from_resolved_issue(conversation, outcome)
        else:
            self._learn_from_unresolved_issue(conversation, outcome)

        return learning_outcome

    def _learn_from_resolved_issue(self, conversation: Dict[str, Any], outcome: Dict[str, Any]):
        """Aprende de problemas resueltos"""
        # Implementar lógica específica de aprendizaje de problemas resueltos
        pass

    def _learn_from_unresolved_issue(self, conversation: Dict[str, Any], outcome: Dict[str, Any]):
        """Aprende de problemas no resueltos"""
        # Implementar lógica específica de aprendizaje de problemas no resueltos
        pass


class CoordinatorAgent(BaseAgent):
    """Agente coordinador que gestiona múltiples agentes especializados"""

    def __init__(self):
        super().__init__("coordinator", "Agente Coordinador")
        self.specialization_areas = ["coordinación",
            "enrutamiento", "gestión", "optimización"]
        self.coordination_metrics = {
            "agents_coordinated": 0,
            "conflicts_resolved": 0,
            "efficiency_score": 0.0
        }

    def coordinate_agents(self, conversation: Dict[str, Any], agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Coordina los resultados de múltiples agentes"""
        try:
            coordination_result = {
                "conversation_id": conversation.get("id"),
                "agents_involved": list(agent_results.keys()),
                "coordination_timestamp": datetime.now().isoformat(),
                "conflicts_detected": 0,
                "conflicts_resolved": 0,
                "unified_plan": {},
                "efficiency_score": 0.8
            }

            # Analizar resultados de agentes
            for agent_type, result in agent_results.items():
                if result.get("success", False):
                    self.coordination_metrics["agents_coordinated"] += 1
                else:
                    # Detectar conflictos
                    coordination_result["conflicts_detected"] += 1

            # Resolver conflictos (simulado)
            if coordination_result["conflicts_detected"] > 0:
                coordination_result["conflicts_resolved"] = coordination_result["conflicts_detected"]
                self.coordination_metrics["conflicts_resolved"] += coordination_result["conflicts_resolved"]

            # Crear plan unificado
            coordination_result["unified_plan"] = self._create_unified_plan(
                agent_results)

            # Aprender de la coordinación
            self.learn_from_conversation(conversation, coordination_result)

            return coordination_result

        except Exception as e:
            logger.error(f"❌ Error coordinando agentes: {e}")
            return {"error": str(e)}

    def _create_unified_plan(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un plan unificado basándose en los resultados de todos los agentes"""
        unified_plan = {
            "actions": [],
            "priorities": [],
            "timeline": {},
            "resources_needed": []
        }

        # Consolidar acciones de todos los agentes
        for agent_type, result in agent_results.items():
            if result.get("success", False) and "result" in result:
                agent_result = result["result"]
                if "recommendations" in agent_result:
                    unified_plan["actions"].extend(
                        agent_result["recommendations"])

        return unified_plan


# Instancias globales de agentes
sales_agent = SalesAgent()
support_agent = SupportAgent()
coordinator_agent = CoordinatorAgent()

# Diccionario de agentes disponibles
available_agents = {
    "sales": sales_agent,
    "support": support_agent,
    "coordinator": coordinator_agent
}


class AgentManager:
    """Gestor central de todos los agentes del sistema"""

    def __init__(self):
        self.agents = available_agents
        self.agent_performance = {}
        self.routing_rules = {}

        logger.info(
            f"🤖 AgentManager inicializado con {len(self.agents)} agentes")

    def route_conversation(self, conversation, agent_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enruta una conversación a un agente específico"""
        try:
            if agent_type not in self.agents:
                logger.warning(
                    f"⚠️ Agente {agent_type} no encontrado, usando coordinador")
                agent_type = "coordinator"

            agent = self.agents.get(agent_type)
            if agent:
                # Procesar con el agente específico
                if agent_type == "sales":
                    result = agent.learn_from_sales_conversation(
                        conversation, context)
                elif agent_type == "support":
                    result = agent.learn_from_support_conversation(
                        conversation, context)
                else:
                    result = agent.learn_from_conversation(
                        conversation, context)

                # Actualizar métricas de rendimiento
                self._update_agent_performance(agent_type, result)
                
                return {
                    "agent_type": agent_type,
                    "result": result,
                    "success": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
            "agent_type": agent_type,
                    "result": None,
                    "success": False,
                    "error": f"Agente {agent_type} no disponible",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Error enrutando conversación a {agent_type}: {e}")
            return {
                "agent_type": agent_type,
                "result": None,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_agent_status(self, agent_type: str) -> Dict[str, Any]:
        """Obtiene el estado de un agente específico"""
        if agent_type in self.agents:
            agent = self.agents[agent_type]
            return agent.get_learning_summary()
        else:
            return {"error": f"Agente {agent_type} no encontrado"}
    
    def get_all_agents_status(self) -> Dict[str, Any]:
        """Obtiene el estado de todos los agentes"""
        status = {}
        for agent_type, agent in self.agents.items():
            status[agent_type] = agent.get_learning_summary()
        return status
    
    def _update_agent_performance(self, agent_type: str, result: Dict[str, Any]):
        """Actualiza las métricas de rendimiento del agente"""
        try:
            if agent_type not in self.agent_performance:
                self.agent_performance[agent_type] = {
                    "total_conversations": 0,
                    "successful_conversations": 0,
                    "learning_count": 0,
                    "last_activity": None
                }
            
            # Actualizar métricas
            self.agent_performance[agent_type]["total_conversations"] += 1
            if result.get("success", False):
                self.agent_performance[agent_type]["successful_conversations"] += 1
            
            if result.get("patterns_identified") or result.get("improvements_suggested"):
                self.agent_performance[agent_type]["learning_count"] += 1
            
            self.agent_performance[agent_type]["last_activity"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"❌ Error actualizando métricas de rendimiento: {e}")


# Instancia global del AgentManager
agent_manager = AgentManager()
