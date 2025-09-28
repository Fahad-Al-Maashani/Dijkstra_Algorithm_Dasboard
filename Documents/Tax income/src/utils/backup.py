import json
from pathlib import Path

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
