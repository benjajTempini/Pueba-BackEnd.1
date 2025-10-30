web: python manage.py collectstatic --noinput --clear && python manage.py migrate --noinput && gunicorn ventasbasico.wsgi:application --bind 0.0.0.0:$PORT
