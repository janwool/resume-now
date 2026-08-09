#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$PROJECT_DIR/dist"

if [[ "$DEPLOY_DIR" != "$PROJECT_DIR/dist" ]]; then
  echo "Refusing to clean an unexpected deploy directory: $DEPLOY_DIR" >&2
  exit 1
fi

rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR/assets/template-previews" "$DEPLOY_DIR/assets"

cp "$PROJECT_DIR"/*.html "$DEPLOY_DIR/"
cp "$PROJECT_DIR/styles.css" "$PROJECT_DIR/script.js" "$PROJECT_DIR/template-manifest.js" "$PROJECT_DIR/template-overlays.js" "$DEPLOY_DIR/"
cp -R "$PROJECT_DIR/assets/template-pages" "$DEPLOY_DIR/assets/template-pages"

find "$PROJECT_DIR/assets/template-previews" -maxdepth 1 -type f -name '*.jpg' -exec cp {} "$DEPLOY_DIR/assets/template-previews/" \;

for source_file in "$PROJECT_DIR/(118)"/*/*.jpg; do
  relative_file="${source_file#"$PROJECT_DIR/"}"
  destination_file="$DEPLOY_DIR/$relative_file"
  mkdir -p "$(dirname "$destination_file")"
  cp "$source_file" "$destination_file"
done

echo "Cloudflare static build created at $DEPLOY_DIR"
