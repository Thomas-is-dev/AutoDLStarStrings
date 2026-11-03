import argparse
import ctypes
import os
import shutil
import sys
from pathlib import Path

import requests

from githubapi import REQUEST_TIMEOUT, find_global_ini
from i18n import available_languages, set_language, t
from settings import GITHUB_TOKEN, SC_PATH

WINDOW_TITLE = 'AutoUpdate StarStrings'
REPO_OWNER = 'mrkraken'
REPO_NAME = 'starstrings'
REPO_BRANCH = 'master'
# Last known location of global.ini, used first to avoid a GitHub API request
KNOWN_URL = (
    f'https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/refs/heads/{REPO_BRANCH}'
    '/src/For_Players/Data/Localization/english/global.ini'
)


def download(url: str) -> bytes:
    """Download a global.ini and make sure it looks like one (non-empty, contains key=value lines)"""
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    if not response.content.strip() or b'=' not in response.content:
        raise requests.RequestException(t('invalid_remote'))
    return response.content


def fetch_remote_file() -> bytes | None:
    """Download global.ini from the known URL, falling back to a GitHub lookup if it fails.
    On success, prints the validity message followed by the URL actually used."""
    try:
        content = download(KNOWN_URL)
        print(t('url_valid'))
        print(t('url_label', url=KNOWN_URL))
        return content
    except requests.RequestException as error:
        print(t('download_warn', error=error))

    new_url = find_global_ini(REPO_OWNER, REPO_NAME, REPO_BRANCH, GITHUB_TOKEN)
    if not new_url or new_url == KNOWN_URL:
        print(t('no_url_found'))
        return None
    try:
        content = download(new_url)
    except requests.RequestException as error:
        print(t('download_failed', error=error))
        return None
    print(t('url_valid'))
    print(t('url_label', url=new_url))
    return content


def save_file(file_path: Path, content: bytes) -> bool:
    """Write the file atomically so an interrupted write never leaves a truncated global.ini"""
    temp_path = file_path.with_name(file_path.name + '.tmp')
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_bytes(content)
        os.replace(temp_path, file_path)
        return True
    except OSError as error:
        print(t('save_error', error=error))
        temp_path.unlink(missing_ok=True)
        return False


def check_for_updates(game_path: Path) -> bool:
    """Download the latest global.ini and install it if it differs from the local one"""
    file_path = game_path / 'data' / 'Localization' / 'english' / 'global.ini'
    remote_content = fetch_remote_file()

    label = t('file_label', path=file_path)
    print(label)
    print('-' * min(len(label), shutil.get_terminal_size().columns))

    if remote_content is None:
        return False

    try:
        local_content = file_path.read_bytes()
    except FileNotFoundError:
        print(t('creating'))
        return save_file(file_path, remote_content)
    except OSError as error:
        print(t('read_error', error=error))
        return False

    if local_content == remote_content:
        print(t('up_to_date'))
        return True

    print(t('update_available'))
    if save_file(file_path, remote_content):
        print(t('update_applied'))
        return True
    print(t('update_failed'))
    return False


class TranslatedHelpFormatter(argparse.HelpFormatter):
    """Help formatter whose 'usage:' prefix comes from the translations"""

    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, prefix=t('cli_usage_prefix') + ' ')


def configure_console() -> None:
    """Make printing never crash on consoles that cannot encode emojis, and set the window title"""
    for stream in (sys.stdout, sys.stderr):
        if stream is not None and hasattr(stream, 'reconfigure'):
            stream.reconfigure(errors='replace')
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(WINDOW_TITLE)
    except (AttributeError, OSError):
        pass


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    # Pre-parse --lang so that the help text itself is translated
    lang_parser = argparse.ArgumentParser(add_help=False)
    lang_parser.add_argument('-l', '--lang')
    known, _ = lang_parser.parse_known_args()
    if known.lang and set_language(known.lang) is None:
        print(t('unknown_language', lang=known.lang, available=', '.join(available_languages())))
        set_language(None)

    # add_help is disabled and the options are put in a custom group so that every help string is translated
    parser = argparse.ArgumentParser(
        prog='autoupdate',
        usage=t('cli_usage'),
        description=t('cli_description'),
        add_help=False,
        formatter_class=TranslatedHelpFormatter,
    )
    options = parser.add_argument_group(t('cli_options'))
    options.add_argument('-h', '--help', action='help', help=t('cli_help_help'))
    options.add_argument('-l', '--lang', help=t('cli_lang_help', available=', '.join(available_languages())))
    options.add_argument('-p', '--path', type=Path, default=Path(SC_PATH), help=t('cli_path_help'))
    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    configure_console()
    args = parse_arguments()

    if not args.path.is_dir():
        print(t('path_missing', path=args.path))
        return 1

    return 0 if check_for_updates(args.path) else 1


def pause_if_frozen() -> None:
    """Keep the console window open when running as an exe (double-click) so the output stays readable"""
    if getattr(sys, 'frozen', False) and sys.stdin is not None and sys.stdin.isatty():
        try:
            input('\n' + t('press_enter'))
        except EOFError:
            pass


if __name__ == '__main__':
    try:
        code = main()
    except SystemExit as exit_request:
        code = exit_request.code
    except Exception as error:
        print(t('unexpected_error', error=error))
        code = 1
    pause_if_frozen()
    sys.exit(code)
