#!/usr/bin/env bash
# Publish everything in static/ to your S3 bucket, then tell CloudFront to
# drop its cached copies so visitors get the new files.
#
# Usage:   bash tools/deploy.sh <bucket-name> <distribution-id>
# Example: bash tools/deploy.sh comp1350-lab9-jdoe-assets E2ABCDEF123456
#
# Runs anywhere the AWS CLI has credentials: AWS CloudShell, your laptop,
# or a GitHub Actions runner.

set -euo pipefail

if [ $# -ne 2 ]; then
  echo "Usage: bash tools/deploy.sh <bucket-name> <distribution-id>" >&2
  exit 1
fi

BUCKET="$1"
DIST="$2"
cd "$(dirname "$0")/.."

echo "1/3  Uploading images and libraries (browsers may reuse them for 1 day)..."
aws s3 sync static/ "s3://$BUCKET/static/" --delete \
  --exclude "*" --include "img/*" --include "vendor/*" \
  --cache-control "public, max-age=86400"

echo "2/3  Uploading CSS and JS (browsers may reuse them for 5 minutes)..."
aws s3 sync static/ "s3://$BUCKET/static/" --delete \
  --exclude "img/*" --exclude "vendor/*" \
  --cache-control "public, max-age=300"

echo "3/3  Clearing CloudFront's cached copies of /static/* ..."
ID=$(aws cloudfront create-invalidation --distribution-id "$DIST" \
       --paths "/static/*" --query Invalidation.Id --output text)
aws cloudfront wait invalidation-completed --distribution-id "$DIST" --id "$ID"

echo "Done. Every edge location will fetch the new files on its next request."
