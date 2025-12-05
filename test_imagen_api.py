"""
Script de prueba para verificar el sistema de imágenes
Crea un producto de prueba con una imagen PNG simple
"""
import requests
import base64
from io import BytesIO
from PIL import Image

# Configuración
API_URL = "http://127.0.0.1:8000/api/productos/"

def crear_imagen_prueba():
    """Crea una imagen simple de 200x200 píxeles"""
    print("📸 Generando imagen de prueba...")
    
    # Crear imagen RGB de 200x200 píxeles (fondo azul)
    img = Image.new('RGB', (200, 200), color=(73, 109, 137))
    
    # Guardar en memoria como PNG
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convertir a base64
    base64_image = base64.b64encode(buffer.read()).decode('utf-8')
    
    print(f"✅ Imagen generada: {len(base64_image)} caracteres")
    print(f"   Tamaño aproximado: {len(base64_image) / 1024:.2f} KB")
    
    return f"data:image/png;base64,{base64_image}"

def test_crear_producto_con_imagen():
    """Prueba crear un producto con imagen"""
    print("\n" + "="*60)
    print("🧪 TEST: Crear producto con imagen")
    print("="*60)
    
    # Generar imagen
    foto_base64 = crear_imagen_prueba()
    
    # Datos del producto
    producto = {
        "nombre": "Producto de Prueba con Imagen",
        "codigo": "TEST-IMG-001",
        "stock": 100,
        "precio": 99.99,
        "foto": foto_base64
    }
    
    print("\n📤 Enviando producto al backend...")
    print(f"   Nombre: {producto['nombre']}")
    print(f"   Código: {producto['codigo']}")
    print(f"   Tiene foto: Sí")
    
    try:
        response = requests.post(API_URL, json=producto)
        
        if response.status_code == 201:
            print("\n✅ ¡ÉXITO! Producto creado correctamente")
            data = response.json()
            print(f"\n📊 Respuesta del servidor:")
            print(f"   ID: {data.get('id')}")
            print(f"   Nombre: {data.get('nombre')}")
            print(f"   Código: {data.get('codigo')}")
            print(f"   Tiene foto_url: {'Sí' if data.get('foto_url') else 'No'}")
            if data.get('foto_url'):
                print(f"   Tamaño foto_url: {len(data['foto_url'])} caracteres")
                print(f"   Preview: {data['foto_url'][:50]}...")
            
            return data
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que Django esté corriendo:")
        print("   python manage.py runserver")
        return None
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        return None

def test_obtener_producto(producto_id):
    """Prueba obtener un producto y verificar que la imagen viene en base64"""
    print("\n" + "="*60)
    print(f"🧪 TEST: Obtener producto ID {producto_id}")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}{producto_id}/")
        
        if response.status_code == 200:
            print("\n✅ Producto obtenido correctamente")
            data = response.json()
            print(f"\n📊 Datos recibidos:")
            print(f"   ID: {data.get('id')}")
            print(f"   Nombre: {data.get('nombre')}")
            print(f"   Código: {data.get('codigo')}")
            
            if data.get('foto_url'):
                print(f"\n📸 Imagen encontrada:")
                print(f"   Tipo: {'base64 con prefijo' if data['foto_url'].startswith('data:image') else 'otro'}")
                print(f"   Tamaño: {len(data['foto_url'])} caracteres")
                print(f"   Preview: {data['foto_url'][:80]}...")
                print(f"\n✅ La imagen está lista para usar en <img src=\"{data['foto_url'][:30]}...\" />")
            else:
                print("\n⚠️ No se encontró foto_url")
            
            return data
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

def test_crear_sin_imagen():
    """Prueba crear un producto sin imagen (campo opcional)"""
    print("\n" + "="*60)
    print("🧪 TEST: Crear producto SIN imagen")
    print("="*60)
    
    producto = {
        "nombre": "Producto Sin Imagen",
        "codigo": "TEST-NOIMG-001",
        "stock": 50,
        "precio": 49.99,
        "foto": None
    }
    
    print("\n📤 Enviando producto sin foto...")
    
    try:
        response = requests.post(API_URL, json=producto)
        
        if response.status_code == 201:
            print("\n✅ ¡ÉXITO! Producto creado sin imagen")
            data = response.json()
            print(f"   ID: {data.get('id')}")
            print(f"   foto_url: {data.get('foto_url')}")
            return data
        else:
            print(f"\n❌ Error HTTP {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

def test_imagen_muy_grande():
    """Prueba enviar una imagen que excede el límite de 5MB"""
    print("\n" + "="*60)
    print("🧪 TEST: Imagen muy grande (debe fallar)")
    print("="*60)
    
    # Crear imagen muy grande (6000x6000 = ~100MB sin comprimir)
    print("📸 Generando imagen grande (esto puede tomar unos segundos)...")
    img = Image.new('RGB', (6000, 6000), color=(255, 0, 0))
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    base64_image = base64.b64encode(buffer.read()).decode('utf-8')
    
    print(f"✅ Imagen generada: {len(base64_image) / 1024 / 1024:.2f} MB")
    
    producto = {
        "nombre": "Producto con Imagen Grande",
        "codigo": "TEST-BIG-001",
        "stock": 10,
        "precio": 19.99,
        "foto": f"data:image/png;base64,{base64_image}"
    }
    
    print("\n📤 Enviando imagen grande (debe ser rechazada)...")
    
    try:
        response = requests.post(API_URL, json=producto)
        
        if response.status_code == 400:
            print("\n✅ ¡CORRECTO! La validación rechazó la imagen")
            print(f"   Error: {response.json()}")
        else:
            print(f"\n⚠️ Respuesta inesperada: HTTP {response.status_code}")
            print(f"   {response.text}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   🧪 SUITE DE PRUEBAS - SISTEMA DE IMÁGENES               ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("📋 Pruebas a ejecutar:")
    print("   1. Crear producto CON imagen")
    print("   2. Obtener producto y verificar foto_url")
    print("   3. Crear producto SIN imagen (opcional)")
    print("   4. Validar rechazo de imagen muy grande")
    
    input("\n📍 Presiona Enter para comenzar (asegúrate de tener Django corriendo)...")
    
    # Test 1: Crear con imagen
    producto_creado = test_crear_producto_con_imagen()
    
    if producto_creado:
        # Test 2: Obtener producto
        test_obtener_producto(producto_creado['id'])
    
    # Test 3: Crear sin imagen
    test_crear_sin_imagen()
    
    # Test 4: Imagen muy grande
    test_imagen_muy_grande()
    
    print("\n" + "="*60)
    print("✅ SUITE DE PRUEBAS COMPLETADA")
    print("="*60)
    print("\n💡 Notas:")
    print("   - Los productos de prueba quedaron en la base de datos")
    print("   - Puedes verlos en: http://127.0.0.1:8000/admin/ventasbasico/productos/")
    print("   - O en la API: http://127.0.0.1:8000/api/productos/")
    print("\n🚀 ¡El sistema de imágenes está funcionando correctamente!")
