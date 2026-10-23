# firewalld configuration

The Linux 2 exercise used the **public** zone and opened TCP/4444 for the SSH service.

Commands corresponding to the lab configuration:

```bash
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --permanent --zone=public --add-port=4444/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-ports
```

- `--permanent` stores the rule for later reloads/restarts.
- `--zone=public` selects the zone used in the lab.
- `--add-port=4444/tcp` permits the selected TCP port.
- `--reload` applies the permanent configuration.

For a clean read-only verification:

```bash
sudo firewall-cmd --zone=public --query-port=4444/tcp
```

This is a coursework configuration example, not a recommendation to open port 4444 on unrelated machines. Verify the active network interface's zone before relying on these rules.
