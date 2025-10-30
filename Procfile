release: python manage.py makemigrations --noinput && python manage.py migrate --noinput
web: python manage.py collectstatic --noinput && gunicorn ventasbasico.wsgi:application --bind 0.0.0.0:$PORT
