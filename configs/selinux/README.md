# SELinux and the SSH port

The lab used SELinux **Enforcing** mode. Moving SSH to TCP/4444 also required adding that port to the SELinux SSH port type.

```bash
getenforce
sudo semanage port -l | grep ssh_port_t
sudo semanage port -a -t ssh_port_t -p tcp 4444
sudo semanage port -l | grep ssh_port_t
```

The `-a` command adds a port association to the local policy if it does not already exist. It is **not idempotent**: when the port is already assigned, the command can fail and the existing mapping should be inspected instead.

- `ssh_port_t`: SELinux label permitted for SSH ports.
- `-p tcp`: the protocol.
- `4444`: the nonstandard port selected for the lab.

SELinux labeling, the sshd listener and the firewall rule solve **different** problems. All three must agree for remote SSH connections to work.

To check persistence, review the policy after reboot instead of assuming a one-time command was applied correctly.
