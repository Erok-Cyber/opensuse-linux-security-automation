# Reproduce the Linux 2 lab in an isolated openSUSE VM

The commands below document the educational configuration used in the assignment. They are **not** a deployment recipe for public production servers. Run them only on a disposable VM you control, and adjust them to the installed version and services.

## Prerequisites

- An openSUSE VM with a working shell and sudo/root access
- `sshd`, SELinux, firewalld, auditd and cron available
- `db` user and the lab's source file
- `rsync`, `7z`, Python 3 and SSH client tools as needed

The lab's existing SSH configuration and baseline setup were established in Linux 1. See the companion [Linux 1 repo](https://github.com/Erok-Cyber/linux-1-server-configuration) for that configuration.

## 1. Verify the VM baseline

```bash
free -h
nproc
lsblk -f
getenforce
sudo systemctl is-active sshd
sudo firewall-cmd --get-default-zone
```

These inspect RAM, CPU, filesystem layout, SELinux mode, SSH service and firewall zone. They do not change the system.

## 2. SSH on 4444

Review the examples in [configs/sshd](../configs/sshd/README.md) and install the relevant drop-in configuration in the VM's `/etc/ssh/sshd_config.d/` directory, respecting the system's existing precedence rules.

Check syntax and effective settings before restarting the service:

```bash
sudo sshd -t
sudo sshd -T | grep -E '^(port|passwordauthentication|kbdinteractiveauthentication) '
```

**Do not disconnect an active remote shell before verifying a new connection works.** Modifying SSH settings may lock you out.

## 3. SELinux and firewall authorization

Review whether port 4444 already has an SELinux mapping:

```bash
sudo semanage port -l | grep ssh_port_t
```

If it is not already assigned and the VM requires the mapping, the lab used:

```bash
sudo semanage port -a -t ssh_port_t -p tcp 4444
```

Then permit the matching firewall port in the public zone used by the assignment:

```bash
sudo firewall-cmd --permanent --zone=public --add-port=4444/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --query-port=4444/tcp
```

Restart SSH only after the configuration is valid and the required permission layers are ready. Verify connectivity with `ssh -p 4444 ...` using an account for which login is allowed.

## 4. Cron schedule

Install the line from [configs/cron/db.crontab](../configs/cron/db.crontab) in the **db** user's crontab:

```cron
*/5 * * * * date > /home/db/date.txt
```

```bash
sudo systemctl enable --now cron
sudo -u db crontab -l
```

After the next scheduled run, inspect `/home/db/date.txt` to verify it was written and updated.

## 5. Sample source and backup account

The course source file was stored as `/home/db/2814.txt.utf-8`, obtained from Project Gutenberg during the lab. If re-creating the same environment, use the course-approved sample and verify its contents rather than assuming a later download has an identical checksum.

The lab created a `backup` user with home `/home/backup` and prepared a key pair for unattended login to `backup@localhost` over TCP/4444.

```bash
sudo useradd -m -d /home/backup -s /bin/bash backup
sudo -u backup mkdir -p /home/backup/.ssh
sudo chmod 700 /home/backup/.ssh
sudo -u backup ssh-keygen -t ed25519 -f /home/backup/.ssh/id_ed25519 -N ""
sudo -u backup cp /home/backup/.ssh/id_ed25519.pub /home/backup/.ssh/authorized_keys
sudo chmod 600 /home/backup/.ssh/authorized_keys
```

The `useradd` command applies only if the account does not already exist. The lab used a **passphrase-free key** for unattended automation; do not use that pattern indiscriminately on exposed systems. Protect key permissions and never commit the private key.

The source's access permissions/ACLs must also permit the intended backup operation, as in the original lab setup.

## 6. G backup: one-line rsync script

The [scripts/backup.sh](../scripts/backup.sh) file contains the lab's exact single rsync command. The assessed installation path was `/root/backup.sh`.

```bash
sudo cp scripts/backup.sh /root/backup.sh
sudo chmod u+x /root/backup.sh
sudo /root/backup.sh
```

The source and copied destination should then have matching checksums. See [verification.md](verification.md).

## 7. auditd rule

The persistent rule is in [configs/auditd/50-passwd.rules](../configs/auditd/50-passwd.rules):

```bash
sudo cp configs/auditd/50-passwd.rules /etc/audit/rules.d/50-passwd.rules
sudo augenrules --load
sudo auditctl -l
cat /etc/passwd > /dev/null
sudo ausearch -k passwd_changes -c cat -i
```

The original lab also addressed a `never,task` filter that could suppress events. Inspect existing audit policies before altering them.

## 8. VG backup: sanitized public adaptation

Unlike the assessed original, the published [scripts/backup_vg.py](../scripts/backup_vg.py) **does not hardcode the exercise password**. It expects `BACKUP_ARCHIVE_PASSWORD` in its environment.

On the isolated VM, supply a disposable archive password to the privileged process without saving it in this repository; then run:

```bash
sudo python3 scripts/backup_vg.py
```

Note that `sudo` may remove environment variables. Ensure `BACKUP_ARCHIVE_PASSWORD` is supplied in the environment of the final **root** Python process, not merely in an unrelated user shell. Do not paste real credentials into your shell history.

This script's use of `7z -p` can expose the supplied password to privileged process inspection during execution. It is included to document the school exercise, **not** as a recommended production encryption mechanism.

Check that the generated archive appears in `/root/` and is transferred into `/home/backup/`. Restore a test copy into an isolated directory and compare it with the original source. Never restore untrusted archives over valuable files.

## Important boundaries

- Sample system paths and the SSH port come from this coursework VM; they are not universal defaults.
- Never copy private keys, archives, real passwords or the grading tool into Git.
- Reproduction commands are for the lab; the accompanying docs explain their purpose and verification.
- The earlier course notes marked the final no-extension archive variant as not yet completely tested at that point; do not describe that earlier check as verified.
