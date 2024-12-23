FROM python:3.10-alpine3.21 AS builder

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD [ "python", "app.py"]