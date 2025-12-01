# 📚 Ejemplos de Integración con IA

Ejemplos de código para integrar las funcionalidades de IA en diferentes lenguajes y frameworks.

---

## 🅰️ Angular / TypeScript

### **Servicio de IA**

```typescript
// src/app/services/ia.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class IAService {
  private apiUrl = 'http://localhost:8000/api/ia';

  constructor(private http: HttpClient) {}

  // 1. Recomendador de Productos
  getRecomendaciones(rutCliente: string, limite: number = 3): Observable<any> {
    return this.http.post(`${this.apiUrl}/productos/recomendar/`, {
      rut_cliente: rutCliente,
      limite: limite
    });
  }

  // 2. Generador de Descripciones (requiere token)
  generarDescripcion(productoId: number, token: string): Observable<any> {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
    
    return this.http.post(
      `${this.apiUrl}/productos/${productoId}/generar-descripcion/`,
      {},
      { headers }
    );
  }

  // 3. Chatbot
  enviarMensajeChatbot(mensaje: string, contexto?: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/chat/`, {
      mensaje: mensaje,
      contexto: contexto
    });
  }
}
```

### **Componente de Recomendaciones**

```typescript
// src/app/components/recomendaciones/recomendaciones.component.ts
import { Component, OnInit, Input } from '@angular/core';
import { IAService } from '../../services/ia.service';

@Component({
  selector: 'app-recomendaciones',
  templateUrl: './recomendaciones.component.html'
})
export class RecomendacionesComponent implements OnInit {
  @Input() rutCliente: string = '';
  
  recomendaciones: any[] = [];
  cargando: boolean = false;
  mensaje: string = '';

  constructor(private iaService: IAService) {}

  ngOnInit() {
    this.cargarRecomendaciones();
  }

  cargarRecomendaciones() {
    if (!this.rutCliente) return;
    
    this.cargando = true;
    this.iaService.getRecomendaciones(this.rutCliente, 3)
      .subscribe({
        next: (data) => {
          this.recomendaciones = data.recomendaciones;
          this.mensaje = data.mensaje;
          this.cargando = false;
        },
        error: (err) => {
          console.error('Error cargando recomendaciones:', err);
          this.cargando = false;
        }
      });
  }
}
```

### **Template HTML**

```html
<!-- recomendaciones.component.html -->
<div class="recomendaciones-container">
  <h3>🤖 Productos Recomendados para Ti</h3>
  <p class="mensaje-ia">{{ mensaje }}</p>
  
  <div *ngIf="cargando" class="loading">
    Generando recomendaciones con IA...
  </div>
  
  <div class="productos-grid" *ngIf="!cargando">
    <div *ngFor="let producto of recomendaciones" class="producto-card">
      <h4>{{ producto.nombre }}</h4>
      <p class="precio">${{ producto.precio | number }}</p>
      <p class="stock">Stock: {{ producto.stock }}</p>
      
      <div class="ia-info">
        <span class="confianza" [class]="'confianza-' + producto.confianza">
          {{ producto.confianza }}
        </span>
        <p class="razon">{{ producto.razon }}</p>
      </div>
      
      <button (click)="agregarAlCarrito(producto.producto_id)">
        Agregar al Carrito
      </button>
    </div>
  </div>
</div>
```

### **Componente de Chatbot**

```typescript
// src/app/components/chatbot/chatbot.component.ts
import { Component } from '@angular/core';
import { IAService } from '../../services/ia.service';

interface Mensaje {
  tipo: 'usuario' | 'bot';
  contenido: string;
  timestamp: Date;
}

@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.css']
})
export class ChatbotComponent {
  mensajes: Mensaje[] = [];
  mensajeInput: string = '';
  cargando: boolean = false;
  sugerencias: string[] = [];
  chatAbierto: boolean = false;

  constructor(private iaService: IAService) {
    // Mensaje de bienvenida
    this.agregarMensaje('bot', '¡Hola! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?');
  }

  toggleChat() {
    this.chatAbierto = !this.chatAbierto;
  }

  enviarMensaje() {
    if (!this.mensajeInput.trim() || this.cargando) return;
    
    const mensaje = this.mensajeInput.trim();
    this.agregarMensaje('usuario', mensaje);
    this.mensajeInput = '';
    this.cargando = true;

    this.iaService.enviarMensajeChatbot(mensaje)
      .subscribe({
        next: (data) => {
          this.agregarMensaje('bot', data.respuesta);
          this.sugerencias = data.sugerencias || [];
          this.cargando = false;
          
          if (data.requiere_humano) {
            setTimeout(() => {
              this.agregarMensaje('bot', 
                'Para asistencia personalizada, contáctanos en ventas@tienda.cl'
              );
            }, 1000);
          }
        },
        error: (err) => {
          console.error('Error en chatbot:', err);
          this.agregarMensaje('bot', 
            'Disculpa, estoy teniendo problemas técnicos. Por favor intenta de nuevo.'
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
      tipo: tipo,
      contenido: contenido,
      timestamp: new Date()
    });
    
    // Scroll al final
    setTimeout(() => {
      const container = document.querySelector('.chat-mensajes');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }, 100);
  }
}
```

### **Template del Chatbot**

```html
<!-- chatbot.component.html -->
<div class="chatbot-widget" [class.abierto]="chatAbierto">
  <!-- Botón flotante -->
  <button class="chat-toggle" (click)="toggleChat()" *ngIf="!chatAbierto">
    💬 Chat
  </button>

  <!-- Ventana del chat -->
  <div class="chat-window" *ngIf="chatAbierto">
    <div class="chat-header">
      <h4>🤖 Asistente Virtual</h4>
      <button (click)="toggleChat()">✕</button>
    </div>

    <div class="chat-mensajes">
      <div *ngFor="let msg of mensajes" 
           [class]="'mensaje mensaje-' + msg.tipo">
        <div class="mensaje-contenido">
          {{ msg.contenido }}
        </div>
        <span class="mensaje-hora">
          {{ msg.timestamp | date:'HH:mm' }}
        </span>
      </div>
      
      <div *ngIf="cargando" class="mensaje mensaje-bot">
        <div class="typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <div class="chat-sugerencias" *ngIf="sugerencias.length > 0">
      <button *ngFor="let sug of sugerencias" 
              (click)="usarSugerencia(sug)"
              class="sugerencia-btn">
        {{ sug }}
      </button>
    </div>

    <div class="chat-input">
      <input 
        type="text" 
        [(ngModel)]="mensajeInput"
        (keyup.enter)="enviarMensaje()"
        placeholder="Escribe tu mensaje..."
        [disabled]="cargando"
      />
      <button (click)="enviarMensaje()" [disabled]="cargando">
        Enviar
      </button>
    </div>
  </div>
</div>
```

### **CSS del Chatbot**

```css
/* chatbot.component.css */
.chatbot-widget {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
}

.chat-toggle {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 30px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transition: all 0.3s;
}

.chat-toggle:hover {
  background: #0056b3;
  transform: scale(1.05);
}

.chat-window {
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h4 {
  margin: 0;
  font-size: 18px;
}

.chat-header button {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
}

.chat-mensajes {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

.mensaje {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.mensaje-usuario {
  align-items: flex-end;
}

.mensaje-bot {
  align-items: flex-start;
}

.mensaje-contenido {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
}

.mensaje-usuario .mensaje-contenido {
  background: #007bff;
  color: white;
  border-bottom-right-radius: 4px;
}

.mensaje-bot .mensaje-contenido {
  background: white;
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.mensaje-hora {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

.chat-sugerencias {
  padding: 10px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sugerencia-btn {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 16px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.sugerencia-btn:hover {
  background: #e0e0e0;
  border-color: #007bff;
}

.chat-input {
  display: flex;
  padding: 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.chat-input input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 24px;
  padding: 12px 16px;
  font-size: 14px;
}

.chat-input button {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 24px;
  padding: 10px 20px;
  margin-left: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.chat-input button:hover:not(:disabled) {
  background: #0056b3;
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}
```

---

## 🐍 Python / Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Recomendador de Productos
def obtener_recomendaciones(rut_cliente, limite=3):
    url = f"{BASE_URL}/api/ia/productos/recomendar/"
    response = requests.post(url, json={
        "rut_cliente": rut_cliente,
        "limite": limite
    })
    return response.json()

# 2. Generar Descripción (requiere auth)
def generar_descripcion(producto_id, token):
    url = f"{BASE_URL}/api/ia/productos/{producto_id}/generar-descripcion/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    return response.json()

# 3. Chatbot
def consultar_chatbot(mensaje, contexto=None):
    url = f"{BASE_URL}/api/ia/chat/"
    data = {"mensaje": mensaje}
    if contexto:
        data["contexto"] = contexto
    response = requests.post(url, json=data)
    return response.json()

# Uso
if __name__ == "__main__":
    # Ejemplo 1: Recomendaciones
    recomendaciones = obtener_recomendaciones("12345678-9")
    print(f"Recomendaciones: {recomendaciones}")
    
    # Ejemplo 2: Chatbot
    respuesta = consultar_chatbot("¿Cuál es el horario de atención?")
    print(f"Bot: {respuesta['respuesta']}")
```

---

## 🟦 JavaScript / Fetch API

```javascript
const BASE_URL = 'http://localhost:8000';

// 1. Recomendador de Productos
async function obtenerRecomendaciones(rutCliente, limite = 3) {
  const response = await fetch(`${BASE_URL}/api/ia/productos/recomendar/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      rut_cliente: rutCliente,
      limite: limite
    })
  });
  
  return await response.json();
}

// 2. Generar Descripción
async function generarDescripcion(productoId, token) {
  const response = await fetch(
    `${BASE_URL}/api/ia/productos/${productoId}/generar-descripcion/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  return await response.json();
}

// 3. Chatbot
async function consultarChatbot(mensaje, contexto = null) {
  const body = { mensaje: mensaje };
  if (contexto) {
    body.contexto = contexto;
  }
  
  const response = await fetch(`${BASE_URL}/api/ia/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  
  return await response.json();
}

// Uso
obtenerRecomendaciones('12345678-9', 3)
  .then(data => console.log('Recomendaciones:', data))
  .catch(err => console.error('Error:', err));
```

---

## ⚛️ React

```jsx
// hooks/useIA.js
import { useState } from 'react';

export const useIA = () => {
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const BASE_URL = 'http://localhost:8000';

  const obtenerRecomendaciones = async (rutCliente, limite = 3) => {
    setCargando(true);
    setError(null);
    
    try {
      const response = await fetch(`${BASE_URL}/api/ia/productos/recomendar/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rut_cliente: rutCliente, limite })
      });
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const consultarChatbot = async (mensaje, contexto) => {
    setCargando(true);
    setError(null);
    
    try {
      const response = await fetch(`${BASE_URL}/api/ia/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje, contexto })
      });
      
      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  return {
    obtenerRecomendaciones,
    consultarChatbot,
    cargando,
    error
  };
};

// Componente de ejemplo
import React, { useEffect, useState } from 'react';
import { useIA } from './hooks/useIA';

export const Recomendaciones = ({ rutCliente }) => {
  const [recomendaciones, setRecomendaciones] = useState([]);
  const { obtenerRecomendaciones, cargando, error } = useIA();

  useEffect(() => {
    if (rutCliente) {
      obtenerRecomendaciones(rutCliente)
        .then(data => setRecomendaciones(data.recomendaciones))
        .catch(err => console.error(err));
    }
  }, [rutCliente]);

  if (cargando) return <div>Cargando recomendaciones...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="recomendaciones">
      <h3>🤖 Productos Recomendados</h3>
      {recomendaciones.map(prod => (
        <div key={prod.producto_id} className="producto">
          <h4>{prod.nombre}</h4>
          <p>{prod.razon}</p>
          <span>${prod.precio}</span>
        </div>
      ))}
    </div>
  );
};
```

---

## 🔵 cURL (Terminal)

```bash
# 1. Recomendador de Productos
curl -X POST http://localhost:8000/api/ia/productos/recomendar/ \
  -H "Content-Type: application/json" \
  -d '{"rut_cliente": "12345678-9", "limite": 3}'

# 2. Generar Descripción (con token)
curl -X POST http://localhost:8000/api/ia/productos/1/generar-descripcion/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_JWT"

# 3. Chatbot
curl -X POST http://localhost:8000/api/ia/chat/ \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "¿Cuál es el horario de atención?"}'

# 4. Chatbot con contexto
curl -X POST http://localhost:8000/api/ia/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "¿Cuál es el estado de mi pedido?",
    "contexto": {
      "venta_numero": "20241128-0001"
    }
  }'
```

---

¿Necesitas ejemplos en otro lenguaje o framework? ¡Déjame saber!
