# Despliegue en Render - Instrucciones

## Problemas Resueltos

### 1. Archivos estáticos del admin (404 errors)
Los archivos estáticos del admin de Django no se estaban sirviendo correctamente, causando errores 404.

### 2. Worker Timeout y Error 500
El servidor se crasheaba con "WORKER TIMEOUT" y "out of memory" causando errores 500. 

**Causas identificadas:**
- Función `generar_numero_venta()` duplicada que podía causar loops infinitos
- Falta de manejo de errores en las vistas
- Configuración inadecuada de Gunicorn (timeout muy bajo)
- Problemas de conexión con la base de datos PostgreSQL

## Cambios Realizados

### 1. Archivo `build.sh`
Script que Render ejecuta antes de iniciar el servidor:
- Instala dependencias
- Recolecta archivos estáticos con `collectstatic`
- Ejecuta migraciones

### 2. Configuración de Static Files en `settings.py`
- Se configuró `STATIC_ROOT` para todos los ambientes
- Se usa WhiteNoise para servir archivos estáticos en producción
- Agregado logging para depuración
- Optimización de conexiones a la base de datos con `CONN_MAX_AGE`

### 3. Correcciones en `views.py`
- Eliminada función `generar_numero_venta()` duplicada
- Agregado manejo de excepciones en todas las vistas
- Implementado logging para errores
- Prevención de loops infinitos en generación de número de venta

### 4. Configuración de Gunicorn (`gunicorn.conf.py`)
- Timeout aumentado a 120 segundos
- 2 workers configurados
- Max requests: 1000 con jitter de 50
- Logging habilitado

### 5. Requirements actualizados
- Cambiado `psycopg2` por `psycopg2-binary` (mejor compatibilidad en Render)

### 6. Archivos adicionales
- `runtime.txt`: Especifica la versión de Python
- `render.yaml`: Configuración completa para Render

## Pasos para Redesplegar en Render

### Paso 1: Hacer commit y push

```bash
git add .
git commit -m "Fix: Corregir timeouts, errores 500 y archivos estáticos"
git push origin main
```

### Paso 2: Configurar en Render Dashboard

1. Ve a tu servicio en [Render Dashboard](https://dashboard.render.com/)
2. En la pestaña "Settings":
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn ventasbasico.wsgi:application -c gunicorn.conf.py`

3. **IMPORTANTE**: Verifica las variables de entorno en la sección "Environment":
   ```
   SECRET_KEY=tu_secret_key_segura_aqui
   DB_NAME=nombre_de_tu_base_de_datos
   DB_USER=usuario_de_base_de_datos
   DB_PASSWORD=password_de_base_de_datos
   DB_HOST=host_de_base_de_datos.render.com
   DB_PORT=6543
   RENDER_EXTERNAL_HOSTNAME=pueba-backend-1.onrender.com
   ```

4. **Verificar la base de datos PostgreSQL**:
   - Asegúrate de que tu base de datos PostgreSQL esté activa y funcionando
   - Ve a la sección de PostgreSQL en Render y verifica que el estado sea "Available"
   - Si la BD está "suspendida", puede causar timeouts

### Paso 3: Redesplegar

Render automáticamente redespleará cuando hagas push, o puedes:
1. Ir a tu servicio en Render
2. Hacer clic en "Manual Deploy" → "Deploy latest commit"

## Verificación

Después del despliegue:
1. Ve a `https://pueba-backend-1.onrender.com/`
2. Verifica que carga sin errores 500
3. Ve a `https://pueba-backend-1.onrender.com/admin/`
4. Los archivos CSS y JS deberían cargarse correctamente (sin errores 404)
5. El admin debería funcionar sin problemas y sin timeouts

## Troubleshooting

### Si sigues viendo Error 500:
1. Revisa los logs en Render (botón "Logs")
2. Busca mensajes de error específicos
3. Verifica que la base de datos PostgreSQL esté activa

### Si ves "WORKER TIMEOUT":
1. El timeout ahora es de 120 segundos (suficiente para consultas normales)
2. Si persiste, puede indicar un problema con la base de datos
3. Verifica la conexión a PostgreSQL

### Si la base de datos no conecta:
1. Verifica que todas las variables de entorno estén correctas
2. El `DB_HOST` debe ser el hostname interno de Render (termina en `.render.com`)
3. El `DB_PORT` es típicamente `5432` o `6543`

### Si los archivos estáticos no cargan:
1. Verifica que `build.sh` se haya ejecutado correctamente
2. En los logs debe aparecer: "Collecting static files..."
3. Verifica que WhiteNoise esté en `MIDDLEWARE` en settings.py

## Plan de Respaldo

Si después de desplegar siguen los problemas:

1. **Activar DEBUG temporalmente** (solo para diagnóstico):
   - En Environment variables, cambiar `DEBUG=True`
   - Redesplegar
   - Ver el error detallado en el navegador
   - **IMPORTANTE**: Volver a `DEBUG=False` después de identificar el problema

2. **Verificar logs de la base de datos**:
   - Ve a tu servicio PostgreSQL en Render
   - Revisa los logs para ver si hay errores de conexión

3. **Crear superusuario** (si no existe):
   ```bash
   # En la shell de Render o localmente con las credenciales de producción
   python manage.py createsuperuser
   ```

## Variables de Entorno Requeridas

```bash
SECRET_KEY=tu_secret_key_muy_segura_y_larga
DB_NAME=nombre_base_datos
DB_USER=usuario_postgres
DB_PASSWORD=password_postgres
DB_HOST=hostname-postgres.render.com
DB_PORT=6543
RENDER_EXTERNAL_HOSTNAME=pueba-backend-1.onrender.com
DEBUG=False
```

## Próximos Pasos Recomendados

1. Una vez funcionando, considera implementar:
   - Redis para caché de sesiones
   - Monitoreo con Sentry
   - Backups automáticos de la base de datos
   - CDN para archivos estáticos (opcional)
