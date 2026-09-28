# Dealwright — Railway deploy image (uv-managed, no dev deps, no node).
# Tailwind builds via the standalone CLI in a dedicated stage (design-log: no npm pipeline).

# --- Stage 1: build Tailwind CSS from templates/python sources ---
FROM python:3.13-slim AS css
ADD https://github.com/tailwindlabs/tailwindcss/releases/download/v4.1.13/tailwindcss-linux-x64 /bin/tailwindcss
RUN chmod +x /bin/tailwindcss
WORKDIR /src
COPY static/css/src/input.css static/css/src/input.css
COPY templates/ templates/
COPY core/ core/
COPY config/ config/
RUN /bin/tailwindcss -i static/css/src/input.css -o static/css/app.css --minify

# --- Stage 2: runtime ---
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/uv

WORKDIR /app

# Install deps first so this layer caches independently of app code.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .
# Fresh CSS build wins over the committed artifact.
COPY --from=css /src/static/css/app.css /app/static/css/app.css
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
# Railway injects PORT; migrate/collectstatic run at container start (system-design.md).
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2"]
