#!/bin/bash
# Script de inicio para Railway

# Obtener el puerto de Railway o usar 8000 por defecto
PORT="${PORT:-8000}"

echo "🚀 Iniciando Gunicorn en puerto $PORT"

# Iniciar Gunicorn
exec gunicorn ventasbasico.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
