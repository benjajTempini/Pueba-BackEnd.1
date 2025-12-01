# 🤖 INTEGRACIÓN DE IA CON GROQ CLOUD - FRONTEND ANGULAR

## 📋 CONTEXTO

Hemos implementado 3 funcionalidades de IA en el backend Django usando Groq Cloud (Llama 3.3 70B). Necesito que integres estas funcionalidades en el frontend Angular.

---

## 🔌 ENDPOINTS DISPONIBLES (Backend Django)

### **Base URL:** `http://localhost:8000` (desarrollo) / `https://tu-backend.railway.app` (producción)

### **1. Recomendador de Productos Inteligente** ⭐
- **Endpoint:** `POST /api/ia/productos/recomendar/`
- **Autenticación:** No requerida (público)
- **Descripción:** Recomienda productos personalizados basándose en el historial de compras del cliente

**Request:**
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
      "nombre": "Mouse Gamer RGB",
      "codigo": "MGR-001",
      "precio": 35000.00,
      "stock": 25,
      "razon": "Basado en tu compra anterior de teclado gamer, este mouse complementaría perfectamente tu setup gaming",
      "confianza": "alta"
    },
    {
      "producto_id": 8,
      "nombre": "Mousepad XXL",
      "codigo": "MP-XXL-002",
      "precio": 12000.00,
      "stock": 50,
      "razon": "Los clientes que compraron periféricos gaming también adquieren este mousepad",
      "confianza": "media"
    }
  ],
  "mensaje": "Estos productos podrían interesarte basado en tus compras anteriores"
}
```

**Casos de uso:**
- Mostrar en la página de producto individual
- Widget en el home después del login
- Sección "Recomendados para ti" en el perfil
- Después de agregar un producto al carrito

---

### **2. Generador de Descripciones de Productos** 📝
- **Endpoint:** `POST /api/ia/productos/{producto_id}/generar-descripcion/`
- **Autenticación:** ✅ REQUERIDA (JWT Token - solo admin)
- **Descripción:** Genera descripciones profesionales y atractivas para productos usando IA

**Headers:**
```
Authorization: Bearer {tu_token_jwt}
Content-Type: application/json
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

**Casos de uso:**
- Panel de administración (agregar/editar productos)
- Botón "Generar descripción con IA" en formularios de productos
- Mejorar descripciones existentes
- Generar contenido para marketing

---

### **3. Chatbot de Atención al Cliente** 💬
- **Endpoint:** `POST /api/ia/chat/`
- **Autenticación:** No requerida (público)
- **Descripción:** Chatbot inteligente que responde preguntas sobre productos, ventas, horarios, políticas, etc.

**Request:**
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
    "¿Cuánto demora el despacho a mi región?",
    "¿Tienen política de devolución?"
  ]
}
```

**Tipos de consulta (campo `tipo`):**
- `informacion` - Info general de la tienda
- `consulta_venta` - Preguntas sobre pedidos
- `consulta_producto` - Preguntas sobre productos
- `politicas` - Políticas de la tienda
- `otro` - Otras consultas

**Casos de uso:**
- Widget de chat flotante en todas las páginas
- Página dedicada de soporte
- Integrar en la página de checkout
- Consultas sobre pedidos en el perfil del usuario

---

## 🎯 TAREAS A IMPLEMENTAR EN ANGULAR

### **1. Crear Servicio de IA**

Crear `src/app/services/ia.service.ts`:

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Recomendacion {
  producto_id: number;
  nombre: string;
  codigo: string;
  precio: number;
  stock: number;
  razon: string;
  confianza: 'alta' | 'media' | 'baja';
}

export interface RecomendacionesResponse {
  cliente: {
    rut: string;
    nombre: string;
  };
  recomendaciones: Recomendacion[];
  mensaje: string;
}

export interface DescripcionProducto {
  producto: {
    id: number;
    nombre: string;
    codigo: string;
    precio: number;
  };
  descripcion_corta: string;
  descripcion_larga: string;
  palabras_clave: string[];
  beneficios: string[];
}

export interface ChatResponse {
  respuesta: string;
  tipo: 'informacion' | 'consulta_venta' | 'consulta_producto' | 'politicas' | 'otro';
  requiere_humano: boolean;
  sugerencias: string[];
}

@Injectable({
  providedIn: 'root'
})
export class IAService {
  private apiUrl = `${environment.apiUrl}/api/ia`;

  constructor(private http: HttpClient) {}

  // 1. Obtener recomendaciones de productos
  getRecomendaciones(rutCliente: string, limite: number = 3): Observable<RecomendacionesResponse> {
    return this.http.post<RecomendacionesResponse>(
      `${this.apiUrl}/productos/recomendar/`,
      { rut_cliente: rutCliente, limite }
    );
  }

  // 2. Generar descripción de producto (requiere auth)
  generarDescripcion(productoId: number): Observable<DescripcionProducto> {
    return this.http.post<DescripcionProducto>(
      `${this.apiUrl}/productos/${productoId}/generar-descripcion/`,
      {}
    );
  }

  // 3. Enviar mensaje al chatbot
  enviarMensajeChatbot(mensaje: string, contexto?: any): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(
      `${this.apiUrl}/chat/`,
      { mensaje, contexto }
    );
  }
}
```

### **2. Componente de Recomendaciones**

Crear `src/app/components/recomendaciones-ia/recomendaciones-ia.component.ts`:

```typescript
import { Component, Input, OnInit } from '@angular/core';
import { IAService, Recomendacion } from '../../services/ia.service';

@Component({
  selector: 'app-recomendaciones-ia',
  templateUrl: './recomendaciones-ia.component.html',
  styleUrls: ['./recomendaciones-ia.component.css']
})
export class RecomendacionesIAComponent implements OnInit {
  @Input() rutCliente: string = '';
  @Input() limite: number = 3;
  
  recomendaciones: Recomendacion[] = [];
  mensaje: string = '';
  cargando: boolean = false;
  error: string = '';

  constructor(
    private iaService: IAService,
    private router: Router
  ) {}

  ngOnInit() {
    if (this.rutCliente) {
      this.cargarRecomendaciones();
    }
  }

  cargarRecomendaciones() {
    this.cargando = true;
    this.error = '';
    
    this.iaService.getRecomendaciones(this.rutCliente, this.limite)
      .subscribe({
        next: (data) => {
          this.recomendaciones = data.recomendaciones;
          this.mensaje = data.mensaje;
          this.cargando = false;
        },
        error: (err) => {
          console.error('Error cargando recomendaciones:', err);
          this.error = 'No se pudieron cargar las recomendaciones';
          this.cargando = false;
        }
      });
  }

  verProducto(productoId: number) {
    this.router.navigate(['/productos', productoId]);
  }

  agregarAlCarrito(productoId: number) {
    // Tu lógica existente de carrito
  }

  getConfianzaClass(confianza: string): string {
    return `confianza-${confianza}`;
  }
}
```

**Template HTML:**
```html
<!-- recomendaciones-ia.component.html -->
<div class="recomendaciones-container" *ngIf="recomendaciones.length > 0 || cargando">
  <div class="header-ia">
    <h3>🤖 Recomendaciones Inteligentes</h3>
    <p class="mensaje-ia">{{ mensaje }}</p>
  </div>

  <div class="loading-container" *ngIf="cargando">
    <div class="spinner"></div>
    <p>Analizando tus preferencias con IA...</p>
  </div>

  <div class="error-message" *ngIf="error">
    {{ error }}
  </div>

  <div class="productos-grid" *ngIf="!cargando && !error">
    <div *ngFor="let producto of recomendaciones" 
         class="producto-card"
         (click)="verProducto(producto.producto_id)">
      
      <div class="producto-header">
        <h4>{{ producto.nombre }}</h4>
        <span class="badge" [class]="getConfianzaClass(producto.confianza)">
          {{ producto.confianza }}
        </span>
      </div>

      <div class="producto-info">
        <p class="precio">${{ producto.precio | number:'1.0-0' }}</p>
        <p class="stock" *ngIf="producto.stock > 0">
          {{ producto.stock }} disponibles
        </p>
        <p class="sin-stock" *ngIf="producto.stock === 0">
          Sin stock
        </p>
      </div>

      <div class="ia-reasoning">
        <p class="razon">
          <span class="icon">💡</span>
          {{ producto.razon }}
        </p>
      </div>

      <button 
        class="btn-agregar"
        (click)="agregarAlCarrito(producto.producto_id); $event.stopPropagation()"
        [disabled]="producto.stock === 0">
        <span *ngIf="producto.stock > 0">Agregar al Carrito</span>
        <span *ngIf="producto.stock === 0">Sin Stock</span>
      </button>
    </div>
  </div>
</div>
```

**CSS:**
```css
/* recomendaciones-ia.component.css */
.recomendaciones-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 30px;
  margin: 30px 0;
  color: white;
}

.header-ia h3 {
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: bold;
}

.mensaje-ia {
  opacity: 0.9;
  font-size: 16px;
  margin-bottom: 20px;
}

.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.producto-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  color: #333;
}

.producto-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.producto-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 15px;
}

.producto-header h4 {
  margin: 0;
  font-size: 18px;
  flex: 1;
}

.badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.confianza-alta {
  background: #10b981;
  color: white;
}

.confianza-media {
  background: #f59e0b;
  color: white;
}

.confianza-baja {
  background: #6b7280;
  color: white;
}

.precio {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
  margin: 10px 0;
}

.stock {
  color: #10b981;
  font-size: 14px;
}

.sin-stock {
  color: #ef4444;
  font-size: 14px;
}

.ia-reasoning {
  background: #f3f4f6;
  border-radius: 8px;
  padding: 12px;
  margin: 15px 0;
}

.razon {
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  color: #4b5563;
}

.icon {
  margin-right: 5px;
}

.btn-agregar {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-agregar:hover:not(:disabled) {
  background: #5568d3;
}

.btn-agregar:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}

.loading-container {
  text-align: center;
  padding: 40px;
}

.spinner {
  border: 4px solid rgba(255,255,255,0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### **3. Componente de Chatbot**

Crear `src/app/components/chatbot-ia/chatbot-ia.component.ts`:

```typescript
import { Component } from '@angular/core';
import { IAService, ChatResponse } from '../../services/ia.service';

interface Mensaje {
  tipo: 'usuario' | 'bot';
  contenido: string;
  timestamp: Date;
}

@Component({
  selector: 'app-chatbot-ia',
  templateUrl: './chatbot-ia.component.html',
  styleUrls: ['./chatbot-ia.component.css']
})
export class ChatbotIAComponent {
  mensajes: Mensaje[] = [];
  mensajeInput: string = '';
  cargando: boolean = false;
  sugerencias: string[] = [];
  chatAbierto: boolean = false;

  constructor(private iaService: IAService) {
    this.agregarMensaje('bot', '¡Hola! 👋 Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?');
  }

  toggleChat() {
    this.chatAbierto = !this.chatAbierto;
    if (this.chatAbierto && this.mensajes.length === 1) {
      // Primera vez que se abre
      this.sugerencias = [
        '¿Cuál es el horario de atención?',
        '¿Qué métodos de pago aceptan?',
        '¿Tienen mouse gamer disponible?'
      ];
    }
  }

  enviarMensaje() {
    if (!this.mensajeInput.trim() || this.cargando) return;
    
    const mensaje = this.mensajeInput.trim();
    this.agregarMensaje('usuario', mensaje);
    this.mensajeInput = '';
    this.cargando = true;
    this.sugerencias = [];

    this.iaService.enviarMensajeChatbot(mensaje)
      .subscribe({
        next: (data: ChatResponse) => {
          this.agregarMensaje('bot', data.respuesta);
          this.sugerencias = data.sugerencias || [];
          this.cargando = false;
          
          if (data.requiere_humano) {
            setTimeout(() => {
              this.agregarMensaje('bot', 
                '📧 Para asistencia personalizada, contáctanos en ventas@tienda.cl o llama al +56 9 1234 5678'
              );
            }, 1000);
          }
        },
        error: (err) => {
          console.error('Error en chatbot:', err);
          this.agregarMensaje('bot', 
            'Disculpa, estoy teniendo problemas técnicos. Por favor intenta de nuevo en unos momentos.'
          );
          this.cargando = false;
        }
      });
  }

  usarSugerencia(sugerencia: string) {
    this.mensajeInput = sugerencia;
    this.enviarMensaje();
  }

  private agregarMensaje(tipo: 'usuario' | 'bot', contenido: string) {
    this.mensajes.push({
      tipo,
      contenido,
      timestamp: new Date()
    });
    
    setTimeout(() => this.scrollToBottom(), 100);
  }

  private scrollToBottom() {
    const container = document.querySelector('.chat-mensajes');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }
}
```

**Template y CSS del chatbot:** (Usa el CSS completo del archivo EJEMPLOS_INTEGRACION.md)

### **4. Generador de Descripciones (Admin)**

En tu componente de administración de productos, agrega:

```typescript
// admin-productos.component.ts
generarDescripcionIA(productoId: number) {
  this.cargandoDescripcion = true;
  
  this.iaService.generarDescripcion(productoId)
    .subscribe({
      next: (data) => {
        // Actualizar el formulario con los datos generados
        this.productoForm.patchValue({
          descripcion_corta: data.descripcion_corta,
          descripcion_larga: data.descripcion_larga,
          keywords: data.palabras_clave.join(', ')
        });
        
        this.cargandoDescripcion = false;
        this.mostrarNotificacion('✅ Descripción generada con IA exitosamente');
      },
      error: (err) => {
        console.error('Error:', err);
        this.cargandoDescripcion = false;
        this.mostrarNotificacion('❌ Error al generar descripción');
      }
    });
}
```

**HTML:**
```html
<button 
  type="button"
  class="btn-ia"
  (click)="generarDescripcionIA(producto.id)"
  [disabled]="cargandoDescripcion">
  <span *ngIf="!cargandoDescripcion">🤖 Generar con IA</span>
  <span *ngIf="cargandoDescripcion">Generando...</span>
</button>
```

---

## 📍 DÓNDE USAR CADA COMPONENTE

### **Recomendaciones IA:**
```html
<!-- En home.component.html (si hay usuario logueado) -->
<app-recomendaciones-ia 
  *ngIf="usuario"
  [rutCliente]="usuario.rut"
  [limite]="3">
</app-recomendaciones-ia>

<!-- En producto-detalle.component.html -->
<app-recomendaciones-ia 
  [rutCliente]="clienteActual?.rut"
  [limite]="4">
</app-recomendaciones-ia>
```

### **Chatbot:**
```html
<!-- En app.component.html (disponible en todo el sitio) -->
<app-chatbot-ia></app-chatbot-ia>
```

---

## 🔧 CONFIGURACIÓN ENVIRONMENT

```typescript
// environment.ts (desarrollo)
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};

// environment.prod.ts (producción)
export const environment = {
  production: true,
  apiUrl: 'https://tu-backend.railway.app'
};
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear `ia.service.ts` con los 3 métodos
- [ ] Crear componente `recomendaciones-ia`
- [ ] Crear componente `chatbot-ia`
- [ ] Agregar botón "Generar con IA" en admin de productos
- [ ] Integrar recomendaciones en home (si usuario logueado)
- [ ] Integrar recomendaciones en detalle de producto
- [ ] Agregar chatbot flotante en `app.component.html`
- [ ] Configurar `environment.ts` con URL del backend
- [ ] Probar en desarrollo
- [ ] Probar en producción

---

## 🎨 DISEÑO UI/UX SUGERIDO

- Widget de chatbot flotante en esquina inferior derecha
- Recomendaciones con diseño de cards atractivo
- Indicador visual de "confianza" de la IA (alta/media/baja)
- Animaciones suaves al cargar
- Loading states claros
- Iconos de IA (🤖, 💡, ✨) para identificar contenido generado por IA

---

## 📞 SOPORTE

Si necesitas ayuda durante la implementación o tienes dudas sobre algún endpoint, consulta la documentación completa en los archivos:
- `GROQ_AI_INTEGRATION.md`
- `EJEMPLOS_INTEGRACION.md`

---

**¡Implementa estas funcionalidades y tendrás un sistema de ventas con IA de última generación! 🚀**
