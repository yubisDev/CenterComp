release: python manage.py migrate
web: gunicorn centercomp.wsgi --timeout 120 --log-file -
