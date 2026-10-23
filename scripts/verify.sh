#!/usr/bin/env bash
# Read-only quick checks for the Linux 2 openSUSE coursework VM.
# Not the teacher's grading script; does not modify services or configuration.
set -u

check() {
  printf '\n=== %s ===\n' "$1"
  shift
  "$@" || printf 'Check unavailable/failed (inspect manually).\n'
}

check "SELinux mode" getenforce
check "SSH service" systemctl is-active sshd
check "SSH listening port" ss -lnt
check "Default firewalld zone" firewall-cmd --get-default-zone
check "Firewall port TCP/4444" firewall-cmd --zone=public --query-port=4444/tcp
check "Cron service" systemctl is-active cron
check "Source file" ls -l /home/db/2814.txt.utf-8
check "Backup directory" ls -ld /home/backup
check "Local audit rule file" ls -l /etc/audit/rules.d/50-passwd.rules
printf '\nQuick checks complete. See docs/verification.md for full testing.\n'
