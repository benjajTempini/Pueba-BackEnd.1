"""
Script para aplicar las migraciones de los nuevos campos de descripción IA
Ejecutar: python aplicar_migraciones_ia.py
"""

import os
import sys
import subprocess

print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   📝 APLICAR MIGRACIONES - CAMPOS DE DESCRIPCIÓN IA       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

print("\n🔧 Nuevos campos agregados al modelo Productos:")
print("   - descripcion_corta (CharField)")
print("   - descripcion_larga (TextField)")
print("   - palabras_clave (CharField)")
print("   - beneficios (TextField)")
print("   - descripcion_generada_fecha (DateTimeField)")

print("\n📋 PASOS:")
print("   1. Crear migración")
print("   2. Aplicar migración a la base de datos")

input("\n📍 Presiona Enter para continuar...")

try:
    print("\n" + "="*60)
    print("PASO 1: Creando archivo de migración...")
    print("="*60)
    
    result = subprocess.run(
        ['python', 'manage.py', 'makemigrations', 'ventasbasico'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("PASO 2: Aplicando migración a la base de datos...")
    print("="*60)
    
    result = subprocess.run(
        ['python', 'manage.py', 'migrate', 'ventasbasico'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ ¡MIGRACIONES APLICADAS EXITOSAMENTE!")
    print("="*60)
    
    print("""
    
📊 VERIFICACIÓN:
   1. Los productos ahora tienen campos para guardar descripciones IA
   2. El endpoint /api/ia/productos/{id}/generar-descripcion/ 
      GUARDARÁ automáticamente en la BD
   3. Puedes ver las descripciones en el admin de Django
   
🎯 PRÓXIMOS PASOS:
   1. Genera descripción para un producto usando el endpoint
   2. Verifica en /admin que se guardó correctamente
   3. Los productos ahora incluirán estos campos en la API REST
   
🚀 ¡Todo listo para usar!
    """)
    
except Exception as e:
    print(f"\n❌ Error inesperado: {str(e)}")
    sys.exit(1)
