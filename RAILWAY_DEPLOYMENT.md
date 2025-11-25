# Railway Deployment Guide

## 📦 Variables de entorno requeridas en Railway:

Configura estas variables en Railway Dashboard:

```env
# Django
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False

# Base de datos Supabase
DATABASE_URL=postgresql://postgres.hgvpoqkrxljatwcnimcb:219484216Benja@aws-1-us-east-2.pooler.supabase.com:6543/postgres

# O usa estas variables individuales:
DB_NAME=postgres
DB_USER=postgres.hgvpoqkrxljatwcnimcb
DB_PASSWORD=219484216Benja
DB_HOST=aws-1-us-east-2.pooler.supabase.com
DB_PORT=6543

# Railway (se configura automáticamente)
RAILWAY_PUBLIC_DOMAIN=tu-app.railway.app
```

## 🚀 Pasos para desplegar en Railway:

### 1. Instalar Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login en Railway
```bash
railway login
```

### 3. Crear nuevo proyecto
```bash
railway init
```

### 4. Vincular con GitHub (Recomendado)
- Ve a https://railway.app
- Crea un nuevo proyecto
- Conecta tu repositorio de GitHub
- Railway detectará automáticamente que es una app Django

### 5. Configurar variables de entorno
En el dashboard de Railway, ve a:
- **Variables** → Agrega las variables de arriba

### 6. Desplegar
```bash
# Si usas Railway CLI:
railway up

# O simplemente haz push a GitHub:
git add .
git commit -m "Deploy to Railway"
git push origin main
```

### 7. Crear superusuario (una vez desplegado)
```bash
railway run python manage.py createsuperuser
```

## ✅ Verificación

Después del despliegue:
1. Railway te dará una URL pública (ej: `https://tu-app.railway.app`)
2. Verifica que funcione: `https://tu-app.railway.app/admin/`
3. Prueba la API: `https://tu-app.railway.app/api/productos/`

## 🔧 Comandos útiles

```bash
# Ver logs
railway logs

# Ejecutar comandos en Railway
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py collectstatic

# Ver variables de entorno
railway variables

# Abrir el proyecto en el navegador
railway open
```

## 📝 Notas importantes:

1. ✅ La base de datos Supabase ya está configurada
2. ✅ Los archivos estáticos se sirven con WhiteNoise
3. ✅ CORS está configurado para permitir requests desde Angular
4. ✅ El proyecto usa PostgreSQL (compatible con Railway)
5. ⚠️ Recuerda cambiar `DEBUG=False` en producción
6. ⚠️ Genera una nueva SECRET_KEY segura para producción

## 🔐 Generar SECRET_KEY segura:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🌐 Configurar CORS para Angular:

En Railway, agrega la URL de tu frontend Angular a las variables:
```env
CORS_ALLOWED_ORIGINS=https://tu-frontend-angular.vercel.app
```

Y actualiza `settings.py` si necesitas restringir CORS.
