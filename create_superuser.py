#!/usr/bin/env python
"""
Script para crear un superusuario en producción
NOTA: Este script debe ejecutarse en la shell de Render
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ventasbasico.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    """Crea un superusuario si no existe"""
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    if User.objects.filter(username=username).exists():
        print(f"⚠️  El usuario '{username}' ya existe")
        return False
    
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Superusuario '{username}' creado exitosamente")
        print(f"   Email: {email}")
        print(f"   ⚠️  CAMBIAR LA CONTRASEÑA DESPUÉS DE INICIAR SESIÓN")
        return True
    except Exception as e:
        print(f"❌ Error al crear superusuario: {str(e)}")
        return False

if __name__ == '__main__':
    success = create_superuser()
    sys.exit(0 if success else 1)
