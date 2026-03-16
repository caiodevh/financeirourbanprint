from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = 'FinanceiroUrbanoPrint'
ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
BUILD = ROOT / 'build'
SPEC = ROOT / f'{APP_NAME}.spec'


def run(cmd: list[str]) -> None:
    print('>>', ' '.join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    if shutil.which('pyinstaller') is None:
        print('PyInstaller não encontrado. Instale com: pip install pyinstaller')
        sys.exit(1)

    if BUILD.exists():
        shutil.rmtree(BUILD)
    if DIST.exists():
        shutil.rmtree(DIST)
    if SPEC.exists():
        SPEC.unlink()

    run([
        sys.executable,
        '-m',
        'PyInstaller',
        '--noconfirm',
        '--clean',
        '--windowed',
        '--onefile',
        '--name',
        APP_NAME,
        'run.py',
    ])

    exe_path = DIST / (APP_NAME + ('.exe' if sys.platform.startswith('win') else ''))
    print(f'Executável gerado em: {exe_path}')


if __name__ == '__main__':
    main()
