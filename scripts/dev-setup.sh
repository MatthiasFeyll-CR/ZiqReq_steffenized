#!/usr/bin/env bash
set -euo pipefail

echo "=== ZiqReq Development Setup ==="

echo "1. Installing frontend dependencies..."
cd "$(dirname "$0")/../frontend"
npm install

echo ""
echo "2. Installing backend dependencies..."
for service in gateway core ai; do
    echo "   Installing ${service} dependencies..."
    cd "$(dirname "$0")/../services/${service}"
    pip install -r requirements.txt
done

echo ""
echo "3. Starting Docker infrastructure..."
cd "$(dirname "$0")/../infra/docker"
docker compose up -d postgresql redis rabbitmq

echo ""
echo "Setup complete. Run 'docker compose up' in infra/docker/ to start all services."
