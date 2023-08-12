FROM python:3.9-slim

WORKDIR /app

RUN pip install retrying

COPY . .

EXPOSE 4040

CMD ["python", "server_app.py"]