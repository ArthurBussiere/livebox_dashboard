# ── Stage 1: Build Angular ────────────────────────────────────────────────────
FROM node:22-alpine AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build -- --configuration production

# ── Stage 2: Python runtime ───────────────────────────────────────────────────
FROM python:3.13-slim
WORKDIR /app

# Install uv and Python dependencies
COPY backend/pyproject.toml backend/uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --no-dev --frozen

# Copy backend source
COPY backend/ ./

# Copy Angular static build
COPY --from=frontend /app/dist/livebox_dashboard/browser/ ./static/
RUN mv ./static/index.csr.html ./static/index.html

EXPOSE 4350
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4350"]
