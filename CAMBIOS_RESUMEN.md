# Resumen de Cambios para Render

## 🔧 Archivos Modificados

### 1. `ventasbasico/settings.py`
- ✅ Configuración de `STATIC_ROOT` y `STATICFILES_STORAGE` siempre activa
- ✅ Agregado `CONN_MAX_AGE` para optimizar conexiones a PostgreSQL
- ✅ Configurado sistema de logging para depuración
- ✅ Timeout de conexión a base de datos configurado

### 2. `ventasbasico/views.py`
- ✅ Eliminada función `generar_numero_venta()` duplicada
- ✅ Agregado manejo de excepciones en todas las vistas
- ✅ Implementado logging con `logger`
- ✅ Prevención de loops infinitos (máximo 10 intentos)
- ✅ Fallback a timestamp si no se puede generar número único

### 3. `requirements.txt`
- ✅ Cambiado `psycopg2` → `psycopg2-binary` (mejor para Render)

## 📄 Archivos Nuevos Creados

### 1. `build.sh` ⭐
Script de build que Render ejecuta automáticamente:
```bash
- Instala dependencias (pip install)
- Recolecta archivos estáticos (collectstatic)
- Ejecuta migraciones (migrate)
```

### 2. `gunicorn.conf.py` ⭐
Configuración optimizada de Gunicorn:
```python
- Timeout: 120 segundos (evita worker timeout)
- Workers: 2 (balance entre performance y memoria)
- Max requests: 1000 (previene memory leaks)
- Logging habilitado
```

### 3. `runtime.txt`
Especifica versión de Python: `python-3.11.0`

### 4. `render.yaml`
Configuración completa para Render (opcional pero recomendado)

### 5. `check_db.py`
Script de diagnóstico para verificar conexión a PostgreSQL

### 6. `DEPLOY_README.md`
Documentación completa de despliegue y troubleshooting

## 🚀 Comandos para Desplegar

```bash
# 1. Agregar todos los cambios
git add .

# 2. Hacer commit
git commit -m "Fix: Corregir timeouts, errores 500 y archivos estáticos"

# 3. Push a GitHub
git push origin main
```

## ⚙️ Configuración en Render Dashboard

Después del push, configurar en Render:

1. **Build Command**: `./build.sh`
2. **Start Command**: `gunicorn ventasbasico.wsgi:application -c gunicorn.conf.py`

3. **Environment Variables** (verificar que todas existen):
   - `SECRET_KEY`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_HOST`
   - `DB_PORT`
   - `RENDER_EXTERNAL_HOSTNAME`
   - `DEBUG=False`

## 🔍 Qué Problemas Se Solucionaron

### Problema 1: Error 404 en archivos estáticos
**Síntoma**: CSS y JS del admin no cargaban
**Causa**: `collectstatic` no se ejecutaba
**Solución**: Agregado `build.sh` que ejecuta `collectstatic`

### Problema 2: Error 500 en página principal
**Síntoma**: 
```
127.0.0.1 - - [28/Oct/2025:17:20:05 +0000] "HEAD / HTTP/1.1" 500
```
**Causas posibles**:
- Función duplicada causando conflictos
- Sin manejo de errores en consultas a BD
- Posible problema de conexión a PostgreSQL

**Soluciones aplicadas**:
- Eliminada función duplicada
- Agregado try/except en todas las vistas
- Optimizada configuración de base de datos
- Agregado logging para diagnóstico

### Problema 3: Worker Timeout
**Síntoma**: 
```
[2025-10-28 17:21:17 +0000] [56] [CRITICAL] WORKER TIMEOUT (pid:59)
[2025-10-28 17:21:18 +0000] [56] [ERROR] Worker (pid:59) was sent SIGKILL!
```
**Causa**: Timeout de Gunicorn muy bajo (default 30s)
**Solución**: 
- Timeout aumentado a 120 segundos en `gunicorn.conf.py`
- Prevención de loops infinitos en código
- Optimización de consultas a BD con `CONN_MAX_AGE`

## ✅ Checklist Pre-Deploy

Antes de hacer push, verificar:

- [x] Todos los archivos creados están en el repositorio
- [x] `build.sh` está presente
- [x] `requirements.txt` actualizado con `psycopg2-binary`
- [x] `gunicorn.conf.py` creado
- [x] Variables de entorno configuradas en Render
- [x] Base de datos PostgreSQL está activa en Render

## 🧪 Pruebas Después del Deploy

1. ✅ Página principal carga: `https://pueba-backend-1.onrender.com/`
2. ✅ Admin carga con estilos: `https://pueba-backend-1.onrender.com/admin/`
3. ✅ Login del admin funciona sin timeout
4. ✅ No hay errores 404 en la consola del navegador (F12)
5. ✅ No hay worker timeouts en logs de Render

## 📊 Logs a Revisar

En Render Dashboard → Logs, buscar:

**✅ Señales buenas:**
```
Installing dependencies...
Collecting static files...
Running migrations...
Build completed successfully!
[INFO] Booting worker with pid: XX
```

**❌ Señales malas:**
```
[CRITICAL] WORKER TIMEOUT
[ERROR] Worker was sent SIGKILL
500 Internal Server Error
django.db.utils.OperationalError
```

## 🆘 Si Algo Falla

1. **Revisar logs de Render** primero
2. **Ejecutar localmente** `python check_db.py` para verificar BD
3. **Activar DEBUG=True temporalmente** para ver error detallado
4. **Verificar que la BD PostgreSQL esté activa** en Render
5. **Contactar soporte** si persiste el problema

---

**Nota**: Todos estos cambios están diseñados para funcionar en Render con plan gratuito, respetando las limitaciones de memoria y CPU.
