FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

# Render (and most PaaS) inject the port to listen on via $PORT; default to 8080 for local use.
# gunicorn serves the Flask app object `app` from the `application` package (see application/__init__.py).
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --timeout 120 application:app