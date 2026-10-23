# Technical notes — Linux 2: Security and Backup Automation

This document describes the openSUSE Linux 2 lab configuration and the reasoning behind it. It distinguishes the **G-level backup** from the **VG-level extension** and explains why SSH, SELinux and the firewall must be configured together.

## Lab environment and objectives

The work builds on an already configured openSUSE Linux server. The relevant system has an SSH daemon, SELinux enforcement, firewalld, system users `db` and `backup`, and the sample file `/home/db/2814.txt.utf-8`.

The main tasks covered:

1. Verify core Linux and service state.
2. Configure SSH on TCP/4444 and permit it through SELinux and firewalld.
3. Schedule a cron job.
4. Prepare a limited backup account and key-based SSH access.
5. Copy a sample file via rsync over SSH (G).
6. Record auditd events when `/etc/passwd` is read.
7. Extend backups with timestamping, compression and encryption (VG).

The course sample file was downloaded from Project Gutenberg for use in the lab. The hash recorded in the lab notes for the tested sample was `a03d4e61e3937f391f5d6b8e74083fe9` (MD5). Hashes are useful for **comparing those two local copies**; MD5 should not be treated as modern collision-resistant proof of authenticity.

## SSH, firewalld and SELinux: three independent controls

Moving SSH from TCP/22 to TCP/4444 requires:

- `sshd` to listen on port 4444.
- SELinux to allow `sshd` to bind that port via `ssh_port_t`.
- firewalld to allow incoming TCP/4444 in the relevant zone.

An SSH service can be active but unreachable if a firewall rule blocks the connection. It can also fail to bind if SELinux rejects the nonstandard port.

The lab used `PasswordAuthentication yes`. This was **coursework behavior**, not general advice to enable password login to exposed production hosts.

See [configs/sshd](../configs/sshd/README.md), [firewalld](../configs/firewalld/README.md) and [SELinux](../configs/selinux/README.md).

## Cron: recurring task execution

The `db` user's crontab contained:

```cron
*/5 * * * * date > /home/db/date.txt
```

The five cron time fields schedule the command every five minutes. The redirection operator `>` overwrites the previous timestamp. The task demonstrates persistence and non-interactive scheduled execution.

## Backup account and SSH keys

The `backup` account has home directory `/home/backup`. Its SSH keypair is stored under `/home/backup/.ssh/` on the lab VM; the public key is authorized for login.

Important permission principles:

- `.ssh` directory: typically mode 700.
- `authorized_keys`: typically mode 600.
- Private key: never publish or check into Git.
- Read access to the source file must exist for the account/transfer process, which was handled by permissions/ACL configuration in the lab.

The lab intentionally used a key without a passphrase for unattended transfer. Such a design requires strict control of access to the private key.

## G-level backup: one rsync command

The original `/root/backup.sh` task required **exactly one rsync command**:

```bash
rsync -avh -e "ssh -p 4444 -i /home/backup/.ssh/id_ed25519" /home/db/2814.txt.utf-8 backup@localhost:/home/backup/
```

What each part means:

| Part | Purpose |
| --- | --- |
| `rsync` | Copy/synchronize files |
| `-a` | Preserve relevant file metadata via archive mode |
| `-v` | Verbose progress |
| `-h` | Human-readable output |
| `-e "ssh ..."` | Use SSH as transport |
| `-p 4444` | Connect to the configured SSH port |
| `-i .../id_ed25519` | Authenticate using the lab's private key |
| `/home/db/2814.txt.utf-8` | Source file |
| `backup@localhost:/home/backup/` | Remote-style destination on the same VM |

This copies the **plaintext source file**. For the G verification, the lab compared MD5 checksums of source and destination and cleared the temporary test copy before the grading test.

## VG-level backup: compress, encrypt, version, transfer

The separate `backup_vg.py` script extended the backup:

```text
source file
    |
    v
timestamp (YYYYMMDD_HH:MM)
    |
    v
check duplicate archive filename
    |
    v
7-Zip compresses and encrypts the content
    |
    v
rsync transfers the archive over SSH/4444
    |
    v
confirmation if both commands succeed
```

The archive filename follows this **lab requirement**:

```text
YYYYMMDD_HH:MM_2814.txt.utf-8
```

Relevant 7-Zip options:

- `a`: create/add to an archive.
- `-t7z`: use 7z archive format.
- `-sae`: do not append a `.7z` extension automatically.
- `-p...`: provide the archive password to 7-Zip.
- `-mhe=on`: encrypt archive headers, including filenames.

Python's `datetime.now().strftime("%Y%m%d_%H:%M")` generates a timestamp. `os.path.exists(archive)` checks whether the same-minute archive already exists. `subprocess.run(..., check=True)` raises an exception when 7-Zip or rsync exits with a nonzero code, so later steps are not incorrectly reported as successful.

The rsync command uses `BatchMode=yes` to prevent an interactive SSH password prompt.

### Public version vs assessed script

The original coursework notes show a **hardcoded demonstration archive password**. The public `scripts/backup_vg.py` replaces that one aspect with an environment variable named `BACKUP_ARCHIVE_PASSWORD`. Its workflow and lab paths otherwise reflect the documented design. **This public script is an adaptation, not a byte-for-byte copy of the submitted VG script.**

7-Zip's `-p` argument may expose the password in process arguments while running. This lab method should not be taken as a production-grade secret-management pattern.

The earlier study notes explicitly recorded that the **final no-extension VG archive variant had not yet been fully function-tested at the time those notes were written**. The documentation does not treat that earlier uncertainty as a verified pass. Final-course grade and the recorded test status are different things.

## auditd: persistent file read monitoring

```text
-w /etc/passwd -p r -k passwd_changes
```

- Watch `/etc/passwd`.
- Generate audit events for **read** access.
- Assign the key `passwd_changes` for later querying.

A drop-in file under `/etc/audit/rules.d/` allows the rule to be loaded using `augenrules --load` and persist after reboot. In the lab, a `never,task` filter needed attention because it could prevent expected events.

The key contains the word “changes,” but the configured permission is **r = read**. This distinction is useful when explaining the rule during a security review.

## Lessons learned

- Reachability depends on service configuration, security policy and network filtering together.
- Automation needs observable success and failure states.
- Passwordless SSH is useful for unattended jobs but makes filesystem permissions on keys particularly important.
- Backups should be tested by restoring them, not merely by checking that files exist.
- Audit rules are only useful when active and verifiably producing the intended events.
- Configuration examples for an isolated assessed VM are **not automatically production hardening recommendations**.

See [reproduction.md](reproduction.md) and [verification.md](verification.md) for specific lab commands.
