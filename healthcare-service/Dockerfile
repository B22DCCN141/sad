FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8015

CMD ["sh", "-c", "python manage.py migrate --settings=config.settings.dev && python manage.py seed_healthcare_data --settings=config.settings.dev && python manage.py runserver 0.0.0.0:8015 --settings=config.settings.dev"]
