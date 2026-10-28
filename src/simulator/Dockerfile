FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN pip install --no-cache-dir "aiohttp==3.11.18" "msgpack==1.1.0"

WORKDIR /app
COPY marketsim /app/marketsim

RUN useradd --create-home --uid 10001 sim
USER sim

EXPOSE 8001 8002 8003 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)" || exit 1

ENTRYPOINT ["python", "-m", "marketsim"]
