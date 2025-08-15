# Integración de WhatsApp Business API con Agent 99

==================================================

## 🎯 **Descripción General**

Esta integración permite que **Agent 99** reciba y responda mensajes de WhatsApp en tiempo real, procesándolos automáticamente con el SuperAgente y los agentes especializados.

## 🔗 **Arquitectura del Sistema**

```
WhatsApp Business API → Webhook → FastAPI → SuperAgente → Agentes Especializados → Respuesta WhatsApp
```

## 🚀 **Configuración Inicial**

### **1. Crear Aplicación en Facebook Developers**

1. Ve a [Facebook Developers](https://developers.facebook.com/)
2. Crea una nueva aplicación o usa una existente
3. Agrega el producto **WhatsApp Business API**
4. Configura tu número de teléfono de WhatsApp Business

### **2. Obtener Credenciales**

#### **Phone Number ID**

- Ve a tu aplicación → WhatsApp → Getting Started
- Copia el **Phone Number ID**

#### **Access Token**

- Ve a tu aplicación → WhatsApp → Getting Started
- Copia el **Access Token** (permanente)

#### **Verify Token**

- Puede ser cualquier string (ej: `agent99_verify_token`)

### **3. Configurar Variables de Entorno**

Crea un archivo `.env` en la raíz del proyecto:

```bash
# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_ACCESS_TOKEN=EAABwzLixnjYBO...
WHATSAPP_VERIFY_TOKEN=agent99_verify_token
```

## 🔧 **Configuración del Webhook**

### **1. URL del Webhook**

```
https://tu-dominio.com/whatsapp/webhook
```

### **2. Verificación del Webhook**

WhatsApp enviará una solicitud GET para verificar:

```
GET /whatsapp/webhook?mode=subscribe&token=agent99_verify_token&challenge=1234567890
```

### **3. Recepción de Mensajes**

WhatsApp enviará mensajes POST al webhook:

```
POST /whatsapp/webhook
```

## 📱 **Endpoints Disponibles**

### **Webhook**

- `GET /whatsapp/webhook` - Verificación del webhook
- `POST /whatsapp/webhook` - Recepción de mensajes

### **Envío de Mensajes**

- `POST /whatsapp/send-message` - Mensaje de texto
- `POST /whatsapp/send-template` - Mensaje de plantilla
- `POST /whatsapp/send-interactive` - Mensaje interactivo

### **Estado y Monitoreo**

- `GET /whatsapp/service-status` - Estado del servicio
- `GET /whatsapp/message-status/{message_id}` - Estado de un mensaje

## 🧠 **Flujo de Procesamiento**

### **1. Recepción del Mensaje**

```python
# WhatsApp envía mensaje al webhook
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "573001234567",
          "text": {"body": "¿Tienen leggings?"},
          "id": "msg_123",
          "timestamp": "1234567890"
        }]
      }
    }]
  }]
}
```

### **2. Procesamiento Automático**

1. **Extracción**: Se extrae número, texto y timestamp
2. **Conversación**: Se crea objeto `Conversation`
3. **SuperAgente**: Se procesa con `super_agent.process_conversation()`
4. **Aprendizaje**: Se ejecuta el ciclo de aprendizaje automático
5. **Respuesta**: Se genera respuesta automática basada en la categoría
6. **Envío**: Se envía respuesta por WhatsApp Business API

### **3. Respuesta Automática**

```python
# Basada en la categoría detectada
if category == "ventas":
    return "¡Hola! Gracias por tu consulta sobre ventas. Nuestro equipo especializado te atenderá en breve. 🛍️"
elif category == "soporte":
    return "¡Hola! Entiendo que necesitas soporte técnico. Nuestro equipo de asistencia te ayudará pronto. 🔧"
```

## 🔍 **Pruebas y Testing**

### **1. Verificar Estado del Servicio**

```bash
curl "http://localhost:8000/whatsapp/service-status"
```

### **2. Enviar Mensaje de Prueba**

```bash
curl -X POST "http://localhost:8000/whatsapp/send-message" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "573001234567", "message": "Mensaje de prueba"}'
```

### **3. Simular Webhook de WhatsApp**

```bash
curl -X POST "http://localhost:8000/whatsapp/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "573001234567",
            "text": {"body": "¿Tienen leggings?"},
            "id": "msg_123",
            "timestamp": "1234567890"
          }]
        }
      }]
    }]
  }'
```

## 🚨 **Solución de Problemas**

### **Error: "Configuración de WhatsApp incompleta"**

- Verifica que todas las variables de entorno estén configuradas
- Asegúrate de que el archivo `.env` esté en la raíz del proyecto

### **Error: "Verificación de webhook fallida"**

- Verifica que el `WHATSAPP_VERIFY_TOKEN` coincida con el configurado en Facebook
- Asegúrate de que la URL del webhook sea accesible públicamente

### **Error: "Error enviando mensaje"**

- Verifica que el `WHATSAPP_ACCESS_TOKEN` sea válido
- Confirma que el `WHATSAPP_PHONE_NUMBER_ID` sea correcto
- Revisa los logs para más detalles del error

## 📊 **Monitoreo y Logs**

### **Logs Importantes**

- `📱 Mensaje WhatsApp recibido` - Mensaje entrante
- `✅ Mensaje procesado y respondido` - Procesamiento exitoso
- `📤 Enviando mensaje WhatsApp` - Envío de respuesta
- `✅ Mensaje WhatsApp enviado` - Envío exitoso

### **Métricas del Sistema**

- Total de mensajes procesados
- Tasa de respuesta automática
- Tiempo de procesamiento promedio
- Categorías de mensajes más comunes

## 🔮 **Próximos Pasos**

### **Funcionalidades Futuras**

1. **Respuestas Inteligentes**: Usar LLM para generar respuestas más naturales
2. **Escalamiento**: Múltiples números de WhatsApp
3. **Plantillas Dinámicas**: Respuestas basadas en contexto del cliente
4. **Integración con CRM**: Sincronización con sistemas de gestión de clientes
5. **Analytics Avanzados**: Métricas de conversión y satisfacción

## 📞 **Soporte**

Para problemas técnicos o preguntas sobre la integración:

- Revisa los logs del sistema
- Verifica la configuración de variables de entorno
- Consulta la documentación de [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- Revisa el estado del servicio con `/whatsapp/service-status`
