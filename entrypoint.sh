#!/bin/sh
# Rewrite __KICAD_MIRROR_BASE__ placeholder in JSON files to the real base URL
# at container startup. Controlled by DOWNLOAD_BASE_URL env var.
# Defaults to "http://localhost/" so that plain `docker run -p 80:80` works.

set -e

PLACEHOLDER="http://__KICAD_MIRROR_BASE__/"
TARGET="${DOWNLOAD_BASE_URL:-http://localhost/}"

# Normalize: ensure trailing slash, remove any query/fragment that a user might have pasted
# Use awk (POSIX-compatible) instead of sed - busybox sed (Alpine) does not support \? regex
TARGET=$(echo "$TARGET" | awk '{ sub(/\?$/,""); sub(/\/?$/,"/"); print }')

HTML_DIR="/usr/share/nginx/html"

if [ -d "$HTML_DIR" ]; then
    for f in "$HTML_DIR"/repository.json "$HTML_DIR"/packages.json; do
        if [ -f "$f" ]; then
            # Use awk to handle / in URLs safely
            awk -v ph="$PLACEHOLDER" -v tgt="$TARGET" '
                { gsub(ph, tgt); print }
            ' "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
        fi
    done
    echo "[kicad-mirror] Rewrote download URLs in JSON files to: $TARGET"
fi

exit 0
