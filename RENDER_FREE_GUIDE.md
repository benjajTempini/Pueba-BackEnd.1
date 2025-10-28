# 🚀 Deploy en Render - Web Service (GRATIS - Sin Saldo)

## ✅ OPCIÓN GRATIS - NEW WEB SERVICE

### 🎯 Opción 1: Usar Supabase (Base de datos actual)

#### Paso 1: Crear Web Service en Render

1. **Ve a Render.com**
   - Click en **"New +"** → **"Web Service"**
   - Conecta tu repositorio GitHub
   - Selecciona: `Pueba-BackEnd.1`

2. **Configuración Básica:**
   ```
   Name: ventasbasico-backend
   Region: Oregon (US West) o la que prefieras
   Branch: main
   Runtime: Python 3
   ```

3. **Build & Start Commands:**
   ```
   Build Command: ./build.sh
   Start Command: gunicorn ventasbasico.wsgi:application
   ```

4. **Plan:**
   - Selecciona: **FREE** 🎉
   - (NO necesitas saldo para este plan)

#### Paso 2: Variables de Entorno

En la sección **"Environment Variables"**, agrega estas:

```bash
# Base de datos Supabase (tu actual)
DATABASE_URL=postgresql://postgres.hgvpoqkrxljatwcnimcb:219484216Benja@aws-1-us-east-2.pooler.supabase.com:6543/postgres

# Seguridad
DEBUG=False

# Genera un SECRET_KEY ejecutando en tu terminal:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=tu-secret-key-generado-aqui

# Hosts permitidos
ALLOWED_HOSTS=.onrender.com

# Versión de Python
PYTHON_VERSION=3.13.0
```

#### Paso 3: Deploy

1. Click en **"Create Web Service"**
2. Espera 5-10 minutos ☕
3. ¡Tu app estará lista!

---

### 🎯 Opción 2: Crear Base de Datos en Render (También GRATIS)

Si prefieres usar PostgreSQL de Render:

#### Paso 1: Crear Base de Datos PostgreSQL

1. **New +** → **PostgreSQL**
2. Configuración:
   ```
   Name: ventasbasico-db
   Database: ventasbasico
   User: ventasbasico
   Region: Oregon (US West)
   Plan: FREE ← IMPORTANTE
   ```
3. Click **"Create Database"**
4. **Copia** el **"Internal Database URL"** que aparece

#### Paso 2: Crear Web Service

Igual que la Opción 1, pero en Variables de Entorno usa:

```bash
# Usa el Internal Database URL que copiaste
DATABASE_URL=postgresql://ventasbasico:xxxxx@dpg-xxxxx/ventasbasico

DEBUG=False
SECRET_KEY=tu-secret-key-generado-aqui
ALLOWED_HOSTS=.onrender.com
PYTHON_VERSION=3.13.0
```

---

## 🔐 Generar SECRET_KEY

En tu terminal local (Windows):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y úsalo en la variable `SECRET_KEY`

---

## ✅ Después del Deploy

### 1. Crear Superusuario

En Render Dashboard:
- Ve a tu **Web Service**
- Click en **"Shell"** (menú lateral)
- Ejecuta:
```bash
python manage.py createsuperuser
```

### 2. Acceder a tu App

Tu URL será algo como:
```
https://ventasbasico-backend.onrender.com/admin/
https://ventasbasico-backend.onrender.com/admin/ventasbasico/venta/reporte-ventas/
```

---

## 📊 Comparación de Opciones

### Opción 1: Supabase (RECOMENDADO)
✅ Ya está configurado
✅ Tus datos actuales se mantienen
✅ Sin configuración adicional
✅ 100% GRATIS

### Opción 2: PostgreSQL de Render
✅ Todo en una plataforma
✅ Fácil de gestionar
⚠️ Plan FREE: 1GB, 90 días de retención
✅ 100% GRATIS

---

## 🐛 Troubleshooting

### Si los logs muestran error de permisos en build.sh:

En tu terminal local:
```bash
git update-index --chmod=+x build.sh
git commit -m "Make build.sh executable"
git push
```

### Si no carga el admin (sin estilos):

En el Shell de Render:
```bash
python manage.py collectstatic --no-input
```

### Si hay error de conexión a la base de datos:

Verifica que el `DATABASE_URL` esté correcto:
- Para Supabase: debe tener el puerto 6543 (pooler)
- Para Render DB: usa el Internal Database URL completo

---

## 🎉 ¡Todo listo!

Con esta configuración:
- ✅ **NO necesitas saldo** en Render
- ✅ Plan **FREE** permanente
- ✅ Web Service gratis (750 horas/mes)
- ✅ Base de datos gratis (Supabase o Render)

**No te van a cobrar NADA** 💰
