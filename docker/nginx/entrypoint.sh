#!/bin/sh
set -e

# Prometheus authentication setup
HTPASSWD_FILE="/etc/nginx/.htpasswd.prometheus"

if [ ! -f "$HTPASSWD_FILE" ]; then
    if [ -n "$PROMETHEUS_USER" ] && [ -n "$PROMETHEUS_PASSWORD" ]; then
        # Generate htpasswd entry using htpasswd command
        htpasswd -bc "$HTPASSWD_FILE" "$PROMETHEUS_USER" "$PROMETHEUS_PASSWORD"
        echo "Generated $HTPASSWD_FILE for user: $PROMETHEUS_USER"
    else
        # Create a file that denies all access (no valid credentials)
        echo "# No credentials configured - access denied" > "$HTPASSWD_FILE"
        echo "Error: PROMETHEUS_USER/PROMETHEUS_PASSWORD not set. Prometheus access will be denied."
    fi
fi

exec "$@"
