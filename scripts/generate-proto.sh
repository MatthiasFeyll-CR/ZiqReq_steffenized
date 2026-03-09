#!/usr/bin/env bash
set -euo pipefail

PROTO_DIR="$(dirname "$0")/../proto"
SERVICES_DIR="$(dirname "$0")/../services"

echo "Compiling proto files..."

for proto_file in "$PROTO_DIR"/*.proto; do
    echo "  Compiling $(basename "$proto_file")"
    python -m grpc_tools.protoc \
        -I"$PROTO_DIR" \
        --python_out="$PROTO_DIR" \
        --grpc_python_out="$PROTO_DIR" \
        "$proto_file"
done

echo "Proto compilation complete."
