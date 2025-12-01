"""
Script de prueba para las funcionalidades de IA con Groq Cloud
Ejecutar: python test_groq_ai.py
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
# Si tienes el servidor en otro puerto o URL, cámbialo aquí

def print_json(data, title=""):
    """Helper para imprimir JSON formateado"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_stats_ia():
    """Verifica cuántos productos ve la IA"""
    print("\n📊 VERIFICANDO ESTADÍSTICAS DE LA IA")
    
    url = f"{BASE_URL}/api/ia/stats/"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print_json(data, "✅ ESTADÍSTICAS DE LA IA")
            print(f"\n💡 {data.get('mensaje', '')}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")

def test_recomendador_productos():
    """Prueba el recomendador de productos con IA"""
    print("\n🤖 PROBANDO RECOMENDADOR DE PRODUCTOS CON IA")
    
    url = f"{BASE_URL}/api/ia/productos/recomendar/"
    data = {
        "rut_cliente": "12345678-9",  # Cambia por un RUT real en tu BD
        "limite": 3
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print_json(response.json(), "✅ RECOMENDACIONES GENERADAS")
        elif response.status_code == 404:
            print(f"❌ Cliente no encontrado. Asegúrate que existe el RUT: {data['rut_cliente']}")
            print("   Puedes crear uno en /api/clientes/ primero")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        print(f"   Asegúrate que el servidor está corriendo en {BASE_URL}")

def test_generar_descripcion():
    """Prueba el generador de descripciones con IA"""
    print("\n📝 PROBANDO GENERADOR DE DESCRIPCIONES CON IA")
    
    # Primero necesitas autenticarte
    print("\n⚠️  Esta función requiere autenticación JWT")
    username = input("Ingresa tu usuario admin (o presiona Enter para saltar): ").strip()
    
    if not username:
        print("⏭️  Saltando prueba de generación de descripciones")
        return
    
    password = input("Ingresa tu contraseña: ").strip()
    
    # Obtener token JWT
    token_url = f"{BASE_URL}/api/token/"
    try:
        token_response = requests.post(token_url, json={
            "username": username,
            "password": password
        })
        
        if token_response.status_code != 200:
            print(f"❌ Error de autenticación: {token_response.text}")
            return
        
        token = token_response.json()['access']
        print("✅ Token JWT obtenido exitosamente")
        
        # Generar descripción para un producto
        producto_id = input("\nIngresa el ID del producto (o presiona Enter para usar 1): ").strip()
        producto_id = producto_id if producto_id else "1"
        
        url = f"{BASE_URL}/api/ia/productos/{producto_id}/generar-descripcion/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print_json(response.json(), "✅ DESCRIPCIÓN GENERADA")
        elif response.status_code == 404:
            print(f"❌ Producto con ID {producto_id} no encontrado")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_chatbot():
    """Prueba el chatbot de atención al cliente"""
    print("\n💬 PROBANDO CHATBOT DE ATENCIÓN AL CLIENTE")
    
    url = f"{BASE_URL}/api/ia/chat/"
    
    # Ejemplos de mensajes
    mensajes_test = [
        "¿Cuál es el horario de atención?",
        "¿Qué métodos de pago aceptan?",
        "¿Tienen mouse gamer disponible?",
        "¿Cuánto demora el despacho a regiones?"
    ]
    
    print("\nMensajes de prueba:")
    for i, msg in enumerate(mensajes_test, 1):
        print(f"{i}. {msg}")
    
    opcion = input("\nSelecciona un mensaje (1-4) o escribe el tuyo: ").strip()
    
    if opcion.isdigit() and 1 <= int(opcion) <= 4:
        mensaje = mensajes_test[int(opcion) - 1]
    else:
        mensaje = opcion if opcion else mensajes_test[0]
    
    data = {
        "mensaje": mensaje
    }
    
    try:
        print(f"\n🧠 Consultando a la IA: '{mensaje}'")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print_json(result, "✅ RESPUESTA DEL CHATBOT")
            
            # Mostrar sugerencias de forma más amigable
            if result.get('sugerencias'):
                print("\n💡 Preguntas relacionadas:")
                for sug in result['sugerencias']:
                    print(f"   - {sug}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_chatbot_con_contexto():
    """Prueba el chatbot con contexto de venta"""
    print("\n🔍 PROBANDO CHATBOT CON CONTEXTO DE VENTA")
    
    venta_numero = input("Ingresa el número de venta (ej: 20241128-0001) o Enter para saltar: ").strip()
    
    if not venta_numero:
        print("⏭️  Saltando prueba con contexto")
        return
    
    url = f"{BASE_URL}/api/ia/chat/"
    data = {
        "mensaje": "¿Cuál es el estado de mi pedido?",
        "contexto": {
            "venta_numero": venta_numero
        }
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print_json(response.json(), "✅ RESPUESTA CON CONTEXTO")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🤖 PRUEBA DE FUNCIONALIDADES DE IA CON GROQ CLOUD     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\n⚙️  CONFIGURACIÓN")
    print(f"   URL Base: {BASE_URL}")
    print(f"   Asegúrate que:")
    print(f"   1. El servidor Django está corriendo")
    print(f"   2. Tienes GROQ_API_KEY configurada en .env")
    print(f"   3. Tienes datos de prueba en la BD")
    
    input("\n📍 Presiona Enter para continuar...")
    
    while True:
        print("\n" + "="*60)
        print("MENÚ DE PRUEBAS")
        print("="*60)
        print("0. 📊 Ver Estadísticas de IA (cuántos productos ve)")
        print("1. 🎯 Probar Recomendador de Productos")
        print("2. 📝 Probar Generador de Descripciones")
        print("3. 💬 Probar Chatbot Básico")
        print("4. 🔍 Probar Chatbot con Contexto de Venta")
        print("5. 🚀 Probar TODO")
        print("9. ❌ Salir")
        print("="*60)
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "0":
            test_stats_ia()
        elif opcion == "1":
            test_recomendador_productos()
        elif opcion == "2":
            test_generar_descripcion()
        elif opcion == "3":
            test_chatbot()
        elif opcion == "4":
            test_chatbot_con_contexto()
        elif opcion == "5":
            test_stats_ia()
            test_recomendador_productos()
            test_generar_descripcion()
            test_chatbot()
            test_chatbot_con_contexto()
        elif opcion == "9":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción inválida")
        
        input("\n📍 Presiona Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario")
