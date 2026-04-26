# autoMate — containerized hub.
#
# Build:   docker build -t automate-hub .
# Run:     docker run --rm -p 8765:8765 -v automate-data:/data automate-hub
# Open:    http://localhost:8765
#
# Notes:
# - Desktop tools are skipped (no display in the container).
# - Browser tools (Playwright) work — Chromium is preinstalled.
# - The browser-extension can still pair from your host machine; just point
#   it at  ws://localhost:8765/api/extension/ws  (it's the default).

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AUTOMATE_HOME=/data \
    AUTOMATE_HOST=0.0.0.0 \
    AUTOMATE_OPEN_BROWSER=0 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Playwright runtime deps; skip if you don't need browser.* tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml requirements.txt ./
COPY automate ./automate

RUN pip install --no-cache-dir '.[mcp,browser]' \
 && python -m playwright install --with-deps chromium

VOLUME ["/data"]
EXPOSE 8765

ENTRYPOINT ["automate"]
CMD ["serve"]
