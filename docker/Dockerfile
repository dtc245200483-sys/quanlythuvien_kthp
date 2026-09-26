FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ACCEPT_EULA=Y

WORKDIR /app

# Cài đặt ODBC Driver 17 for SQL Server và thư viện phụ trợ
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    apt-transport-https \
    unixodbc-dev \
    g++ \
    gcc \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg \
    && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Python dependencies
COPY Backend/requirements.txt /app/Backend/requirements.txt
COPY chatbotAI/requirements.txt /app/chatbotAI/requirements.txt
RUN pip install --no-cache-dir -r /app/Backend/requirements.txt \
    && pip install --no-cache-dir -r /app/chatbotAI/requirements.txt \
    && pip install --no-cache-dir chromadb

# Copy toàn bộ mã nguồn vào image
COPY . /app/
RUN [ -d /app/frontend ] && [ ! -d /app/Frontend ] && ln -s /app/frontend /app/Frontend || true

WORKDIR /app/Backend

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
