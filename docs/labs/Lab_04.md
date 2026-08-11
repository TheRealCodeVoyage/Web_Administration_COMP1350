---
title: "Lab 4: Deployment — GitHub Pages & Modern PaaS"
---

[&larr; Back to course index]({{ '/' | relative_url }})

{% raw %}
# Lab 4: Deployment — GitHub Pages & Modern PaaS

*COMP 1350 — Web Administration, Week 4*

In this lab you will deploy two things to the public internet: a static site via GitHub Pages, and the Node.js/Express application you built in Lab 3 via a modern PaaS provider (Render). By the end of this lab you will have a live, public URL for each.

## Prerequisites

- A [GitHub](https://github.com) account
- Git installed and configured locally (`git config --global user.name` / `user.email` already set)
- The Node.js/Express + PM2 project from Lab 3, committed to a local Git repository
- A free [Render](https://render.com) account (sign in with GitHub for the smoothest setup)

## Part 1: Deploy a Static Site to GitHub Pages

1. Create a new public repository on GitHub named `<yourname>-portfolio`.
2. Clone it locally and add a minimal static site:

```bash
git clone https://github.com/<your-username>/<yourname>-portfolio.git
cd <yourname>-portfolio
```

Create `index.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Portfolio</title>
</head>
<body>
  <h1>Hello from GitHub Pages!</h1>
  <p>Deployed by <yourname> — COMP 1350, Week 4.</p>
</body>
</html>
```

3. Commit and push:

```bash
git add index.html
git commit -m "Add initial static site"
git push origin main
```

4. On GitHub, go to **Settings → Pages**. Under **Build and deployment**, set **Source** to "Deploy from a branch", branch `main`, folder `/ (root)`. Save.
5. Wait 1–2 minutes, then visit `https://<your-username>.github.io/<yourname>-portfolio/`.
6. Make a small change to `index.html`, commit, and push again. Confirm the live site updates automatically within a minute or two — this is the Git-based deployment workflow from lecture in action.

## Part 2: Deploy the Node/Express App to Render

1. Push your Lab 3 Node/Express project to a **new** GitHub repository (`<yourname>-webapp`).
2. Confirm your `package.json` has a valid `start` script, e.g.:

```json
"scripts": {
  "start": "node server.js"
}
```

   Render runs `npm install` then `npm start` — it does not need PM2 directly; Render's platform plays the role PM2 played on your own VM (keeping the process alive, restarting on crash).

3. In the Render dashboard: **New → Web Service**, connect the `<yourname>-webapp` repository.
4. Configure:
   - **Environment**: Node
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Instance Type**: Free
5. Click **Create Web Service**. Watch the build log — this is the same "build runs" step from the lecture diagram.
6. Once deployed, Render gives you a public URL like `https://<yourname>-webapp.onrender.com`. Confirm your app responds correctly.
7. Make a small change to a route's response text, commit, and push. Confirm Render automatically rebuilds and redeploys.

> **Note on the free tier:** Render's free web services "sleep" after a period of inactivity and take a few seconds to wake on the next request. This is expected — do not treat the first slow request as a bug.

## Part 3: Environment Variables on Render

1. In your Express app, add a route that reads an environment variable:

```js
app.get('/version', (req, res) => {
  res.send(`App version: ${process.env.APP_VERSION || 'unset'}`);
});
```

2. In the Render dashboard, go to your service's **Environment** tab and add:

```
APP_VERSION=1.0.0
```

3. Redeploy (Render will prompt you, or trigger a manual deploy) and visit `/version` to confirm the value is read from the environment, not hardcoded.
4. Add a `.env.example` file to your repo (do **not** commit a real `.env` file) documenting which variables the app expects:

```
APP_VERSION=
```

## Part 4 (Bonus): Custom Domain

If you own a domain (or want to use a free subdomain provider), attach it to your Render service under **Settings → Custom Domains**, and follow Render's DNS instructions (typically a `CNAME` record). Confirm HTTPS is automatically provisioned once DNS propagates.

## Deliverables

Submit a short writeup (1 page) with:

- Your live GitHub Pages URL and your live Render URL
- A screenshot of each site/app running in a browser
- A screenshot of the Render environment variables panel showing `APP_VERSION`
- One paragraph: compare the deployment experience of GitHub Pages vs. Render — what could each one **not** do that the other could?
{% endraw %}
