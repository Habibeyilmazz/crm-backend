FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# copy requirements first for better layer caching
COPY requirements.txt .

# install python deps (wheels) — no apt needed
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# copy the app
COPY . .

# lightweight entrypoint that switches API/Worker by env
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
CMD ["/entrypoint.sh"]
