# ---------- Stage 1: Crawler ----------
FROM python:3.12-slim AS crawler

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kicad_adds_on_spider/ kicad_adds_on_spider/
COPY main.py .

# Use a placeholder that entrypoint.sh will later replace with the real base URL
RUN python main.py /mirror_data --download-url "http://__KICAD_MIRROR_BASE__/"


# ---------- Stage 2: Nginx static server ----------
FROM nginx:alpine AS final

COPY --from=crawler /mirror_data /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /docker-entrypoint.d/90-rewrite-urls.sh
RUN chmod +x /docker-entrypoint.d/90-rewrite-urls.sh

EXPOSE 80

# nginx:alpine's default CMD already runs "nginx -g 'daemon off;'"
