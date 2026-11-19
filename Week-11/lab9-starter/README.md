# COMP 1350 Lab 9: CDN speed-test site

Starter site for Lab 9. Push this folder to a **public** GitHub repository named
`comp1350-lab9-site`.

```
index.html          The page. Loads 5 static assets from /static/...
static/vendor/      Bootstrap 5.3.3 (CSS + JS)
static/css/         Your own CSS. Part 2 changes --accent.
static/js/          Your own JS. Shows timing results on the page. Part 2 changes ASSET_VERSION.
static/img/         A ~1.2 MB hero image
tools/measure.sh    Times a URL several times with curl
tools/deploy.sh     Publishes static/ to S3 and clears the CloudFront cache (Part 2)
```

The page measures itself. After it loads, it lists every static asset, where it
came from, and how long it took.
