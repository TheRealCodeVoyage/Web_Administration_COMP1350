# Lab 9: Eliminating Single Points of Failure

*COMP 1350 — Web Administration, Week 10*

Last week you built a load-balanced setup — but look closely and it still has single points of failure. In this lab you'll map every SPOF in your Lab 8 architecture, then redesign and rebuild it so the load balancer itself is no longer the weak link.

> **Apple Silicon (M1/M2/M3/M4) Mac?** If you used the VMware Fusion / arm64 path for Lab 8, keep using it here — add `lb2` in Part 3 with the same arm64 box and `vmware_desktop` provider block as your other VMs, and use `vagrant up lb2 --provider=vmware_desktop`.

## Part 1: Audit Your Current Architecture

1. Reopen your Lab 8 project directory and bring the VMs back up if needed:

```bash
cd ~/comp1350-lab8
vagrant up
```

2. Draw (on paper, in a slide, or in any diagramming tool) your current architecture from Lab 8: client → `lb` (HAProxy) → `backend1` / `backend2`.

3. For each component, mark whether it is a SPOF (single point of failure) and why:

| Component | Is it a SPOF? | Why / Why not |
|---|---|---|
| `backend1` or `backend2` alone | No | Load balancer routes around a failed one (you proved this in Lab 8, Part 6) |
| The `lb` VM (HAProxy) itself | ? | ? |
| Your host machine's network connection | ? | ? |

**Q1**: Complete the table. Pay particular attention to the `lb` row — you removed the backend-server SPOF last week, but did you introduce a new one?

## Part 2: Prove the Load Balancer Is a SPOF

1. Simulate the load balancer itself failing:

```bash
vagrant ssh lb -c "sudo systemctl stop haproxy"
```

2. Try to reach your site:

```bash
curl http://192.168.56.20
```

3. Confirm the whole system is down, even though both backends are perfectly healthy:

```bash
curl http://192.168.56.21
curl http://192.168.56.22
```

**Q2**: Both backends are up, yet the site is unreachable. In one sentence, explain why removing the app-server SPOF in Lab 8 didn't actually remove *all* single points of failure from the system.

4. Restart HAProxy before continuing:

```bash
vagrant ssh lb -c "sudo systemctl start haproxy"
```

## Part 3: Add a Second Load Balancer

1. Add a second HAProxy VM to your `Vagrantfile`:

```ruby
config.vm.define "lb2" do |lb2|
  lb2.vm.box = "ubuntu/jammy64"
  lb2.vm.hostname = "lb2"
  lb2.vm.network "private_network", ip: "192.168.56.23"
end
```

```bash
vagrant up lb2
```

2. Copy the identical HAProxy configuration from `lb` onto `lb2`:

```bash
vagrant ssh lb2
sudo apt update && sudo apt install haproxy -y
sudo nano /etc/haproxy/haproxy.cfg
```

   Use the same `frontend`/`backend` block from Lab 8, Part 3, pointing at the same two backends.

```bash
sudo systemctl restart haproxy
```

3. Confirm `lb2` independently load-balances across both backends:

```bash
for i in {1..6}; do curl http://192.168.56.23; done
```

**Reflection**: You now have two load balancers, each capable of serving all traffic. But clients still need *one* address to connect to — having two independent load balancer IPs doesn't automatically give you failover. This is the detection-and-switchover problem from this week's lecture.

## Part 4: Detection and Switchover (Conceptual Design)

*A full floating-IP/VRRP (keepalived) setup is beyond this lab's scope, but understanding the mechanism is the actual learning goal here.*

1. Research **keepalived** and the **VRRP** protocol (Virtual Router Redundancy Protocol) — this is the standard way to give two Linux load balancers a single shared "virtual IP" that automatically moves to the surviving node if one fails.
2. Sketch (diagram or written description) how this would slot into your two-load-balancer setup from Part 3: where would the virtual IP live, and what would trigger the switch from `lb` to `lb2`?

**Q3**: In your own words, why is *detection* (noticing `lb` died) just as important as *redundancy* (having `lb2` ready to go)? What specifically would go wrong if you had `lb2` running but no mechanism to detect `lb`'s failure and redirect traffic?

## Part 5: Redesign Diagram

Produce a final "after" diagram of your redundant architecture:

```
Client → [Virtual IP, handled by keepalived] → lb (active) or lb2 (standby)
                                                    ↓
                                    backend1  /  backend2
```

Compare this explicitly against your Lab 8 "before" diagram from Part 1.

## Deliverables

- Your completed SPOF audit table from Part 1
- Screenshot proving the site went down when `lb` alone was stopped (Part 2)
- Screenshot of `lb2` independently load-balancing across both backends (Part 3)
- Your written answers to Q1, Q2, and Q3
- Your "before" (Lab 8) and "after" (this lab) architecture diagrams
- **Connect this explicitly to Milestone C** of your group project, which requires a redundant, load-balanced deployment — this lab is the design thinking behind that requirement
