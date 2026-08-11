---
title: "Lab 11: Centralized Logging"
---

[&larr; Back to course index]({{ '/' | relative_url }})

{% raw %}
# Lab 11: Centralized Logging

*COMP 1350 — Web Administration, Week 12*

In this lab you will forward logs from an application server to a dedicated, central log-collector VM using rsyslog — closing the gap between "logs scattered across many servers" and an actual centralized log server. GA4 instrumentation for your group project (Milestone C) is assigned separately as take-home work; see the note at the end of this lab.

> **Apple Silicon (M1/M2/M3/M4) Mac?** See Lab 1's Apple Silicon Setup section first. Replace `ubuntu/jammy64` below with your arm64 box in both VM definitions, add a `vmware_desktop` provider block to each, and run `vagrant up --provider=vmware_desktop`. Everything else in this lab — commands, config — is identical.

## Prerequisites

- Two Vagrant/VirtualBox VMs: reuse your Week 9/10 load-balanced backend setup if convenient, or provision two fresh Ubuntu VMs — `app-server` and `log-server`

```bash
vagrant init ubuntu/jammy64
vagrant up
```

## Part 1: Set Up the Central Log Server

*On `log-server`:*

1. Install and enable rsyslog (usually pre-installed on Ubuntu; confirm it's running):

```bash
sudo systemctl status rsyslog
```

2. Configure rsyslog to accept remote log messages over UDP and TCP on port 514. Edit `/etc/rsyslog.conf`:

```bash
sudo nano /etc/rsyslog.conf
```

Uncomment (or add) these lines in the `MODULES` and `GLOBAL DIRECTIVES` sections:

```
module(load="imudp")
input(type="imudp" port="514")

module(load="imtcp")
input(type="imtcp" port="514")
```

3. Configure a template that stores incoming logs in per-host files:

```
$template RemoteLogs,"/var/log/remote/%HOSTNAME%/%PROGRAMNAME%.log"
*.* ?RemoteLogs
& stop
```

4. Restart rsyslog and confirm it's listening:

```bash
sudo mkdir -p /var/log/remote
sudo systemctl restart rsyslog
sudo ss -tulnp | grep 514
```

## Part 2: Configure the Application Server to Forward Logs

*On `app-server`:*

1. Confirm the log server's IP (from `log-server`, run `hostname -I`).
2. Edit `/etc/rsyslog.conf` on `app-server` and add a forwarding rule at the end of the file (replace `<LOG-SERVER-IP>`):

```
*.* @@<LOG-SERVER-IP>:514
```

   (`@@` = TCP forwarding; a single `@` would mean UDP — TCP is more reliable and preferred for this lab.)

3. Restart rsyslog:

```bash
sudo systemctl restart rsyslog
```

4. Generate a test log entry:

```bash
logger "Test message from app-server"
```

5. On `log-server`, confirm the message arrived:

```bash
find /var/log/remote -type f
cat /var/log/remote/app-server/*.log
```

## Part 3: Forward Real Application Logs

1. If you still have Nginx or your Node/Express app (Weeks 2–3) running on `app-server`, point its logs at syslog as well. For an Express app using a logger like `morgan`, pipe output through `logger`, or configure your logging library to write to syslog directly. A simple approach for this lab:

```bash
# simulate ongoing app activity being logged
while true; do logger -t comp1350-app "request served: $(date)"; sleep 5; done &
```

2. Confirm on `log-server` that these tagged messages are arriving continuously:

```bash
tail -f /var/log/remote/app-server/comp1350-app.log
```

3. Stop the background loop (`fg` then Ctrl+C, or `kill %1`) once you've confirmed forwarding works.

## Part 4: Basic Search & Analysis

On `log-server`, practice the kind of searching a centralized log server exists to make easy:

```bash
grep "request served" /var/log/remote/app-server/comp1350-app.log | wc -l
grep "$(date +%Y-%m-%d)" /var/log/remote/app-server/comp1350-app.log | tail -20
```

Reflect: if you had 10 app servers instead of 1, would this still be manageable with `grep` alone? What would you reach for next (Logstash/ELK, Grafana Loki, a SaaS log platform)?

## Deliverables

- Screenshot of `/var/log/remote/app-server/` on `log-server`, showing forwarded log files
- Screenshot of a live `tail -f` capturing forwarded application log entries
- Your final `rsyslog.conf` forwarding rule from `app-server`
- One paragraph: what would you need to add to this setup (tooling, not just more `grep`) to make it usable at 10+ servers?

---

## Milestone C Follow-Up: GA4 Instrumentation (Take-Home)

This is graded as part of the group project's **Milestone C**, not as part of this in-class lab:

1. Create a GA4 property for your group project site in the Google Analytics dashboard.
2. Add the `gtag.js` tracking snippet to every page (see lecture slides, Part 2).
3. Instrument at least one custom event (e.g. a signup button, a project link click).
4. In your Milestone C submission, include a screenshot of the GA4 Realtime report showing at least one tracked event from your own testing.
{% endraw %}
