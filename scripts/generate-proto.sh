#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROTO_DIR="$SCRIPT_DIR/../proto"

echo "Compiling proto files..."

python -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$PROTO_DIR" \
    --grpc_python_out="$PROTO_DIR" \
    --pyi_out="$PROTO_DIR" \
    "$PROTO_DIR"/common.proto \
    "$PROTO_DIR"/core.proto \
    "$PROTO_DIR"/ai.proto \
    "$PROTO_DIR"/gateway.proto \
    "$PROTO_DIR"/pdf.proto

echo "Proto compilation complete. Generated files in $PROTO_DIR:"
ls "$PROTO_DIR"/*_pb2*.py "$PROTO_DIR"/*_pb2*.pyi 2>/dev/null || true
