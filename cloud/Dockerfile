FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Dashboard only in cloud mode (no PyQt6 / audio in container)
ENV NISHA_CLOUD_MODE=true
EXPOSE 8765

CMD ["python", "dashboard/server.py"]
