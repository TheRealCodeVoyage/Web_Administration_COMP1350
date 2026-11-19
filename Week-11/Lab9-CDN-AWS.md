# Lab 9: CDN — Prove the Speed-Up, Then Build Your Own on AWS

*COMP 1350 — Web Administration, Week 11*

Your team's web server is in Ohio, and your manager wants proof that a CDN would make the site faster for visitors here in Vancouver, plus a CDN the team controls.

- **Part 1 (about 60 min):** Run the same site on two AWS EC2 servers. One serves its own CSS, JS and image. The other serves only the HTML and gets every static asset from the public jsDelivr CDN. Measure the difference.
- **Part 2 (about 60 min):** Build your own CDN with Amazon S3 and Amazon CloudFront. Then publish asset updates with one command.

**Learning outcomes:** measure and explain CDN performance with real data; put a private origin behind a CDN; automate static-asset updates and cache invalidation.

## Before You Start

You need:

- A **free AWS account**, the one you created for this course.
- A **GitHub account** and Git on your laptop.
- A terminal with `curl`. On macOS or Linux, the built-in Terminal works. On Windows, use **Git Bash** (installed with Git for Windows).

**Stay on the free plan.** Everything in this lab works on a free AWS account. If the console ever asks you to **Upgrade your plan** or **Activate advanced features**, close the dialog. Activating advanced features can't be undone, and it removes the spending limit that protects you. Whenever the console gives you a choice, pick the option labelled **Free tier eligible**.

**Use your account's region.** A free account works in only one region, shown at the top right of the console. For accounts with a Canadian address it's **US East (Ohio), `us-east-2`**. This lab uses `us-east-2` in its examples. If your account shows a different region, use yours everywhere instead. CloudFront is global, so it has no region.

---

## Part 1: Prove That a CDN Loads Faster

### 1.1 Put the Starter Site on GitHub

1. Download [lab9-starter.zip](https://codevoyage.dev/Web_Administration_COMP1350/static/lab9-starter.zip). It contains:

```
comp1350-lab9-site/
├── index.html            the page; loads 5 static assets from /static/...
├── static/
│   ├── vendor/           Bootstrap 5.3.3 CSS + JS
│   ├── css/styles.css    your own CSS
│   ├── js/app.js         your own JS; shows timing results on the page
│   └── img/hero.jpg      a ~1.2 MB image, like an unoptimized photo
└── tools/
    ├── measure.sh        times a URL several times with curl
    └── deploy.sh         publishes static/ to your own CDN (Part 2)
```

The page measures itself: when it finishes loading, a table shows each static asset, **which server it came from** and **how long it took**.

2. On GitHub, create a new **public**, empty repository named exactly `comp1350-lab9-site`.

3. Unzip the starter and push it, replacing `YOUR-GITHUB-USER` with your username. Then tag the version as `v1`:

```bash
unzip lab9-starter.zip
cd comp1350-lab9-site
git init -b main
git add .
git commit -m "Lab 9 starter site"
git remote add origin https://github.com/YOUR-GITHUB-USER/comp1350-lab9-site.git
git push -u origin main
git tag v1
git push origin v1
```

### 1.2 Launch Two EC2 Instances

In the **EC2** console, click **Launch instances**:

| Setting | Value |
|---|---|
| Name | `lab9-web` (you'll rename them after launch) |
| AMI | **Ubuntu Server 24.04 LTS** (Free tier eligible) |
| Instance type | the one labelled **Free tier eligible**, usually `t3.micro` |
| Key pair | **Proceed without a key pair**. You'll connect from the browser. |
| Network settings | Allow **SSH traffic from Anywhere**, and allow **HTTP traffic from the internet** |
| Advanced details → User data | Paste the script below, with your GitHub username in it |
| Number of instances (right-hand Summary panel) | **2** |

```bash
#!/bin/bash
# Runs once, as root, the first time each instance boots.
apt-get update -y
apt-get install -y nginx git
rm -f /var/www/html/index.nginx-debian.html
git clone https://github.com/YOUR-GITHUB-USER/comp1350-lab9-site.git /home/ubuntu/site
chown -R ubuntu:ubuntu /home/ubuntu/site
```

When both instances show **Running**, use the pencil icon in the **Name** column to rename them `local-static` and `cdn-hosted`. Note each one's **Public IPv4 address**.

To open a terminal on an instance, select it, click **Connect**, choose the **EC2 Instance Connect** tab, then click **Connect**. Wait about a minute after the instance boots, then check that `ls ~/site` lists `index.html` and `static`. If it doesn't, the user data probably had a typo in the URL. Run the `git clone` line yourself, without `sudo`.

### 1.3 Deploy the "Local Assets" Version

*On `local-static`:*

```bash
sudo cp -r ~/site/index.html ~/site/static /var/www/html/
```

Open `http://<local-static-IP>`. Type `http://` yourself: there's no HTTPS on this server, so click through any "not secure" warning. In the page's table, every file should say **this server**.

### 1.4 Deploy the "CDN-Backed" Version

*On `cdn-hosted`:* rewrite the five asset URLs in `index.html` to point at jsDelivr. Bootstrap comes from jsDelivr's copy of the npm package. Your own CSS, JS and image come from jsDelivr's mirror of **your** GitHub repo, pinned to the `v1` tag.

```bash
cd ~/site
GH_USER=YOUR-GITHUB-USER        # <- change this
GH="https://cdn.jsdelivr.net/gh/$GH_USER/comp1350-lab9-site@v1"

sed -i \
  -e "s#/static/vendor/bootstrap.min.css#https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css#" \
  -e "s#/static/vendor/bootstrap.bundle.min.js#https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js#" \
  -e "s#\"/static/#\"$GH/static/#g" \
  index.html

grep -c 'cdn.jsdelivr' index.html                          # expect 5
sudo cp index.html /var/www/html/                          # deploy ONLY the HTML
curl -sI http://localhost/static/css/styles.css | head -1  # 404: this server has no assets
```

Open `http://<cdn-hosted-IP>`. It should look identical to the first site, but the table should show `cdn.jsdelivr.net` for all five files.

### 1.5 Measure

1. Load `http://<cdn-hosted-IP>` **once** before you measure. That first request makes jsDelivr fetch your files from GitHub and cache them at an edge server near you.
2. Open an **Incognito/InPrivate** window and open DevTools → **Network**. Tick **Disable cache**.
3. Hard-refresh (Ctrl+Shift+R / Cmd+Shift+R) **3 times** on each site. Each time, record the **Load** time from the status bar at the bottom of the Network tab:

| Run | `local-static` Load (ms) | `cdn-hosted` Load (ms) |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| **Average** | | |

4. On your laptop, inside your `comp1350-lab9-site` folder, time the image from each source:

```bash
bash tools/measure.sh http://<local-static-IP>/static/img/hero.jpg
bash tools/measure.sh https://cdn.jsdelivr.net/gh/YOUR-GITHUB-USER/comp1350-lab9-site@v1/static/img/hero.jpg
```

The `connect` column is the time for one network round trip to whichever server answered.

5. Find out which edge server answered you:

```bash
curl -sI https://cdn.jsdelivr.net/gh/YOUR-GITHUB-USER/comp1350-lab9-site@v1/static/img/hero.jpg \
  | grep -i -E 'x-served-by|cf-ray'
```

The last three letters are an airport code: `YVR` is Vancouver, `SEA` is Seattle.

**Q1**: Compare the average `connect` time to your EC2 server with the average to jsDelivr, and say where each server physically is. Why does that difference grow for a 1.2 MB image, which needs many round trips to download?

**Q2**: Describe the path `hero.jpg` took the very first time anyone requested it from jsDelivr (step 1), and how that path is different on every request after that.

**Q3**: In the on-page table, `bootstrap.min.css` is about **228 KB** from `local-static` but only about **22 KB** from jsDelivr. It's the same file. What is jsDelivr doing that your Nginx server isn't? Hint: run `curl -sI -H 'Accept-Encoding: br, gzip'` on both URLs and look at `content-encoding`. Could you fix this on your own server?

---

## Part 2: Build Your Own CDN on AWS

jsDelivr only serves files from public open-source repos. For your own company's assets, you build the same thing yourself:

```
your files ──► S3 bucket (private origin, Ohio)
                       ▲
                       │ only CloudFront is allowed to read it
browser in Vancouver ──► CloudFront edge (YVR/SEA) ──┘   cached? served straight from the edge
```

### 2.1 Create a Private S3 Bucket

1. **S3 → Create bucket.**
2. Name: `comp1350-lab9-<yourname>-assets`, for example `comp1350-lab9-jdoe-assets`. Bucket names are global, so make yours unique.
3. Leave **Block all public access** turned **on**, and every other setting as default. Click **Create bucket**.

### 2.2 Create a CloudFront Distribution

**CloudFront → Create distribution.** AWS changes this screen's layout often, so the step names may differ. These are the settings that matter:

| Setting | Value |
|---|---|
| Pricing plan (if asked) | **Free** |
| Distribution name | `lab9-assets` |
| Origin type | **Amazon S3**, then choose your bucket |
| Origin access | **Allow private S3 bucket access to CloudFront** (recommended). This lets the console add the bucket policy for you. |
| Cache settings | the recommended defaults |
| Security protections (WAF) | **Do not enable** (not available on free accounts) |

Create it, then copy the **Distribution domain name** (like `d1a2b3c4d5e6f7.cloudfront.net`) and the **Distribution ID** (like `E2ABCDEF123456`). Wait until **Last modified** shows a date instead of **Deploying**, which usually takes a few minutes.

### 2.3 Publish Your Assets with One Command

Open **AWS CloudShell**: click the `>_` icon at the top of the console. It's a terminal in your browser, already signed in to your account with the AWS CLI installed.

```bash
git clone https://github.com/YOUR-GITHUB-USER/comp1350-lab9-site.git
cd comp1350-lab9-site
BUCKET=comp1350-lab9-<yourname>-assets       # <- yours
DIST=E2ABCDEF123456                          # <- your distribution ID
CF=d1a2b3c4d5e6f7.cloudfront.net             # <- your distribution domain

bash tools/deploy.sh "$BUCKET" "$DIST"
```

Read `tools/deploy.sh`. It is only three steps:

1. **`aws s3 sync`** uploads new and changed files and deletes files you removed. Images and libraries are uploaded with `Cache-Control: max-age=86400`, so browsers may reuse them for a day.
2. A second `sync` uploads CSS and JS with `max-age=300`, so browsers recheck them every 5 minutes.
3. **`create-invalidation`** tells every CloudFront edge location to discard its cached `/static/*` files, so the next request fetches the new version from S3.

Now prove the bucket is private while CloudFront still works:

```bash
curl -sI "https://$BUCKET.s3.us-east-2.amazonaws.com/static/img/hero.jpg" | head -1   # 403 Forbidden
curl -sI "https://$CF/static/img/hero.jpg" | head -1                                  # 200 OK
```

### 2.4 Watch the Edge Cache Work

On your **laptop**, not CloudShell, which runs inside AWS:

```bash
CF=d1a2b3c4d5e6f7.cloudfront.net                       # <- yours
bash tools/measure.sh "https://$CF/static/img/hero.jpg"  # run 1 = cache miss, runs 2-5 = hits
curl -sI "https://$CF/static/css/styles.css" | grep -i -E 'x-cache|x-amz-cf-pop'
curl -sI "https://$CF/static/css/styles.css" | grep -i -E 'x-cache|x-amz-cf-pop'
```

The first `curl -sI` should say `Miss from cloudfront` and the second `Hit from cloudfront`. `x-amz-cf-pop` names the edge location, using an airport code again, for example `YVR52-P1`.

**Q4**: Compare run 1 (miss) with runs 2–5 (hits), and with `local-static`'s numbers from Part 1. Why is a cache miss about as slow as going straight to the origin?

**Q5**: The direct S3 URL returned `403`, but CloudFront could read the same file. What gives CloudFront that access? Name one security or cost problem it prevents compared with a public bucket.

### 2.5 Switch the Site to Your CDN and Ship an Update

1. *On `cdn-hosted`:* point your three own files at CloudFront. Bootstrap stays on jsDelivr.

```bash
cd ~/site
CF=d1a2b3c4d5e6f7.cloudfront.net        # <- yours
sed -i "s#https://cdn.jsdelivr.net/gh/[^/]*/comp1350-lab9-site@v1#https://$CF#g" index.html
grep -c "$CF" index.html                # expect 3
sudo cp index.html /var/www/html/
```

Reload `http://<cdn-hosted-IP>`. The table should now show your `….cloudfront.net` domain for `styles.css`, `hero.jpg` and `app.js`.

2. **Make a change.** On GitHub, edit the files directly with the pencil icon and commit each one to `main`:
   - `static/css/styles.css`: change `--accent: #0d6efd;` to another colour, for example `#d63384`
   - `static/js/app.js`: change `const ASSET_VERSION = "v1";` to `"v2"`

3. **Publish it.** In CloudShell:

```bash
cd ~/comp1350-lab9-site
git pull
bash tools/deploy.sh "$BUCKET" "$DIST"
```

(If CloudShell was closed in the meantime, set `BUCKET` and `DIST` again first.)

4. Reload `http://<cdn-hosted-IP>` with **Disable cache** ticked. It should show **v2** in your new colour, and you never logged into a web server. `local-static` still shows **v1**: someone would have to copy files onto it by hand.

**Q6**: A visitor who loaded the page just before your update may still see the old CSS for up to 5 minutes, even though the invalidation finished. Why, and which setting in `deploy.sh` controls it? Large sites often put a fingerprint in each filename instead (`styles.3f9a1c.css`) and never invalidate. Explain how that avoids the problem.

---

## Stretch Goals (Optional)

**Deploy on every `git push` with GitHub Actions.** GitHub needs AWS credentials to run `deploy.sh` for you. The best practice is OIDC, which avoids stored keys, but free AWS accounts block it. So this goal uses an access key:

1. **IAM → Users → Create user** named `lab9-deployer`, with no console access and no policies.
2. On the user, go to **Permissions → Add permissions → Create inline policy → JSON**. Paste the policy below with your values filled in:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "s3:ListBucket", "Resource": "arn:aws:s3:::BUCKET-NAME" },
    { "Effect": "Allow", "Action": ["s3:PutObject", "s3:DeleteObject"], "Resource": "arn:aws:s3:::BUCKET-NAME/static/*" },
    { "Effect": "Allow", "Action": ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"],
      "Resource": "arn:aws:cloudfront::ACCOUNT-ID:distribution/DISTRIBUTION-ID" }
  ]
}
```

3. **Security credentials → Create access key**, use case **Third-party service**. In your GitHub repo, go to **Settings → Secrets and variables → Actions** and add secrets `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. On the **Variables** tab, add `S3_BUCKET` and `CF_DISTRIBUTION_ID`.
4. Add `.github/workflows/deploy.yml`:

```yaml
name: Deploy static assets
on:
  push:
    branches: [main]
    paths: ["static/**"]
  workflow_dispatch:
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - run: bash tools/deploy.sh "${{ vars.S3_BUCKET }}" "${{ vars.CF_DISTRIBUTION_ID }}"
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: us-east-2
```

5. Change `ASSET_VERSION` to `"v3"` on GitHub and watch the **Actions** tab publish it with no CloudShell. **Delete the access key** when you're done: a leaked long-lived key is the main risk of this method.

**Simulate a server on the other side of the world.** On both EC2 instances, add 150 ms of delay to every packet the server sends, then repeat the Part 1 measurement:

```bash
sudo tc qdisc add dev $(ip route show default | awk '{print $5}') root netem delay 150ms   # add
sudo tc qdisc del dev $(ip route show default | awk '{print $5}') root                    # remove
```

The CDN-backed site barely slows down, because only its HTML comes from the "far" server.

---

## The Same Thing on Azure (For Reference)

| What it does | AWS (this lab) | Azure |
|---|---|---|
| Stores the original files | S3 bucket | Storage account (Blob container) |
| Edge caching network | CloudFront | Azure Front Door |
| Upload changed files | `aws s3 sync` | `az storage blob sync` |
| Clear the edge cache | `aws cloudfront create-invalidation` | `az afd endpoint purge` |

The ideas are identical. This lab uses AWS because Azure Front Door charges a monthly base fee, while CloudFront is free at this scale.

---

## Clean Up

- **EC2 → Instances →** select both **→ Instance state → Terminate.** Running instances use up your free credits every hour.
- **Keep** the S3 bucket and CloudFront distribution if you'll use them for the group project. They cost nothing when idle. Otherwise: **disable** the distribution, wait until it finishes deploying, **delete** it, then **empty** and **delete** the bucket.
- If you did the GitHub Actions stretch goal, delete the `lab9-deployer` access key, or the whole user.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Region unavailable" dialog | Free accounts use one region. Close the dialog and switch back to your account's region. Don't activate advanced features. |
| Browser can't reach `http://<IP>` | Make sure you typed `http://`, not `https://`. Check the security group allows **HTTP**. |
| `ls ~/site` is empty | A typo in the user data URL. Run the `git clone` line yourself. |
| jsDelivr returns 404 | Make sure the repo is **public**, you pushed the tag (`git push origin v1`), and the path's capitalization matches. |
| CloudFront returns 403 | The bucket policy is missing (re-check **Origin access** in 2.2), or `deploy.sh` hasn't run yet. |
| Page still shows v1 after deploying | Your browser cached `app.js`. Tick **Disable cache** in DevTools and reload. |

## Deliverables

**Part 1**

- Screenshots of both sites' on-page tables: **this server** for `local-static`, **cdn.jsdelivr.net** for `cdn-hosted`
- The `404` output from 1.4
- Your measurement table, the two `measure.sh` outputs, and the edge header from 1.5
- Answers to Q1–Q3

**Part 2**

- The `403` (S3) and `200` (CloudFront) outputs from 2.3
- The `measure.sh` output and the Miss/Hit headers from 2.4
- Screenshots of the `cdn-hosted` page before (**v1**) and after (**v2**) your update
- Answers to Q4–Q6
