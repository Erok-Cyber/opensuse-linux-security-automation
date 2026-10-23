"""Portfolio adaptation of the Linux 2 VG backup lab.

Differences from the submitted coursework version:
- The demonstration archive password is NOT embedded in public source.
- Set BACKUP_ARCHIVE_PASSWORD securely in the environment before running.

This intentionally keeps the lab's paths and workflow. It is an educational
example, not a production backup system. 7-Zip's -p argument may expose a
password to privileged local process inspection during execution.
"""

import os
from datetime import datetime
import subprocess


timestamp = datetime.now().strftime("%Y%m%d_%H:%M")
source = "/home/db/2814.txt.utf-8"
archive = "/root/" + timestamp + "_2814.txt.utf-8"

# Portfolio-only adaptation: replace the original hardcoded demo password.
password = os.environ["BACKUP_ARCHIVE_PASSWORD"]

if os.path.exists(archive):
    raise SystemExit("Backup finns redan för denna minut.")


subprocess.run([
    "7z", "a", "-t7z", "-sae", "-p" + password, "-mhe=on",
    archive, source
], check=True)
print("Backup skapad:", archive)


subprocess.run([
    "rsync", "-avh",
    "-e", "ssh -p 4444 -i /home/backup/.ssh/id_ed25519 -o BatchMode=yes",
    archive, "backup@localhost:/home/backup/"
], check=True)
print("Backup överförd till /home/backup/")
