# 🤖 Integración de IA con Groq Cloud

## ✅ **Características Implementadas**

Se han integrado **3 funcionalidades de IA** usando **Groq Cloud** (Llama 3.1 70B):

1. ✅ **Recomendador de Productos Inteligente**
2. ✅ **Generación Automática de Descripciones**
3. ✅ **Chatbot de Atención al Cliente**

---

## 📋 **Pasos para Activar la IA**

### **1. Obtener API Key de Groq (GRATIS)**

1. Ve a: **https://console.groq.com**
2. Regístrate con tu email o GitHub/Google
3. Confirma tu email
4. En el dashboard, ve a **"API Keys"**
5. Click en **"Create API Key"**
6. Copia la key (formato: `gsk_xxxxxxxxxxxxx`)

### **2. Configurar tu API Key**

Edita tu archivo `.env` y agrega:

```env
GROQ_API_KEY=gsk_tu_api_key_real_aqui
```

### **3. Instalar Dependencias**

```bash
pip install -r requirements.txt
```

Esto instalará:
- `groq>=0.11.0` - SDK oficial de Groq Cloud

### **4. Probar la Integración**

```bash
python manage.py runserver
```

---

## 🔌 **Endpoints Disponibles**

### **1. Recomendador de Productos Inteligente**

**Endpoint:** `POST /api/ia/productos/recomendar/`

**Descripción:** Analiza el historial de compras del cliente y recomienda productos usando IA

**Autenticación:** No requerida (público)

**Body:**
```json
{
    "rut_cliente": "12345678-9",
    "limite": 3
}
```

**Response:**
```json
{
    "cliente": {
        "rut": "12345678-9",
        "nombre": "Juan Pérez"
    },
    "recomendaciones": [
        {
            "producto_id": 5,
            "nombre": "Teclado Mecánico RGB",
            "codigo": "TECH-KB-001",
            "precio": 45000.00,
            "stock": 25,
            "razon": "Basado en tu compra anterior de mouse gamer, este teclado complementaría tu setup",
            "confianza": "alta"
        },
        {
            "producto_id": 8,
            "nombre": "Mousepad XXL",
            "codigo": "ACC-MP-002",
            "precio": 12000.00,
            "stock": 50,
            "razon": "Los clientes que compraron mouse y teclado también adquieren mousepad",
            "confianza": "media"
        }
    ],
    "mensaje": "Estos productos podrían interesarte basado en tus compras anteriores"
}
```

**Ejemplo de Uso (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/ia/productos/recomendar/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        rut_cliente: '12345678-9',
        limite: 3
    })
});

const data = await response.json();
console.log(data.recomendaciones);
```

---

### **2. Generación Automática de Descripciones**

**Endpoint:** `POST /api/ia/productos/{producto_id}/generar-descripcion/`

**Descripción:** Genera descripciones atractivas y profesionales para productos usando IA

**Autenticación:** ✅ Requerida (solo admin con JWT)

**Headers:**
```
Authorization: Bearer tu_token_jwt_aqui
```

**Response:**
```json
{
    "producto": {
        "id": 1,
        "nombre": "Mouse Gamer Pro X",
        "codigo": "MGP-X-2024",
        "precio": 35000.00
    },
    "descripcion_corta": "Mouse gamer de alta precisión con sensor óptico de 16000 DPI y diseño ergonómico para sesiones prolongadas",
    "descripcion_larga": "El Mouse Gamer Pro X redefine la experiencia de juego con su sensor óptico de última generación que ofrece 16000 DPI ajustables. Su diseño ergonómico ha sido meticulosamente desarrollado para proporcionar comodidad durante largas sesiones de gaming. Equipado con 8 botones programables y retroiluminación RGB personalizable, este mouse combina rendimiento profesional con estilo. La construcción premium garantiza durabilidad, mientras que el cable trenzado previene enredos. Ideal para gamers competitivos y usuarios que demandan precisión absoluta.",
    "palabras_clave": [
        "mouse gamer",
        "16000 dpi",
        "ergonómico",
        "rgb",
        "gaming profesional"
    ],
    "beneficios": [
        "Precisión extrema con sensor de 16000 DPI para movimientos exactos",
        "Diseño ergonómico que reduce la fatiga en sesiones largas",
        "8 botones programables para personalizar tu experiencia de juego",
        "Iluminación RGB customizable para combinar con tu setup"
    ]
}
```

**Ejemplo de Uso (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/ia/productos/1/generar-descripcion/', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
});

const data = await response.json();
console.log(data.descripcion_larga);
```

---

### **3. Chatbot de Atención al Cliente**

**Endpoint:** `POST /api/ia/chat/`

**Descripción:** Chatbot inteligente que responde preguntas sobre productos, ventas, políticas y más

**Autenticación:** No requerida (público)

**Body:**
```json
{
    "mensaje": "¿Cuál es el horario de atención?",
    "contexto": {
        "venta_numero": "20241128-0001",
        "producto_id": 5
    }
}
```

**Response:**
```json
{
    "respuesta": "Nuestro horario de atención es de Lunes a Viernes de 9:00 a 18:00 horas, y los Sábados de 10:00 a 14:00 horas. ¿Hay algo más en lo que pueda ayudarte?",
    "tipo": "informacion",
    "requiere_humano": false,
    "sugerencias": [
        "¿Cuáles son los métodos de pago disponibles?",
        "¿Cuánto demora el despacho a mi región?"
    ]
}
```

**Tipos de Consultas:**
- `informacion` - Información general de la tienda
- `consulta_venta` - Preguntas sobre ventas específicas
- `consulta_producto` - Preguntas sobre productos
- `politicas` - Políticas de devolución, garantía, etc.
- `otro` - Otras consultas

**Ejemplo con Contexto de Venta:**
```json
{
    "mensaje": "¿Cuál es el estado de mi pedido?",
    "contexto": {
        "venta_numero": "20241128-0001"
    }
}
```

**Response con Contexto:**
```json
{
    "respuesta": "Tu pedido #20241128-0001 realizado el 28 de noviembre por un total de $85,000 está confirmado. Incluye Mouse Gamer Pro X (2 unidades) y Teclado Mecánico RGB (1 unidad). El despacho se realizará en las próximas 24-48 horas en Santiago.",
    "tipo": "consulta_venta",
    "requiere_humano": false,
    "sugerencias": [
        "¿Puedo cancelar mi pedido?",
        "¿Cómo puedo rastrear mi pedido?"
    ]
}
```

**Ejemplo de Uso (JavaScript/Angular):**
```typescript
// chat.service.ts
async enviarMensaje(mensaje: string, contexto?: any) {
    const response = await fetch('http://localhost:8000/api/ia/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mensaje: mensaje,
            contexto: contexto
        })
    });
    
    return await response.json();
}

// Uso en componente
const respuesta = await this.chatService.enviarMensaje(
    '¿Tienen mouse gamer disponible?'
);
console.log(respuesta.respuesta);
```

---

## 💡 **Casos de Uso Recomendados**

### **Frontend Angular**

#### **1. Página de Producto - Recomendaciones**
```typescript
// product-detail.component.ts
ngOnInit() {
    // Mostrar recomendaciones basadas en el cliente
    this.productService.getRecomendaciones(this.clienteRut)
        .subscribe(data => {
            this.productosRecomendados = data.recomendaciones;
        });
}
```

#### **2. Panel Admin - Generador de Descripciones**
```typescript
// admin-product.component.ts
generarDescripcion(productoId: number) {
    this.productService.generarDescripcion(productoId)
        .subscribe(data => {
            this.producto.descripcion = data.descripcion_larga;
            this.producto.keywords = data.palabras_clave.join(', ');
        });
}
```

#### **3. Widget de Chat - Soporte**
```typescript
// chat-widget.component.ts
enviarMensaje() {
    this.chatService.enviarMensaje(this.mensajeUsuario)
        .subscribe(response => {
            this.agregarMensaje('bot', response.respuesta);
            this.mostrarSugerencias(response.sugerencias);
        });
}
```

---

## 🚀 **Ventajas de Groq Cloud**

| Característica | Groq Cloud | OpenAI |
|---------------|-----------|--------|
| **Velocidad** | ⚡ Ultra rápido (10x más rápido) | Estándar |
| **Costo** | 💰 Más económico | Más caro |
| **Plan Gratuito** | ✅ 14,400 requests/día | ❌ Requiere pago |
| **Modelos** | Llama 3.1, Mixtral, Gemma | GPT-4, GPT-3.5 |
| **Tarjeta Requerida** | ❌ No | ✅ Sí |

---

## 🔒 **Seguridad y Mejores Prácticas**

### **1. Protege tu API Key**
- ✅ Nunca subas la API key a Git
- ✅ Usa variables de entorno (`.env`)
- ✅ No la expongas en el frontend
- ✅ Rótala periódicamente

### **2. Rate Limiting**
Groq tiene límites:
- **Free Tier:** 14,400 requests/día (600/hora)
- Implementa caché si es necesario
- Maneja errores de cuota excedida

### **3. Validación de Datos**
- Valida siempre las respuestas de la IA
- No confíes ciegamente en el output
- Sanitiza inputs del usuario

### **4. Privacidad**
- No envíes datos sensibles (contraseñas, tarjetas)
- Anonimiza información personal cuando sea posible
- Cumple con GDPR si aplica

---

## 🧪 **Testing Manual**

### **Probar con cURL**

**1. Recomendador:**
```bash
curl -X POST http://localhost:8000/api/ia/productos/recomendar/ \
  -H "Content-Type: application/json" \
  -d '{"rut_cliente": "12345678-9", "limite": 3}'
```

**2. Generador de Descripciones:**
```bash
# Primero obtén un token JWT
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "tu_password"}'

# Usa el token para generar descripción
curl -X POST http://localhost:8000/api/ia/productos/1/generar-descripcion/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu_token_aqui"
```

**3. Chatbot:**
```bash
curl -X POST http://localhost:8000/api/ia/chat/ \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "¿Cuál es el horario de atención?"}'
```

---

## 📊 **Monitoreo y Logs**

Los servicios de IA registran logs automáticamente:

```python
# Ver logs en consola
python manage.py runserver

# Logs de errores aparecerán como:
# ERROR: Error en chatbot_atencion: [detalle del error]
# ERROR: Error parseando respuesta JSON: [detalle]
```

---

## 🔧 **Troubleshooting**

### **Error: "GROQ_API_KEY no está configurada"**
- Verifica que el archivo `.env` existe
- Confirma que la variable `GROQ_API_KEY` está definida
- Reinicia el servidor Django

### **Error: "Import groq could not be resolved"**
```bash
pip install groq>=0.11.0
```

### **Error 401: Unauthorized**
- Tu API key es inválida o expiró
- Genera una nueva en https://console.groq.com

### **Error 429: Rate Limit Exceeded**
- Has excedido el límite gratuito (14,400/día)
- Espera unas horas o actualiza tu plan

### **Respuestas Vacías o Errores JSON**
- El modelo puede generar JSON inválido ocasionalmente
- El servicio tiene fallbacks automáticos
- Revisa los logs para más detalles

---

## 📈 **Próximas Mejoras Sugeridas**

1. ✅ Caché de recomendaciones (Redis)
2. ✅ Historial de conversaciones del chatbot
3. ✅ Análisis de sentimientos en reviews
4. ✅ Predicción de demanda de productos
5. ✅ Validación automática de datos de clientes
6. ✅ Detección de fraude en compras

---

## 📞 **Soporte**

- **Documentación Groq:** https://console.groq.com/docs
- **Modelos disponibles:** https://console.groq.com/docs/models
- **Pricing:** https://console.groq.com/settings/billing

---

## 📝 **Changelog**

### v1.0.0 (2024-11-30)
- ✅ Implementado recomendador de productos con IA
- ✅ Agregado generador automático de descripciones
- ✅ Creado chatbot de atención al cliente
- ✅ Integración con Groq Cloud (Llama 3.1 70B)
- ✅ Documentación completa de endpoints

---

**¡Tu sistema de ventas ahora tiene inteligencia artificial! 🎉**
