"""
Super Agente - Cerebro Central del Sistema
Se retroalimenta de todos los agentes especializados y aprende continuamente
"""
from models.agent import SuperAgentModel
from models.agent import AgentLearning as AgentLearningModel
from models.metric import AgentMetrics as AgentMetricModel
from models.customer import CustomerProfile as CustomerProfileModel
from models.conversation import Conversation as ConversationModel
from sqlmodel import Session, select
from core.db import get_session
from models.metric import AgentMetrics
from models.customer import CustomerProfile
from models.conversation import Conversation
from models.agent_models import AgentAction, AgentMemory
from services.smart_tagging import smart_tagging_service
from services.agents import agent_manager
from services.vector_store import vector_store
from services.llm import llm_service
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import logging
from collections import defaultdict, Counter
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import pytz

# Configuración de zona horaria
COLOMBIA_TZ = pytz.timezone("America/Bogota")


# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SuperAgent:
    """
    Super Agente - Cerebro central que coordina y aprende de todos los agentes
    """

    def __init__(self):
        self.name = "SuperAgent"
        self.version = "1.0"
        self.creation_date = datetime.now()

        # Memoria central del sistema
        self.global_memory = {
            "customer_patterns": {},      # Patrones de comportamiento de clientes
            "conversation_trends": {},    # Tendencias en conversaciones
            "agent_performance": {},      # Rendimiento de agentes
            "business_insights": {},      # Insights de negocio
            "learning_cycles": [],        # Ciclos de aprendizaje
            "optimization_history": [],   # Historial de optimizaciones
            "agent_optimizations": [],    # Optimizaciones de agentes
            "routing_optimizations": []   # Optimizaciones de enrutamiento
        }

        # Métricas agregadas
        self.aggregated_metrics = {
            "total_conversations": 0,
            "success_rate": 0.0,
            "average_response_time": 0.0,
            "customer_satisfaction": 0.0,
            "conversion_rate": 0.0
        }

        # Configuración de aprendizaje
        self.learning_config = {
            "min_data_points": 10,        # Mínimo de datos para aprender
            "learning_threshold": 0.7,    # Umbral de confianza para cambios
            "optimization_frequency": 24,  # Horas entre optimizaciones
            "memory_retention_days": 90   # Días de retención de memoria
        }

        # Estado del sistema
        self.last_optimization = datetime.now()
        self.is_learning = False
        self.optimization_count = 0

        # 🆕 REGISTRAR EL SUPER AGENTE EN LA BASE DE DATOS
        self._register_in_database()

        logger.info(
            "🧠 Super Agente inicializado - Sistema de aprendizaje activo")

    def _register_in_database(self):
        """Registra el Super Agente en la base de datos"""
        try:
            from models.agent import SuperAgentModel
            from core.db import get_session
            from sqlmodel import select

            with get_session() as session:
                # Verificar si ya existe un Super Agente
                existing_super_agent = session.exec(
                    select(SuperAgentModel)
                    .where(SuperAgentModel.name == self.name)
                ).first()

                if existing_super_agent:
                    # Actualizar el existente
                    existing_super_agent.version = self.version
                    existing_super_agent.status = "active"
                    existing_super_agent.updated_at = datetime.now()
                    existing_super_agent.metadata = {
                        "uptime_hours": 0,
                        "total_learning_cycles": len(self.global_memory["learning_cycles"]),
                        "total_optimizations": self.optimization_count
                    }
                    session.add(existing_super_agent)
                    self.db_id = existing_super_agent.id
                    logger.info(
                        f"🔄 Super Agente existente actualizado en BD: {self.db_id}")
                else:
                    # Crear nuevo registro
                    super_agent_record = SuperAgentModel(
                        name=self.name,
                        version=self.version,
                        status="active",
                        is_learning=False,
                        total_conversations_processed=0,
                        total_learnings_generated=0,
                        success_rate=0.0,
                        learning_threshold=self.learning_config["learning_threshold"],
                        optimization_frequency_hours=self.learning_config["optimization_frequency"],
                        metadata={
                            "uptime_hours": 0,
                            "total_learning_cycles": 0,
                            "total_optimizations": 0
                        }
                    )
                    session.add(super_agent_record)
                    session.commit()
                    session.refresh(super_agent_record)
                    self.db_id = super_agent_record.id
                    logger.info(
                        f"✅ Super Agente registrado en BD con ID: {self.db_id}")

        except Exception as e:
            logger.error(f"❌ Error registrando Super Agente en BD: {e}")
            self.db_id = None

    def process_conversation(self, conversation: Conversation) -> Dict[str, Any]:
        """
        Procesa una conversación completa usando todos los agentes
        y extrae aprendizaje para el sistema
        """
        try:
            logger.info(
                f"🧠 Super Agente procesando conversación: {conversation.id}")

            # 1. Análisis inicial de la conversación
            initial_analysis = self._analyze_conversation_context(conversation)

            # 2. 🆕 APLICAR APRENDIZAJES PARA ENRUTAMIENTO INTELIGENTE
            intelligent_routing = self._apply_learnings_for_routing(
                conversation)
            logger.info(
                f"🧠 Enrutamiento inteligente basado en aprendizajes: {intelligent_routing}")

            # 3. Enrutar a agentes especializados usando aprendizajes
            agent_results = self._route_to_specialized_agents_with_learnings(
                conversation, initial_analysis, intelligent_routing)

            # 4. Sintetizar resultados de todos los agentes
            synthesis = self._synthesize_agent_results(
                agent_results, conversation)

            # 5. Aprender del proceso completo
            learning_outcome = self._learn_from_conversation(
                conversation, synthesis)

            # 6. 🆕 APLICAR OPTIMIZACIONES BASADAS EN APRENDIZAJES
            if intelligent_routing.get("optimization_applied", False):
                logger.info(
                    f"🔧 Optimizaciones aplicadas basándose en aprendizajes")

            # 7. Guardar aprendizajes en BD
            self._save_learnings_to_db(conversation, learning_outcome)

            # 8. Actualizar métricas
            self._update_metrics_in_db(conversation, synthesis)

            # 9. Actualizar memoria global
            self._update_global_memory(
                conversation, synthesis, learning_outcome)

            # 10. Verificar si hay aprendizajes significativos
            if self._has_significant_learning(learning_outcome):
                self._trigger_learning_cycle(learning_outcome)

            return {
                "conversation_id": conversation.id,
                "intelligent_routing": intelligent_routing,
                "agent_results": agent_results,
                "synthesis": synthesis,
                "learning_outcome": learning_outcome,
                "optimizations_applied": intelligent_routing.get("optimization_applied", False)
            }

        except Exception as e:
            logger.error(f"❌ Error procesando conversación: {e}")
            return {"error": str(e)}

    def _analyze_conversation_context(self, conversation: Conversation) -> Dict[str, Any]:
        """Analiza el contexto completo de una conversación"""
        context = {
            "customer_profile": self._analyze_customer_profile(conversation.customer_id),
            "conversation_history": self._get_conversation_history(conversation.customer_id),
            "business_context": self._get_business_context(),
            "temporal_factors": self._analyze_temporal_factors(conversation),
            "complexity_score": self._calculate_complexity_score(conversation)
        }

        return context

    def _analyze_customer_profile(self, customer_id: str) -> Dict[str, Any]:
        """Analiza el perfil completo del cliente"""
        try:
            # Si el customer_id no es un UUID válido, crear un perfil básico
            if not customer_id or not self._is_valid_uuid(customer_id):
                return {
                    "status": "new_customer",
                    "customer_id": customer_id,
                    "patterns": {},
                    "risk_score": 0.5,
                    "opportunity_score": 0.5
                }

            # Obtener perfil del cliente
            customer = self._get_customer_profile(customer_id)
            if not customer:
                return {"status": "new_customer"}

            # Análisis de patrones
            patterns = {
                "preferred_products": self._extract_preferred_products(customer_id),
                "communication_style": self._analyze_communication_style(customer_id),
                "purchase_history": self._analyze_purchase_history(customer_id),
                "support_tickets": self._analyze_support_history(customer_id),
                "lifetime_value": self._calculate_customer_lifetime_value(customer_id)
            }

            return {
                "customer_id": customer_id,
                "status": "existing_customer",
                "patterns": patterns,
                "risk_score": self._calculate_customer_risk_score(patterns),
                "opportunity_score": self._calculate_customer_opportunity_score(patterns)
            }

        except Exception as e:
            logger.error(f"❌ Error analizando perfil del cliente: {e}")
            return {"status": "error", "error": str(e)}

    def _is_valid_uuid(self, uuid_string: str) -> bool:
        """Verifica si un string es un UUID válido"""
        try:
            import uuid
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False

    def _route_to_specialized_agents(self, conversation: Conversation,
                                     context: Dict[str, Any]) -> Dict[str, Any]:
        """Enruta la conversación a los agentes especializados apropiados"""
        agent_results = {}

        try:
            # Determinar qué agentes necesitamos
            required_agents = self._determine_required_agents(
                conversation, context)

            # Ejecutar agentes en paralelo (simulado)
            for agent_type in required_agents:
                logger.info(f"🧠 Enrutando a agente: {agent_type}")

                agent_result = agent_manager.route_conversation(
                    conversation,
                    agent_type=agent_type,
                    context=context
                )

                agent_results[agent_type] = agent_result

            # Coordinación entre agentes
            coordination_result = self._coordinate_agents(
                agent_results, conversation)
            agent_results["coordination"] = coordination_result

            return agent_results

        except Exception as e:
            logger.error(f"❌ Error enrutando a agentes: {e}")
            return {"error": str(e)}

    def _apply_learnings_for_routing(self, conversation: Conversation) -> Dict[str, Any]:
        """Usa aprendizajes acumulados para tomar decisiones inteligentes de enrutamiento"""
        try:
            logger.info(
                f"🧠 Aplicando aprendizajes para enrutamiento de conversación: {conversation.id}")

            routing_decision = {
                "recommended_agents": [],
                "confidence_score": 0.0,
                "learning_based": False,
                "patterns_used": [],
                "optimization_applied": False
            }

            with get_session() as session:
                # 1. Buscar patrones similares en conversaciones previas
                similar_patterns = self._find_similar_conversation_patterns(
                    session, conversation)

                # 2. Buscar aprendizajes de agentes para esta categoría
                agent_learnings = self._find_agent_learnings_for_category(
                    session, conversation.category)

                # 3. Buscar patrones de éxito del cliente
                customer_patterns = self._find_customer_success_patterns(
                    session, conversation.customer_id)

                # 4. Tomar decisión basada en aprendizajes
                if similar_patterns or agent_learnings or customer_patterns:
                    routing_decision = self._make_intelligent_routing_decision(
                        conversation, similar_patterns, agent_learnings, customer_patterns
                    )
                    routing_decision["learning_based"] = True

                    # 5. Aplicar optimizaciones basadas en aprendizajes
                    optimizations = self._apply_learnings_optimizations(
                        session, conversation, routing_decision)
                    routing_decision["optimization_applied"] = bool(
                        optimizations)

                    logger.info(
                        f"✅ Decisión de enrutamiento basada en aprendizajes: {routing_decision}")
                else:
                    logger.info(
                        f"⚠️ No hay aprendizajes suficientes, usando enrutamiento por defecto")
                    routing_decision["recommended_agents"] = [
                        conversation.category, "coordinator"]
                    routing_decision["confidence_score"] = 0.5

            return routing_decision

        except Exception as e:
            logger.error(
                f"❌ Error aplicando aprendizajes para enrutamiento: {e}")
            return {
                "recommended_agents": [conversation.category, "coordinator"],
                "confidence_score": 0.3,
                "learning_based": False,
                "patterns_used": [],
                "optimization_applied": False
            }

    def _find_similar_conversation_patterns(self, session: Session, conversation: Conversation) -> List[Dict[str, Any]]:
        """Encuentra patrones de conversaciones similares basándose en tags y categoría"""
        try:
            patterns = []

            # Buscar conversaciones con tags similares
            if conversation.tags:
                # Usar solo los 3 tags más importantes
                for tag in conversation.tags[:3]:
                    # Buscar conversaciones que contengan este tag
                    similar_conversations = session.exec(
                        select(ConversationModel)
                        # Usar .any() en lugar de .contains()
                        .where(ConversationModel.tags.any(tag))
                        .where(ConversationModel.id != conversation.id)
                        .order_by(ConversationModel.created_at.desc())
                        .limit(5)
                    ).all()

                    for similar_conv in similar_conversations:
                        patterns.append({
                            "type": "tag_similarity",
                            "tag": tag,
                            "conversation_id": similar_conv.id,
                            "category": similar_conv.category,
                            "sentiment": similar_conv.sentiment,
                            "success_rate": self._get_conversation_success_rate(similar_conv.id),
                            "similarity_score": 0.8
                        })

            # Buscar conversaciones de la misma categoría con sentimiento similar
            category_conversations = session.exec(
                select(ConversationModel)
                .where(ConversationModel.category == conversation.category)
                .where(ConversationModel.id != conversation.id)
                .order_by(ConversationModel.created_at.desc())
                .limit(10)
            ).all()

            for cat_conv in category_conversations:
                if cat_conv.sentiment == conversation.sentiment:
                    patterns.append({
                        "type": "category_sentiment_similarity",
                        "conversation_id": cat_conv.id,
                        "category": cat_conv.category,
                        "sentiment": cat_conv.sentiment,
                        "success_rate": self._get_conversation_success_rate(cat_conv.id),
                        "similarity_score": 0.7
                    })

            return patterns

        except Exception as e:
            logger.error(f"❌ Error encontrando patrones de conversación: {e}")
            return []

    def _find_agent_learnings_for_category(self, session: Session, category: str) -> List[Dict[str, Any]]:
        """Encuentra aprendizajes de agentes para una categoría específica"""
        try:
            learnings = []

            # Buscar aprendizajes de agentes para esta categoría
            agent_learnings = session.exec(
                select(AgentLearningModel)
                .where(AgentLearningModel.category == category)
                .where(AgentLearningModel.confidence_score > 0.6)
                .order_by(AgentLearningModel.confidence_score.desc())
                .limit(10)
            ).all()

            for learning in agent_learnings:
                learnings.append({
                    "agent_type": learning.agent_type,
                    "learning_type": learning.learning_type,
                    "content": learning.content,
                    "confidence_score": learning.confidence_score,
                    "category": learning.category,
                    "created_at": learning.created_at.isoformat()
                })

            return learnings

        except Exception as e:
            logger.error(f"❌ Error encontrando aprendizajes de agentes: {e}")
            return []

    def _find_customer_success_patterns(self, session: Session, customer_id: str) -> List[Dict[str, Any]]:
        """Encuentra patrones de éxito del cliente basándose en conversaciones previas"""
        try:
            patterns = []

            if not customer_id or not self._is_valid_uuid(customer_id):
                return patterns

            # Buscar conversaciones exitosas del cliente
            customer_conversations = session.exec(
                select(ConversationModel)
                .where(ConversationModel.customer_id == customer_id)
                .order_by(ConversationModel.created_at.desc())
                .limit(10)
            ).all()

            for conv in customer_conversations:
                success_rate = self._get_conversation_success_rate(conv.id)
                if success_rate > 0.7:  # Solo conversaciones exitosas
                    patterns.append({
                        "type": "customer_success_pattern",
                        "conversation_id": conv.id,
                        "category": conv.category,
                        "tags": conv.tags,
                        "sentiment": conv.sentiment,
                        "success_rate": success_rate,
                        "pattern_strength": 0.8
                    })

            return patterns

        except Exception as e:
            logger.error(
                f"❌ Error encontrando patrones de éxito del cliente: {e}")
            return []

    def _make_intelligent_routing_decision(self, conversation: Conversation,
                                           similar_patterns: List[Dict],
                                           agent_learnings: List[Dict],
                                           customer_patterns: List[Dict]) -> Dict[str, Any]:
        """Toma una decisión inteligente de enrutamiento basándose en todos los aprendizajes"""
        try:
            routing_decision = {
                "recommended_agents": [],
                "confidence_score": 0.0,
                "learning_based": True,
                "patterns_used": [],
                "optimization_applied": False
            }

            # 1. Analizar patrones de conversaciones similares
            if similar_patterns:
                successful_categories = [
                    p["category"] for p in similar_patterns if p.get("success_rate", 0) > 0.7]
                if successful_categories:
                    routing_decision["recommended_agents"].extend(
                        successful_categories[:2])
                    routing_decision["patterns_used"].append(
                        "conversation_similarity")

            # 2. Analizar aprendizajes de agentes
            if agent_learnings:
                successful_agents = [l["agent_type"] for l in agent_learnings if l.get(
                    "confidence_score", 0) > 0.8]
                if successful_agents:
                    routing_decision["recommended_agents"].extend(
                        successful_agents[:2])
                    routing_decision["patterns_used"].append("agent_learnings")

            # 3. Analizar patrones de éxito del cliente
            if customer_patterns:
                customer_success_categories = [
                    p["category"] for p in customer_patterns if p.get("success_rate", 0) > 0.8]
                if customer_success_categories:
                    routing_decision["recommended_agents"].extend(
                        customer_success_categories[:2])
                    routing_decision["patterns_used"].append(
                        "customer_success_patterns")

            # 4. Agregar agente de coordinación si no hay suficientes agentes
            if len(routing_decision["recommended_agents"]) < 2:
                routing_decision["recommended_agents"].append("coordinator")

            # 5. Eliminar duplicados y calcular confianza
            routing_decision["recommended_agents"] = list(
                set(routing_decision["recommended_agents"]))

            # Calcular confianza basada en la cantidad y calidad de patrones
            pattern_count = len(routing_decision["patterns_used"])
            routing_decision["confidence_score"] = min(
                0.9, 0.5 + (pattern_count * 0.1))

            return routing_decision

        except Exception as e:
            logger.error(f"❌ Error tomando decisión de enrutamiento: {e}")
            return {
                "recommended_agents": [conversation.category, "coordinator"],
                "confidence_score": 0.3,
                "learning_based": False,
                "patterns_used": [],
                "optimization_applied": False
            }

    def _apply_learnings_optimizations(self, session: Session, conversation: Conversation,
                                       routing_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Aplica optimizaciones basándose en aprendizajes acumulados"""
        try:
            optimizations = []

            # 1. Optimizar parámetros de agentes basándose en éxito previo
            agent_optimizations = self._optimize_agent_parameters_from_learnings(
                session, conversation)
            if agent_optimizations:
                optimizations.extend(agent_optimizations)

            # 2. Optimizar lógica de enrutamiento
            routing_optimizations = self._optimize_routing_from_learnings(
                session, conversation, routing_decision)
            if routing_optimizations:
                optimizations.extend(routing_optimizations)

            # 3. Aplicar optimizaciones
            for optimization in optimizations:
                self._apply_single_optimization(optimization)

            return optimizations

        except Exception as e:
            logger.error(f"❌ Error aplicando optimizaciones: {e}")
            return []

    def _get_conversation_success_rate(self, conversation_id: str) -> float:
        """Calcula la tasa de éxito de una conversación basándose en métricas"""
        try:
            # Por ahora, retornar un valor por defecto
            # En el futuro, esto debería calcularse basándose en:
            # - Tiempo de resolución
            # - Satisfacción del cliente
            # - Métricas del agente
            # - Estado de la conversación
            return 0.8  # Valor por defecto
        except Exception as e:
            logger.error(f"❌ Error calculando tasa de éxito: {e}")
            return 0.5

    def _determine_required_agents(self, conversation: Conversation,
                                   context: Dict[str, Any]) -> List[str]:
        """Determina qué agentes especializados se necesitan"""
        required_agents = []

        # Agente base según categoría
        base_agent = conversation.category
        if base_agent in ["ventas", "soporte", "reclamo"]:
            required_agents.append(base_agent)

        # Agentes adicionales según contexto
        if context.get("complexity_score", 0) > 0.7:
            required_agents.append("escalation")

        if context.get("customer_profile", {}).get("risk_score", 0) > 0.8:
            required_agents.append("risk_management")

        if "product" in conversation.tags:
            required_agents.append("product_expert")

        # Agente de coordinación siempre presente
        required_agents.append("coordinator")

        return list(set(required_agents))  # Eliminar duplicados

    def _coordinate_agents(self, agent_results: Dict[str, Any],
                           conversation: Conversation) -> Dict[str, Any]:
        """Coordina los resultados de múltiples agentes"""
        try:
            # Analizar conflictos entre agentes
            conflicts = self._detect_agent_conflicts(agent_results)

            # Resolver conflictos
            resolved_conflicts = self._resolve_agent_conflicts(conflicts)

            # Crear plan de acción unificado
            unified_plan = self._create_unified_action_plan(
                agent_results, resolved_conflicts)

            # Priorizar acciones
            prioritized_actions = self._prioritize_actions(
                unified_plan, conversation)

            return {
                "conflicts_detected": len(conflicts),
                "conflicts_resolved": len(resolved_conflicts),
                "unified_plan": unified_plan,
                "prioritized_actions": prioritized_actions,
                "coordination_score": self._calculate_coordination_score(agent_results)
            }

        except Exception as e:
            logger.error(f"❌ Error coordinando agentes: {e}")
            return {"error": str(e)}

    def _synthesize_agent_results(self, agent_results: Dict[str, Any],
                                  conversation: Conversation) -> Dict[str, Any]:
        """Sintetiza los resultados de todos los agentes"""
        synthesis = {
            "conversation_id": conversation.id,
            "timestamp": datetime.now().isoformat(),
            "agent_participation": list(agent_results.keys()),
            "overall_sentiment": self._calculate_overall_sentiment(agent_results),
            "confidence_score": self._calculate_overall_confidence(agent_results),
            "recommended_actions": self._extract_recommended_actions(agent_results),
            "risk_assessment": self._assess_overall_risk(agent_results),
            "opportunity_identification": self._identify_opportunities(agent_results),
            "learning_points": self._extract_learning_points(agent_results)
        }

        return synthesis

    def _learn_from_conversation(self, conversation: Conversation,
                                 synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Aprende de la conversación completa"""
        try:
            learning_outcome = {
                "conversation_id": conversation.id,
                "learning_timestamp": datetime.now().isoformat(),
                "patterns_identified": [],
                "system_improvements": [],
                "agent_optimizations": [],
                "business_insights": []
            }

            # Identificar patrones
            patterns = self._identify_patterns(conversation, synthesis)
            learning_outcome["patterns_identified"] = patterns

            # Aprender del rendimiento de agentes
            agent_learnings = self._learn_from_agent_performance(synthesis)
            learning_outcome["agent_optimizations"] = agent_learnings

            # Extraer insights de negocio
            business_insights = self._extract_business_insights(
                conversation, synthesis)
            learning_outcome["business_insights"] = business_insights

            # Actualizar memoria global
            self._update_global_memory(
                conversation, synthesis, learning_outcome)

            # Verificar si hay aprendizajes significativos
            if self._has_significant_learning(learning_outcome):
                self._trigger_learning_cycle(learning_outcome)

            # 🆕 SINCRONIZAR MEMORIA CON BASE DE DATOS
            self._sync_memory_to_database()

            return learning_outcome

        except Exception as e:
            logger.error(f"❌ Error aprendiendo de la conversación: {e}")
            return {"error": str(e)}

    def _identify_patterns(self, conversation: Conversation,
                           synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifica patrones en la conversación"""
        patterns = []

        try:
            # Patrones de comportamiento del cliente
            customer_patterns = self._identify_customer_patterns(conversation)
            patterns.extend(customer_patterns)

            # Patrones de conversación
            conversation_patterns = self._identify_conversation_patterns(
                conversation)
            patterns.extend(conversation_patterns)

            # Patrones de agente
            agent_patterns = self._identify_agent_patterns(synthesis)
            patterns.extend(agent_patterns)

            # Patrones de negocio
            business_patterns = self._identify_business_patterns(
                conversation, synthesis)
            patterns.extend(business_patterns)

        except Exception as e:
            logger.error(f"❌ Error identificando patrones: {e}")

        return patterns

    def _identify_customer_patterns(self, conversation: Conversation):
        """Identifica patrones del cliente basándose en datos históricos de la BD"""
        try:
            patterns = []

            # Si no hay customer_id válido, no buscar patrones
            if not conversation.customer_id or not self._is_valid_uuid(conversation.customer_id):
                return patterns

            with get_session() as session:
                # Analizar conversaciones previas del cliente
                statement = select(ConversationModel).where(
                    ConversationModel.customer_id == conversation.customer_id
                ).order_by(ConversationModel.created_at.desc())

                prev_conversations = session.exec(statement).all()

                if len(prev_conversations) > 1:
                    # Patrón de categorías preferidas
                    categories = [
                        c.category for c in prev_conversations if c.category]
                    if categories:
                        most_common_category = max(
                            set(categories), key=categories.count)
                        patterns.append({
                            "type": "category_preference",
                            "pattern": f"Cliente prefiere categoría: {most_common_category}",
                            "confidence": 0.8,
                            "data_points": len(categories)
                        })

                    # Patrón de sentimientos
                    sentiments = [
                        c.sentiment for c in prev_conversations if c.sentiment]
                    if sentiments:
                        avg_sentiment = sum(1 if s == "positive" else -1 if s == "negative" else 0
                                            for s in sentiments) / len(sentiments)
                        patterns.append({
                            "type": "sentiment_trend",
                            "pattern": f"Tendencia de sentimiento: {avg_sentiment:.2f}",
                            "confidence": 0.7,
                            "data_points": len(sentiments)
                        })

                    # Patrón de tags frecuentes
                    all_tags = []
                    for conv in prev_conversations:
                        if conv.tags:
                            all_tags.extend(conv.tags)

                    if all_tags:
                        tag_counts = Counter(all_tags)
                        most_common_tags = tag_counts.most_common(3)
                        patterns.append({
                            "type": "tag_preference",
                            "pattern": f"Tags más frecuentes: {[tag for tag, count in most_common_tags]}",
                            "confidence": 0.6,
                            "data_points": len(all_tags)
                        })

            return patterns

        except Exception as e:
            logger.error(f"❌ Error identificando patrones de cliente: {e}")
            return []

    def _identify_conversation_patterns(self, conversation: Conversation):
        """Identifica patrones en la conversación actual"""
        patterns = []

        try:
            # Patrón de categoría
            if conversation.category:
                patterns.append({
                    "type": "conversation_category",
                    "pattern": f"Categoría de conversación: {conversation.category}",
                    "confidence": 0.9,
                    "data_points": 1
                })

            # Patrón de tags
            if conversation.tags:
                patterns.append({
                    "type": "conversation_tags",
                    "pattern": f"Tags utilizados: {conversation.tags}",
                    "confidence": 0.8,
                    "data_points": len(conversation.tags)
                })

            # Patrón de sentimiento
            if conversation.sentiment:
                patterns.append({
                    "type": "conversation_sentiment",
                    "pattern": f"Sentimiento detectado: {conversation.sentiment}",
                    "confidence": 0.7,
                    "data_points": 1
                })

        except Exception as e:
            logger.error(
                f"❌ Error identificando patrones de conversación: {e}")

        return patterns

    def _identify_agent_patterns(self, synthesis: Dict[str, Any]):
        """Identifica patrones en el rendimiento de agentes"""
        patterns = []

        try:
            # Patrón de participación de agentes
            if synthesis.get("agent_participation"):
                patterns.append({
                    "type": "agent_participation",
                    "pattern": f"Agentes involucrados: {synthesis['agent_participation']}",
                    "confidence": 0.8,
                    "data_points": len(synthesis["agent_participation"])
                })

            # Patrón de confianza general
            if synthesis.get("confidence_score"):
                patterns.append({
                    "type": "overall_confidence",
                    "pattern": f"Confianza general del sistema: {synthesis['confidence_score']:.2f}",
                    "confidence": 0.7,
                    "data_points": 1
                })

        except Exception as e:
            logger.error(f"❌ Error identificando patrones de agentes: {e}")

        return patterns

    def _identify_business_patterns(self, conversation: Conversation, synthesis: Dict[str, Any]):
        """Identifica patrones de negocio"""
        patterns = []

        try:
            # Patrón de riesgo
            if synthesis.get("risk_assessment"):
                risk = synthesis["risk_assessment"]
                patterns.append({
                    "type": "business_risk",
                    "pattern": f"Nivel de riesgo: {risk.get('level', 'unknown')} (score: {risk.get('score', 0):.2f})",
                    "confidence": 0.6,
                    "data_points": 1
                })

            # Patrón de oportunidades
            if synthesis.get("opportunity_identification"):
                opportunities = synthesis["opportunity_identification"]
                if opportunities:
                    patterns.append({
                        "type": "business_opportunity",
                        "pattern": f"Oportunidades identificadas: {len(opportunities)}",
                        "confidence": 0.7,
                        "data_points": len(opportunities)
                    })

        except Exception as e:
            logger.error(f"❌ Error identificando patrones de negocio: {e}")

        return patterns

    def _trigger_learning_cycle(self, learning_outcome: Dict[str, Any]):
        """Dispara un ciclo de aprendizaje del sistema"""
        try:
            logger.info("🧠 Iniciando ciclo de aprendizaje del sistema")

            # Marcar inicio del ciclo
            self.is_learning = True

            # Ejecutar optimizaciones
            self._optimize_agent_parameters(learning_outcome)
            self._optimize_routing_logic(learning_outcome)
            self._optimize_response_templates(learning_outcome)

            # Actualizar configuración del sistema
            self._update_system_configuration(learning_outcome)

            # Registrar ciclo de aprendizaje
            learning_cycle = {
                "timestamp": datetime.now().isoformat(),
                "conversations_analyzed": 1,
                "patterns_identified": len(learning_outcome.get("patterns_identified", [])),
                "optimizations_applied": len(learning_outcome.get("agent_optimizations", [])),
                "insights_generated": len(learning_outcome.get("business_insights", []))
            }

            self.global_memory["learning_cycles"].append(learning_cycle)

            # Marcar fin del ciclo
            self.is_learning = False

            logger.info("🧠 Ciclo de aprendizaje completado")

        except Exception as e:
            logger.error(f"❌ Error en ciclo de aprendizaje: {e}")
            self.is_learning = False

    def _run_optimization_cycle(self):
        """Ejecuta un ciclo completo de optimización del sistema"""
        try:
            logger.info("🚀 Iniciando ciclo de optimización del sistema")

            # Análisis de rendimiento
            performance_analysis = self._analyze_system_performance()

            # Optimización de agentes
            agent_optimizations = self._optimize_agent_performance(
                performance_analysis)

            # Optimización de enrutamiento
            routing_optimizations = self._optimize_conversation_routing(
                performance_analysis)

            # Optimización de memoria
            memory_optimizations = self._optimize_memory_usage()

            # Aplicar optimizaciones
            self._apply_system_optimizations({
                "agents": agent_optimizations,
                "routing": routing_optimizations,
                "memory": memory_optimizations
            })

            # Registrar optimización
            optimization_record = {
                "timestamp": datetime.now().isoformat(),
                "performance_metrics": performance_analysis,
                "optimizations_applied": {
                    "agents": len(agent_optimizations),
                    "routing": len(routing_optimizations),
                    "memory": len(memory_optimizations)
                },
                "expected_improvement": self._estimate_optimization_impact()
            }

            self.global_memory["optimization_history"].append(
                optimization_record)
            self.last_optimization = datetime.now()
            self.optimization_count += 1

            logger.info(
                f"🚀 Ciclo de optimización completado (#{self.optimization_count})")

        except Exception as e:
            logger.error(f"❌ Error en ciclo de optimización: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo del sistema"""
        return {
            "super_agent": {
                "name": self.name,
                "version": self.version,
                "status": "active" if not self.is_learning else "learning",
                "uptime_hours": (datetime.now() - self.creation_date).total_seconds() / 3600,
                "learning_cycles": len(self.global_memory["learning_cycles"]),
                "optimization_count": self.optimization_count,
                "last_optimization": self.last_optimization.isoformat()
            },
            "global_metrics": self.aggregated_metrics,
            "memory_status": {
                "total_patterns": len(self.global_memory["customer_patterns"]),
                "total_trends": len(self.global_memory["conversation_trends"]),
                "total_insights": len(self.global_memory["business_insights"])
            },
            "learning_status": {
                "is_learning": self.is_learning,
                "learning_threshold": self.learning_config["learning_threshold"],
                "next_optimization": (self.last_optimization +
                                      timedelta(hours=self.learning_config["optimization_frequency"])).isoformat()
            }
        }

    def get_business_insights(self) -> Dict[str, Any]:
        """Obtiene insights de negocio del sistema desde la base de datos"""
        try:
            insights = {
                "customer_insights": self._generate_customer_insights(),
                "conversation_insights": self._generate_conversation_insights(),
                "agent_insights": self._generate_agent_insights(),
                "business_trends": self._generate_business_trends(),
                "optimization_recommendations": self._generate_optimization_recommendations()
            }

            return insights

        except Exception as e:
            logger.error(f"❌ Error generando insights: {e}")
            return {"error": str(e)}

    def get_database_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas directamente desde la base de datos"""
        try:
            with get_session() as session:
                stats = {}

                # Estadísticas de conversaciones
                statement = select(ConversationModel)
                conversations = session.exec(statement).all()
                stats["conversations"] = {
                    "total": len(conversations),
                    "by_category": {},
                    "by_sentiment": {},
                    "recent_count": len([c for c in conversations if c.created_at and
                                         (datetime.now() - c.created_at).days <= 7])
                }

                # Agrupar por categoría
                for conv in conversations:
                    if conv.category:
                        if conv.category not in stats["conversations"]["by_category"]:
                            stats["conversations"]["by_category"][conv.category] = 0
                        stats["conversations"]["by_category"][conv.category] += 1

                    if conv.sentiment:
                        if conv.sentiment not in stats["conversations"]["by_sentiment"]:
                            stats["conversations"]["by_sentiment"][conv.sentiment] = 0
                        stats["conversations"]["by_sentiment"][conv.sentiment] += 1

                # Estadísticas de clientes
                statement = select(CustomerProfileModel)
                customers = session.exec(statement).all()
                stats["customers"] = {
                    "total": len(customers),
                    "active": len([c for c in customers if c.created_at and
                                   (datetime.now() - c.created_at).days <= 30])
                }

                # Estadísticas de agentes
                statement = select(AgentMetricModel)
                agent_metrics = session.exec(statement).all()
                stats["agents"] = {
                    "total_metrics": len(agent_metrics),
                    "average_success_rate": 0.0,
                    "by_agent": {}
                }

                if agent_metrics:
                    success_rates = [
                        m.success_rate for m in agent_metrics if m.success_rate is not None]
                    if success_rates:
                        stats["agents"]["average_success_rate"] = sum(
                            success_rates) / len(success_rates)

                    # Agrupar por agente
                    for metric in agent_metrics:
                        if metric.agent_id not in stats["agents"]["by_agent"]:
                            stats["agents"]["by_agent"][metric.agent_id] = {
                                "total_conversations": 0,
                                "success_rate": 0.0
                            }
                        stats["agents"]["by_agent"][metric.agent_id]["total_conversations"] += 1

                # Estadísticas de aprendizajes
                statement = select(AgentLearningModel)
                learnings = session.exec(statement).all()
                stats["learnings"] = {
                    "total": len(learnings),
                    "by_type": {},
                    "recent": len([l for l in learnings if l.created_at and
                                   (datetime.now() - l.created_at).days <= 7])
                }

                # Agrupar por tipo de aprendizaje
                for learning in learnings:
                    if learning.learning_type not in stats["learnings"]["by_type"]:
                        stats["learnings"]["by_type"][learning.learning_type] = 0
                    stats["learnings"]["by_type"][learning.learning_type] += 1

                return stats

        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas de BD: {e}")
            return {"error": str(e)}

    # Métodos auxiliares (implementaciones simplificadas)
    def _get_customer_profile(self, customer_id: str):
        """Obtiene el perfil del cliente desde la base de datos"""
        try:
            # Si no hay customer_id válido, retornar None
            if not customer_id or not self._is_valid_uuid(customer_id):
                return None

            with get_session() as session:
                # Buscar cliente en la base de datos
                statement = select(CustomerProfileModel).where(
                    CustomerProfileModel.id == customer_id
                )
                customer = session.exec(statement).first()

                if customer:
                    return {
                        "id": customer.id,
                        "name": customer.name,
                        "email": customer.email,
                        "phone": customer.phone,
                        "preferences": customer.preferences,
                        "created_at": customer.created_at.isoformat() if customer.created_at else None
                    }
                return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo perfil del cliente: {e}")
            return None

    def _get_conversation_history(self, customer_id: str):
        """Obtiene el historial de conversaciones del cliente desde la base de datos"""
        try:
            # Si no hay customer_id válido, retornar lista vacía
            if not customer_id or not self._is_valid_uuid(customer_id):
                return []

            with get_session() as session:
                # Buscar conversaciones del cliente
                statement = select(ConversationModel).where(
                    ConversationModel.customer_id == customer_id
                ).order_by(ConversationModel.created_at.desc())

                conversations = session.exec(statement).all()

                history = []
                for conv in conversations[:10]:  # Últimas 10 conversaciones
                    history.append({
                        "id": conv.id,
                        "category": conv.category,
                        "tags": conv.tags,
                        "sentiment": conv.sentiment,
                        "created_at": conv.created_at.isoformat() if conv.created_at else None,
                        "status": conv.status
                    })

                return history

        except Exception as e:
            logger.error(
                f"❌ Error obteniendo historial de conversaciones: {e}")
            return []

    def _get_business_context(self):
        """Obtiene el contexto de negocio desde la base de datos"""
        try:
            with get_session() as session:
                context = {}

                # Obtener métricas generales del sistema
                statement = select(AgentMetricModel)
                metrics = session.exec(statement).all()

                if metrics:
                    context["total_metrics"] = len(metrics)
                    success_rates = [
                        m.success_rate for m in metrics if m.success_rate is not None]
                    if success_rates:
                        context["average_success_rate"] = sum(
                            success_rates) / len(success_rates)
                    else:
                        context["average_success_rate"] = 0.0

                # Obtener aprendizajes de agentes
                statement = select(AgentLearningModel)
                learnings = session.exec(statement).all()

                if learnings:
                    context["total_learnings"] = len(learnings)
                    context["recent_learnings"] = [
                        {
                            "agent_type": l.agent_type,
                            "learning_type": l.learning_type,
                            "content": l.content,
                            "confidence_score": l.confidence_score
                        }
                        for l in learnings[-5:]  # Últimos 5 aprendizajes
                    ]

                return context

        except Exception as e:
            logger.error(f"❌ Error obteniendo contexto de negocio: {e}")
            return {}

    def _analyze_temporal_factors(self, conversation: Conversation):
        # Implementar análisis de factores temporales
        return {}

    def _calculate_complexity_score(self, conversation: Conversation):
        # Implementar cálculo de score de complejidad
        return 0.5

    def _extract_preferred_products(self, customer_id: str):
        # Implementar extracción de productos preferidos
        return []

    def _analyze_communication_style(self, customer_id: str):
        # Implementar análisis de estilo de comunicación
        return {}

    def _analyze_purchase_history(self, customer_id: str):
        # Implementar análisis de historial de compras
        return []

    def _analyze_support_history(self, customer_id: str):
        # Implementar análisis de historial de soporte
        return []

    def _calculate_customer_lifetime_value(self, customer_id: str):
        # Implementar cálculo de valor de por vida del cliente
        return 0.0

    def _calculate_customer_risk_score(self, patterns: Dict[str, Any]):
        # Implementar cálculo de score de riesgo del cliente
        return 0.5

    def _calculate_customer_opportunity_score(self, patterns: Dict[str, Any]):
        # Implementar cálculo de score de oportunidad
        return 0.5

    def _detect_agent_conflicts(self, agent_results: Dict[str, Any]):
        # Implementar detección de conflictos entre agentes
        return []

    def _resolve_agent_conflicts(self, conflicts: List[Dict[str, Any]]):
        # Implementar resolución de conflictos
        return []

    def _create_unified_action_plan(self, agent_results: Dict[str, Any],
                                    resolved_conflicts: List[Dict[str, Any]]):
        # Implementar creación de plan unificado
        return {}

    def _prioritize_actions(self, action_plan: Dict[str, Any],
                            conversation: Conversation):
        # Implementar priorización de acciones
        return []

    def _calculate_coordination_score(self, agent_results: Dict[str, Any]):
        # Implementar cálculo de score de coordinación
        return 0.8

    def _calculate_overall_sentiment(self, agent_results: Dict[str, Any]):
        """Implementar cálculo de sentimiento general"""
        try:
            # Por ahora, retornar neutral
            # En el futuro, esto debería calcularse basándose en:
            # - Sentimiento de la conversación original
            # - Resultados de los agentes
            # - Métricas de satisfacción
            return "neutral"
        except Exception as e:
            logger.error(f"❌ Error calculando sentimiento general: {e}")
        return "neutral"

    def _calculate_overall_confidence(self, agent_results: Dict[str, Any]):
        """Implementar cálculo de confianza general"""
        try:
            # Por ahora, retornar un valor por defecto
            # En el futuro, esto debería calcularse basándose en:
            # - Confianza de cada agente
            # - Calidad de los resultados
            # - Consistencia entre agentes
            return 0.8
        except Exception as e:
            logger.error(f"❌ Error calculando confianza general: {e}")
            return 0.5

    def _extract_recommended_actions(self, agent_results: Dict[str, Any]):
        """Implementar extracción de acciones recomendadas"""
        actions = []

        try:
            # Extraer recomendaciones de todos los agentes
            for agent_type, result in agent_results.items():
                if isinstance(result, dict) and "recommendations" in result:
                    actions.extend(result["recommendations"])

        except Exception as e:
            logger.error(f"❌ Error extrayendo acciones recomendadas: {e}")

        return actions

    def _assess_overall_risk(self, agent_results: Dict[str, Any]):
        """Implementar evaluación de riesgo general"""
        try:
            # Por ahora, retornar un valor por defecto
            # En el futuro, esto debería calcularse basándose en:
            # - Riesgo identificado por cada agente
            # - Conflictos entre agentes
            # - Métricas de calidad
            return {"level": "low", "score": 0.3}
        except Exception as e:
            logger.error(f"❌ Error evaluando riesgo general: {e}")
            return {"level": "unknown", "score": 0.5}

    def _identify_opportunities(self, agent_results: Dict[str, Any]):
        """Implementar identificación de oportunidades"""
        opportunities = []

        try:
            # Identificar oportunidades basándose en resultados de agentes
            for agent_type, result in agent_results.items():
                if isinstance(result, dict) and result.get("success", False):
                    opportunities.append({
                        "type": f"agent_{agent_type}_opportunity",
                        "description": f"Agente {agent_type} funcionando correctamente",
                        "confidence": 0.8
                    })

        except Exception as e:
            logger.error(f"❌ Error identificando oportunidades: {e}")

        return opportunities

    def _extract_learning_points(self, agent_results: Dict[str, Any]):
        """Implementar extracción de puntos de aprendizaje"""
        learning_points = []

        try:
            # Extraer puntos de aprendizaje de todos los agentes
            for agent_type, result in agent_results.items():
                if isinstance(result, dict) and "learning_generated" in result:
                    learning_points.extend(result["learning_generated"])

        except Exception as e:
            logger.error(f"❌ Error extrayendo puntos de aprendizaje: {e}")

        return learning_points

    def _learn_from_agent_performance(self, synthesis: Dict[str, Any]):
        """Implementar aprendizaje del rendimiento de agentes"""
        learnings = []

        try:
            # Aprender de la participación de agentes
            if synthesis.get("agent_participation"):
                learnings.append({
                    "type": "agent_participation_learning",
                    "content": f"Agentes involucrados: {synthesis['agent_participation']}",
                    "confidence": 0.8,
                    "category": "agent_learning"
                })

            # Aprender de la confianza general
            if synthesis.get("confidence_score"):
                confidence = synthesis["confidence_score"]
                if confidence > 0.8:
                    learnings.append({
                        "type": "high_confidence_learning",
                        "content": f"Alta confianza del sistema: {confidence:.2f}",
                        "confidence": 0.9,
                        "category": "system_learning"
                    })
                elif confidence < 0.5:
                    learnings.append({
                        "type": "low_confidence_learning",
                        "content": f"Baja confianza del sistema: {confidence:.2f} - requiere optimización",
                        "confidence": 0.7,
                        "category": "system_learning"
                    })

        except Exception as e:
            logger.error(
                f"❌ Error aprendiendo del rendimiento de agentes: {e}")

        return learnings

    def _extract_business_insights(self, conversation: Conversation,
                                   synthesis: Dict[str, Any]):
        """Implementar extracción de insights de negocio"""
        insights = []

        try:
            # Insight de categoría de conversación
            if conversation.category:
                insights.append({
                    "type": "category_insight",
                    "content": f"Conversación de categoría {conversation.category} procesada exitosamente",
                    "confidence": 0.8,
                    "category": "business_insight"
                })

            # Insight de sentimiento del cliente
            if conversation.sentiment:
                insights.append({
                    "type": "sentiment_insight",
                    "content": f"Cliente con sentimiento {conversation.sentiment} - requiere atención especial",
                    "confidence": 0.7,
                    "category": "customer_insight"
                })

            # Insight de rendimiento del sistema
            if synthesis.get("confidence_score"):
                confidence = synthesis["confidence_score"]
                if confidence > 0.8:
                    insights.append({
                        "type": "performance_insight",
                        "content": f"Sistema funcionando con alta eficiencia: {confidence:.2f}",
                        "confidence": 0.9,
                        "category": "system_insight"
                    })

        except Exception as e:
            logger.error(f"❌ Error extrayendo insights de negocio: {e}")

        return insights

    def _has_significant_learning(self, learning_outcome: Dict[str, Any]):
        """Implementar verificación de aprendizaje significativo"""
        try:
            # Verificar si hay patrones identificados
            patterns = learning_outcome.get("patterns_identified", [])
            if len(patterns) > 2:
                return True

            # Verificar si hay optimizaciones de agentes
            optimizations = learning_outcome.get("agent_optimizations", [])
            if len(optimizations) > 1:
                return True

            # Verificar si hay insights de negocio
            insights = learning_outcome.get("business_insights", [])
            if len(insights) > 2:
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Error verificando aprendizaje significativo: {e}")
            return False

    def _optimize_agent_parameters(self, learning_outcome: Dict[str, Any]):
        # Implementar optimización de parámetros de agentes
        pass

    def _optimize_routing_logic(self, learning_outcome: Dict[str, Any]):
        # Implementar optimización de lógica de enrutamiento
        pass

    def _optimize_response_templates(self, learning_outcome: Dict[str, Any]):
        # Implementar optimización de plantillas de respuesta
        pass

    def _update_system_configuration(self, learning_outcome: Dict[str, Any]):
        # Implementar actualización de configuración del sistema
        pass

    def _analyze_system_performance(self):
        """Implementar análisis de rendimiento del sistema"""
        try:
            performance = {
                "total_conversations": self.aggregated_metrics["total_conversations"],
                "success_rate": self.aggregated_metrics["success_rate"],
                "learning_cycles": len(self.global_memory["learning_cycles"]),
                "optimization_count": self.optimization_count
            }
            return performance
        except Exception as e:
            logger.error(f"❌ Error analizando rendimiento del sistema: {e}")
            return {}

    def _optimize_agent_performance(self, performance_analysis: Dict[str, Any]):
        """Implementar optimización de rendimiento de agentes"""
        try:
            optimizations = []

            # Si la tasa de éxito es baja, optimizar
            if performance_analysis.get("success_rate", 0) < 0.7:
                optimizations.append({
                    "type": "agent_performance_optimization",
                    "description": "Baja tasa de éxito - optimizando parámetros de agentes",
                    "priority": "high"
                })

            return optimizations
        except Exception as e:
            logger.error(f"❌ Error optimizando rendimiento de agentes: {e}")
        return []

    def _optimize_conversation_routing(self, performance_analysis: Dict[str, Any]):
        """Implementar optimización de enrutamiento de conversaciones"""
        try:
            optimizations = []

            # Si hay muchos ciclos de aprendizaje, optimizar enrutamiento
            if performance_analysis.get("learning_cycles", 0) > 10:
                optimizations.append({
                    "type": "routing_optimization",
                    "description": "Muchos ciclos de aprendizaje - optimizando enrutamiento",
                    "priority": "medium"
                })

            return optimizations
        except Exception as e:
            logger.error(f"❌ Error optimizando enrutamiento: {e}")
            return []

    def _optimize_memory_usage(self):
        """Implementar optimización de uso de memoria"""
        try:
            optimizations = []

            # Limpiar memoria antigua si es necesario
            if len(self.global_memory["conversation_trends"]) > 1000:
                optimizations.append({
                    "type": "memory_cleanup",
                    "description": "Memoria grande - limpiando datos antiguos",
                    "priority": "low"
                })

            return optimizations
        except Exception as e:
            logger.error(f"❌ Error optimizando uso de memoria: {e}")
            return []

    def _apply_system_optimizations(self, optimizations: Dict[str, Any]):
        """Implementar aplicación de optimizaciones del sistema"""
        try:
            logger.info(
                f"🔧 Aplicando {sum(len(opt) for opt in optimizations.values())} optimizaciones del sistema")

            # Por ahora, solo registrar las optimizaciones
            # En el futuro, esto debería aplicar cambios reales
            for optimization_type, optimization_list in optimizations.items():
                for optimization in optimization_list:
                    logger.info(f"🔧 Aplicando optimización: {optimization}")

        except Exception as e:
            logger.error(f"❌ Error aplicando optimizaciones del sistema: {e}")

    def _estimate_optimization_impact(self):
        """Implementar estimación del impacto de optimización"""
        try:
            return {"expected_improvement": 0.15}
        except Exception as e:
            logger.error(f"❌ Error estimando impacto de optimización: {e}")
            return {"expected_improvement": 0.0}

    def _should_optimize(self):
        """Implementar verificación de si se debe optimizar"""
        try:
            return (datetime.now() - self.last_optimization).total_seconds() / 3600 >= self.learning_config["optimization_frequency"]
        except Exception as e:
            logger.error(f"❌ Error verificando si se debe optimizar: {e}")
            return False

    def _get_optimization_status(self):
        """Implementar obtención del estado de optimización"""
        try:
            return {
                "last_optimization": self.last_optimization.isoformat(),
                "next_optimization": (self.last_optimization +
                                      timedelta(hours=self.learning_config["optimization_frequency"])).isoformat(),
                "optimization_count": self.optimization_count
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo estado de optimización: {e}")
            return {}

    def _update_global_metrics(self, conversation: Conversation,
                               synthesis: Dict[str, Any]):
        """Implementar actualización de métricas globales"""
        try:
            self.aggregated_metrics["total_conversations"] += 1

            # Actualizar tasa de éxito
            if synthesis.get("confidence_score"):
                current_success_rate = self.aggregated_metrics["success_rate"]
                new_success_rate = (current_success_rate +
                                    synthesis["confidence_score"]) / 2
                self.aggregated_metrics["success_rate"] = new_success_rate

        except Exception as e:
            logger.error(f"❌ Error actualizando métricas globales: {e}")

    def _generate_customer_insights(self):
        """Implementar generación de insights de clientes"""
        try:
            insights = {}

            # Por ahora, retornar insights básicos
            # En el futuro, esto debería analizar datos reales de clientes
            insights["total_customers"] = 0
            insights["active_customers"] = 0
            insights["customer_satisfaction"] = 0.8

            return insights
        except Exception as e:
            logger.error(f"❌ Error generando insights de clientes: {e}")
            return {}

    def _generate_conversation_insights(self):
        """Implementar generación de insights de conversaciones"""
        try:
            insights = {}

            # Por ahora, retornar insights básicos
            # En el futuro, esto debería analizar datos reales de conversaciones
            insights["total_conversations"] = self.aggregated_metrics["total_conversations"]
            insights["success_rate"] = self.aggregated_metrics["success_rate"]
            insights["average_response_time"] = self.aggregated_metrics["average_response_time"]

            return insights
        except Exception as e:
            logger.error(f"❌ Error generando insights de conversaciones: {e}")
            return {}

    def _generate_agent_insights(self):
        """Implementar generación de insights de agentes"""
        try:
            insights = {}

            # Por ahora, retornar insights básicos
            # En el futuro, esto debería analizar datos reales de agentes
            insights["total_agents"] = 3  # sales, support, coordinator
            insights["active_agents"] = 3
            insights["average_agent_performance"] = 0.8

            return insights
        except Exception as e:
            logger.error(f"❌ Error generando insights de agentes: {e}")
            return {}

    def _generate_business_trends(self):
        """Implementar generación de tendencias de negocio"""
        try:
            trends = {}

            # Por ahora, retornar tendencias básicas
            # En el futuro, esto debería analizar datos reales de tendencias
            trends["conversation_growth"] = "stable"
            trends["customer_satisfaction_trend"] = "improving"
            trends["system_efficiency"] = "high"

            return trends
        except Exception as e:
            logger.error(f"❌ Error generando tendencias de negocio: {e}")
            return {}

    def _generate_optimization_recommendations(self):
        """Implementar generación de recomendaciones de optimización"""
        try:
            recommendations = []

            # Por ahora, retornar recomendaciones básicas
            # En el futuro, esto debería basarse en análisis real de datos
            if self.aggregated_metrics["success_rate"] < 0.8:
                recommendations.append({
                    "type": "performance_optimization",
                    "description": "La tasa de éxito es menor al 80% - considerar optimizaciones",
                    "priority": "high",
                    "expected_impact": "15-20% improvement"
                })

            if len(self.global_memory["learning_cycles"]) > 5:
                recommendations.append({
                    "type": "learning_optimization",
                    "description": "Muchos ciclos de aprendizaje - optimizar algoritmos",
                    "priority": "medium",
                    "expected_impact": "10-15% improvement"
                })

            return recommendations
        except Exception as e:
            logger.error(
                f"❌ Error generando recomendaciones de optimización: {e}")
            return []

    def _optimize_agent_parameters_from_learnings(self, session: Session, conversation: Conversation) -> List[Dict[str, Any]]:
        """Optimiza parámetros de agentes basándose en aprendizajes acumulados"""
        try:
            optimizations = []

            # Buscar aprendizajes de agentes exitosos para esta categoría
            successful_agent_learnings = session.exec(
                select(AgentLearningModel)
                .where(AgentLearningModel.learning_type == "agent_optimization")
                .where(AgentLearningModel.category == conversation.category)
                .where(AgentLearningModel.confidence_score > 0.8)
                .order_by(AgentLearningModel.confidence_score.desc())
                .limit(5)
            ).all()

            for learning in successful_agent_learnings:
                optimization = {
                    "type": "agent_parameter_optimization",
                    "agent_type": learning.agent_type,
                    "optimization": learning.content,
                    "confidence": learning.confidence_score,
                    "category": learning.category,
                    "applied": False
                }

                # Aplicar la optimización
                if self._apply_agent_parameter_optimization(optimization):
                    optimization["applied"] = True
                    optimizations.append(optimization)

            return optimizations

        except Exception as e:
            logger.error(f"❌ Error optimizando parámetros de agentes: {e}")
            return []

    def _optimize_routing_from_learnings(self, session: Session, conversation: Conversation,
                                         routing_decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimiza la lógica de enrutamiento basándose en aprendizajes"""
        try:
            optimizations = []

            # Buscar patrones de enrutamiento exitosos
            routing_patterns = session.exec(
                select(AgentLearningModel)
                .where(AgentLearningModel.learning_type == "routing_optimization")
                .where(AgentLearningModel.category == conversation.category)
                .where(AgentLearningModel.confidence_score > 0.7)
                .order_by(AgentLearningModel.confidence_score.desc())
                .limit(3)
            ).all()

            for pattern in routing_patterns:
                optimization = {
                    "type": "routing_logic_optimization",
                    "pattern": pattern.content,
                    "confidence": pattern.confidence_score,
                    "category": pattern.category,
                    "applied": False
                }

                # Aplicar la optimización de enrutamiento
                if self._apply_routing_optimization(optimization, routing_decision):
                    optimization["applied"] = True
                    optimizations.append(optimization)

            return optimizations

        except Exception as e:
            logger.error(f"❌ Error optimizando enrutamiento: {e}")
            return []

    def _apply_agent_parameter_optimization(self, optimization: Dict[str, Any]) -> bool:
        """Aplica una optimización específica de parámetros de agente"""
        try:
            logger.info(f"🔧 Aplicando optimización de agente: {optimization}")

            # Por ahora, solo registrar la optimización
            # En el futuro, esto debería:
            # - Ajustar parámetros del agente
            # - Modificar configuraciones
            # - Actualizar pesos de decisión

            # Guardar la optimización aplicada
            self.global_memory["agent_optimizations"].append({
                "timestamp": datetime.now().isoformat(),
                "optimization": optimization,
                "status": "applied"
            })

            return True

        except Exception as e:
            logger.error(f"❌ Error aplicando optimización de agente: {e}")
            return False

    def _apply_routing_optimization(self, optimization: Dict[str, Any], routing_decision: Dict[str, Any]) -> bool:
        """Aplica una optimización específica de enrutamiento"""
        try:
            logger.info(
                f"🔧 Aplicando optimización de enrutamiento: {optimization}")

            # Por ahora, solo registrar la optimización
            # En el futuro, esto debería:
            # - Ajustar pesos de enrutamiento
            # - Modificar reglas de decisión
            # - Actualizar umbrales de confianza

            # Guardar la optimización aplicada
            self.global_memory["routing_optimizations"].append({
                "timestamp": datetime.now().isoformat(),
                "optimization": optimization,
                "routing_decision": routing_decision,
                "status": "applied"
            })

            return True

        except Exception as e:
            logger.error(
                f"❌ Error aplicando optimización de enrutamiento: {e}")
            return False

    def _apply_single_optimization(self, optimization: Dict[str, Any]):
        """Aplica una optimización individual"""
        try:
            if optimization["type"] == "agent_parameter_optimization":
                return self._apply_agent_parameter_optimization(optimization)
            elif optimization["type"] == "routing_logic_optimization":
                return self._apply_routing_optimization(optimization, {})
            else:
                logger.warning(
                    f"⚠️ Tipo de optimización desconocido: {optimization['type']}")
                return False

        except Exception as e:
            logger.error(f"❌ Error aplicando optimización: {e}")
            return False

    def _route_to_specialized_agents_with_learnings(self, conversation: Conversation,
                                                    initial_analysis: Dict[str, Any],
                                                    intelligent_routing: Dict[str, Any]) -> Dict[str, Any]:
        """Enruta a agentes especializados usando aprendizajes acumulados"""
        try:
            agent_results = {}

            # Usar agentes recomendados por el sistema de aprendizaje
            recommended_agents = intelligent_routing.get(
                "recommended_agents", [])

            if recommended_agents and intelligent_routing.get("learning_based", False):
                logger.info(
                    f"🧠 Usando enrutamiento basado en aprendizajes: {recommended_agents}")

                for agent_type in recommended_agents:
                    try:
                        agent_result = self._process_with_specific_agent(
                            conversation, agent_type, initial_analysis)
                        if agent_result:
                            agent_results[agent_type] = agent_result
                    except Exception as e:
                        logger.error(f"❌ Error con agente {agent_type}: {e}")
                        agent_results[agent_type] = {"error": str(e)}
            else:
                logger.info(
                    f"⚠️ Usando enrutamiento por defecto para categoría: {conversation.category}")
                # Enrutamiento por defecto
                default_agent = conversation.category if conversation.category else "coordinator"
                agent_result = self._process_with_specific_agent(
                    conversation, default_agent, initial_analysis)
                if agent_result:
                    agent_results[default_agent] = agent_result

            return agent_results

        except Exception as e:
            logger.error(f"❌ Error enrutando a agentes especializados: {e}")
            return {"error": str(e)}

    def _process_with_specific_agent(self, conversation: Conversation, agent_type: str,
                                     initial_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa la conversación con un agente específico"""
        try:
            logger.info(f"🤖 Procesando con agente: {agent_type}")

            # Por ahora, simular el procesamiento del agente
            # En el futuro, esto debería llamar a agentes reales
            agent_result = {
                "agent_type": agent_type,
                "conversation_id": conversation.id,
                "processing_timestamp": datetime.now().isoformat(),
                "confidence_score": 0.8,
                "recommendations": [],
                "actions_taken": [],
                "learning_generated": []
            }

            # Simular recomendaciones basadas en el tipo de agente
            if agent_type == "soporte":
                agent_result["recommendations"] = [
                    "Verificar historial de problemas similares",
                    "Aplicar soluciones probadas anteriormente",
                    "Escalar si es necesario"
                ]
            elif agent_type == "ventas":
                agent_result["recommendations"] = [
                    "Identificar necesidades del cliente",
                    "Presentar productos relevantes",
                    "Gestionar objeciones"
                ]
            elif agent_type == "coordinator":
                agent_result["recommendations"] = [
                    "Coordinar entre múltiples agentes",
                    "Asegurar resolución completa",
                    "Mantener consistencia en la experiencia"
                ]

            # Generar aprendizaje del agente
            agent_result["learning_generated"] = [
                {
                    "type": "agent_performance",
                    "content": f"Agente {agent_type} procesó conversación de categoría {conversation.category}",
                    "confidence": 0.8,
                    "category": conversation.category
                }
            ]

            return agent_result

        except Exception as e:
            logger.error(f"❌ Error procesando con agente {agent_type}: {e}")
            return {"error": str(e)}

    def _update_global_memory(self, conversation: Conversation,
                              synthesis: Dict[str, Any],
                              learning_outcome: Dict[str, Any]):
        """Actualiza la memoria global y guarda aprendizajes en la base de datos"""
        try:
            # Actualizar memoria en memoria
            self.global_memory["conversation_trends"][conversation.id] = {
                "category": conversation.category,
                "tags": conversation.tags,
                "timestamp": datetime.now().isoformat(),
                "synthesis": synthesis
            }

            # Actualizar métricas en la base de datos
            self._update_metrics_in_db(conversation, synthesis)

            # Actualizar métricas globales
            self._update_global_metrics(conversation, synthesis)

            logger.info(
                f"🧠 Memoria global actualizada para conversación: {conversation.id}")

        except Exception as e:
            logger.error(f"❌ Error actualizando memoria global: {e}")

    def _save_learnings_to_db(self, conversation: Conversation, learning_outcome: Dict[str, Any]):
        """Guarda los aprendizajes en la base de datos"""
        try:
            with get_session() as session:
                # 🚨 VALIDACIÓN: Verificar si ya existe un aprendizaje para esta conversación
                # Usar una búsqueda más simple para evitar errores de metadata
                existing_learning = session.exec(
                    select(AgentLearningModel)
                    .where(AgentLearningModel.agent_type == "super_agent")
                    .where(AgentLearningModel.learning_type == "conversation_learning")
                    .where(AgentLearningModel.content.contains(conversation.id))
                ).first()

                if existing_learning:
                    logger.info(
                        f"⚠️ Aprendizaje ya existe para conversación: {conversation.id}, no se duplica")
                    return

                # 🆕 Crear registro de aprendizaje más detallado
                patterns_count = len(
                    learning_outcome.get('patterns_identified', []))
                agent_optimizations = len(
                    learning_outcome.get('agent_optimizations', []))
                business_insights = len(
                    learning_outcome.get('business_insights', []))

                # Crear contenido más descriptivo
                content = f"Super Agente aprendió de conversación {conversation.id[:8]}... - {patterns_count} patrones, {agent_optimizations} optimizaciones, {business_insights} insights"

                # Crear registro de aprendizaje
                learning = AgentLearningModel(
                    agent_type="super_agent",
                    learning_type="conversation_learning",
                    content=content,
                    confidence_score=0.8,
                    category=conversation.category or "general",
                    metadata={
                        "conversation_id": conversation.id,
                        "patterns_count": patterns_count,
                        "agent_optimizations": agent_optimizations,
                        "business_insights": business_insights,
                        "tags_analyzed": conversation.tags or [],
                        "learning_timestamp": datetime.now().isoformat()
                    }
                )

                session.add(learning)
                session.commit()

                logger.info(
                    f"💾 Aprendizaje del Super Agente guardado en BD para conversación: {conversation.id}")

                # 🆕 También guardar aprendizajes específicos de tags si existen
                if conversation.tags:
                    self._save_tag_learnings_to_db(
                        session, conversation, learning_outcome)

                # 🆕 Guardar aprendizajes de patrones identificados
                self._save_pattern_learnings_to_db(
                    session, conversation, learning_outcome)

                # 🆕 Guardar insights de negocio
                self._save_business_insights_to_db(
                    session, conversation, learning_outcome)

                # 🆕 ACTUALIZAR MÉTRICAS DEL SUPER AGENTE EN LA BD
                self._update_super_agent_metrics(
                    session, conversation, learning_outcome)

        except Exception as e:
            logger.error(f"❌ Error guardando aprendizaje en BD: {e}")
            import traceback
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")

    def _save_tag_learnings_to_db(self, session: Session, conversation: Conversation, learning_outcome: Dict[str, Any]):
        """Guarda aprendizajes específicos relacionados con tags"""
        try:
            # Solo los 3 tags más importantes
            for tag in conversation.tags[:3]:
                # Crear aprendizaje específico del tag
                tag_learning = AgentLearningModel(
                    agent_type="super_agent",
                    learning_type="tag_learning",
                    content=f"Super Agente aprendió del tag '{tag}' en conversación {conversation.id[:8]}...",
                    confidence_score=0.7,
                    category=conversation.category or "general",
                    metadata={
                        "conversation_id": conversation.id,
                        "tag_analyzed": tag,
                        "tag_context": conversation.category,
                        "learning_timestamp": datetime.now().isoformat()
                    }
                )

                session.add(tag_learning)

            session.commit()
            logger.info(
                f"🏷️ Aprendizajes de tags del Super Agente guardados en BD")

        except Exception as e:
            logger.error(f"❌ Error guardando aprendizajes de tags: {e}")

    def _save_pattern_learnings_to_db(self, session: Session, conversation: Conversation, learning_outcome: Dict[str, Any]):
        """Guarda aprendizajes de patrones específicos identificados"""
        try:
            patterns = learning_outcome.get('patterns_identified', [])

            for pattern in patterns[:5]:  # Solo los 5 patrones más importantes
                # Crear aprendizaje específico del patrón
                pattern_learning = AgentLearningModel(
                    agent_type="super_agent",
                    learning_type="pattern_learning",
                    content=f"Super Agente identificó patrón: {pattern.get('type', 'unknown')} - {pattern.get('pattern', 'Sin descripción')[:50]}...",
                    confidence_score=pattern.get('confidence', 0.7),
                    category=conversation.category or "general",
                    metadata={
                        "conversation_id": conversation.id,
                        "pattern_type": pattern.get('type', 'unknown'),
                        "pattern_description": pattern.get('pattern', ''),
                        "pattern_confidence": pattern.get('confidence', 0.7),
                        "data_points": pattern.get('data_points', 1),
                        "learning_timestamp": datetime.now().isoformat()
                    }
                )

                session.add(pattern_learning)

            if patterns:
                session.commit()
                logger.info(
                    f"🔍 Aprendizajes de patrones del Super Agente guardados en BD: {len(patterns)} patrones")

        except Exception as e:
            logger.error(f"❌ Error guardando aprendizajes de patrones: {e}")

    def _save_business_insights_to_db(self, session: Session, conversation: Conversation, learning_outcome: Dict[str, Any]):
        """Guarda insights de negocio identificados por el Super Agente"""
        try:
            insights = learning_outcome.get('business_insights', [])

            for insight in insights[:3]:  # Solo los 3 insights más importantes
                # Crear aprendizaje específico del insight
                insight_learning = AgentLearningModel(
                    agent_type="super_agent",
                    learning_type="business_insight",
                    content=f"Super Agente identificó insight: {insight.get('type', 'unknown')} - {insight.get('content', 'Sin descripción')[:50]}...",
                    confidence_score=insight.get('confidence', 0.7),
                    category=conversation.category or "general",
                    metadata={
                        "conversation_id": conversation.id,
                        "insight_type": insight.get('type', 'unknown'),
                        "insight_content": insight.get('content', ''),
                        "insight_confidence": insight.get('confidence', 0.7),
                        "learning_timestamp": datetime.now().isoformat()
                    }
                )

                session.add(insight_learning)

            if insights:
                session.commit()
                logger.info(
                    f"💡 Insights de negocio del Super Agente guardados en BD: {len(insights)} insights")

        except Exception as e:
            logger.error(f"❌ Error guardando insights de negocio: {e}")

    def _update_super_agent_metrics(self, session: Session, conversation: Conversation, learning_outcome: Dict[str, Any]):
        """Actualiza las métricas del Super Agente en la base de datos"""
        try:
            if not hasattr(self, 'db_id') or not self.db_id:
                logger.warning(
                    "⚠️ Super Agente no tiene ID de BD, no se pueden actualizar métricas")
                return

            # Buscar el registro del Super Agente
            super_agent_record = session.exec(
                select(SuperAgentModel)
                .where(SuperAgentModel.id == self.db_id)
            ).first()

            if super_agent_record:
                # Actualizar métricas
                super_agent_record.total_conversations_processed += 1
                super_agent_record.total_learnings_generated += len(
                    learning_outcome.get('patterns_identified', []))
                super_agent_record.total_learnings_generated += len(
                    learning_outcome.get('agent_optimizations', []))
                super_agent_record.total_learnings_generated += len(
                    learning_outcome.get('business_insights', []))

                # Calcular nueva tasa de éxito
                if hasattr(self, 'aggregated_metrics') and self.aggregated_metrics.get('success_rate'):
                    current_success = super_agent_record.success_rate
                    new_success = learning_outcome.get('confidence_score', 0.8)
                    super_agent_record.success_rate = (
                        current_success + new_success) / 2

                # Actualizar metadatos
                super_agent_record.metadata.update({
                    "uptime_hours": (datetime.now() - self.creation_date).total_seconds() / 3600,
                    "total_learning_cycles": len(self.global_memory.get("learning_cycles", [])),
                    "total_optimizations": self.optimization_count,
                    "last_conversation_processed": conversation.id,
                    "last_learning_timestamp": datetime.now().isoformat()
                })

                super_agent_record.updated_at = datetime.now(COLOMBIA_TZ)
                session.add(super_agent_record)
                session.commit()

                logger.info(
                    f"📊 Métricas del Super Agente actualizadas en BD: {conversation.id}")
            else:
                logger.warning(
                    "⚠️ No se encontró registro del Super Agente en BD")

        except Exception as e:
            logger.error(
                f"❌ Error actualizando métricas del Super Agente: {e}")

    def _update_metrics_in_db(self, conversation: Conversation, synthesis: Dict[str, Any]):
        """Actualiza métricas en la base de datos"""
        try:
            with get_session() as session:
                # Crear métrica del agente
                metric = AgentMetricModel(
                    agent_id="super_agent",
                    conversation_id=conversation.id,
                    success_rate=synthesis.get("confidence_score", 0.8),
                    response_time=0.0,  # Por ahora 0
                    customer_satisfaction=0.8,  # Por ahora 0.8
                    metadata={
                        "agent_participation": synthesis.get("agent_participation", []),
                        "overall_sentiment": synthesis.get("overall_sentiment", "neutral")
                    }
                )

                session.add(metric)
                session.commit()

                logger.info(
                    f"📊 Métricas actualizadas en BD para conversación: {conversation.id}")

        except Exception as e:
            logger.error(f"❌ Error actualizando métricas en BD: {e}")

    def _sync_memory_to_database(self):
        """Sincroniza la información de la memoria con la base de datos"""
        try:
            if not self.db_id:
                logger.warning("⚠️ No hay ID de BD para sincronizar")
                return

            with get_session() as session:
                # Obtener el registro actual
                super_agent_record = session.exec(
                    select(SuperAgentModel).where(
                        SuperAgentModel.id == self.db_id)
                ).first()

                if not super_agent_record:
                    logger.error(
                        "❌ No se encontró el registro del Super Agente en BD")
                    return

                # Sincronizar campos de memoria
                super_agent_record.last_learning_cycle = (
                    self.global_memory["learning_cycles"][-1]["timestamp"]
                    if self.global_memory["learning_cycles"]
                    else None
                )

                super_agent_record.last_optimization = (
                    self.global_memory["optimization_history"][-1]["timestamp"]
                    if self.global_memory["optimization_history"]
                    else None
                )

                # Actualizar métricas
                super_agent_record.total_conversations_processed = self.aggregated_metrics[
                    "total_conversations"]
                super_agent_record.total_learnings_generated = len(
                    self.global_memory["learning_cycles"])
                super_agent_record.success_rate = self.aggregated_metrics["success_rate"]

                # Actualizar metadata
                super_agent_record.agent_metadata = {
                    "uptime_hours": (datetime.now() - self.creation_date).total_seconds() / 3600,
                    "total_learning_cycles": len(self.global_memory["learning_cycles"]),
                    "total_optimizations": self.optimization_count,
                    "total_patterns": len(self.global_memory["customer_patterns"]),
                    "total_trends": len(self.global_memory["conversation_trends"]),
                    "total_insights": len(self.global_memory["business_insights"]),
                    "last_sync": datetime.now(COLOMBIA_TZ).isoformat()
                }

                super_agent_record.updated_at = datetime.now(COLOMBIA_TZ)

                session.add(super_agent_record)
                session.commit()

                logger.info(
                    f"💾 Memoria sincronizada con BD - Ciclos: {len(self.global_memory['learning_cycles'])}, Optimizaciones: {self.optimization_count}")

        except Exception as e:
            logger.error(f"❌ Error sincronizando memoria con BD: {e}")
            import traceback
            logger.error(f"🔍 Traceback: {traceback.format_exc()}")


# Instancia global del Super Agente
super_agent = SuperAgent()
