# auditd monitoring

The Linux 2 lab used this persistent drop-in rule:

```text
-w /etc/passwd -p r -k passwd_changes
```

The exact configuration is provided in [50-passwd.rules](50-passwd.rules).

## Meaning

- `-w /etc/passwd`: watch this file.
- `-p r`: log read access attempts.
- `-k passwd_changes`: attach a searchable audit key (the key name was specified by the exercise).

Despite the key's name, the rule watches **reads**, not only changes.

## Activation and verification

Install the file as `/etc/audit/rules.d/50-passwd.rules` on the lab VM, then load the rules and inspect them:

```bash
sudo augenrules --load
sudo auditctl -l
cat /etc/passwd > /dev/null
sudo ausearch -k passwd_changes -c cat -i
```

The course environment also had a `never,task` setting that could suppress audit events. The lab notes record disabling that setting before testing the rule. Do not change global audit filters on a production system without reviewing their purpose.

An expected event is a `cat` read involving `/etc/passwd`. Reboot and verify again to test persistence.
