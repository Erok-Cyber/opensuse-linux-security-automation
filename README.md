# Linux 2 – openSUSE Security & Backup Automation

A hands-on Linux administration and security lab completed as part of the **IT Security Analyst** program at Medieinstitutet.

Building on my [Linux 1 server configuration project](https://github.com/Erok-Cyber/linux-1-server-configuration), this assignment focused on **SSH access, access controls, firewalld, SELinux, scheduled tasks, audit logging, secure transfer and backup automation**.

**Final course grade: VG.**

> This repository documents the completed educational lab and its configuration. It contains the G-level rsync command and a **security-sanitized public adaptation** of the VG backup script. The original assessed scripts are not silently represented as production-ready code.

## What I configured

- An openSUSE Linux VM with the existing Linux 1 server baseline
- SSH service on **TCP/4444**, with connectivity and authentication tests
- SELinux in **Enforcing** mode with TCP/4444 associated with `ssh_port_t`
- firewalld rule opening TCP/4444 in the `public` zone
- Cron job writing the current date to `/home/db/date.txt` every five minutes
- Backup user `backup` with home directory `/home/backup`
- Ed25519 public-key authentication for non-interactive SSH access
- File permissions/ACLs allowing the intended backup workflow
- **G-level:** a one-command rsync backup over SSH
- **VG-level:** Python-driven compression, encryption, timestamping and rsync transfer
- Persistent auditd file-read monitoring of `/etc/passwd`
- Manual verification through service checks, logs, transfer tests and checksum comparisons

## Repository structure

```text
opensuse-linux-security-automation/
├── .gitignore
├── README.md
├── docs/
│   ├── notes.md
│   ├── reproduction.md
│   └── verification.md
├── configs/
│   ├── sshd/
│   │   ├── README.md
│   │   ├── port.conf
│   │   └── auth-policy.conf
│   ├── firewalld/
│   │   └── README.md
│   ├── selinux/
│   │   └── README.md
│   ├── auditd/
│   │   ├── README.md
│   │   └── 50-passwd.rules
│   └── cron/
│       ├── README.md
│       └── db.crontab
└── scripts/
    ├── backup.sh
    ├── backup_vg.py
    └── verify.sh
```

## Documentation

- [Technical notes](docs/notes.md) — project goals, SSH/firewall/SELinux layers, cron, auditd, G vs VG backups and lessons learned
- [Reproduction guide](docs/reproduction.md) — annotated lab setup and commands for an isolated openSUSE VM
- [Verification guide](docs/verification.md) — checks for connectivity, cron, audit logging, backup integrity and restoration
- [SSH configuration](configs/sshd/README.md) — listener and authentication settings
- [firewalld](configs/firewalld/README.md) — persistent TCP/4444 rule
- [SELinux](configs/selinux/README.md) — SSH port labeling with `semanage`
- [auditd](configs/auditd/README.md) — persistent file-watch rule
- [cron](configs/cron/README.md) — scheduling as the `db` user

## System and tools

| Item | Lab setup |
| --- | --- |
| OS | openSUSE Linux (building on Linux 1) |
| SSH | TCP/4444 |
| Firewall | firewalld, `public` zone |
| Access control | SELinux Enforcing; standard Unix permissions / ACLs |
| Backup source | `/home/db/2814.txt.utf-8` |
| Backup user/destination | `backup@localhost:/home/backup/` |
| Authentication | Ed25519 SSH key for the automated transfer |
| Audit log | auditd rule watching read access to `/etc/passwd` |
| Scheduler | Cron every five minutes |
| Automation tools | Bash, Python 3, rsync, 7-Zip |

The `2814.txt.utf-8` source was a course sample downloaded from Project Gutenberg. It is intentionally **not mirrored** in this repository.

## SSH on 4444 — three security layers

A nonstandard SSH port needs more than changing `sshd_config`.

1. **OpenSSH / sshd** listens on port 4444.
2. **SELinux** permits `sshd` to use TCP/4444 under `ssh_port_t`.
3. **firewalld** allows inbound TCP/4444 in the appropriate zone.

Example read-only checks:

```bash
sudo sshd -T | grep '^port '
getenforce
sudo semanage port -l | grep ssh_port_t
sudo firewall-cmd --zone=public --query-port=4444/tcp
```

The coursework used `PasswordAuthentication yes`; this reproduces the educational lab requirements and is **not** recommended as a default security policy for exposed production systems.

## Scheduled tasks — cron

The `db` user runs:

```cron
*/5 * * * * date > /home/db/date.txt
```

This runs every fifth minute and replaces the file's previous timestamp. Verify it through `crontab -l` and the changing file contents.

## Backup automation — G and VG

### G: rsync over SSH

The original G-level file `/root/backup.sh` contained **one rsync command**:

```bash
rsync -avh -e "ssh -p 4444 -i /home/backup/.ssh/id_ed25519" /home/db/2814.txt.utf-8 backup@localhost:/home/backup/
```

The file in [scripts/backup.sh](scripts/backup.sh) records the command. It uses the `backup` user's private SSH key on the lab VM to transfer the source file to the backup directory without an interactive password prompt.

The original file and transferred copy can be compared with `md5sum` to verify equality for this exercise.

### VG: Python, encryption and versioned archives

The VG part added **compression, encryption and versioning** to the existing backup workflow.

```text
/home/db/2814.txt.utf-8
         |
         v
Python generates timestamp and filename
         |
         v
Check if that archive already exists
         |
         v
7-Zip compresses and encrypts the source
         |
         v
rsync transfers archive using SSH/4444
         |
         v
Confirm completion (or stop on command error)
```

The required archive name was:

```text
YYYYMMDD_HH:MM_2814.txt.utf-8
```

The script uses:

- `datetime.now().strftime()` for version timestamps.
- `os.path.exists()` to stop if a same-minute archive already exists.
- `7z a -t7z -sae -p... -mhe=on` for creation, compression and encryption including archive headers.
- `rsync -avh -e "ssh -p 4444 ... -o BatchMode=yes"` for transfer.
- `subprocess.run(..., check=True)` to stop on external-command failure.

**Important public-code difference:** The original educational VG script used a hardcoded demonstration password. [scripts/backup_vg.py](scripts/backup_vg.py) preserves the documented workflow but reads the password from `BACKUP_ARCHIVE_PASSWORD` instead. It is explicitly a **sanitized portfolio adaptation**, not the original exact submission. The 7-Zip `-p` argument can still reveal the secret in process arguments; this is not a production-grade secret-handling design.

The earlier course notes indicated that the final extensionless-archive variant had not yet been completely tested at the time of writing. Accordingly, this repo does **not** claim a verified restore of that exact variant based solely on those notes.

## Persistent audit logging

The audited file was `/etc/passwd`. The drop-in file is:

```text
/etc/audit/rules.d/50-passwd.rules
```

Contents:

```text
-w /etc/passwd -p r -k passwd_changes
```

- `-w` watches a path.
- `-p r` captures **reads**.
- `-k` assigns a searchable key.

The rule was activated using `augenrules --load` and checked with `auditctl -l` and `ausearch -k passwd_changes`. The key name suggests changes, but the permission is specifically **read**.

## Verification

The lab covers several independently testable components:

| Area | How to verify |
| --- | --- |
| SSH | `sshd -t`, `ss -lnt`, new SSH connection on 4444 |
| Firewall | `firewall-cmd --query-port=4444/tcp` |
| SELinux | `getenforce`, `semanage port -l` |
| Cron | `crontab -l`, inspect the periodically updated date file |
| Backup login | SSH with private key and `BatchMode=yes` |
| G backup | Compare the source/destination checksums |
| Audit logging | Read `/etc/passwd`, inspect `ausearch` output |
| VG backup | Inspect encrypted archive, restore in a test directory, compare checksums |

A **read-only quick-inspection helper** is available:

```bash
bash scripts/verify.sh
```

It does not replace the manual checks, prove successful restoration or run the official assessment tests. Details are in [docs/verification.md](docs/verification.md).

## Key takeaways

This project reinforced how multiple security layers work together: service configuration controls listening ports, SELinux constrains service behavior, firewalld filters connections and auditd provides evidence of file access. It also shows how scripts can automate routine transfers and why backup correctness should be checked through **restoration and comparison**, not just successful copy messages.

## Security and publication notes

The repository intentionally excludes:

- Private SSH keys and the contents of `authorized_keys`
- Real passwords and credentials
- Backup archives and restored data
- VM images and original assessment scripts
- Other machine-specific secrets

All instructions are for an isolated coursework VM. They do not constitute a hardened production backup design.
