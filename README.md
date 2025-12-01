# Sistema de Ventas - Backend Django

Backend API REST para sistema de ventas con Django REST Framework.

## 🚀 Despliegue Rápido en Railway

### Opción 1: Usar Railway CLI

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Inicializar proyecto
railway init

# 4. Desplegar
railway up
```

### Opción 2: Usar GitHub (Recomendado)

1. Sube tu código a GitHub
2. Ve a [railway.app](https://railway.app)
3. Crea nuevo proyecto → Deploy from GitHub
4. Selecciona este repositorio
5. Railway detectará automáticamente la configuración

### Variables de entorno en Railway:

```env
SECRET_KEY=tu-secret-key-segura
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
```

Ver [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) para instrucciones completas.

## 📦 Instalación Local

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales

# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Correr servidor
python manage.py runserver
```

## 🔌 Endpoints API

### Productos
- `GET /api/productos/` - Listar productos (público)
- `POST /api/productos/` - Crear producto (requiere auth)
- `GET /api/productos/{codigo}/` - Ver producto (público)
- `PUT /api/productos/{codigo}/` - Actualizar producto (requiere auth)
- `DELETE /api/productos/{codigo}/` - Eliminar producto (requiere auth)

### Clientes
- `GET /api/clientes/` - Listar clientes (requiere auth)
- `POST /api/clientes/` - Registrar cliente (público)
- `PUT /api/clientes/{rut}/` - Actualizar cliente (público)
- `DELETE /api/clientes/{rut}/` - Eliminar cliente (requiere auth)

### Ventas
- `GET /api/venta/` - Historial de ventas (requiere auth)
- `POST /api/venta/` - Crear venta (público)
- `GET /api/venta/{id}/` - Ver venta (requiere auth)

### Detalles de Venta
- `GET /api/detalleVenta/` - Todos los detalles (público)
- `GET /api/detalleVenta/?venta=20251124-0001` - Filtrar por venta (público)

### Autenticación
- `POST /api/token/` - Obtener token JWT
- `POST /api/token/refresh/` - Refrescar token

### 🤖 Inteligencia Artificial (Groq Cloud)
- `POST /api/ia/productos/recomendar/` - Recomendador de productos (público)
- `POST /api/ia/productos/{id}/generar-descripcion/` - Generar descripción (requiere auth)
- `POST /api/ia/chat/` - Chatbot de atención (público)

## 🛠️ Tecnologías

- Django 5.2
- Django REST Framework
- PostgreSQL (Supabase)
- JWT Authentication
- WhiteNoise (archivos estáticos)
- 🤖 **Groq Cloud AI** (Llama 3.1 70B) - Ver [GROQ_AI_INTEGRATION.md](GROQ_AI_INTEGRATION.md)

## 🤖 Funcionalidades con IA

Este proyecto incluye **3 características impulsadas por IA** usando Groq Cloud:

1. **Recomendador de Productos Inteligente** - Analiza historial y sugiere productos
2. **Generación Automática de Descripciones** - Crea descripciones atractivas con IA
3. **Chatbot de Atención al Cliente** - Responde preguntas 24/7

📖 **[Ver documentación completa de IA →](GROQ_AI_INTEGRATION.md)**
- Gunicorn (servidor WSGI)

## 📝 Estructura del Proyecto

```
├── clientes/          # App de clientes
├── ventasbasico/      # App principal y configuración
├── manage.py
├── requirements.txt
├── Procfile          # Configuración Railway/Heroku
├── runtime.txt       # Versión de Python
└── railway.json      # Configuración Railway
```

## 🔐 Seguridad

- ✅ JWT Authentication
- ✅ CORS configurado
- ✅ CSRF protection
- ✅ SSL/TLS en producción
- ✅ Variables de entorno para secrets

## 📄 Licencia

MIT
