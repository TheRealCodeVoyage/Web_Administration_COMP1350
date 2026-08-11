---
title: "COMP 1350: Web Administration"
---

# COMP 1350: Web Administration

Labs, online activities, and the group project for BCIT's COMP 1350. The course takes you from installing your first web server to running a load-balanced, redundant, TLS-secured, CDN-backed web stack with centralized logging — the same progression a junior developer or web administrator manages on the job.

Everything students need for hands-on work lives here. Slides, quizzes, and exams are distributed through the course LMS, not this site.

## Labs Index

| # | Lab | Week |
|---|---|---|
| 1 | [Development VM Setup with VirtualBox & Vagrant](labs/Lab_01.html) | Week 1 |
| 2 | [Apache & Nginx Side-by-Side](labs/Lab_02.html) | Week 2 |
| 3 | [IIS & Node.js/Express.js with PM2](labs/Lab_03.html) | Week 3 |
| 4 | [Deployment — GitHub Pages & Modern PaaS](labs/Lab_04.html) | Week 4 |
| 5 | [SSL/TLS — Self-Signed Certificates & Let's Encrypt](labs/Lab_05.html) | Week 5 |
| 6 | [Reverse Proxy Terminating TLS](labs/Lab_06.html) | Week 6 |
| 7 | [OAuth Login with Passport.js](labs/Lab_07.html) | Week 7 |
| 8 | [Load Balancing with HAProxy](labs/Lab_08.html) | Week 9 |
| 9 | [Eliminating Single Points of Failure](labs/Lab_09.html) | Week 10 |
| 10 | [CDN — jsDelivr Latency Test & Cloudflare Setup](labs/Lab_10.html) | Week 11 |
| 11 | [Centralized Logging](labs/Lab_11.html) | Week 12 |

## Online Activities (Flipped Material)

Each online activity is assigned **one week before** the class it prepares you for. Complete it before that class — its guided questions form the basis of that week's quiz, and the lecture then extends the material in more depth.

| Assigned | Activity | Prepares you for |
|---|---|---|
| Week 0 | [Web Stack Basics](online-activities/OA_01.html) | Week 1 — Intro & the web stack |
| Week 1 | [Apache vs. Nginx Recap](online-activities/OA_02.html) | Week 2 — Apache & Nginx side by side |
| Week 2 | [Application Servers Recap](online-activities/OA_03.html) | Week 3 — IIS & Node.js/Express |
| Week 3 | [Deployment Models Recap](online-activities/OA_04.html) | Week 4 — GitHub Pages & PaaS |
| Week 4 | [SSL/TLS Recap](online-activities/OA_05.html) | Week 5 — SSL/TLS |
| Week 5 | [PKI & Proxy Recap](online-activities/OA_06.html) | Week 6 — PKI & reverse proxy |
| Week 6 | [Authentication Concepts Recap](online-activities/OA_07.html) | Week 7 — OAuth |
| Week 7 | [Load Balancing Recap](online-activities/OA_08.html) | Week 9 — Load balancing |
| Week 9 | [SPOF & High Availability Recap](online-activities/OA_09.html) | Week 10 — Single points of failure |
| Week 10 | [CDN Recap](online-activities/OA_10.html) | Week 11 — Content delivery networks |
| Week 11 | [Logging & Analytics Recap](online-activities/OA_11.html) | Week 12 — Centralized logging & GA4 |

*Week 8 is the midterm exam week and Week 14 is the final exam week — no classes are held during either. Week 13 is course review and project presentations, with no new content.*

## Group Project

[**Deploy & Harden a Team Site**](projects/Group_Project.html) — 20% of your final grade, worked on in teams of 3–4 across the whole term.

| Milestone | Due | Covers |
|---|---|---|
| Released | Week 4 | Brief distributed |
| Milestone A | Week 6 | Site live via web server + reverse proxy + TLS |
| Milestone B | Week 9 | OAuth login + Node/Express backend |
| Milestone C | Week 12 | Load balancing, redundancy, CDN, centralized logging, GA4 |
| Final delivery | Week 13 | Recorded video presentation |

## Course Overview

COMP 1350 introduces students to installing, configuring, and running HTTP servers such as Apache, IIS, and Nginx. Students run real web applications on those servers, create and manage virtual hosts, and work through the issues that matter in production: security, HTTPS, redirects, logging, performance optimization, and troubleshooting — first locally, then on remote hosts.

### Learning Outcomes

By the end of this course, students will be able to:

1. Describe the components of a scalable, distributed web stack.
2. Set up, manage, and deploy web servers.
3. Integrate dynamic web applications with web server modules, reverse proxies, and standalone application servers.
4. Define load balancing, explain why it is needed, and describe common solutions and algorithms.
5. Identify solutions to eliminate single points of failure in a web stack.
6. Configure transport layer security with TLS and X.509 certificates.
7. Implement token-based authentication mechanisms including OAuth.
8. Integrate Content Delivery Networks.
9. Implement a centralized log server.
10. Implement simple directives in config files, ini files, and .htaccess-type files.
11. Move a web application from running on a local server to running on a remote host server.
12. Describe, measure, and optimize metrics such as those provided by Google Analytics to attract, hold, and convert users, and to identify abnormalities and opportunities for improvement.

### Technical Stack

- **Virtualization:** VirtualBox + Vagrant
- **Web servers:** Apache, Nginx, IIS
- **Application server:** Node.js / Express, managed with PM2
- **Deployment:** GitHub Pages, PaaS (Render / Vercel / Netlify)
- **Security:** OpenSSL, Let's Encrypt / Certbot, OAuth 2.0 with Passport.js
- **Availability:** HAProxy, Nginx `upstream`, keepalived / VRRP concepts
- **Performance:** jsDelivr, Cloudflare
- **Observability:** rsyslog centralized logging, Google Analytics 4

## Getting Started

Start with [Lab 1](labs/Lab_01.html), which sets up the VirtualBox and Vagrant environment every later lab depends on. Complete it before Week 2 — the labs build on each other, and a broken environment in Week 1 becomes a broken lab in Week 6.
