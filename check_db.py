#!/usr/bin/env python
"""
Script para verificar la conexión a la base de datos
Ejecutar con: python check_db.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventasbasico.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def check_database():
    """Verifica la conexión a la base de datos"""
    try:
        print("🔍 Verificando conexión a la base de datos...")
        
        # Intentar una consulta simple
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        print("✅ Conexión exitosa a la base de datos!")
        print(f"   Engine: {connection.settings_dict['ENGINE']}")
        print(f"   Name: {connection.settings_dict['NAME']}")
        print(f"   Host: {connection.settings_dict['HOST']}")
        print(f"   Port: {connection.settings_dict['PORT']}")
        
        # Verificar migraciones
        print("\n🔍 Verificando migraciones...")
        call_command('showmigrations', '--list')
        
        return True
        
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos:")
        print(f"   {type(e).__name__}: {str(e)}")
        return False

if __name__ == '__main__':
    success = check_database()
    sys.exit(0 if success else 1)
