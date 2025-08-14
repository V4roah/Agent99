import ollama
from typing import List, Dict, Any, Optional
import json
import time


class OllamaService:
    def __init__(self, model_name: str = "gemma3:1b"):
        self.model_name = model_name
        self.client = ollama.Client()

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> str:
        """Genera texto usando el modelo local"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": temperature,
                    "top_p": 0.9,
                    "top_k": 40
                }
            )

            return response['message']['content']

        except Exception as e:
            print(f"Error generating with Ollama: {e}")
            return f"Error: {str(e)}"

    def classify_conversation(self, conversation: str, categories: List[str]) -> Dict[str, Any]:
        """Clasifica una conversación en categorías predefinidas"""
        system_prompt = f"""Eres un clasificador experto de conversaciones. 
        Debes clasificar la conversación en una de estas categorías: {', '.join(categories)}
        
        Responde solo con un JSON válido con esta estructura:
        {{
            "category": "nombre_categoria",
            "confidence": 0.95,
            "reasoning": "explicación breve de por qué",
            "tags": ["tag1", "tag2"],
            "sentiment": "positivo/negativo/neutral"
        }}"""

        prompt = f"Clasifica esta conversación:\n\n{conversation}"

        try:
            response = self.generate(prompt, system_prompt, temperature=0.3)

            # Intentar parsear JSON
            if response.startswith("```json"):
                response = response.split("```json")[1].split("```")[0]
            elif response.startswith("```"):
                response = response.split("```")[1].split("```")[0]

            result = json.loads(response.strip())
            return result

        except Exception as e:
            print(f"Error parsing classification: {e}")
            return {
                "category": "unknown",
                "confidence": 0.0,
                "reasoning": f"Error parsing response: {str(e)}",
                "tags": [],
                "sentiment": "neutral"
            }

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extrae entidades del texto (productos, precios, fechas, etc.)"""
        system_prompt = """Eres un extractor de entidades experto. 
        Extrae información relevante del texto y responde en JSON.
        
        Estructura esperada:
        {
            "products": ["producto1", "producto2"],
            "prices": ["$100", "$200"],
            "dates": ["2024-01-01"],
            "quantities": ["3", "5"],
            "sizes": ["M", "L"],
            "colors": ["rojo", "azul"],
            "customer_info": {
                "name": "nombre",
                "phone": "teléfono",
                "email": "email"
            }
        }"""

        prompt = f"Extrae entidades de este texto:\n\n{text}"

        try:
            response = self.generate(prompt, system_prompt, temperature=0.1)

            # Limpiar respuesta
            if response.startswith("```json"):
                response = response.split("```json")[1].split("```")[0]
            elif response.startswith("```"):
                response = response.split("```")[1].split("```")[0]

            result = json.loads(response.strip())
            return result

        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {
                "products": [],
                "prices": [],
                "dates": [],
                "quantities": [],
                "sizes": [],
                "colors": [],
                "customer_info": {}
            }

    def analyze_intent(self, conversation: str, context: str = "", intent_type: str = "general") -> Dict[str, Any]:
        """Analiza la intención del usuario en una conversación"""

        intent_prompts = {
            "purchase_intent": "Eres un analista de intenciones de compra. Analiza si el cliente tiene intención de comprar y qué tan urgente es.",
            "problem_analysis": "Eres un analista de problemas. Identifica el tipo de problema, su severidad y qué tan urgente es la solución.",
            "complaint_analysis": "Eres un analista de quejas. Identifica el tipo de queja, su severidad y qué tan urgente es la resolución.",
            "general": "Eres un analista de intenciones. Identifica la intención principal del usuario en la conversación."
        }

        system_prompt = intent_prompts.get(
            intent_type, intent_prompts["general"])
        system_prompt += """
        
        Responde solo con un JSON válido con esta estructura:
        {
            "intent": "descripción_de_la_intención",
            "confidence": 0.95,
            "urgency": "low/medium/high",
            "details": "explicación_detallada",
            "next_steps": ["paso1", "paso2"]
        }"""

        if context:
            system_prompt += f"\n\nContexto adicional: {context}"

        prompt = f"Analiza la intención en esta conversación:\n\n{conversation}"

        try:
            response = self.generate(prompt, system_prompt, temperature=0.3)

            # Limpiar respuesta
            if response.startswith("```json"):
                response = response.split("```json")[1].split("```")[0]
            elif response.startswith("```"):
                response = response.split("```")[1].split("```")[0]

            result = json.loads(response.strip())
            return result

        except Exception as e:
            print(f"Error analyzing intent: {e}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "urgency": "low",
                "details": f"Error parsing response: {str(e)}",
                "next_steps": ["continue_conversation"]
            }

    def generate_response(self, conversation: str, context: str = "", agent_type: str = "general") -> str:
        """Genera una respuesta apropiada para la conversación"""

        agent_prompts = {
            "ventas": "Eres un agente de ventas amigable y profesional. Ayuda al cliente a encontrar productos, resolver dudas y cerrar ventas.",
            "soporte": "Eres un agente de soporte técnico. Ayuda a resolver problemas, explicar procesos y dar soluciones claras.",
            "reclamos": "Eres un agente especializado en manejo de reclamos. Escucha con empatía, documenta el problema y ofrece soluciones.",
            "general": "Eres un asistente virtual amigable y útil. Responde de manera clara y profesional."
        }

        system_prompt = agent_prompts.get(agent_type, agent_prompts["general"])

        if context:
            system_prompt += f"\n\nContexto adicional: {context}"

        prompt = f"Conversación:\n{conversation}\n\nResponde de manera apropiada:"

        return self.generate(prompt, system_prompt, temperature=0.7)

    def list_models(self) -> List[str]:
        """Lista los modelos disponibles en Ollama"""
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def switch_model(self, model_name: str) -> bool:
        """Cambia al modelo especificado"""
        try:
            # Verificar si el modelo existe
            models = self.list_models()
            if model_name in models:
                self.model_name = model_name
                return True
            else:
                print(
                    f"Modelo {model_name} no encontrado. Modelos disponibles: {models}")
                return False
        except Exception as e:
            print(f"Error switching model: {e}")
            return False


# Instancia global del servicio LLM
llm_service = OllamaService()
