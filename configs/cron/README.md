# Cron scheduling

The lab requested that the `db` user write the current date and time to `/home/db/date.txt` every five minutes.

See [db.crontab](db.crontab):

```cron
*/5 * * * * date > /home/db/date.txt
```

- `*/5` means every fifth minute.
- The other four wildcard fields mean any hour, day, month and weekday.
- `>` replaces the file's previous contents each time the job runs.

To install this as **db's crontab**, use `crontab -e` while logged in as `db`. Do not paste the job into root's crontab unless the environment specifically requires it.

Useful checks:

```bash
systemctl is-active cron
crontab -l
ls -l /home/db/date.txt
cat /home/db/date.txt
```

For the scheduled-job test, check that the output's timestamp changes after the next scheduled execution.
