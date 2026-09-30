#!/usr/bin/env python3
"""Install one self-contained HWP skill; preserve an existing installation."""
import argparse
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', default='~/.codex/skills/hwp')
    parser.add_argument('--replace', action='store_true')
    args = parser.parse_args()
    if any(c in args.dest for c in '\r\n\0'):
        parser.error('destination must not contain CR, LF, or NUL')
    source = Path(__file__).resolve().parents[1] / 'plugins/easy-hwp/skills/hwp'
    destination = Path(args.dest).expanduser().absolute()
    if source == destination.resolve() or source in destination.resolve().parents:
        parser.error('destination must be outside the source skill')
    exists = destination.exists() or destination.is_symlink()
    if exists and not args.replace:
        parser.error('destination exists; use --replace to back it up')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.hwp-install-', dir=destination.parent) as temporary:
        staged = Path(temporary) / 'hwp'
        shutil.copytree(source, staged)
        backup = None
        if exists:
            backup = Path.home() / '.local/share/easy-hwp/backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') / destination.name
            backup.parent.mkdir(parents=True)
            shutil.move(str(destination), str(backup))
            print(f'Backup: {backup}')
        try:
            staged.rename(destination)
        except OSError:
            if backup:
                shutil.move(str(backup), str(destination))
            raise
    print(f'Installed: {destination}\nStart a new agent session to load the skill.')


if __name__ == '__main__':
    main()
