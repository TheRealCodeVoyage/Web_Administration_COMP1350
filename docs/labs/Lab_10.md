---
title: "Lab 10: CDN — jsDelivr Latency Test & Cloudflare Setup"
---

[&larr; Back to course index]({{ '/' | relative_url }})

{% raw %}
# Lab 10: CDN — jsDelivr Latency Test & Cloudflare Setup

*COMP 1350 — Web Administration, Week 11*

In this lab you'll measure the real latency difference a CDN makes on static assets, then route your own project's domain through Cloudflare to see CDN behavior configured end to end on a production-grade free tier.

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box in both VM definitions, add a `vmware_desktop` provider block to each, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — IPs, commands, config files — is identical.

## Part 1: Provision Two VMs

```bash
mkdir ~/comp1350-lab10 && cd ~/comp1350-lab10
vagrant init
```

```ruby
Vagrant.configure("2") do |config|
  config.vm.define "local-static" do |a|
    a.vm.box = "ubuntu/jammy64"
    a.vm.hostname = "local-static"
    a.vm.network "private_network", ip: "192.168.56.31"
  end

  config.vm.define "cdn-hosted" do |b|
    b.vm.box = "ubuntu/jammy64"
    b.vm.hostname = "cdn-hosted"
    b.vm.network "private_network", ip: "192.168.56.32"
  end
end
```

```bash
vagrant up
```

## Part 2: Install Nginx on Both VMs

*On both `local-static` and `cdn-hosted`:*

```bash
sudo apt update
sudo apt install nginx git -y
```

## Part 3: Set Up the "Local Assets" Version

*On `local-static`:*

1. Clone a small static demo project (any small HTML/CSS/JS project works — use your own portfolio site from Week 4, or a simple demo):

```bash
git clone https://github.com/imananoosheh/wordle-replica-project.git
cd wordle-replica-project
sudo cp index.html script.js styles.css /var/www/html/
sudo rm -f /var/www/html/index.nginx-debian.html
sudo nginx -t
sudo systemctl restart nginx
```

2. Confirm it loads at `http://192.168.56.31` from your host browser.

## Part 4: Set Up the "CDN-Backed" Version

*On `cdn-hosted`:*

1. Clone the same project:

```bash
git clone https://github.com/imananoosheh/wordle-replica-project.git
cd wordle-replica-project
```

2. Edit `index.html` and replace the local `<link>`/`<script>` references to `styles.css` and `script.js` with jsDelivr CDN URLs pointing at the same public GitHub repo:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/imananoosheh/wordle-replica-project@master/styles.css">
<script src="https://cdn.jsdelivr.net/gh/imananoosheh/wordle-replica-project@master/script.js"></script>
```

3. Deploy only `index.html` — the CSS/JS now come from jsDelivr's edge network instead of this server:

```bash
sudo cp index.html /var/www/html/
sudo rm -f /var/www/html/index.nginx-debian.html
sudo nginx -t
sudo systemctl restart nginx
```

4. Confirm it loads at `http://192.168.56.32`.

## Part 5: Measure and Compare Latency

1. Open `http://192.168.56.31` in an **Incognito/InPrivate** window. Open DevTools → Network tab, hard-refresh (Ctrl+Shift+R) 5 times, and record the "Finish" time each time.
2. Repeat for `http://192.168.56.32`.
3. Average each set of 5 readings.

| Run | Local Assets (ms) | CDN-Backed (ms) |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| **Average** | | |

**Q1**: Your lab VMs are on the same machine, so this test won't show a dramatic real-world difference the way a globally distributed audience would. Explain in your own words why the gap would be much larger for a real user in, say, Singapore, hitting a server physically located in Vancouver.

## Part 6: Cloudflare Free Tier on a Real Domain

*This part requires a domain you control — use your Week 4 PaaS deployment's custom domain, or a free subdomain from your registrar if available.*

1. Sign up for a free Cloudflare account at [cloudflare.com](https://www.cloudflare.com) and add your domain as a site.
2. Cloudflare will scan your existing DNS records and ask you to update your domain's nameservers at your registrar to point to Cloudflare's nameservers. Do this.
3. Once active (may take a few minutes to a few hours), confirm your site still loads normally — Cloudflare now sits in front of it as a reverse proxy/CDN.
4. In the Cloudflare dashboard, enable **Auto Minify** for HTML/CSS/JS under Speed settings.
5. Under **Caching**, review the default caching rules for static assets.
6. Find and enable **"I'm Under Attack Mode"** temporarily (Security settings), reload your site, and observe the interstitial challenge page it shows visitors. Turn it back off afterward.

**Q2**: "I'm Under Attack Mode" is a visible, dramatic example of one specific CDN benefit from this week's lecture. Which one, and why does putting it at the CDN layer (rather than your own server) make it effective against a real DDoS attempt?

## Deliverables

- Your completed latency comparison table from Part 5, with your Q1 answer
- Screenshot of your Cloudflare dashboard showing your domain as **Active**
- Screenshot of "I'm Under Attack Mode" enabled, showing the challenge page
- Your written answer to Q2
{% endraw %}
