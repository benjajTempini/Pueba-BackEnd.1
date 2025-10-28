# 🚀 Guía de Deployment en Render

## 📋 Preparación (Ya completada)

✅ Archivos creados:
- `build.sh` - Script de construcción
- `render.yaml` - Configuración de Render
- `requirements.txt` - Dependencias actualizadas
- `settings.py` - Configurado para producción

## 🔧 Pasos para Deployar en Render

### Opción 1: Deployment Automático con render.yaml (Recomendado)

1. **Sube tu código a GitHub**
   ```bash
   git add .
   git commit -m "Configuración para Render"
   git push origin main
   ```

2. **Ve a Render.com**
   - Ingresa a https://render.com
   - Haz login o crea una cuenta (puedes usar GitHub)

3. **Crea un nuevo Blueprint**
   - Click en "New +" → "Blueprint"
   - Conecta tu repositorio GitHub
   - Selecciona el repositorio `Pueba-BackEnd.1`
   - Render detectará automáticamente el archivo `render.yaml`
   - Click en "Apply"

4. **¡Listo!** 
   - Render creará automáticamente:
     - Base de datos PostgreSQL
     - Web Service con tu aplicación Django
   - Espera 5-10 minutos mientras se construye

### Opción 2: Deployment Manual

1. **Crea la Base de Datos**
   - En Render Dashboard, click "New +" → "PostgreSQL"
   - Name: `ventasbasico-db`
   - Database: `ventasbasico`
   - User: `ventasbasico`
   - Region: `Oregon (US West)` (o la más cercana)
   - Plan: Free
   - Click "Create Database"
   - **Guarda** el "Internal Database URL"

2. **Crea el Web Service**
   - Click "New +" → "Web Service"
   - Conecta tu repositorio GitHub
   - Selecciona `Pueba-BackEnd.1`
   - Configuración:
     - **Name**: `ventasbasico-backend`
     - **Region**: La misma que la base de datos
     - **Branch**: `main`
     - **Runtime**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn ventasbasico.wsgi:application`
     - **Plan**: Free

3. **Agrega Variables de Entorno**
   En la sección "Environment Variables", agrega:
   
   ```
   DATABASE_URL=<pega aquí el Internal Database URL de tu base de datos>
   SECRET_KEY=<genera una clave segura - ver abajo>
   DEBUG=False
   PYTHON_VERSION=3.13.0
   ```
   
   Para generar un SECRET_KEY seguro, ejecuta en tu terminal local:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Espera 5-10 minutos

## 🔐 Después del Deploy

### 1. Crear un Superusuario

Desde el Dashboard de Render:
- Ve a tu Web Service
- Click en "Shell" (en el menú lateral)
- Ejecuta:
  ```bash
  python manage.py createsuperuser
  ```

### 2. Acceder a tu aplicación

Tu aplicación estará disponible en:
- `https://ventasbasico-backend.onrender.com/`
- Admin: `https://ventasbasico-backend.onrender.com/admin/`
- Reporte: `https://ventasbasico-backend.onrender.com/admin/ventasbasico/venta/reporte-ventas/`

## ⚠️ Notas Importantes

### Conexión con Supabase (Alternativa)

Si prefieres usar tu base de datos de Supabase existente:

1. **NO** crees la base de datos en Render
2. En las variables de entorno, usa:
   ```
   DATABASE_URL=postgresql://postgres.hgvpoqkrxljatwcnimcb:219484216Benja@aws-1-us-east-2.pooler.supabase.com:6543/postgres
   ```

### Plan Free de Render

⚠️ **Limitaciones del plan gratuito**:
- El servicio se "duerme" después de 15 minutos de inactividad
- Primer request después de dormir toma ~30 segundos
- 750 horas gratis al mes
- Perfecto para desarrollo/testing

### Archivos Estáticos

Los archivos estáticos se sirven automáticamente con Whitenoise.
No necesitas configuración adicional.

## 🐛 Troubleshooting

### Si el build falla:

1. **Revisa los logs** en Render Dashboard → "Logs"
2. **Errores comunes**:
   - Permisos en `build.sh`: El archivo debe ser ejecutable
   - Variables de entorno faltantes
   - Problemas de dependencias en `requirements.txt`

### Si la app no carga:

1. Verifica que `DEBUG=False` en variables de entorno
2. Verifica que `DATABASE_URL` esté correctamente configurado
3. Revisa los logs de runtime

### Si los estilos del admin no cargan:

Ejecuta en el Shell de Render:
```bash
python manage.py collectstatic --no-input
```

## 📞 Siguientes Pasos

Después de deployar:
1. ✅ Crear superusuario
2. ✅ Probar login en admin
3. ✅ Verificar reporte de ventas
4. ✅ Probar CRUD de clientes y productos
5. ✅ Realizar una venta de prueba

## 🔒 Seguridad en Producción

- ✅ DEBUG está en False
- ✅ SECRET_KEY es único y secreto
- ✅ DATABASE_URL es privado
- ✅ ALLOWED_HOSTS configurado automáticamente
- ✅ Whitenoise maneja archivos estáticos de forma segura

¡Tu aplicación está lista para producción! 🎉
