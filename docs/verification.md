# Verification — Linux 2

This is a set of **read-only checks and controlled lab tests** based on the course notes, not the teacher's original grading script. Do not run destructive commands on unrelated systems.

## Baseline

```bash
free -h
nproc
lsblk -f
swapon --show
getenforce
```

Check the VM meets the lab's memory, CPU, filesystem, swap and SELinux requirements as applicable.

## SSH and network security

```bash
sudo sshd -t
sudo sshd -T | grep '^port '
sudo ss -lntp | grep 4444
sudo semanage port -l | grep ssh_port_t
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --zone=public --query-port=4444/tcp
```

On the lab VM, verify that the SSH daemon actually listens on 4444, SELinux permits it and the relevant firewall zone allows it. A configured port does not itself prove external reachability.

Perform an authorized SSH connectivity test in a separate session before closing your original shell.

## Cron

```bash
sudo systemctl is-active cron
sudo -u db crontab -l
ls -l /home/db/date.txt
cat /home/db/date.txt
```

Verify the scheduled line exists and the date file changes after the next five-minute interval.

## G: key-based transfer and checksums

The source file for the exercise was `/home/db/2814.txt.utf-8`.

```bash
sudo -u backup ssh -p 4444 -i /home/backup/.ssh/id_ed25519 -o BatchMode=yes backup@localhost whoami
sudo /root/backup.sh
sudo md5sum /home/db/2814.txt.utf-8 /home/backup/2814.txt.utf-8
```

Expected SSH output is `backup`. The two checksums should **match each other**. In the original lab's test, the recorded MD5 for the sample was `a03d4e61e3937f391f5d6b8e74083fe9`; a fresh copy obtained from elsewhere may differ.

The grading workflow required removing the **test backup copy**, not the source file, before the G assessment. Do cleanup only in your disposable VM and only after checking the destination.

## auditd

```bash
sudo auditctl -l
cat /etc/passwd > /dev/null
sudo ausearch -k passwd_changes -c cat -i
```

Look for the persistent watch rule, a read event associated with `cat` and the watched path `/etc/passwd`. Reboot and recheck if persistence is being assessed.

## VG: archive and restore

The **public** `scripts/backup_vg.py` is a sanitized adaptation requiring `BACKUP_ARCHIVE_PASSWORD` in its process environment.

After running it in an authorized lab VM:

1. Check that `/root/` contains a new archive named `YYYYMMDD_HH:MM_2814.txt.utf-8`.
2. Check that `/home/backup/` contains the transferred version.
3. Create a disposable restore directory, such as `/root/restore`.
4. Use 7-Zip's `x -t7z` command to extract the archive with the password to the restore directory.
5. Compare `md5sum` of the restored file with the original.
6. Re-run in a **different minute** to check versioning (same-minute files are deliberately rejected).

Example restore command (substitute the actual archive name and enter the password only when prompted):

```bash
sudo mkdir -p /root/restore
sudo 7z x -t7z /home/backup/YYYYMMDD_HH:MM_2814.txt.utf-8 -o/root/restore
sudo md5sum /home/db/2814.txt.utf-8 /root/restore/2814.txt.utf-8
```

### Test-status distinction

The earlier explanatory notes said the final VG archive **without** a `.7z` suffix had not been completely function-tested **at the time of writing**. Therefore this checklist does not claim a verified successful restore of that exact final variant. The lab's overall grade is a separate, later outcome.

## Local helper

Run `bash scripts/verify.sh` for read-only quick inspection of several machine settings. It does not replace manual networking, audit or restore tests and is **not** the official assessment test.
