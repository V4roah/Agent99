# 🤖 Agent99 - Sistema Inteligente para Pequeñas Empresas

**Agent99** es un sistema inteligente que automatiza procesos para pequeñas empresas mediante scraping de productos, análisis de conversaciones de WhatsApp y clasificación inteligente de interacciones.

## 🎯 Características Principales

### 🔍 **Scraping Inteligente**

- **Playwright**: Scraping de páginas con JavaScript dinámico
- **BeautifulSoup**: Procesamiento eficiente de HTML
- **Extracción automática** de productos, precios y detalles

### 💬 **Análisis de WhatsApp**

- **Parseo automático** de exports de conversaciones
- **Clasificación inteligente** por categorías (ventas, soporte, reclamos)
- **Análisis de sentimiento** y extracción de entidades
- **Métricas de conversación** (tiempo de respuesta, participación)

### 🧠 **Sistema de Agentes Especializados**

- **Agente de Ventas**: Análisis de intención de compra y cierre de ventas
- **Agente de Soporte**: Resolución de problemas y escalación inteligente
- **Agente de Reclamos**: Manejo empático y resolución prioritaria
- **Aprendizaje cruzado** entre agentes para mejora continua

### 🧠 **Super Agente - Cerebro Central**

- **Coordinación Inteligente**: Orquesta todos los agentes especializados
- **Aprendizaje Continuo**: Se retroalimenta de cada conversación
- **Optimización Automática**: Mejora parámetros del sistema cada 24h
- **Memoria Global**: Mantiene patrones de clientes y tendencias
- **Insights de Negocio**: Genera análisis automático del rendimiento

### 🔍 **Búsqueda Vectorial**

- **FAISS**: Búsquedas semánticas ultra-rápidas
- **Embeddings locales** con Sentence Transformers
- **Búsqueda por similitud** en conversaciones y productos

### 🏷️ **Sistema de Etiquetas Inteligentes**

- **Machine Learning**: Generación automática de etiquetas usando scikit-learn
- **Análisis Semántico**: Embeddings para etiquetas contextuales
- **Etiquetas Predefinidas**: Categorías organizadas por dominio
- **Sugerencias Inteligentes**: Autocompletado y búsqueda de etiquetas

### 🤖 **LLM Local con Ollama**

- **Modelos locales** (gemma3:1b recomendado para empezar)
- **Sin dependencias externas** ni costos de API
- **Procesamiento en tiempo real** de conversaciones

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- Ollama instalado ([Descargar aquí](https://ollama.ai))
- 4GB+ RAM disponible

### 1. Clonar y configurar entorno

```bash
git clone <tu-repositorio>
cd Agent99

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configuración automática

```bash
python setup.py
```

Este script:

- ✅ Verifica dependencias
- 🔧 Instala navegadores de Playwright
- 📥 Descarga modelos de embeddings
- 📁 Crea directorios necesarios
- ⚙️ Genera archivo de configuración

### 3. Descargar modelo de Ollama

```bash
ollama pull gemma3:1b
```

## 🏃‍♂️ Uso Rápido

### Iniciar servidor

```bash
python main.py
```

### Acceder a la API

- **Documentación**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

## 📚 API Endpoints

### 🔍 **Scraping**

```http
POST /scraping/scrape
{
  "url": "https://ejemplo.com/productos",
  "wait_selector": ".product-card"
}
```

### 💬 **Análisis de WhatsApp**

```http
POST /whatsapp/analyze
{
  "conversation_text": "[01/01/2024, 10:00:00] Cliente: Hola..."
}
```

### 🤖 **Procesamiento con Agentes**

```http
POST /agents/process
{
  "conversation_text": "Quiero comprar leggins",
  "customer_name": "María"
}
```

### 🔍 **Búsqueda Vectorial**

```http
POST /vector/search
{
  "query": "problemas con entrega",
  "k": 5
}
```

### 🧠 **Generación con LLM**

```http
POST /llm/generate
{
  "prompt": "Responde a un cliente enojado",
  "system_prompt": "Eres un agente de soporte empático",
  "temperature": 0.7
}
```

### 🎯 **Clasificación**

```http
POST /classification/classify
{
  "texts": ["Quiero comprar", "Tengo un problema"]
}
```

### 🔧 **Gestión de Modelos**

```http
GET /models/ollama
POST /models/ollama/switch?model_name=gemma3:4b
```

### 🏷️ **Sistema de Etiquetas Inteligentes**

```http
# Generar etiquetas inteligentes
POST /tagging/generate
{
  "text": "Hola, me interesa comprar un producto",
  "category": "ventas",
  "max_tags": 8
}

# Sugerir etiquetas
POST /tagging/suggest
{
  "partial_tag": "comp",
  "category": "ventas"
}

# Estadísticas del sistema
GET /tagging/statistics

# Categorías disponibles
GET /tagging/categories

# Etiquetas por categoría
GET /tagging/tags/ventas

# Búsqueda de etiquetas
GET /tagging/search?query=producto&category=ventas&max_results=10
```

### 🧠 **Super Agente - Cerebro Central**

```http
# Procesar conversación con Super Agente
POST /super-agent/process
{
  "conversation_id": "conv_123",
  "customer_id": "cust_456",
  "category": "ventas",
  "tags": ["producto", "precio"],
  "content": "Hola, me interesa comprar un producto"
}

# Estado del Super Agente
GET /super-agent/status

# Insights de negocio
GET /super-agent/insights

# Memoria global del sistema
GET /super-agent/memory

# Métricas agregadas
GET /super-agent/metrics

# Ciclos de aprendizaje
GET /super-agent/learning-cycles

# Historial de optimizaciones
GET /super-agent/optimization-history

# Disparar optimización manual
POST /super-agent/optimize

# Resetear memoria (desarrollo)
POST /super-agent/reset-memory
```

## 📊 Casos de Uso

### 1. **Análisis de Conversaciones de WhatsApp**

```python
from services.whatsapp_analyzer import whatsapp_analyzer

# Analizar export de WhatsApp
with open("whatsapp_export.txt", "r", encoding="utf-8") as f:
    conversations = whatsapp_analyzer.parse_whatsapp_export(f.read())

# Obtener insights
for conv in conversations:
    analysis = whatsapp_analyzer.analyze_conversation(conv)
    insights = whatsapp_analyzer.get_conversation_insights(conv)
    print(f"Cliente: {conv.customer_name}")
    print(f"Categoría: {conv.category}")
    print(f"Sentimiento: {conv.sentiment}")
```

### 2. **Scraping de Productos**

```python
from services.scraping import fetch_html, extract_products

# Obtener HTML de página
html = fetch_html("https://tienda.com/productos", ".product-card")

# Extraer productos
products = extract_products(html)
for product in products:
    print(f"{product['title']}: {product['price']}")
```

### 3. **Uso de Agentes Especializados**

```python
from services.agents import agent_orchestrator

# Procesar conversación con agentes
result = agent_orchestrator.route_conversation(conversation)
print(f"Agente: {result['agent_id']}")
print(f"Respuesta: {result['response']}")
print(f"Próxima acción: {result['next_action']}")
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Ollama
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=gemma3:1b

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Scraping
SCRAPING_TIMEOUT=8000
SCRAPING_HEADLESS=true
```

### Modelos de Ollama Recomendados

| Modelo           | Tamaño | Uso Recomendado                    |
| ---------------- | ------ | ---------------------------------- |
| `gemma3:1b`      | ~2GB   | **Inicio** - Rápido y eficiente    |
| `gemma3:4b`      | ~5GB   | **Producción** - Mejor calidad     |
| `qwen3:4b`       | ~5GB   | **Alternativa** - Buen rendimiento |
| `deepseek-r1:8b` | ~9GB   | **Avanzado** - Máxima calidad      |

## 🏗️ Arquitectura

```
Agent99/
├── main.py                 # API FastAPI principal (solo configuración)
├── config.py              # Configuración centralizada
├── setup.py               # Script de configuración
├── requirements.txt       # Dependencias Python
├── routes/                # 🆕 Endpoints organizados por funcionalidad
│   ├── __init__.py        # Inicialización del paquete
│   ├── api.py             # Agrupador principal de rutas
│   ├── basic.py           # Endpoints básicos (health, root)
│   ├── models.py          # Gestión de modelos Ollama
│   ├── classification.py  # Clasificación ML
│   ├── scraping.py        # Scraping web
│   ├── llm.py            # Generación y análisis con LLM
│   ├── whatsapp.py        # Análisis de WhatsApp
│   ├── agents.py         # Sistema de agentes
│   ├── vector.py         # Búsqueda vectorial
│   ├── tagging.py        # Sistema de etiquetas inteligentes
│   └── super_agent.py    # Super Agente - Cerebro central
├── services/              # Lógica de negocio
│   ├── scraping.py        # Scraping con Playwright
│   ├── classify.py        # Clasificación con scikit-learn
│   ├── vector_store.py    # Búsqueda vectorial FAISS
│   ├── llm.py            # Integración con Ollama
│   ├── whatsapp_analyzer.py # Análisis de conversaciones
│   ├── agents.py         # Sistema de agentes especializados
│   ├── smart_tagging.py  # Sistema de etiquetas inteligentes
│   └── super_agent.py    # Super Agente - Cerebro central
├── models/                # Modelos entrenados
├── data/                  # Datos de entrenamiento
└── venv/                  # Entorno virtual
```

## 🔧 Desarrollo

### Estructura de Rutas

- **`routes/basic.py`**: Endpoints básicos del sistema
- **`routes/models.py`**: Gestión de modelos de Ollama
- **`routes/classification.py`**: Entrenamiento y clasificación ML
- **`routes/scraping.py`**: Scraping de páginas web
- **`routes/llm.py`**: Generación y análisis con LLM
- **`routes/whatsapp.py`**: Análisis de conversaciones de WhatsApp
- **`routes/agents.py`**: Sistema de agentes especializados
- **`routes/vector.py`**: Búsqueda vectorial y gestión del vector store

### Estructura de Servicios

- **`scraping.py`**: Manejo de web scraping
- **`classify.py`**: Clasificación con scikit-learn
- **`vector_store.py`**: Almacenamiento y búsqueda vectorial
- **`llm.py`**: Integración con Ollama
- **`whatsapp_analyzer.py`**: Análisis de conversaciones
- **`agents.py`**: Sistema de agentes especializados

### Agregar Nuevos Endpoints

```python
# En routes/nuevo_modulo.py
from fastapi import APIRouter

router = APIRouter(prefix="/nuevo", tags=["nuevo"])

@router.get("/endpoint")
def nuevo_endpoint():
    return {"message": "Nuevo endpoint"}

# En routes/api.py
from . import nuevo_modulo
api_router.include_router(nuevo_modulo.router)
```

### Agregar Nuevos Agentes

```python
class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom_agent", "custom_type")

    def process(self, conversation: Conversation, context: str = "") -> Dict[str, Any]:
        # Lógica personalizada del agente
        pass

# Registrar en el orquestador
agent_orchestrator.agents["custom"] = CustomAgent()
```

## 📈 Monitoreo y Métricas

### Rendimiento de Agentes

```http
GET /agents/performance
```

### Estadísticas del Vector Store

```http
GET /vector/stats
```

### Estado del Sistema

```http
GET /health
```

## 🚨 Solución de Problemas

### Ollama no responde

```bash
# Verificar que Ollama esté ejecutándose
ollama list

# Reiniciar servicio
ollama serve
```

### Error de Playwright

```bash
# Reinstalar navegadores
playwright install chromium
```

### Modelo de embeddings no descarga

```bash
# Verificar conexión a internet
# Ejecutar setup.py nuevamente
python setup.py
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/Agent99/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/Agent99/wiki)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/Agent99/discussions)

---

**Agent99** - Transformando pequeñas empresas con inteligencia artificial 🤖✨
