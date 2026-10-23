# Linux 2 – Security & Backup Automation

Hands-on openSUSE security coursework from my IT Security Analyst education. **Final grade: VG.**

## What I implemented
- SSH on port 4444 with tested password and key-based authentication
- firewalld rules and SELinux SSH port labeling
- Persistent auditd monitoring of `/etc/passwd`
- Cron scheduling and verification
- Backup user, SSH key authentication, ACLs and rsync transfer
- Python backup automation using timestamped archives, 7-Zip compression and encryption, and rsync over SSH

## Backup workflow
1. Generate a timestamp and archive filename.
2. Stop if an archive with the same name exists.
3. Use `subprocess.run(..., check=True)` to run 7-Zip, compress and encrypt the source.
4. Transfer the archive with rsync over SSH on port 4444.
5. Print success only after the commands complete.

## Verification
SSH connectivity, firewalld, SELinux, auditd, cron and backup transfers were tested during the assignment.

## Security
The original exercise used a demonstration password embedded in the backup script. It must be replaced with a placeholder or securely supplied secret before any public code is uploaded. Do not publish private keys, credentials, archives or assessment scripts.

## Tools
openSUSE · Linux · SSH · SELinux · firewalld · auditd · cron · rsync · 7-Zip · Python · Bash

*This repository documents the completed educational lab. The original graded solution is not modified.*
