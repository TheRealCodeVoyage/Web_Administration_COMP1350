# Lab 1: Development VM Setup with VirtualBox & Vagrant

*COMP 1350 — Web Administration, Week 1*

Every lab this term happens inside a disposable Linux VM you can rebuild in minutes. In this lab you'll install VirtualBox and Vagrant, provision your first VM, and learn the reset workflow you'll rely on for the rest of the course.

## Part 1: Install VirtualBox

1. Download VirtualBox for your OS from [virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads) and run the installer, accepting the defaults.
2. On Windows, if prompted, also enable **Hyper-V** exclusion or install the **VirtualBox Extension Pack** if you plan to use USB passthrough later (not required for this course).
3. **Apple Silicon Mac (M1/M2/M3/M4):** make sure you install **version 7.1 or later** — that's the first line to officially support Apple Silicon as both host and guest. If you already have an older VirtualBox installed, uninstall it first and grab the current release from the link above.
4. Verify the install:

```bash
VBoxManage --version
```

## Part 2: Install Vagrant

1. Download Vagrant for your OS from [vagrantup.com/downloads](https://www.vagrantup.com/downloads) and run the installer.
2. Verify the install:

```bash
vagrant --version
```

3. Vagrant needs a "provider" to actually run VMs — that's VirtualBox, which you just installed. Confirm Vagrant can see it:

```bash
vagrant plugin list
```

## Part 3: Provision Your First VM

1. Create a directory for this lab and initialize a Vagrant project:

```bash
mkdir ~/comp1350-lab1 && cd ~/comp1350-lab1
vagrant init bento/ubuntu-22.04
```

   This creates a `Vagrantfile` — the configuration file that describes your VM (base image, RAM, CPUs, networking, shared folders). We use the `bento/ubuntu-22.04` box (rather than Canonical's own `ubuntu/jammy64`) because it publishes both an `amd64` build (Intel/AMD machines — Windows, Linux, Intel Macs) and an `arm64` build (Apple Silicon Macs) for the VirtualBox provider. Vagrant automatically detects your machine's CPU architecture and downloads the matching one — everyone in this course runs the exact same command and gets a working VM, regardless of what laptop they're on.

2. Open the `Vagrantfile` and set a private network IP so you can reach the VM at a fixed address all term. Find the commented-out line for `config.vm.network "private_network"` and uncomment it with a static IP:

```ruby
config.vm.network "private_network", ip: "192.168.56.10"
```

3. While you're in there, bump the VM's resources for the heavier labs later this term (reverse proxy, load balancing):

```ruby
config.vm.provider "virtualbox" do |vb|
  vb.memory = "2048"
  vb.cpus = 2
end
```

4. Bring the VM up:

```bash
vagrant up
```

   The first run downloads the `bento/ubuntu-22.04` base box (a few hundred MB) — this only happens once; future `vagrant up` calls reuse the cached box.

5. SSH into your new VM:

```bash
vagrant ssh
```

6. Confirm you're inside a real, isolated Ubuntu system:

```bash
lsb_release -a
hostname
ip addr show
```

7. Update the package index and confirm internet access from inside the VM:

```bash
sudo apt update
```

## Part 4: The Reset Workflow

This is the single most useful Vagrant habit for this course — being able to throw away a broken VM and start clean in under two minutes.

1. Exit the VM and check its status:

```bash
exit
vagrant status
```

2. Suspend it (fast, preserves RAM state — good for a lunch break):

```bash
vagrant suspend
vagrant resume
```

3. Halt it (clean shutdown, like powering off a real machine):

```bash
vagrant halt
vagrant up
```

4. Destroy and rebuild it from scratch (use this whenever a lab goes sideways and you'd rather start over than debug someone else's broken state):

```bash
vagrant destroy -f
vagrant up
```

5. Confirm your custom IP survived the rebuild:

```bash
vagrant ssh -c "ip addr show | grep 192.168.56.10"
```

## Part 5: Shared Folders (Editing Files from Your Host)

1. By default, Vagrant syncs your project directory (`~/comp1350-lab1` on your host) to `/vagrant` inside the VM. Confirm this:

```bash
vagrant ssh -c "ls /vagrant"
```

2. Create a file on your host machine in that folder using your normal text editor, then confirm it appears inside the VM without any extra steps:

```bash
vagrant ssh -c "cat /vagrant/hello.txt"
```

   This is how you'll edit code all term: files in your host editor, commands run inside the VM via `vagrant ssh`.

## Deliverables

- Output of `vagrant status` showing the VM `running`
- Output of `ip addr show` from inside the VM, showing your static `192.168.56.10` address
- Screenshot of a file created on your host machine appearing inside the VM via the shared `/vagrant` folder
- One paragraph: why is `vagrant destroy && vagrant up` a safer habit than trying to manually fix a broken VM, especially under a lab time limit?
