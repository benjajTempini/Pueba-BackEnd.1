# 📸 Documentación - Manejo de Imágenes en la API

## ✅ Implementación Completada

El backend ahora está **100% configurado** para recibir imágenes en cualquier formato y convertirlas automáticamente a BLOB para guardar en la base de datos.

---

## 🎯 Características Implementadas

### ✅ Formatos Soportados
- **JPEG / JPG**
- **PNG**
- **GIF**
- **WEBP**
- **BMP**

### ✅ Validaciones Automáticas
- ✅ Validación de formato (solo imágenes válidas)
- ✅ Validación de corrupción (detecta archivos dañados)
- ✅ Límite de tamaño: **5MB máximo**
- ✅ Conversión automática base64 → bytes (BLOB)
- ✅ Conversión automática bytes → base64 (para respuestas)

### ✅ Seguridad
- Verifica integridad de imagen con Pillow
- Rechaza archivos corruptos o maliciosos
- Límite de memoria configurado

---

## 📤 Cómo Enviar Imágenes desde el Frontend

### Opción 1: Base64 con Prefijo (Recomendado)
```json
{
  "nombre": "Laptop Lenovo",
  "codigo": "LAP-001",
  "stock": 10,
  "precio": 999.99,
  "foto": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

### Opción 2: Base64 Puro
```json
{
  "nombre": "Mouse Gamer",
  "codigo": "MOU-001",
  "stock": 50,
  "precio": 29.99,
  "foto": "/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

### Opción 3: Sin Imagen (Opcional)
```json
{
  "nombre": "Teclado Mecánico",
  "codigo": "TEC-001",
  "stock": 20,
  "precio": 79.99,
  "foto": null
}
```

---

## 📥 Respuesta de la API

### GET /api/productos/
```json
[
  {
    "id": 1,
    "nombre": "Laptop Lenovo",
    "codigo": "LAP-001",
    "stock": 10,
    "precio": "999.99",
    "foto_url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...",
    "descripcion_corta": null,
    "descripcion_larga": null,
    "palabras_clave": null,
    "beneficios": null,
    "descripcion_generada_fecha": null
  }
]
```

### GET /api/productos/{codigo}/ (Buscar por código)
```json
{
  "id": 1,
  "nombre": "Laptop Lenovo",
  "codigo": "LAP-001",
  "stock": 10,
  "precio": "999.99",
  "foto_url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
}
```

**Notas:** 
- El campo `foto` (bytes) NO se envía en las respuestas, solo `foto_url` (base64)
- **La API usa el campo `codigo` como identificador** en lugar del `id` autogenerado
- Endpoints: `GET /api/productos/LAP-001/`, `PUT /api/productos/LAP-001/`, `DELETE /api/productos/LAP-001/`

---

## 🧪 Ejemplo con JavaScript/TypeScript

### Angular Service
```typescript
// producto.service.ts
import { HttpClient } from '@angular/common/http';

crearProductoConImagen(producto: any, archivo: File): Observable<any> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = () => {
      // Convertir archivo a base64
      const base64 = reader.result as string;
      
      // Agregar al producto
      producto.foto = base64;
      
      // Enviar al backend
      this.http.post('http://localhost:8000/api/productos/', producto)
        .subscribe(
          response => resolve(response),
          error => reject(error)
        );
    };
    
    reader.onerror = error => reject(error);
    reader.readAsDataURL(archivo); // Genera base64 con prefijo
  });
}

// Obtener producto por CODIGO (no por ID)
obtenerProducto(codigo: string): Observable<any> {
  return this.http.get(`http://localhost:8000/api/productos/${codigo}/`);
}

// Actualizar producto por CODIGO
actualizarProducto(codigo: string, producto: any, archivo?: File): Observable<any> {
  if (archivo) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        producto.foto = reader.result as string;
        this.http.put(`http://localhost:8000/api/productos/${codigo}/`, producto)
          .subscribe(resolve, reject);
      };
      reader.readAsDataURL(archivo);
    });
  } else {
    return this.http.put(`http://localhost:8000/api/productos/${codigo}/`, producto);
  }
}

// Eliminar producto por CODIGO
eliminarProducto(codigo: string): Observable<any> {
  return this.http.delete(`http://localhost:8000/api/productos/${codigo}/`);
}
```

### React Example
```javascript
const handleImageUpload = async (file) => {
  const base64 = await convertToBase64(file);
  
  const producto = {
    nombre: "Producto Nuevo",
    codigo: "PROD-001",
    stock: 100,
    precio: 49.99,
    foto: base64
  };
  
  const response = await fetch('http://localhost:8000/api/productos/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(producto)
  });
  
  return response.json();
};

const convertToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
};
```

---

## ❌ Mensajes de Error

### Error: Formato no permitido
```json
{
  "foto": ["Formato TIFF no permitido. Usa: JPEG, JPG, PNG, GIF, WEBP, BMP"]
}
```

### Error: Imagen muy grande
```json
{
  "foto": ["Imagen muy grande. Máximo 5MB, recibido: 8.45MB"]
}
```

### Error: Imagen corrupta
```json
{
  "foto": ["Imagen corrupta o inválida: cannot identify image file"]
}
```

### Error: Base64 inválido
```json
{
  "foto": ["Base64 inválido"]
}
```

---

## 🔧 Configuración del Backend

### Modelo (ventasbasico/models.py)
2. **Probar con curl:**
   ```bash
   # Crear producto
   curl -X POST http://localhost:8000/api/productos/ \
     -H "Content-Type: application/json" \
     -d @test_producto_imagen.json
   
   # Obtener producto por CODIGO (no por ID)
   curl http://localhost:8000/api/productos/LAP-001/
   
   # Actualizar producto por CODIGO
   curl -X PUT http://localhost:8000/api/productos/LAP-001/ \
     -H "Content-Type: application/json" \
     -d '{"nombre":"Laptop HP Actualizada","codigo":"LAP-001","stock":20,"precio":799.99}'
   
   # Eliminar producto por CODIGO
   curl -X DELETE http://localhost:8000/api/productos/LAP-001/
   ```

3. **Verificar en admin:**
   - Accede a `/admin/ventasbasico/productos/`
   - Las imágenes se guardan como BLOB en la BD
   - Se pueden visualizar en el admin
- ✅ Conversión automática base64 → bytes
- ✅ Validación de formato con Pillow
- ✅ Validación de tamaño (5MB max)
- ✅ Conversión automática bytes → base64 para respuestas
- ✅ Campo `foto_url` en respuestas (listo para usar en `<img src="">`)

---

## 🚀 Próximos Pasos

1. **Aplicar migraciones:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Probar con curl:**
   ```bash
   curl -X POST http://localhost:8000/api/productos/ \
     -H "Content-Type: application/json" \
     -d @test_producto_imagen.json
   ```

3. **Verificar en admin:**
   - Accede a `/admin/ventasbasico/productos/`
   - Las imágenes se guardan como BLOB en la BD
   - Se pueden visualizar en el admin

---

## 📊 Ventajas de BinaryField (BLOB)

✅ **Portabilidad:** Base de datos contiene todo (no depende de carpeta media/)  
✅ **Backups simples:** Un dump de BD tiene todo incluido  
✅ **Sin rutas rotas:** No hay problemas de archivos eliminados  
✅ **Transaccional:** Rollback automático si falla la creación  

⚠️ **Consideraciones:**
- Puede aumentar el tamaño de la base de datos
- Para miles de imágenes grandes, considerar ImageField + storage externo
- Ideal para catálogos pequeños/medianos (< 1000 productos)

---

## 🎨 Mostrar Imagen en Frontend

### HTML Directo
```html
<img [src]="producto.foto_url" alt="{{ producto.nombre }}" />
```

### Angular
```typescript
<img [src]="producto.foto_url" 
     [alt]="producto.nombre"
     class="product-image" />
```
## 🔑 Importante: Identificador por CODIGO

**La API usa `codigo` como identificador único, NO el `id` autogenerado:**

```bash
❌ Incorrecto: GET /api/productos/1/
✅ Correcto:   GET /api/productos/LAP-001/

❌ Incorrecto: PUT /api/productos/1/
✅ Correcto:   PUT /api/productos/LAP-001/

❌ Incorrecto: DELETE /api/productos/1/
✅ Correcto:   DELETE /api/productos/LAP-001/
```

**En el frontend:**
```typescript
// ❌ NO usar el ID
const producto = await fetch(`/api/productos/${producto.id}/`);

// ✅ SÍ usar el CODIGO
const producto = await fetch(`/api/productos/${producto.codigo}/`);
```

---

## ✅ Resumen

🎉 **Backend 100% listo para recibir imágenes:**
- ✅ Acepta cualquier formato (JPG, PNG, GIF, WEBP, BMP)
- ✅ Conversión automática base64 → BLOB
- ✅ Validación de formato y tamaño
- ✅ Respuestas con base64 listo para usar
- ✅ Límite de 5MB configurado
- ✅ Sin configuración adicional requerida
- ✅ **Identificación por `codigo` (no por `id`)**

**Solo envía las imágenes en base64 desde tu frontend y el backend hace todo el resto automáticamente.** 🚀

## ✅ Resumen

🎉 **Backend 100% listo para recibir imágenes:**
- ✅ Acepta cualquier formato (JPG, PNG, GIF, WEBP, BMP)
- ✅ Conversión automática base64 → BLOB
- ✅ Validación de formato y tamaño
- ✅ Respuestas con base64 listo para usar
- ✅ Límite de 5MB configurado
- ✅ Sin configuración adicional requerida

**Solo envía las imágenes en base64 desde tu frontend y el backend hace todo el resto automáticamente.** 🚀
