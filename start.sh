#!/usr/bin/env bash
set -e

# Configuration
PROJECT_DIR="${1:-.}"
TARGET_LLM_URL="${TARGET_LLM_URL:-http://localhost:11434/v1}"
FALKORDB_PORT=6379

echo "========================================="
echo "🚀 CamShaft Unified Startup Sequence"
echo "========================================="

# 1. Check if FalkorDB is running on port 6379
echo "[1/3] Checking FalkorDB Status..."
if nc -z localhost $FALKORDB_PORT 2>/dev/null; then
    echo "✅ FalkorDB is already running on port $FALKORDB_PORT."
else
    echo "❌ ERROR: FalkorDB is NOT running on port $FALKORDB_PORT."
    echo "Please start FalkorDB natively before running this script."
    exit 1
fi

# 2. Ingest Codebase (Optional)
echo ""
if [ "$PROJECT_DIR" = "--skip-ingest" ]; then
    echo "[2/3] Skipping Codebase Ingestion..."
else
    echo "[2/3] Ingesting Codebase at '$PROJECT_DIR' into Memory..."
    # Running ingestion module
    python3 -m camshaft.cli ingest "$PROJECT_DIR"
    echo "✅ Codebase ingested successfully."
fi

# 3. Start the Proxy Server
echo ""
echo "[3/3] Starting the CamShaft Proxy Server..."
echo "🔗 Pointing to Local LLM at: $TARGET_LLM_URL"
echo ""
echo "--------------------------------------------------------"
echo "✅ CamShaft is now fully active!"
echo "👉 Point your Chat App to: http://localhost:8000/v1"
echo "--------------------------------------------------------"

# Execute the proxy in the foreground so it keeps running
exec python3 -m camshaft.proxy --target-url "$TARGET_LLM_URL"
