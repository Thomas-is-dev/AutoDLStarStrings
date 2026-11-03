"""Build a standalone Windows executable (dist/AutoDLStarStrings.exe) with PyInstaller."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
DIST = ROOT / 'dist'
BUILD = ROOT / 'build'
APP_NAME = 'AutoDLStarStrings'


def ensure_pyinstaller() -> None:
    """Install PyInstaller in the current environment if it is missing"""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print('PyInstaller not found, installing it...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])


def main() -> int:
    ensure_pyinstaller()

    command = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        '--onefile',
        '--name', APP_NAME,
        '--paths', str(SRC),
        '--add-data', f'{SRC / "locales"};locales',
        '--distpath', str(DIST),
        '--workpath', str(BUILD),
        '--specpath', str(BUILD),
        str(SRC / 'autoupdate.py'),
    ]
    print(' '.join(command))
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        print('Build failed.')
        return result.returncode

    print(f'\nBuild complete: {DIST / (APP_NAME + ".exe")}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
