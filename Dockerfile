# Stage 1: Build Python dependencies
FROM python:3.12-slim AS python-deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Build frontend
FROM node:20-alpine AS frontend-deps
WORKDIR /build

ARG VITE_CDN_BASE_URL
ARG VITE_LOGIN_BG_PC
ARG VITE_LOGIN_BG_MOBILE
ARG VITE_AUTH_TIMEOUT_MINUTES
ARG VITE_SITE_TITLE

ENV VITE_CDN_BASE_URL=${VITE_CDN_BASE_URL}
ENV VITE_LOGIN_BG_PC=${VITE_LOGIN_BG_PC}
ENV VITE_LOGIN_BG_MOBILE=${VITE_LOGIN_BG_MOBILE}
ENV VITE_AUTH_TIMEOUT_MINUTES=${VITE_AUTH_TIMEOUT_MINUTES}
ENV VITE_SITE_TITLE=${VITE_SITE_TITLE}

COPY web/package*.json ./
RUN npm install

COPY web/ ./
RUN npm install && npm run build

# Stage 3: Final runtime image
FROM python:3.12-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies from stage 1
COPY --from=python-deps /install /usr/local

# Copy built frontend (dist -> web/dist)
COPY --from=frontend-deps /build/dist ./web/dist

# Copy backend code
COPY backend/ ./backend/

# Create data directory
RUN mkdir -p /app/data

ENV PYTHONPATH=/app
ENV PATH=/usr/local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
