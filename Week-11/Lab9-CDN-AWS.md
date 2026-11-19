# Lab 9: CDN — Prove the Speed-Up, Then Build Your Own on AWS

*COMP 1350 — Web Administration, Week 11*

You've joined a small team whose web server sits in **Singapore**, while most of its visitors are here in Vancouver. Your manager has heard that "a CDN will make it faster" and wants proof before paying for anything, and then wants a CDN the team owns, where a `git push` updates the site's images, CSS and JS with no manual copying.

- **Part 1 (about 75 min):** Run two copies of the same site on AWS EC2. One serves its CSS, JS and image itself. The other serves only its HTML, and every static asset comes from the public jsDelivr CDN. Then measure the difference.
- **Part 2 (about 90 min):** Build your own CDN with Amazon S3 and Amazon CloudFront, then automate asset updates with GitHub Actions, so pushing a change to `static/` publishes it worldwide.

**Learning outcomes:** measure and explain CDN performance with real data (latency, edge locations, cache hits and misses); configure a private origin behind a CDN; automate static-asset deployment and cache invalidation.

## Before You Start

You need:

- A **personal AWS account**. Sign in as an IAM or Identity Center user if you have one, not the root user.
- A **GitHub account** and Git on your laptop.
- A terminal with `curl` and `ssh`. On macOS or Linux, the built-in Terminal works. On Windows, use **Git Bash** (installed with Git for Windows) or WSL.

**Set a budget alert first (2 minutes).** In the AWS console go to **Billing and Cost Management → Budgets → Create budget**, choose the **Zero spend budget** template, and enter your email. If anything you build ever starts costing money, you'll know the same day. If you clean up at the end (see the last section), this lab costs a few cents or nothing, depending on your account's free credits.

**Use one region for everything: Asia Pacific (Singapore), `ap-southeast-1`.** Select it in the region menu (top right of the console) before you create anything. CloudFront is global and has no region.

> **Why Singapore?** It is about 12,800 km from Vancouver. Light in fibre covers about 200 km per millisecond, so a round trip can't take less than about 130 ms, and real routes take 160–200 ms. Every new connection costs at least one round trip. A 1.2 MB image costs several more, because TCP starts slowly and speeds up one round trip at a time. Putting the server far away makes the effect large enough to measure clearly. In real life the far-away user might be in Singapore and the server in Vancouver. The physics is the same.

---

## Part 1: Prove That a CDN Loads Faster

### 1.1 Put the Starter Site on GitHub

1. Download the starter site: [lab9-starter.zip](https://codevoyage.dev/Web_Administration_COMP1350/static/lab9-starter.zip). It contains:

```
comp1350-lab9-site/
├── index.html            the page; loads 5 static assets from /static/...
├── static/
│   ├── vendor/           Bootstrap 5.3.3 CSS + JS (~310 KB)
│   ├── css/styles.css    your own CSS
│   ├── js/app.js         your own JS; shows timing results on the page
│   └── img/hero.jpg      a ~1.2 MB hero image, like an unoptimized photo
└── tools/measure.sh      times a URL several times with curl
```

The page measures itself. When it finishes loading, it shows a table of every static asset, **which server it came from**, and **how long it took**.

2. On GitHub, create a new **public** repository named exactly `comp1350-lab9-site`. Leave it empty: no README, no .gitignore.

3. Unzip the starter and push it, replacing `YOUR-GITHUB-USER` with your username:

```bash
unzip lab9-starter.zip
cd comp1350-lab9-site
git init -b main
git add .
git commit -m "Lab 9 starter site"
git remote add origin https://github.com/YOUR-GITHUB-USER/comp1350-lab9-site.git
git push -u origin main
```

4. Tag this version as `v1`. jsDelivr will serve the files exactly as they are at this tag:

```bash
git tag v1
git push origin v1
```

### 1.2 Launch Two EC2 Instances

In the EC2 console (region **Singapore**), click **Launch instances**:

| Setting | Value |
|---|---|
| Name | `lab9-web` (you'll rename them in a moment) |
| AMI | **Ubuntu Server 24.04 LTS**, 64-bit (x86) |
| Instance type | `t3.micro` (or whichever type is labelled **Free tier eligible**) |
| Key pair | **Create new key pair** → name `lab9-key`, type RSA, format `.pem` → download it |
| Network settings | **Create security group** named `lab9-web-sg`. Allow **SSH from My IP**. Allow **HTTP from the internet**. |
| Advanced details → User data | Paste the script below, with your GitHub username in it |
| Number of instances (Summary panel) | **2** |

```bash
#!/bin/bash
# Runs once, as root, the first time each instance boots.
apt-get update -y
apt-get install -y nginx git
rm -f /var/www/html/index.nginx-debian.html
git clone https://github.com/YOUR-GITHUB-USER/comp1350-lab9-site.git /home/ubuntu/site
chown -R ubuntu:ubuntu /home/ubuntu/site
```

When both instances show **Running**, rename them by clicking the pencil icon in the **Name** column. Call one `local-static` and the other `cdn-hosted`. Note each one's **Public IPv4 address**.

Connect to each instance in its own terminal window:

```bash
chmod 400 ~/Downloads/lab9-key.pem          # macOS/Linux/Git Bash: once only
ssh -i ~/Downloads/lab9-key.pem ubuntu@<PUBLIC-IP>
```

Wait about a minute after boot, then confirm the user data finished: `ls ~/site` should list `index.html` and `static`. If it doesn't, check `sudo tail -50 /var/log/cloud-init-output.log`. The usual cause is a typo in the repository URL. You can then run the `git clone` line yourself as `ubuntu`.

### 1.3 Deploy the "Local Assets" Version

*On `local-static`:*

```bash
sudo cp -r ~/site/index.html ~/site/static /var/www/html/
sudo nginx -t && sudo systemctl reload nginx
```

Open `http://<local-static-IP>` in your browser. Type `http://` yourself. There is no HTTPS on this server, so if Chrome shows a "not secure" warning, click **Continue to site**. Every row in the page's table should say **this server**.

### 1.4 Deploy the "CDN-Backed" Version

*On `cdn-hosted`:*

1. Rewrite the five asset URLs in `index.html` so they point at jsDelivr instead of this server:
   - **Bootstrap** comes from jsDelivr's copy of the npm package. Thousands of other sites use the same URL, so it is almost always already cached at the edge.
   - **Your own CSS, JS and image** come from jsDelivr's GitHub mirror of *your* repository, pinned to the `v1` tag.

```bash
cd ~/site
GH_USER=YOUR-GITHUB-USER        # <- change this
GH="https://cdn.jsdelivr.net/gh/$GH_USER/comp1350-lab9-site@v1"

sed -i \
  -e "s#/static/vendor/bootstrap.min.css#https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css#" \
  -e "s#/static/vendor/bootstrap.bundle.min.js#https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js#" \
  -e "s#\"/static/#\"$GH/static/#g" \
  index.html

grep -n 'cdn.jsdelivr' index.html    # expect exactly 5 lines
```

2. Deploy **only** `index.html`. This server no longer hosts any CSS, JS or images:

```bash
sudo cp ~/site/index.html /var/www/html/
sudo nginx -t && sudo systemctl reload nginx
ls /var/www/html                                       # only index.html
curl -sI http://localhost/static/css/styles.css | head -1   # 404 Not Found: proof
```

3. Open `http://<cdn-hosted-IP>`. The page should look identical to `local-static`, but the table should now show `cdn.jsdelivr.net` for all five assets.

> **Why pin to `@v1`?** A URL like `.../comp1350-lab9-site@main/...` follows a branch, and jsDelivr caches branch URLs for hours. If you push a change, visitors keep getting the old file and you can't tell which version anyone has. A tag (or commit hash) never changes, so it can be cached forever. You'll handle "how do updates reach the edge?" properly in Part 2.

### 1.5 Measure

**A. In the browser (both sites).**

1. Load `http://<cdn-hosted-IP>` **once** before you measure. That first request makes jsDelivr fetch your files from GitHub and cache them at the edge near you. Note how long that "cold" load took for Q2.
2. Open an **Incognito/InPrivate** window and open DevTools → **Network**. Tick **Disable cache**, so your browser can't reuse files it already downloaded.
3. Hard-refresh (Ctrl+Shift+R / Cmd+Shift+R) **5 times** on each site. Each time, record the **Load** time from the Network tab's bottom status bar and the **Time** of the `hero.jpg` row.

| Run | `local-static` Load (ms) | `local-static` hero.jpg (ms) | `cdn-hosted` Load (ms) | `cdn-hosted` hero.jpg (ms) |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
| **Average** | | | | |

**B. From the command line.** On your laptop, from inside your `comp1350-lab9-site` folder:

```bash
bash tools/measure.sh http://<local-static-IP>/static/img/hero.jpg 5
bash tools/measure.sh https://cdn.jsdelivr.net/gh/YOUR-GITHUB-USER/comp1350-lab9-site@v1/static/img/hero.jpg 5
```

The `connect` column is the time to finish the TCP handshake, which is roughly **one network round trip** to whoever answered.

**C. Find out which edge answered you.**

```bash
curl -sI https://cdn.jsdelivr.net/gh/YOUR-GITHUB-USER/comp1350-lab9-site@v1/static/img/hero.jpg \
  | grep -i -E 'x-served-by|x-cache|cf-ray|age:'
```

jsDelivr runs on more than one CDN. Fastly answers with `x-served-by: ...-YVR` and Cloudflare with `cf-ray: ...-YVR`. Either way, the last three letters are the airport code of the edge location: `YVR` is Vancouver, `SEA` is Seattle.

**Q1**: Compare the average `connect` time to your EC2 instance with the average `connect` time to jsDelivr. Why are they so different? Use your numbers, and say where each server physically is.

**Q2**: Which edge location answered your request in step C? Describe the full path `hero.jpg` took on `cdn-hosted` **the very first time** anyone requested it (the cold load in step A.1), and how that path differs on every request after that.

**Q3**: A fair test changes only one thing. Run these two commands:

```bash
curl -sI -H 'Accept-Encoding: br, gzip' http://<local-static-IP>/static/vendor/bootstrap.min.css | grep -i -E 'content-encoding|content-length|cache-control'
curl -sI -H 'Accept-Encoding: br, gzip' https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css | grep -i -E 'content-encoding|content-length|cache-control'
```

Besides distance, name **two** differences in how the two servers deliver the same file. Use the output above, and also look at the **Protocol** column in DevTools (right-click a column header to add it). For each difference, say whether you could fix it on your own Nginx server, or whether only a CDN can give you that benefit.

---

## Part 2: Build Your Own CDN on AWS and Automate Updates

jsDelivr is great for open-source files in public repositories. Real company assets are often private, need custom cache rules, and must update the moment the team ships a change. In this part you'll build that yourself:

```
 git push ──► GitHub Actions ──► S3 bucket (private origin, Singapore)
                                         ▲
                                         │ only CloudFront may read it (OAC)
 browser in Vancouver ──► CloudFront edge (YVR/SEA) ──┘  cache hit? served from the edge
```

### 2.1 Create a Private S3 Bucket (the Origin)

1. **S3 → Create bucket**, region **Singapore**.
2. Bucket name: `comp1350-lab9-<yourname>-assets`, for example `comp1350-lab9-jdoe-assets`. Bucket names are global, so pick something unique.
3. Leave **Block all public access** turned **on**. Nobody, including you in a browser, will be able to read files straight from S3. Only CloudFront will.
4. Leave everything else as default and click **Create bucket**.

Upload the first copy of your assets from **AWS CloudShell**. Click the terminal icon `>_` at the top of the console. It's a browser shell with the AWS CLI already logged in as you.

```bash
git clone https://github.com/YOUR-GITHUB-USER/comp1350-lab9-site.git
cd comp1350-lab9-site
BUCKET=comp1350-lab9-<yourname>-assets
aws s3 sync static/ "s3://$BUCKET/static/"
aws s3 ls "s3://$BUCKET/static/" --recursive     # expect 5 files
```

Prove the bucket is private. Expect `403 Forbidden`:

```bash
curl -sI "https://$BUCKET.s3.ap-southeast-1.amazonaws.com/static/img/hero.jpg" | head -1
```

### 2.2 Create a CloudFront Distribution

**CloudFront → Create distribution.** AWS changes this screen's layout often. The step names below may differ slightly, but these are the settings that matter:

| Setting | Value |
|---|---|
| Pricing plan (if asked) | **Free** flat-rate plan if your account offers it, otherwise **Pay-as-you-go**. This lab uses a tiny fraction of CloudFront's always-free allowance of 1 TB and 10 million requests per month. |
| Distribution name | `lab9-assets` |
| Origin type | **Amazon S3**, then choose your `comp1350-lab9-<yourname>-assets` bucket |
| Origin access | **Allow private S3 bucket access to CloudFront** / **Origin access control (OAC)**: *recommended*. Let the console update the bucket policy for you. |
| Cache settings | Use the recommended settings: cache policy **CachingOptimized** |
| Viewer protocol policy | **Redirect HTTP to HTTPS** |
| Security / WAF | **Do not enable** for this lab |

Click **Create distribution**. Copy the **Distribution domain name** (like `d1a2b3c4d5e6f7.cloudfront.net`) and the **Distribution ID** (like `E2ABCDEF123456`). Wait until **Last modified** shows a date instead of **Deploying**. This usually takes a few minutes.

Now check the bucket's policy: **S3 → your bucket → Permissions → Bucket policy**. It should look like the policy below. If it's empty, paste this in, replacing the three placeholders. Find your 12-digit account ID in the top-right menu.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontReadOnly",
      "Effect": "Allow",
      "Principal": { "Service": "cloudfront.amazonaws.com" },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::BUCKET-NAME/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT-ID:distribution/DISTRIBUTION-ID"
        }
      }
    }
  ]
}
```

### 2.3 Watch the Edge Cache Work

On your laptop, inside your repo folder:

```bash
CF=d1a2b3c4d5e6f7.cloudfront.net        # <- your distribution domain

# Run 1 should be a cache MISS: the edge has to fetch from Singapore.
# Runs 2-5 should be HITs: served straight from the edge near you.
bash tools/measure.sh "https://$CF/static/img/hero.jpg" 5

# Now look at the headers, twice in a row:
curl -sI "https://$CF/static/css/styles.css" | grep -i -E 'x-cache|x-amz-cf-pop|age:'
curl -sI "https://$CF/static/css/styles.css" | grep -i -E 'x-cache|x-amz-cf-pop|age:'
```

The first `curl -sI` should say `x-cache: Miss from cloudfront` and the second `Hit from cloudfront`. `x-amz-cf-pop` names the edge location, using airport codes again (for example `YVR52-P1` or `SEA900-P2`). If run 1 isn't a miss, you requested that file earlier, which is fine.

**Q4**: Using your `measure.sh` output, compare run 1 (miss) with the average of runs 2–5 (hits), and with your `local-static` EC2 numbers from Part 1. Why is a cache **miss** through CloudFront about as slow as going to the origin directly?

### 2.4 Point the CDN-Backed Site at Your Own CDN

*On `cdn-hosted`:* swap your own three files from jsDelivr to CloudFront. Bootstrap stays on jsDelivr's shared copy.

```bash
cd ~/site
CF=d1a2b3c4d5e6f7.cloudfront.net        # <- your distribution domain
sed -i "s#https://cdn.jsdelivr.net/gh/[^/]*/comp1350-lab9-site@v1#https://$CF#g" index.html
grep -n "$CF" index.html                # expect 3 lines: styles.css, hero.jpg, app.js
sudo cp index.html /var/www/html/
```

Reload `http://<cdn-hosted-IP>`. The table should now show your `….cloudfront.net` domain for `styles.css`, `hero.jpg` and `app.js`.

**Q5**: The direct S3 URL in 2.1 returned `403`, yet CloudFront can read the same file. Explain what origin access control (OAC) and the bucket policy are doing. Then give one **security** or **cost** problem that would exist if the bucket were public and attackers could skip CloudFront and download from it directly.

### 2.5 Let GitHub Deploy to AWS Without Storing Any Keys (OIDC)

GitHub Actions needs permission to write to your bucket and clear CloudFront's cache. The old way was to create an AWS access key and paste it into GitHub as a secret. The modern way is **OIDC**: on each run, GitHub gives the job a signed, short-lived token that says "I am a workflow in repo X on branch main." AWS checks that token and hands back credentials that expire within an hour. Nothing long-lived is stored anywhere.

**1. Tell AWS to trust GitHub's tokens.** Go to **IAM → Identity providers → Add provider**:

- Provider type: **OpenID Connect**
- Provider URL: `https://token.actions.githubusercontent.com`
- Audience: `sts.amazonaws.com`

**2. Create the role that the workflow will assume.** Go to **IAM → Roles → Create role**:

- Trusted entity type: **Web identity**
- Identity provider: `token.actions.githubusercontent.com`, Audience: `sts.amazonaws.com`
- GitHub organization: *your GitHub username*. GitHub repository: `comp1350-lab9-site`. GitHub branch: `main`.
- On the permissions step, attach **nothing** and click **Next**.
- Role name: `lab9-github-deploy`, then **Create role**.

Open the new role → **Trust relationships**. It should contain a condition like this. It means *only* workflows on the `main` branch of *your* repository can use this role:

```json
"Condition": {
  "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
  "StringLike":   { "token.actions.githubusercontent.com:sub": "repo:YOUR-GITHUB-USER/comp1350-lab9-site:ref:refs/heads/main" }
}
```

**3. Give the role only what the deploy needs.** On the role, go to **Permissions → Add permissions → Create inline policy → JSON**. Paste the policy below with your three values filled in, and name it `lab9-deploy-static`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListTheBucket",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::BUCKET-NAME"
    },
    {
      "Sid": "WriteStaticAssetsOnly",
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::BUCKET-NAME/static/*"
    },
    {
      "Sid": "ClearThisDistributionsCache",
      "Effect": "Allow",
      "Action": ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"],
      "Resource": "arn:aws:cloudfront::ACCOUNT-ID:distribution/DISTRIBUTION-ID"
    }
  ]
}
```

Copy the role's **ARN** from its summary page (`arn:aws:iam::123456789012:role/lab9-github-deploy`).

**4. Give the workflow its settings.** In your GitHub repo, go to **Settings → Secrets and variables → Actions → Variables** tab and add four **repository variables**. None of these values are secret: without GitHub's signed token, the role ARN is useless.

| Name | Value |
|---|---|
| `AWS_ROLE_ARN` | the role ARN you just copied |
| `AWS_REGION` | `ap-southeast-1` |
| `S3_BUCKET` | `comp1350-lab9-<yourname>-assets` |
| `CF_DISTRIBUTION_ID` | your distribution ID, like `E2ABCDEF123456` |

### 2.6 Write the Deploy Workflow

On your laptop, in your repo, create `.github/workflows/deploy-static.yml`:

```yaml
name: Deploy static assets

on:
  push:
    branches: [main]
    paths: ["static/**"]     # only run when an asset actually changed
  workflow_dispatch:         # adds a "Run workflow" button for manual runs

permissions:
  id-token: write            # allow the job to request GitHub's OIDC token
  contents: read

concurrency:
  group: deploy-static       # two pushes in a row deploy one after the other, never at once

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Check out the repository
        uses: actions/checkout@v5

      - name: Get short-lived AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v5
        with:
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: ${{ vars.AWS_REGION }}

      - name: Upload images and vendor libraries (browsers may cache 1 day)
        run: |
          aws s3 sync static/ "s3://${{ vars.S3_BUCKET }}/static/" --delete \
            --exclude "*" --include "img/*" --include "vendor/*" \
            --cache-control "public, max-age=86400"

      - name: Upload our own CSS and JS (browsers may cache 5 minutes)
        run: |
          aws s3 sync static/ "s3://${{ vars.S3_BUCKET }}/static/" --delete \
            --exclude "img/*" --exclude "vendor/*" \
            --cache-control "public, max-age=300"

      - name: Clear CloudFront's cached copies
        run: |
          ID=$(aws cloudfront create-invalidation \
                 --distribution-id "${{ vars.CF_DISTRIBUTION_ID }}" \
                 --paths "/static/*" \
                 --query Invalidation.Id --output text)
          echo "Invalidation $ID created; waiting for every edge location to drop its copy..."
          aws cloudfront wait invalidation-completed \
            --distribution-id "${{ vars.CF_DISTRIBUTION_ID }}" --id "$ID"
          echo "Done. The next request at each edge fetches the new files from S3."
```

What each step does:

- **`aws s3 sync --delete`** uploads new or changed files and removes files from the bucket that you deleted from the repo. Each `sync` only touches the files its `--include`/`--exclude` filters select.
- **`--cache-control`** stores a header with each file. It tells browsers, and CloudFront, how long they may reuse the file without checking again.
- **`create-invalidation`** tells every CloudFront edge location to throw away its cached `/static/*` files, so the next visitor gets the new version from S3. One wildcard path counts as one invalidation, and the first 1,000 invalidation paths each month are free.

Commit and push it:

```bash
git add .github/workflows/deploy-static.yml
git commit -m "Deploy static assets to S3 + CloudFront"
git push
```

This push didn't change anything in `static/`, so the workflow won't start by itself. Start it manually: in your repo, go to **Actions → Deploy static assets → Run workflow → Run workflow**. Watch the run. Every step should get a green check. This proves the OIDC role and permissions work before you depend on them.

### 2.7 Ship a Change with `git push`

1. Make two visible changes:
   - In `static/css/styles.css`, change `--accent: #0d6efd;` to another colour, for example `--accent: #d63384;`
   - In `static/js/app.js`, change `const ASSET_VERSION = "v1";` to `"v2"`

2. Note the time, then push:

```bash
git add static/
git commit -m "v2: new accent colour"
git push
```

3. Watch the run in the **Actions** tab. When it's green, confirm the edge is serving the new file:

```bash
curl -s "https://$CF/static/js/app.js" | grep ASSET_VERSION      # "v2"
curl -sI "https://$CF/static/js/app.js" | grep -i -E 'x-cache|cache-control'
```

4. Reload `http://<cdn-hosted-IP>` with DevTools **Disable cache** ticked. The version label should read **v2**, in the new colour. You never logged into a server, and you never touched S3 or CloudFront by hand.

5. For comparison, reload `http://<local-static-IP>`. It still shows **v1**: someone would have to SSH in and copy files again. jsDelivr's `@v1` URLs also still serve v1, by design.

**Q6**: Your workflow got into AWS without any access key stored in GitHub. Give **two** reasons this is safer than creating an IAM user's access key and saving it as a GitHub secret. Then explain what the `sub` condition in the role's trust policy prevents: what would happen if someone forked your repository and ran the same workflow?

**Q7**: The invalidation finished within about a minute, but a visitor who loaded your page right before your push might still see the **old** CSS for a while.

- (a) Why? Which header from your workflow decides how long?
- (b) Many large sites never invalidate. Instead they put a content hash in each filename, for example `styles.3f9a1c.css`, and cache every file for a year. Explain how that solves (a), and what has to change in `index.html` on every deploy.
- (c) Compare the three update methods you've now seen: manual copy (`local-static`), pinned tag (jsDelivr `@v1`), and push-to-deploy (CloudFront). Which would you choose for your group project's static assets, and why?

## Stretch Goals (Optional)

- **Make the test fairer.** On `local-static`, enable gzip for CSS and JS in `/etc/nginx/nginx.conf` by uncommenting `gzip_types` and including `text/css` and `application/javascript`. Reload Nginx and repeat the Part 1 measurement. How much of the gap closes, and how much can never close?
- **Prove the trust policy.** Create a branch named `test`, change a file in `static/` on it, and run the workflow on that branch from the **Run workflow** menu. It should fail at the credentials step with `Not authorized to perform sts:AssumeRoleWithWebIdentity`. Screenshot that: it's your trust policy doing its job.
- **Use a real domain.** If you have one, attach `assets.yourdomain.com` to your distribution with a free ACM certificate. The certificate must be requested in `us-east-1` for CloudFront.

---

## The Same Thing on Azure (Read Only, No Deliverable)

Every major cloud has the same building blocks under different names. If a future employer runs on Azure:

| What it does | AWS (this lab) | Azure |
|---|---|---|
| Stores the original files (origin) | S3 bucket | Storage account → Blob container |
| Edge caching network | CloudFront | **Azure Front Door** (Standard or Premium tier) |
| Only the CDN may read the origin | Origin access control + bucket policy | Private Link origin (Premium tier only). On Standard, the origin must be publicly readable. |
| CI/CD signs in without stored keys | IAM OIDC provider + role | Entra ID app registration + **federated credential** for your repo/branch |
| Upload changed files | `aws s3 sync` | `az storage blob sync` (or `azcopy sync`) |
| Clear the edge cache | `aws cloudfront create-invalidation` | `az afd endpoint purge` |
| GitHub Action to sign in | `aws-actions/configure-aws-credentials` | `azure/login` |

The deploy steps of an equivalent workflow look like this:

```yaml
      - uses: azure/login@v2
        with:
          client-id: ${{ vars.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

      - run: |
          az storage blob sync --account-name "${{ vars.STORAGE_ACCOUNT }}" \
            --container assets --source static --destination static --auth-mode login
          az afd endpoint purge --resource-group "${{ vars.RESOURCE_GROUP }}" \
            --profile-name "${{ vars.AFD_PROFILE }}" --endpoint-name "${{ vars.AFD_ENDPOINT }}" \
            --content-paths "/static/*"
```

Why this lab uses AWS: Microsoft's older, cheaper "Azure CDN Standard from Microsoft (classic)" no longer accepts new profiles and retires in September 2027. Its replacement, Front Door Standard, charges a monthly base fee even with no traffic. CloudFront's always-free allowance covers a student project for $0.

---

## Clean Up

| Resource | What to do | Why |
|---|---|---|
| Both EC2 instances | **EC2 → Instances → select both → Instance state → Terminate** | They bill every hour they run, including their public IPv4 addresses |
| Security group, key pair | Delete after the instances are gone (optional) | Free, but tidy |
| CloudFront distribution, S3 bucket, IAM role | **Keep them** if you'll use this CDN for Milestone C. Idle, they cost nothing. Otherwise: **disable** the distribution, wait for it to finish deploying, then **delete** it. **Empty** the bucket, then **delete** it. Delete the `lab9-github-deploy` role and the GitHub identity provider. | No leftover resources, no surprise bills |

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Browser can't reach `http://<IP>` | Security group missing **HTTP from anywhere**. Or you typed `https://`. Or Nginx isn't running: `systemctl status nginx` |
| `ssh` hangs, then times out | Your IP changed (new Wi-Fi), so **SSH from My IP** no longer matches. Edit the security group rule. |
| jsDelivr returns 404 | Repository isn't public, the `v1` tag wasn't pushed (`git push origin v1`), or the path's capitalization doesn't match |
| CloudFront returns **403 AccessDenied** | Bucket policy missing or wrong (see 2.2). Or the file isn't in the bucket. Because the policy doesn't grant `ListBucket`, a missing file returns 403, not 404. |
| Actions fails: `Not authorized to perform sts:AssumeRoleWithWebIdentity` | The trust policy's `sub` doesn't match your repo/branch exactly (check the username's capitalization). Or the workflow is missing `id-token: write`. Or `AWS_ROLE_ARN` is wrong. |
| Actions fails: `AccessDenied` on `s3 sync` or `CreateInvalidation` | A typo in the inline policy's bucket name, account ID or distribution ID |
| `git push` rejected: "refusing to allow … to create or update workflow" | Your Git login token lacks the `workflow` scope. Create the file in GitHub's web editor instead (**Add file → Create new file**). |
| Page still shows v1 after a green run | Your browser cached `app.js`. Tick **Disable cache** in DevTools and reload. |

## Deliverables

**Part 1**

- Screenshot of each site's on-page asset table: `local-static` showing **this server**, `cdn-hosted` showing **cdn.jsdelivr.net**
- Output of `curl -sI http://localhost/static/css/styles.css` on `cdn-hosted` showing the 404
- Your completed measurement table from 1.5A
- `measure.sh` output for `hero.jpg` from both sources (1.5B), and the edge-location header from 1.5C
- Written answers to Q1–Q3

**Part 2**

- Output showing the direct S3 URL returning `403`, and CloudFront returning `Hit from cloudfront` with an `x-amz-cf-pop` header
- `measure.sh` output against CloudFront (2.3)
- Screenshot of the `cdn-hosted` page's table showing your `….cloudfront.net` domain
- Link to your GitHub repository, which shows `.github/workflows/deploy-static.yml`
- Screenshot of the **successful Actions run** triggered by your v2 push, and the time from `git push` to the change appearing on the page
- Before/after screenshots of the `cdn-hosted` page showing **v1** and then **v2** in the new colour
- Written answers to Q4–Q7
