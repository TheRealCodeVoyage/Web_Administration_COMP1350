# Lab 3: IIS & Node.js/Express.js with PM2

*COMP 1350 — Web Administration, Week 3*

In this lab you will configure IIS to serve a static site on Windows, then build a small Node.js/Express application and keep it running in production using PM2 on your VirtualBox/Vagrant Linux VM.

## Part 1: Configure IIS

*IIS requires Windows. If your primary machine is Windows 10/11, enable IIS as a built-in Windows feature below. If you are on macOS/Linux, use a lab-provided Windows machine or a Windows Server evaluation VM — ask your instructor for access details.*

1. Enable IIS (Windows 10/11): **Control Panel → Programs → Turn Windows features on or off** → check **Internet Information Services** → OK. Windows installs and starts IIS automatically.
2. Confirm it's running by browsing to `http://localhost` — you should see the default IIS welcome page.
3. Open **IIS Manager** (search "IIS" in the Start menu).
4. Create a new site:
   - Right-click **Sites → Add Website**
   - **Site name**: `comp1350-site`
   - **Physical path**: `C:\inetpub\comp1350-site` (create the folder first)
   - **Port**: `8081` (to avoid colliding with the Default Web Site on 80)
5. Add `index.html` to `C:\inetpub\comp1350-site`:

```html
<!DOCTYPE html>
<html>
<head><title>COMP1350 IIS Lab</title></head>
<body><h1>Served by IIS</h1></body>
</html>
```

6. Browse to `http://localhost:8081` and confirm your page loads.
7. In IIS Manager, explore **Application Pools** — note that each site runs inside an isolated application pool (process boundary), similar in spirit to how PM2 will isolate our Node app later in this lab.

## Part 2: Build a Minimal Express App

*Do this part on your VirtualBox/Vagrant Linux VM.*

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box, add a `vmware_desktop` provider block instead of the VirtualBox one, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — commands, config — is identical.

1. If you haven't already, provision a VM:

```bash
vagrant init ubuntu/jammy64
vagrant up
vagrant ssh
```

2. Install Node.js and npm:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

3. Create the project:

```bash
mkdir ~/comp1350-app && cd ~/comp1350-app
npm init -y
npm install express
```

4. Create `server.js`:

```js
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello from Express! Running under PM2.');
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Listening on port ${PORT}`));
```

5. Run it directly first, to see the problem PM2 solves:

```bash
node server.js
```

   In another terminal (or via `curl` on the VM), confirm `curl http://localhost:3000` responds. Now press **Ctrl+C** in the first terminal — the app is dead. This is the gap PM2 fills.

## Part 3: Manage the App with PM2

1. Install PM2 globally:

```bash
sudo npm install -g pm2
```

2. Start the app under PM2 instead of running it directly:

```bash
pm2 start server.js --name comp1350-app
pm2 list
```

3. Confirm the app survives even after you close your SSH session and reconnect:

```bash
exit
vagrant ssh
pm2 list
curl http://localhost:3000
```

4. Explore PM2's operational commands:

```bash
pm2 logs comp1350-app --lines 20
pm2 restart comp1350-app
pm2 stop comp1350-app
pm2 start comp1350-app
```

5. Force a crash to see PM2's auto-restart in action. Temporarily add a route that throws:

```js
app.get('/crash', (req, res) => {
  throw new Error('Simulated crash');
});
```

   Restart the app (`pm2 restart comp1350-app`), hit `/crash`, then immediately run `pm2 list` — confirm PM2 restarted the process and the **restart count** incremented.

6. Configure PM2 to survive a VM reboot:

```bash
pm2 startup
# run the exact command PM2 prints (uses sudo)
pm2 save
```

7. Test it: `vagrant reload`, SSH back in, and confirm `pm2 list` shows your app already running without you starting it manually.

## Deliverables

- Screenshot of the IIS site running at `http://localhost:8081`
- Screenshot of `pm2 list` showing `comp1350-app` online, including a nonzero restart count from the crash test
- Your `server.js` file
- One paragraph: in your own words, what is the difference between what IIS does for your static site and what PM2 does for your Node app? Where do their responsibilities overlap, and where do they differ?
