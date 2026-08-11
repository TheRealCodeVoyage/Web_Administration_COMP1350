---
title: "Lab 2: Apache & Nginx Side-by-Side"
---

[&larr; Back to course index]({{ '/' | relative_url }})

{% raw %}
# Lab 2: Apache & Nginx Side-by-Side

*COMP 1350 — Web Administration, Week 2*

In this lab you'll install Apache and Nginx on separate Vagrant VMs, configure a virtual host on each, and directly compare how the two handle the same job — reinforcing this week's "same job, different architecture" theme.

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box, add a `vmware_desktop` provider block instead of the VirtualBox one, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — IPs, commands, config files — is identical.

## Part 1: Provision Two VMs

1. From a new lab directory, create a `Vagrantfile` that defines two VMs at once:

```bash
mkdir ~/comp1350-lab2 && cd ~/comp1350-lab2
vagrant init
```

2. Replace the `Vagrantfile` contents with:

```ruby
Vagrant.configure("2") do |config|
  config.vm.define "apache-server" do |apache|
    apache.vm.box = "ubuntu/jammy64"
    apache.vm.hostname = "apache-server"
    apache.vm.network "private_network", ip: "192.168.56.11"
  end

  config.vm.define "nginx-server" do |nginx|
    nginx.vm.box = "ubuntu/jammy64"
    nginx.vm.hostname = "nginx-server"
    nginx.vm.network "private_network", ip: "192.168.56.12"
  end
end
```

3. Bring both VMs up:

```bash
vagrant up
```

## Part 2: Apache Web Server

*SSH into `apache-server`: `vagrant ssh apache-server`*

1. Update packages and install Apache:

```bash
sudo apt update
sudo apt install apache2 -y
```

2. Confirm it's running:

```bash
sudo systemctl status apache2
```

3. From your host machine, browse to `http://192.168.56.11` — you should see the default Apache welcome page.

4. Replace the default page with a custom one:

```bash
sudo rm /var/www/html/index.html
echo "<h1>Served by Apache</h1>" | sudo tee /var/www/html/index.html
```

5. Set up a named virtual host. Create a site directory and page:

```bash
sudo mkdir /var/www/mysite
echo "<h1>My Site on Apache</h1>" | sudo tee /var/www/mysite/index.html
```

6. Create the virtual host config:

```bash
sudo nano /etc/apache2/sites-available/mysite.conf
```

```apache
<VirtualHost *:80>
    ServerName mysite.local
    DocumentRoot /var/www/mysite
    ErrorLog ${APACHE_LOG_DIR}/mysite-error.log
    CustomLog ${APACHE_LOG_DIR}/mysite-access.log combined
</VirtualHost>
```

7. Enable the site and reload:

```bash
sudo a2ensite mysite.conf
sudo apachectl configtest
sudo systemctl reload apache2
```

8. On your **host machine**, add a hosts-file entry mapping `mysite.local` to `192.168.56.11`, then browse to `http://mysite.local` and confirm you see "My Site on Apache".
   - Windows: `C:\Windows\System32\drivers\etc\hosts`
   - macOS/Linux: `/etc/hosts`

9. Enable a module (`mod_rewrite`) and note that Apache requires a restart to load new modules:

```bash
sudo a2enmod rewrite
sudo systemctl restart apache2
```

## Part 3: Nginx Web Server

*SSH into `nginx-server`: `vagrant ssh nginx-server`*

1. Update packages and install Nginx:

```bash
sudo apt update
sudo apt install nginx -y
```

2. Confirm it's running:

```bash
sudo systemctl status nginx
```

3. From your host machine, browse to `http://192.168.56.12` — you should see the default Nginx welcome page.

4. Create a virtual host (Nginx calls these "server blocks"):

```bash
sudo mkdir -p /var/www/mysite
echo "<h1>My Site on Nginx</h1>" | sudo tee /var/www/mysite/index.html
```

```bash
sudo nano /etc/nginx/sites-available/mysite
```

```nginx
server {
    listen 80;
    server_name mysite.local;
    root /var/www/mysite;
    index index.html;
}
```

5. Enable the site with a symlink, test the config, and reload:

```bash
sudo ln -s /etc/nginx/sites-available/mysite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

6. On your host machine, point `mysite.local` at `192.168.56.12` instead (edit the hosts file entry from Part 2), and confirm you see "My Site on Nginx".

7. Enable gzip compression — a good example of Nginx's directive-driven config style:

```bash
sudo nano /etc/nginx/nginx.conf
```

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Part 4: Side-by-Side Comparison

Fill in this table from your own observations across Parts 2–3:

| Aspect | Apache | Nginx |
|---|---|---|
| Config file format | ? | ? |
| Enabling a new site | `a2ensite` + reload | symlink into `sites-enabled` + reload |
| Enabling a module | `a2enmod` + **restart** | built into the binary, no separate enable step |
| Config syntax check command | `apachectl configtest` | `nginx -t` |
| Process model (check with `ps aux \| grep`) | ? | ? |

Use `ps aux | grep apache2` on `apache-server` and `ps aux | grep nginx` on `nginx-server` to fill in the process-model row — count how many processes each shows and note what you observe.

## Deliverables

- Screenshots of both custom virtual hosts loading correctly by domain name (`mysite.local` resolving to each server in turn)
- Your completed comparison table from Part 4
- The `mysite.conf` (Apache) and `mysite` (Nginx) virtual host files
- One paragraph: based on the process-model difference you observed, which architecture do you think would use less memory under heavy concurrent load, and why?
{% endraw %}
