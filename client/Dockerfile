FROM python:3.9-slim

WORKDIR /app

RUN pip install inputimeout

COPY . .

EXPOSE 4050

CMD ["python", "client_app.py"]