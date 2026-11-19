#!/usr/bin/env bash
# Time how long one URL takes to download, several times in a row.
#
# Usage:   ./tools/measure.sh <url> [runs]
# Example: ./tools/measure.sh http://203.0.113.10/static/img/hero.jpg 5
#
# Columns (all in milliseconds):
#   connect  TCP handshake finished: roughly one round trip to the server
#   tls      TLS handshake finished (0 for plain http://)
#   ttfb     first byte of the response arrived
#   total    last byte arrived
# Windows: run this from Git Bash or WSL.

url="$1"
runs="${2:-5}"

if [ -z "$url" ]; then
  echo "Usage: $0 <url> [runs]" >&2
  exit 1
fi

echo "URL: $url"
printf "%-4s %9s %9s %9s %9s %10s %5s\n" run connect tls ttfb total bytes code

for i in $(seq 1 "$runs"); do
  curl -s -o /dev/null \
    -w "$i %{time_connect} %{time_appconnect} %{time_starttransfer} %{time_total} %{size_download} %{http_code}\n" \
    "$url"
done | awk '
  {
    printf "%-4s %9.0f %9.0f %9.0f %9.0f %10s %5s\n", $1, $2*1000, $3*1000, $4*1000, $5*1000, $6, $7
    c += $2; t += $5; n++
  }
  END {
    if (n) printf "avg  %9.0f %9s %9s %9.0f\n", c/n*1000, "", "", t/n*1000
  }'
