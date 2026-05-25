#!/bin/bash
# ============================================================
# JEET Database Schema Bootstrap
# Runs all SQL files in order against jeet_dev database
# ============================================================

set -e  # Exit on first error

DB_NAME="jeet_dev"
SCHEMA_DIR="$(dirname "$0")"

echo "🗄️  JEET Database Bootstrap"
echo "================================"
echo "Database: $DB_NAME"
echo ""

for file in "$SCHEMA_DIR"/*.sql; do
  filename=$(basename "$file")
  echo "▶️  Running $filename..."
  psql -d "$DB_NAME" -f "$file" -v ON_ERROR_STOP=1 > /dev/null
  echo "   ✅ $filename complete"
done

echo ""
echo "🎉 All schema files applied successfully!"
echo ""
echo "Verify with: psql -d $DB_NAME -c '\\dt'"