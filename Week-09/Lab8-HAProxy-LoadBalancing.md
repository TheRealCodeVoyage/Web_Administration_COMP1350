# Lab 8: Load Balancing with HAProxy

*COMP 1350 — Web Administration, Week 9*

Welcome back from the midterm. In this lab you'll build a real load-balanced setup — one HAProxy VM in front of two backend web servers — test multiple balancing algorithms, and then compare HAProxy directly against Nginx's built-in `upstream` module doing the same job.

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box in **all three** VM definitions, add a `vmware_desktop` provider block to each instead of relying on VirtualBox, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — IPs, commands, config files — is identical.

## Part 1: Provision Three VMs

```bash
mkdir ~/comp1350-lab8 && cd ~/comp1350-lab8
vagrant init
```

Replace the `Vagrantfile`:

```ruby
Vagrant.configure("2") do |config|
  config.vm.define "backend1" do |b1|
    b1.vm.box = "ubuntu/jammy64"
    b1.vm.hostname = "backend1"
    b1.vm.network "private_network", ip: "192.168.56.21"
  end

  config.vm.define "backend2" do |b2|
    b2.vm.box = "ubuntu/jammy64"
    b2.vm.hostname = "backend2"
    b2.vm.network "private_network", ip: "192.168.56.22"
  end

  config.vm.define "lb" do |lb|
    lb.vm.box = "ubuntu/jammy64"
    lb.vm.hostname = "lb"
    lb.vm.network "private_network", ip: "192.168.56.20"
  end
end
```

```bash
vagrant up
```

## Part 2: Set Up the Backend Servers

*On both `backend1` and `backend2` (`vagrant ssh backend1`, then repeat on `backend2`):*

```bash
sudo apt update
sudo apt install nginx -y
```

Make each backend identify itself so you can see load balancing actually working:

```bash
# on backend1:
echo "Hello from backend1 (192.168.56.21)" | sudo tee /var/www/html/index.html

# on backend2:
echo "Hello from backend2 (192.168.56.22)" | sudo tee /var/www/html/index.html
```

Confirm each responds directly:

```bash
curl http://192.168.56.21
curl http://192.168.56.22
```

## Part 3: Install and Configure HAProxy

*On `lb`:*

```bash
sudo apt update
sudo apt install haproxy -y
sudo nano /etc/haproxy/haproxy.cfg
```

Add to the end of the file:

```haproxy
frontend http_front
    bind *:80
    stats uri /haproxy?stats
    default_backend app_servers

backend app_servers
    balance roundrobin
    server backend1 192.168.56.21:80 check
    server backend2 192.168.56.22:80 check
```

Restart HAProxy:

```bash
sudo systemctl restart haproxy
```

## Part 4: Test Round Robin

From your host machine (or from `lb` itself), hit the load balancer repeatedly:

```bash
for i in {1..6}; do curl http://192.168.56.20; done
```

You should see the response alternate between `backend1` and `backend2`.

## Part 5: Test Least Connections and Weighted Round Robin

1. Change `balance roundrobin` to `balance leastconn`, restart HAProxy, and re-test:

```bash
sudo systemctl restart haproxy
```

2. Now try weighting the servers unevenly — `backend1` should receive roughly twice the traffic of `backend2`:

```haproxy
backend app_servers
    balance roundrobin
    server backend1 192.168.56.21:80 check weight 2
    server backend2 192.168.56.22:80 check weight 1
```

3. Restart and run the loop from Part 4 with a higher count (`{1..20}`) to see the 2:1 pattern emerge.

## Part 6: Health Checks

1. Simulate a backend failure:

```bash
vagrant ssh backend2 -c "sudo systemctl stop nginx"
```

2. Open `http://192.168.56.20/haproxy?stats` in your host browser. Confirm `backend2` shows as **DOWN** and that all traffic now goes to `backend1` only.

3. Bring `backend2` back and confirm it returns to **UP**:

```bash
vagrant ssh backend2 -c "sudo systemctl start nginx"
```

## Part 7: Nginx as a Load Balancer — the Alternative

*Provision a fourth VM, or repurpose one you're not using, to compare Nginx's `upstream` module doing the identical job.*

```bash
vagrant ssh lb
sudo apt install nginx -y
sudo systemctl stop haproxy
```

```bash
sudo nano /etc/nginx/sites-available/lb
```

```nginx
upstream backend_servers {
    least_conn;
    server 192.168.56.21;
    server 192.168.56.22;
}

server {
    listen 8080;
    location / {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/lb /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Test it the same way as Part 4, against port 8080:

```bash
for i in {1..6}; do curl http://192.168.56.20:8080; done
```

**Q1**: HAProxy has a dedicated stats page built in. What would you need to add to get equivalent visibility (which backend is healthy, current connection counts) out of the Nginx setup?

## Deliverables

- Screenshot of the round-robin test alternating between both backends
- Screenshot of the HAProxy stats page (`/haproxy?stats`) showing one backend marked DOWN during the health-check test
- Your final `haproxy.cfg` `backend` block with weights configured
- Output of the Nginx `upstream` test from Part 7
- Your written answer to Q1
