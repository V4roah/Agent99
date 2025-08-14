from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from services.llm import llm_service
from services.vector_store import vector_store
from services.whatsapp_analyzer import WhatsAppConversation
from models.agent_models import AgentAction, AgentMemory
from models.whatsapp import WhatsAppMessage


class BaseAgent:
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.memory: Dict[str, AgentMemory] = {}
        self.actions: List[AgentAction] = []
        self.performance_metrics = {
            "total_actions": 0,
            "successful_actions": 0,
            "average_confidence": 0.0
        }

    def process(self, WhatsAppConversation: WhatsAppConversation, context: str = "") -> Dict[str, Any]:
        """Procesa una conversación y retorna la acción recomendada"""
        raise NotImplementedError

    def learn(self, action: AgentAction, feedback: Dict[str, Any]):
        """Aprende de las acciones y feedback"""
        self.actions.append(action)
        self.performance_metrics["total_actions"] += 1

        if feedback.get("success", False):
            self.performance_metrics["successful_actions"] += 1

        # Actualizar métricas
        total_confidence = sum(a.confidence for a in self.actions)
        self.performance_metrics["average_confidence"] = total_confidence / \
            len(self.actions)

        # Actualizar memoria
        conversation_id = action.input_data.get("conversation_id")
        if conversation_id and conversation_id not in self.memory:
            self.memory[conversation_id] = AgentMemory(
                agent_id=self.agent_id,
                conversation_id=conversation_id,
                key_insights=[],
                successful_patterns=[],
                failed_patterns=[],
                customer_preferences={},
                last_updated=datetime.now()
            )

        if conversation_id:
            memory = self.memory[conversation_id]
            memory.last_updated = datetime.now()

            if feedback.get("success", False):
                memory.successful_patterns.append(str(action.input_data))
            else:
                memory.failed_patterns.append(str(action.input_data))

    def get_context(self, WhatsAppConversation: WhatsAppConversation) -> str:
        """Obtiene contexto relevante para la conversación"""
        # Buscar conversaciones similares
        WhatsAppConversation_text = "\n".join(
            [msg.content for msg in WhatsAppConversation.messages])
        similar = vector_store.search(WhatsAppConversation_text, 3)

        context = f"Conversación actual: {WhatsAppConversation.customer_name}\n"
        context += f"Categoría: {WhatsAppConversation.category}\n"
        context += f"Sentimiento: {WhatsAppConversation.sentiment}\n"

        if similar:
            context += "\nConversaciones similares:\n"
            for conv in similar:
                context += f"- {conv['metadata']['customer_name']}: {conv['text'][:100]}...\n"

        return context


class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__("sales_agent", "ventas")

    def process(self, WhatsAppConversation: WhatsAppConversation, context: str = "") -> Dict[str, Any]:
        """Procesa conversaciones de ventas"""

        # Obtener contexto
        full_context = context + "\n" + self.get_context(WhatsAppConversation)

        # Analizar intención de compra
        purchase_intent = self._analyze_purchase_intent(
            WhatsAppConversation, full_context)

        # Generar respuesta de ventas
        response = llm_service.generate_response(
            str(WhatsAppConversation.messages[-1].content),
            full_context,
            "ventas"
        )

        # Determinar siguiente acción
        next_action = self._determine_next_action(
            purchase_intent, WhatsAppConversation)

        action = AgentAction(
            agent_id=self.agent_id,
            action_type="sales_process",
            timestamp=datetime.now(),
            input_data={
                "WhatsAppConversation_id": WhatsAppConversation.id,
                "customer_name": WhatsAppConversation.customer_name,
                "last_message": str(WhatsAppConversation.messages[-1].content)
            },
            output_data={
                "purchase_intent": purchase_intent,
                "response": response,
                "next_action": next_action
            },
            confidence=purchase_intent.get("confidence", 0.5)
        )

        self.learn(action, {"success": True})

        return {
            "agent_id": self.agent_id,
            "action_type": "sales_process",
            "response": response,
            "purchase_intent": purchase_intent,
            "next_action": next_action,
            "confidence": purchase_intent.get("confidence", 0.5)
        }

    def _analyze_purchase_intent(self, WhatsAppConversation: WhatsAppConversation, context: str) -> Dict[str, Any]:
        """Analiza la intención de compra del cliente"""
        WhatsAppConversation_text = "\n".join(
            [msg.content for msg in WhatsAppConversation.messages])

        analysis = llm_service.analyze_intent(
            WhatsAppConversation_text,
            context,
            "purchase_intent"
        )

        return {
            "intent": analysis.get("intent", "unknown"),
            "confidence": analysis.get("confidence", 0.5),
            "urgency": analysis.get("urgency", "low"),
            "budget_indication": analysis.get("budget", "unknown"),
            "product_interest": analysis.get("products", [])
        }

    def _determine_next_action(self, purchase_intent: Dict[str, Any], WhatsAppConversation: WhatsAppConversation) -> str:
        """Determina la siguiente acción basada en la intención de compra"""
        intent = purchase_intent.get("intent", "unknown")
        urgency = purchase_intent.get("urgency", "low")

        if intent == "high_intent":
            if urgency == "high":
                return "immediate_quote"
            else:
                return "detailed_presentation"
        elif intent == "medium_intent":
            return "follow_up"
        elif intent == "low_intent":
            return "nurture"
        else:
            return "qualify"


class SupportAgent(BaseAgent):
    def __init__(self):
        super().__init__("support_agent", "soporte")

    def process(self, WhatsAppConversation: WhatsAppConversation, context: str = "") -> Dict[str, Any]:
        """Procesa conversaciones de soporte"""

        # Obtener contexto
        full_context = context + "\n" + self.get_context(WhatsAppConversation)

        # Analizar el problema
        problem_analysis = self._analyze_problem(
            WhatsAppConversation, full_context)

        # Generar respuesta de soporte
        response = llm_service.generate_response(
            str(WhatsAppConversation.messages[-1].content),
            full_context,
            "soporte"
        )

        # Determinar solución
        solution = self._determine_solution(
            problem_analysis, WhatsAppConversation)

        action = AgentAction(
            agent_id=self.agent_id,
            action_type="support_process",
            timestamp=datetime.now(),
            input_data={
                "WhatsAppConversation_id": WhatsAppConversation.id,
                "customer_name": WhatsAppConversation.customer_name,
                "last_message": str(WhatsAppConversation.messages[-1].content)
            },
            output_data={
                "problem_analysis": problem_analysis,
                "response": response,
                "solution": solution
            },
            confidence=problem_analysis.get("confidence", 0.5)
        )

        self.learn(action, {"success": True})

        return {
            "agent_id": self.agent_id,
            "action_type": "support_process",
            "response": response,
            "problem_analysis": problem_analysis,
            "solution": solution,
            "confidence": problem_analysis.get("confidence", 0.5)
        }

    def _analyze_problem(self, WhatsAppConversation: WhatsAppConversation, context: str) -> Dict[str, Any]:
        """Analiza el problema del cliente"""
        WhatsAppConversation_text = "\n".join(
            [msg.content for msg in WhatsAppConversation.messages])

        analysis = llm_service.analyze_intent(
            WhatsAppConversation_text,
            context,
            "problem_analysis"
        )

        return {
            "problem_type": analysis.get("problem_type", "unknown"),
            "severity": analysis.get("severity", "low"),
            "confidence": analysis.get("confidence", 0.5),
            "affected_products": analysis.get("affected_products", []),
            "customer_satisfaction": analysis.get("satisfaction", "neutral")
        }

    def _determine_solution(self, problem_analysis: Dict[str, Any], WhatsAppConversation: WhatsAppConversation) -> str:
        """Determina la solución basada en el análisis del problema"""
        problem_type = problem_analysis.get("problem_type", "unknown")
        severity = problem_analysis.get("severity", "low")

        if severity == "high":
            return "escalate"
        elif problem_type == "technical":
            return "technical_support"
        elif problem_type == "billing":
            return "billing_support"
        else:
            return "general_support"


class ComplaintAgent(BaseAgent):
    def __init__(self):
        super().__init__("complaint_agent", "quejas")

    def process(self, WhatsAppConversation: WhatsAppConversation, context: str = "") -> Dict[str, Any]:
        """Procesa conversaciones de quejas"""

        # Obtener contexto
        full_context = context + "\n" + self.get_context(WhatsAppConversation)

        # Analizar la queja
        complaint_analysis = self._analyze_complaint(
            WhatsAppConversation, full_context)

        # Generar respuesta de quejas
        response = llm_service.generate_response(
            str(WhatsAppConversation.messages[-1].content),
            full_context,
            "quejas"
        )

        # Determinar acción de resolución
        resolution_action = self._determine_resolution_action(
            complaint_analysis, WhatsAppConversation)

        action = AgentAction(
            agent_id=self.agent_id,
            action_type="complaint_process",
            timestamp=datetime.now(),
            input_data={
                "WhatsAppConversation_id": WhatsAppConversation.id,
                "customer_name": WhatsAppConversation.customer_name,
                "last_message": str(WhatsAppConversation.messages[-1].content)
            },
            output_data={
                "complaint_analysis": complaint_analysis,
                "response": response,
                "resolution_action": resolution_action
            },
            confidence=complaint_analysis.get("confidence", 0.5)
        )

        self.learn(action, {"success": True})

        return {
            "agent_id": self.agent_id,
            "action_type": "complaint_process",
            "response": response,
            "complaint_analysis": complaint_analysis,
            "resolution_action": resolution_action,
            "confidence": complaint_analysis.get("confidence", 0.5)
        }

    def _analyze_complaint(self, WhatsAppConversation: WhatsAppConversation, context: str) -> Dict[str, Any]:
        """Analiza la queja del cliente"""
        WhatsAppConversation_text = "\n".join(
            [msg.content for msg in WhatsAppConversation.messages])

        analysis = llm_service.analyze_intent(
            WhatsAppConversation_text,
            context,
            "complaint_analysis"
        )

        return {
            "complaint_type": analysis.get("complaint_type", "unknown"),
            "severity": analysis.get("severity", "low"),
            "confidence": analysis.get("confidence", 0.5),
            "affected_products": analysis.get("affected_products", []),
            "customer_emotion": analysis.get("emotion", "neutral"),
            "resolution_urgency": analysis.get("urgency", "low")
        }

    def _determine_resolution_action(self, complaint_analysis: Dict[str, Any], WhatsAppConversation: WhatsAppConversation) -> str:
        """Determina la acción de resolución basada en el análisis de la queja"""
        complaint_type = complaint_analysis.get("complaint_type", "unknown")
        severity = complaint_analysis.get("severity", "low")
        urgency = complaint_analysis.get("resolution_urgency", "low")

        if severity == "high" or urgency == "high":
            return "immediate_escalation"
        elif complaint_type == "service":
            return "service_recovery"
        elif complaint_type == "product":
            return "product_replacement"
        else:
            return "standard_resolution"


class AgentManager:
    """Gestiona y coordina múltiples agentes"""

    def __init__(self):
        self.agents = {
            "ventas": SalesAgent(),
            "soporte": SupportAgent(),
            "quejas": ComplaintAgent()
        }
        self.WhatsAppConversation_history: Dict[str, List[Dict[str, Any]]] = {}

    def route_WhatsAppConversation(self, WhatsAppConversation: WhatsAppConversation) -> Dict[str, Any]:
        """Enruta una conversación al agente apropiado"""
        agent_type = WhatsAppConversation.category or "general"

        if agent_type in self.agents:
            result = self.agents[agent_type].process(WhatsAppConversation)
        else:
            result = self._general_processing(WhatsAppConversation)

        # Guardar historial
        if WhatsAppConversation.id not in self.WhatsAppConversation_history:
            self.WhatsAppConversation_history[WhatsAppConversation.id] = []

        self.WhatsAppConversation_history[WhatsAppConversation.id].append({
            "timestamp": datetime.now(),
            "agent_type": agent_type,
            "result": result
        })

        return result

    def _general_processing(self, WhatsAppConversation: WhatsAppConversation) -> Dict[str, Any]:
        """Procesamiento general para conversaciones no categorizadas"""
        WhatsAppConversation_text = "\n".join(
            [msg.content for msg in WhatsAppConversation.messages])

        # Clasificar la conversación
        classification = llm_service.classify_conversation(
            WhatsAppConversation_text,
            ["ventas", "soporte", "quejas", "consulta", "otro"]
        )

        # Actualizar categoría
        WhatsAppConversation.category = classification.get(
            "category", "consulta")

        # Reenrutar con la nueva categoría
        return self.route_WhatsAppConversation(WhatsAppConversation)

    def get_agent_performance(self, agent_type: str = None) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento de los agentes"""
        if agent_type:
            if agent_type in self.agents:
                return self.agents[agent_type].performance_metrics
            else:
                return {}

        return {
            agent_type: agent.performance_metrics
            for agent_type, agent in self.agents.items()
        }

    def get_WhatsAppConversation_history(self, WhatsAppConversation_id: str) -> List[Dict[str, Any]]:
        """Obtiene el historial de una conversación específica"""
        return self.WhatsAppConversation_history.get(WhatsAppConversation_id, [])


# Instancia global del gestor de agentes
agent_manager = AgentManager()
