# COMP 1350 — Web Administration
## Group Project: Deploy & Harden a Team Site

**Weight:** 20% of final course grade
**Team size:** 3–4 students
**Released:** Week 4 (Thu Oct 1) — the week the Deployment module lands
**Final delivery:** Week 13 (Thu Dec 3)

---

## Overview

Your team will take a small web application from "runs on my laptop" to "runs like a real production service" over the course of the term. Each project milestone lands the same week you've just learned the skills to build it — this project is not a one-shot assignment at the end of the course, it's the running thread that ties every lab together.

By the end of the term your team will have: built and deployed a real site, put it behind a reverse proxy with TLS, added authenticated login, scaled it across multiple backend instances with a load balancer, removed single points of failure, sped up asset delivery with a CDN, and instrumented it with centralized logging and analytics. That is, in miniature, the same lifecycle a junior developer or web admin manages on the job.

**Choose one project type as a team:**
- **Portfolio site** — a professional team or individual portfolio (resume, project showcase, contact) — the direct successor to ACIT 3475's portfolio project, or
- **Small product/utility app** — any small web app with at least one form of user interaction (e.g., a note-taking tool, a link shortener, a simple booking board) — recommended if your team wants something more substantial to show employers.

Either type must satisfy every milestone's technical requirements below; the *content* of the site is your choice, the *infrastructure* around it is not.

---

## Milestone A — Site Live, Reverse Proxy, TLS (25%)

**Due:** Week 6 (Thu Oct 15)

- A working frontend (HTML/CSS/JS, or a framework of your choice) and a backend built with Node.js/Express (per Lab 3), managed as a persistent process with PM2 — not `node app.js` left running in a terminal.
- The app is deployed to a real host: either a cloud VM (AWS/DigitalOcean/Azure — your choice) or a PaaS provider from Week 4 (Render/Vercel/Netlify), whichever fits your app type.
- Your Node/Express app binds to `127.0.0.1` only. A web server — **Nginx or Apache**, your team's choice — sits in front of it as a reverse proxy and is the only publicly-facing service (per Lab 6). *(This replaces ACIT 3475 Project 1's use of the Caddy web server — Caddy isn't taught in COMP 1350, so the reverse proxy is built with the server your team has actually learned in Weeks 2, 3, and 6.)*
- TLS is enabled at the reverse proxy — a self-signed certificate is acceptable for local/VM demos; a Let's Encrypt certificate is required if you're on a real public domain (Lab 5).
- HTTP requests are redirected to HTTPS.

**Deliverables:** live URL, GitHub repo link, and a short (1–2 page) Markdown write-up covering your reverse-proxy config (with annotations) and any troubleshooting you hit.

---

## Milestone B — Authenticated Login & Integrated Backend (25%)

**Due:** Week 9 (Thu Nov 5) — the week after the midterm buffer

- "Sign in with Google" implemented via Passport.js and Google Cloud OAuth 2.0 (per Lab 7). Client ID/secret are stored as environment variables — never hardcoded or committed to the repo.
- At least one part of your site is gated behind authentication (e.g., only a logged-in user can edit the portfolio's "Projects" section, or only a logged-in user can create/edit content in a product app).
- Your Express backend from Milestone A is still the app serving these routes — this milestone extends it, it doesn't replace it.

**Optional stretch feature:** embed a GitHub contributions calendar widget (e.g., [github-contributions-widget](https://github.com/imananoosheh/github-contributions-widget)) loaded via CDN, styled to match your site. Not required for full marks, but a nice, low-effort way to make a portfolio look more current.

**Deliverables:** updated live URL demonstrating login-gated functionality, and a short write-up of your OAuth setup (redirect URIs, consent screen config, how secrets are managed).

---

## Milestone C — Load Balancing, Redundancy, CDN, Logging & Analytics (30%)

**Due:** Week 12 (Thu Nov 26)

This is the heaviest milestone — it's where your project graduates from "one server" to "a small distributed system."

- **Load balancing:** at least two backend instances of your app running behind an HAProxy load balancer (per Lab 8), using round-robin or least-connections.
- **Redundancy:** apply the SPOF analysis from Lab 9 to your own architecture — identify where your remaining single point of failure is (it's very likely your one load balancer) and either implement a second load balancer with keepalived/VRRP, or, if time-constrained, document the design for how you *would* remove it and why.
- **CDN:** static assets (images, CSS, JS) served through a CDN — either jsDelivr (if your static assets live in a public GitHub repo) or Cloudflare's free tier in front of your domain (per Lab 10).
- **Centralized logging:** logs from all your backend instances are forwarded to a single collector (rsyslog remote forwarding, or a hosted option like Loki/Papertrail), not left scattered across individual servers (per Lab 11).
- **Analytics:** Google Analytics 4 (GA4) tag installed and confirmed collecting real pageview/event data.

**Deliverables:** updated live URL, HAProxy config with annotations, a short SPOF write-up (what you found, what you did about it), and a screenshot of GA4 showing live data.

---

## Final Delivery — Presentation (20%)

**Due:** Week 13 (Thu Dec 3) — course review week, no new technical requirement is added here

- A recorded video presentation, **10–15 minutes**, walking through: what you built, your architecture (a simple diagram is expected), what broke and how you fixed it, and a live demo of the working, load-balanced site.
- Submitted asynchronously ahead of Week 13's class; Week 13's class time is used for a live Q&A and course review, not first viewings.
- Every team member should have a speaking role in the video.

**Deliverables:** video file or link (e.g., unlisted YouTube/Drive link), plus final versions of all prior write-ups consolidated into one repo README.

---

## Submission Format

Everything lives in one team GitHub repository:

- `/README.md` — project overview, architecture diagram, links to the live site, and links to (or inlined copies of) each milestone's write-up.
- Configuration files (Nginx/Apache config, HAProxy config, Vagrantfiles if used) committed with clear inline comments — never commit real secrets; use a `.env.example` file to show what variables are needed.
- A short section in the README naming which team member led which milestone (individual contribution is factored into peer-assessment, see below).

---

## Grading Breakdown

| Component | Weight (of the 20% project grade) |
|---|---|
| Milestone A — Site live, reverse proxy, TLS | 25% |
| Milestone B — OAuth login, integrated backend | 25% |
| Milestone C — Load balancing, redundancy, CDN, logging, GA4 | 30% |
| Final delivery — presentation | 20% |

A short peer-assessment form is submitted individually alongside the Final Delivery; significant, documented imbalance in contribution can adjust an individual's project grade independently of the team grade.

---

## Academic Integrity

Using AI tools (including Claude, ChatGPT, or GitHub Copilot) to help write code, debug configs, or draft documentation is permitted and expected — this mirrors how junior developers actually work. What is not permitted is submitting infrastructure you don't understand: any team member should be able to explain, live, what any line of their Nginx/HAProxy config or OAuth flow does. Milestone write-ups must be in your own words even if a tool helped you get there.

---

## Source Note

This project consolidates ACIT 3475's two separate projects — Project 1 (*Research and Deployment of a Professional Portfolio Web Server*, built around the Caddy web server) and Project 2 (*High-Availability Portfolio with OAuth and GitHub Contributions*) — into a single milestone-based project spanning the whole term, matching COMP 1350's own week-by-week technical progression. The Caddy-specific research component from Project 1 (Part 1: a graded video presentation comparing Caddy/Apache/Nginx) has been dropped, since Caddy is not part of COMP 1350's outline; its grading weight has been redistributed across the four milestones above. All other technical requirements (TLS, OAuth, HAProxy load balancing, GitHub contributions widget, scalability documentation) are retained, resequenced to match when each skill is actually taught.
