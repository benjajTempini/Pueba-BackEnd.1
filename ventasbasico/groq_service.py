"""
Servicio centralizado para interactuar con Groq Cloud API
Proporciona funcionalidades de IA para el sistema de ventas
"""
from groq import Groq
from django.conf import settings
import logging
import json

logger = logging.getLogger(__name__)


class GroqService:
    """
    Cliente para interactuar con Groq Cloud API
    Utiliza el modelo Llama 3.3 70B para análisis y generación de texto
    """
    
    def __init__(self):
        """Inicializa el cliente de Groq con la API key desde settings"""
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY no está configurada. "
                "Agrega GROQ_API_KEY=tu_clave en el archivo .env"
            )
        self.client = Groq(api_key=api_key)
        # Usar Llama 3.3 70B - modelo más reciente (reemplaza a 3.1-70b-versatile)
        self.model = "llama-3.3-70b-versatile"
    
    def _call_groq(self, messages, temperature=0.7, max_tokens=1024):
        """
        Método interno para realizar llamadas a Groq API
        
        Args:
            messages: Lista de mensajes en formato ChatML
            temperature: Controla la aleatoriedad (0-2)
            max_tokens: Máximo de tokens en la respuesta
        
        Returns:
            str: Respuesta generada por el modelo
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error llamando a Groq API: {str(e)}")
            raise Exception(f"Error en Groq API: {str(e)}")
    
    def recomendar_productos(self, historial_cliente, productos_disponibles, limite=3):
        """
        Recomienda productos basándose en el historial de compras del cliente
        
        Args:
            historial_cliente: Dict con información de compras previas
            productos_disponibles: Lista de productos disponibles en tienda
            limite: Número máximo de productos a recomendar
        
        Returns:
            dict: {
                "recomendaciones": [
                    {
                        "producto_id": int,
                        "nombre": str,
                        "razon": str,
                        "confianza": str
                    }
                ],
                "mensaje": str
            }
        """
        # Construir prompt con contexto - optimizado para listas grandes
        total_productos = len(productos_disponibles)
        
        prompt = f"""Eres un asistente de ventas experto. Analiza el historial de compras del cliente y recomienda {limite} productos que podrían interesarle.

HISTORIAL DE COMPRAS DEL CLIENTE:
{json.dumps(historial_cliente, indent=2, ensure_ascii=False)}

CATÁLOGO COMPLETO DE PRODUCTOS DISPONIBLES ({total_productos} productos en total):
{json.dumps(productos_disponibles, indent=2, ensure_ascii=False)}

INSTRUCCIONES IMPORTANTES:
1. Tienes acceso a TODOS los {total_productos} productos del catálogo
2. Recomienda EXACTAMENTE {limite} productos diferentes
3. Usa SOLO productos que existen en el catálogo proporcionado
4. Verifica que los producto_id coincidan exactamente con los del catálogo
5. Basa tus recomendaciones en patrones de compra del cliente
6. Si el cliente no tiene historial, recomienda productos populares o variados
7. Para cada producto, explica brevemente por qué lo recomiendas
8. Responde SOLO en formato JSON válido

FORMATO DE RESPUESTA (JSON):
{{
    "recomendaciones": [
        {{
            "producto_id": 123,
            "nombre": "Nombre del producto",
            "razon": "Explicación breve de por qué se recomienda",
            "confianza": "alta|media|baja"
        }}
    ],
    "mensaje": "Mensaje personalizado para el cliente"
}}
"""
        
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente de ventas experto que recomienda productos basándose en el historial de compras. Siempre respondes en formato JSON válido."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._call_groq(messages, temperature=0.3, max_tokens=1024)
            
            # Limpiar respuesta y parsear JSON
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            resultado = json.loads(response_clean.strip())
            return resultado
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta JSON: {str(e)}")
            logger.error(f"Respuesta recibida: {response}")
            return {
                "recomendaciones": [],
                "mensaje": "No se pudieron generar recomendaciones en este momento."
            }
    
    def generar_descripcion_producto(self, nombre_producto, caracteristicas=None):
        """
        Genera una descripción atractiva y profesional para un producto
        
        Args:
            nombre_producto: Nombre del producto
            caracteristicas: Dict opcional con características adicionales
                            (ej: {"precio": 25000, "stock": 50, "codigo": "ABC123"})
        
        Returns:
            dict: {
                "descripcion_corta": str,  # 1-2 líneas
                "descripcion_larga": str,  # Párrafo completo
                "palabras_clave": [str],   # Keywords para SEO
                "beneficios": [str]        # Lista de beneficios
            }
        """
        caract_text = ""
        if caracteristicas:
            caract_text = f"\n\nCARACTERÍSTICAS ADICIONALES:\n{json.dumps(caracteristicas, indent=2, ensure_ascii=False)}"
        
        prompt = f"""Eres un experto en marketing y copywriting. Genera una descripción atractiva y profesional para este producto:

NOMBRE DEL PRODUCTO: {nombre_producto}{caract_text}

INSTRUCCIONES:
1. Crea una descripción corta (1-2 líneas) para listados
2. Crea una descripción larga (1 párrafo) detallada y persuasiva
3. Sugiere 5 palabras clave relevantes para SEO
4. Lista 3-4 beneficios principales del producto
5. Usa un tono profesional pero cercano
6. Responde SOLO en formato JSON válido

FORMATO DE RESPUESTA (JSON):
{{
    "descripcion_corta": "Descripción breve y atractiva en 1-2 líneas",
    "descripcion_larga": "Descripción detallada en un párrafo completo",
    "palabras_clave": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
    "beneficios": [
        "Beneficio 1",
        "Beneficio 2",
        "Beneficio 3"
    ]
}}
"""
        
        messages = [
            {
                "role": "system",
                "content": "Eres un experto en marketing y copywriting que crea descripciones atractivas de productos. Siempre respondes en formato JSON válido."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._call_groq(messages, temperature=0.7, max_tokens=800)
            
            # Limpiar y parsear JSON
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            resultado = json.loads(response_clean.strip())
            return resultado
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta JSON: {str(e)}")
            logger.error(f"Respuesta recibida: {response}")
            return {
                "descripcion_corta": f"Producto de calidad: {nombre_producto}",
                "descripcion_larga": f"{nombre_producto} - Descripción no disponible temporalmente.",
                "palabras_clave": [nombre_producto.lower()],
                "beneficios": ["Producto de calidad", "Entrega rápida", "Garantía incluida"]
            }
    
    def chatbot_atencion(self, mensaje_usuario, contexto=None):
        """
        Chatbot para atención al cliente
        Responde preguntas sobre productos, ventas, políticas, etc.
        
        Args:
            mensaje_usuario: Pregunta o mensaje del usuario
            contexto: Dict opcional con información relevante
                     (ej: {"productos": [...], "venta": {...}})
        
        Returns:
            dict: {
                "respuesta": str,
                "tipo": "informacion|consulta_venta|consulta_producto|otro",
                "requiere_humano": bool,
                "sugerencias": [str]  # Sugerencias de follow-up
            }
        """
        contexto_text = ""
        total_productos_info = ""
        
        if contexto:
            # Agregar información sobre cantidad total de productos
            if 'total_productos' in contexto:
                total_productos_info = f"\n- Tenemos {contexto['total_productos']} productos diferentes en catálogo"
            
            contexto_text = f"\n\nCONTEXTO DISPONIBLE:\n{json.dumps(contexto, indent=2, ensure_ascii=False)}"
        
        prompt = f"""Eres un asistente virtual de atención al cliente para una tienda de ventas. Tu objetivo es ayudar a los clientes de manera amable y profesional.

MENSAJE DEL CLIENTE: {mensaje_usuario}{contexto_text}

INFORMACIÓN DE LA TIENDA:
- Horario de atención: Lunes a Viernes 9:00-18:00, Sábados 10:00-14:00
- Métodos de pago: Webpay, transferencia, efectivo
- Despacho: 24-48 horas en Santiago, 3-5 días regiones
- Devoluciones: 30 días con boleta
- Contacto: ventas@tiendaonline.cl / +56 9 3341 7458{total_productos_info}

INSTRUCCIONES IMPORTANTES:
1. Responde de manera clara, amable y profesional
2. Si tienes información en el CONTEXTO (productos, ventas), úsala para respuestas precisas
3. Si preguntan por productos disponibles, usa la lista completa del CONTEXTO
4. Puedes mencionar productos específicos del catálogo si es relevante
5. Si no puedes responder, indica que se requiere atención humana
6. Sugiere 2-3 preguntas de follow-up que el cliente podría hacer
7. Clasifica el tipo de consulta
8. Responde SOLO en formato JSON válido

FORMATO DE RESPUESTA (JSON):
{{
    "respuesta": "Tu respuesta completa al cliente",
    "tipo": "informacion|consulta_venta|consulta_producto|politicas|otro",
    "requiere_humano": false,
    "sugerencias": [
        "¿Pregunta relacionada 1?",
        "¿Pregunta relacionada 2?"
    ]
}}
"""
        
        messages = [
            {
                "role": "system",
                "content": "Eres un asistente virtual de atención al cliente amable, profesional y servicial. Siempre respondes en formato JSON válido y en español."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._call_groq(messages, temperature=0.5, max_tokens=1024)
            
            # Limpiar y parsear JSON
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            resultado = json.loads(response_clean.strip())
            return resultado
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando respuesta JSON: {str(e)}")
            logger.error(f"Respuesta recibida: {response}")
            return {
                "respuesta": "Disculpa, estoy teniendo problemas técnicos. Por favor, contacta a nuestro equipo directamente en ventas@tienda.cl o llama al +56 9 1234 5678.",
                "tipo": "otro",
                "requiere_humano": True,
                "sugerencias": []
            }
