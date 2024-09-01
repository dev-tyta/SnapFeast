pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --noinput

gunicorn snapfeast.wsgi:application --bind -w 2