---
title: "Lab 5: SSL/TLS — Self-Signed Certificates & Let's Encrypt"
---

[&larr; Back to course index]({{ '/' | relative_url }})

{% raw %}
# Lab 5: SSL/TLS — Self-Signed Certificates & Let's Encrypt

*COMP 1350 — Web Administration, Week 5*

In this lab you'll generate a self-signed TLS certificate by hand (to see every moving part), configure Nginx to serve HTTPS with it, then contrast that manual process with Certbot's fully automated Let's Encrypt workflow.

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box, add a `vmware_desktop` provider block instead of the VirtualBox one, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — IPs, commands, config files — is identical.

## Part 1: Provision the VM

```bash
mkdir ~/comp1350-lab5 && cd ~/comp1350-lab5
vagrant init ubuntu/jammy64
```

Add a private network line to the `Vagrantfile`:

```ruby
config.vm.network "private_network", ip: "192.168.56.15"
```

```bash
vagrant up
vagrant ssh
sudo apt update
sudo apt install nginx openssl -y
```

## Part 2: Generate a Self-Signed Certificate

1. Create a directory to hold your key material:

```bash
sudo mkdir -p /etc/nginx/ssl_key
cd /etc/nginx/ssl_key
```

2. Generate a private key (4096-bit RSA):

```bash
sudo openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out server.key
```

3. Generate a Certificate Signing Request (CSR). When prompted, set **Common Name** to `192.168.56.15` (your VM's IP):

```bash
sudo openssl req -new -key server.key -out csr.pem
```

4. Self-sign the CSR to produce the final certificate (valid 365 days):

```bash
sudo openssl x509 -req -days 365 -in csr.pem -signkey server.key -out server.crt
```

5. Verify the key and CSR match:

```bash
sudo openssl req -in csr.pem -noout -verify -key server.key
```

6. You now have three files. Note what each is for:

| File | Purpose |
|---|---|
| `server.key` | Private key — never share this, never commit it to Git |
| `server.crt` | The certificate itself (contains the public key) |
| `csr.pem` | The signing request — safe to delete now, no longer needed |

## Part 3: Configure Nginx for HTTPS

1. Create a site root and page:

```bash
sudo mkdir -p /var/www/wsalab5.info
echo "<h1>Secured by Self-Signed TLS</h1>" | sudo tee /var/www/wsalab5.info/index.html
```

2. Create the site config:

```bash
sudo nano /etc/nginx/sites-available/wsalab5.info
```

```nginx
server {
    listen 443 ssl;
    server_name wsalab5.info;

    ssl_certificate /etc/nginx/ssl_key/server.crt;
    ssl_certificate_key /etc/nginx/ssl_key/server.key;

    root /var/www/wsalab5.info;
    index index.html;
}
```

3. Enable the site, test, and restart:

```bash
sudo ln -s /etc/nginx/sites-available/wsalab5.info /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

4. On your host machine, add `192.168.56.15 wsalab5.info` to your hosts file, then visit `https://wsalab5.info`.

**Q1**: You will get a browser security warning. Take a screenshot of it and be ready to explain to your instructor exactly *why* the browser doesn't trust this certificate, even though the connection is genuinely encrypted.

5. View the certificate details in your browser (Chrome: click the padlock → Certificate). Screenshot the Common Name and validity dates.

## Part 4: Enforce HTTPS (Redirect HTTP → HTTPS)

1. Add a second server block to the same config file for port 80 that redirects to HTTPS:

```nginx
server {
    listen 80;
    server_name wsalab5.info;
    return 301 https://$host$request_uri;
}
```

2. Test and reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

3. Confirm the redirect with curl:

```bash
curl -I http://wsalab5.info
```

**Q2**: Show your instructor the `301` status code and the `Location` header in the curl output.

## Part 5: Let's Encrypt with Certbot (Automated Alternative)

*Let's Encrypt requires a publicly resolvable domain name and port 80/443 reachable from the internet — it cannot issue a certificate for a private IP like `192.168.56.15` or an unregistered `.local`/`.info` name. This part is a guided walkthrough you'll run against your live PaaS deployment from Week 4 (Render/Vercel/Netlify), which already provisions valid certificates automatically — or, if your instructor has arranged a shared public test domain, against that.*

1. If working against your own domain pointed at a real public server, install Certbot:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

2. Run Certbot's Nginx plugin — it automatically edits your Nginx config, obtains the certificate, and reloads Nginx for you:

```bash
sudo certbot --nginx -d yourdomain.com
```

3. Certbot will ask whether to redirect HTTP to HTTPS automatically — compare this to the manual `return 301` block you wrote by hand in Part 4.

4. Certificates from Let's Encrypt expire every **90 days**. Certbot installs a renewal timer automatically. Confirm it:

```bash
sudo systemctl list-timers | grep certbot
sudo certbot renew --dry-run
```

**Q3**: List every manual step from Parts 2–4 that Certbot's `--nginx` flag replaced with a single command.

## Deliverables

- Screenshot of the browser security warning from Part 3, plus your written explanation for Q1
- Screenshot of the certificate details (Common Name, validity dates) from Part 3
- Screenshot of the `curl -I` output from Part 4 showing the 301 redirect
- Your completed answer to Q3
- Your final Nginx site config file
{% endraw %}
