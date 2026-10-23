# SSH configuration

The lab's SSH daemon listens on **TCP/4444** rather than the default TCP/22.

- [port.conf](port.conf): sets the listener port.
- [auth-policy.conf](auth-policy.conf): enables password authentication and disables keyboard-interactive authentication, reproducing this specific course lab setup.

On openSUSE, these can be represented as drop-in files under `/etc/ssh/sshd_config.d/`, subject to the installed SSH package's effective configuration and precedence.

## Why three layers matter

An SSH daemon listening on 4444 is not sufficient on its own:

1. **sshd** must bind the port.
2. **SELinux** must permit `sshd` to use it.
3. **firewalld** must allow traffic to that port.

Useful *read-only* checks:

```bash
sudo sshd -t
sudo sshd -T | grep -E '^(port|passwordauthentication|kbdinteractiveauthentication) '
sudo ss -lntp | grep 4444
```

`sshd -t` validates syntax; `sshd -T` shows effective settings; `ss` checks the listening socket. Test a **new** connection before closing any existing SSH session.

**Scope:** the password-authentication setting reflects the assignment, not general guidance for an internet-facing production SSH server.
