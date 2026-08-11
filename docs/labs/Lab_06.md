---
title: "Lab 6: Reverse Proxy Terminating TLS"
---

[&larr; Back to course index]({{ '/' | relative_url }})

{% raw %}
# Lab 6: Reverse Proxy Terminating TLS

*COMP 1350 — Web Administration, Week 6*

This lab connects everything you've built so far: the Node/Express app from Week 3, the TLS certificate skills from Week 5, and this week's reverse-proxy concept — all in one working, HTTPS-secured application. This is also **Milestone A** of your group project.

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box, add a `vmware_desktop` provider block instead of the VirtualBox one, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — IPs, commands, config files — is identical.

## Part 1: Provision the VM

```bash
mkdir ~/comp1350-lab6 && cd ~/comp1350-lab6
vagrant init ubuntu/jammy64
```

Add to the `Vagrantfile`:

```ruby
config.vm.network "private_network", ip: "192.168.56.16"
```

```bash
vagrant up
vagrant ssh
sudo apt update
sudo apt install nginx openssl -y
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

## Part 2: Bring Up the Node/Express Backend

1. Reuse (or recreate) your Week 3 Express app:

```bash
mkdir ~/app && cd ~/app
npm init -y
npm install express
```

2. Create `server.js`:

```js
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello from behind the reverse proxy!');
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(3000, '127.0.0.1', () => console.log('App listening on 127.0.0.1:3000'));
```

   Note the app binds to `127.0.0.1` only, not `0.0.0.0` — it should never be reachable directly from outside the VM. Only Nginx should be publicly exposed.

3. Start it under PM2:

```bash
pm2 start server.js --name comp1350-app
pm2 save
```

4. Confirm it responds locally, but only locally:

```bash
curl http://127.0.0.1:3000
```

## Part 3: Generate a TLS Certificate

*Reuse the process from Lab 5.*

```bash
sudo mkdir -p /etc/nginx/ssl_key && cd /etc/nginx/ssl_key
sudo openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out server.key
sudo openssl req -new -key server.key -out csr.pem
sudo openssl x509 -req -days 365 -in csr.pem -signkey server.key -out server.crt
```

   Set the Common Name to `192.168.56.16` when prompted.

## Part 4: Configure Nginx as a Reverse Proxy with TLS Termination

1. Create the site config:

```bash
sudo nano /etc/nginx/sites-available/comp1350-app
```

```nginx
server {
    listen 443 ssl;
    server_name comp1350-app.local;

    ssl_certificate     /etc/nginx/ssl_key/server.crt;
    ssl_certificate_key /etc/nginx/ssl_key/server.key;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name comp1350-app.local;
    return 301 https://$host$request_uri;
}
```

2. Enable the site, test, and restart:

```bash
sudo ln -s /etc/nginx/sites-available/comp1350-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

3. On your host machine, add `192.168.56.16 comp1350-app.local` to your hosts file. Visit `https://comp1350-app.local` — you should see your Express app's response, served over HTTPS, even though Express itself knows nothing about TLS.

## Part 5: Confirm the Architecture

1. Confirm the Node app is genuinely unreachable from outside the VM. From your **host machine**:

```bash
curl http://192.168.56.16:3000
```

   This should fail (connection refused) — the app only listens on `127.0.0.1` inside the VM, and Nginx is the only public entry point.

2. Inspect the forwarded headers your backend receives. Temporarily add a debug route to `server.js`:

```js
app.get('/whoami', (req, res) => {
  res.json({
    host: req.headers['host'],
    realIp: req.headers['x-real-ip'],
    forwardedFor: req.headers['x-forwarded-for'],
    forwardedProto: req.headers['x-forwarded-proto'],
  });
});
```

3. Restart the app and hit the route through the proxy:

```bash
pm2 restart comp1350-app
curl -k https://comp1350-app.local/whoami
```

**Q1**: Explain in your own words what each of the three `proxy_set_header` lines is preserving for the backend, and why the backend would lose that information without them.

## Deliverables

- Screenshot of `https://comp1350-app.local` loading successfully with a valid padlock-click showing your self-signed cert
- Screenshot of the failed `curl` attempt directly to port 3000 from your host machine
- Output of the `/whoami` route showing the forwarded headers arriving correctly
- Your final Nginx site config
- Your written answer to Q1
- **This lab is Milestone A of your group project** — submit your working URL/setup per the project spec alongside your individual lab deliverables
{% endraw %}
