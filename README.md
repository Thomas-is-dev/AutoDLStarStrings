# AutoDLStarStrings

Automatic downloader and installer of the [StarStrings](https://github.com/MrKraken/StarStrings) localization file (`global.ini`) for Star Citizen.

It finds the latest `global.ini` in the StarStrings repository, compares it with your installed copy and updates it only when needed.

## Features

- One-click update with `scripts\launch.bat` (the virtual environment is created automatically)
- Automatic fallback: if the known file URL breaks, `global.ini` is looked up in the repository through the GitHub API
- The file is written atomically and the download is validated, so a failed update never corrupts your installed copy
- Multi-language interface, with community-contributed translations
- Optional GitHub token to raise the API rate limit

## Requirements

- Windows
- Python 3.10 or newer (available through the `py` launcher)

## Quick start

1. Create a `.env` file at the project root (next to the `.exe` if you use the executable) with your Star Citizen folder, and optionally a [GitHub token](https://github.com/settings/tokens) to increase the rate limit:
   ```
   SC_PATH=C:\Program Files\Roberts Space Industries\StarCitizen\LIVE
   GITHUB_TOKEN=your_token_here
   ```
2. Run `scripts\launch.bat`. On first run it calls `scripts\setup_venv.bat`, which creates `.venv` and installs `requirements.txt`. The game folder is read from `SC_PATH` in `.env`.

To run it manually instead:

```
pip install -r requirements.txt
python src\autoupdate.py
```

## Usage

```
python src\autoupdate.py [-h] [-l LANG] [-p PATH]
```

| Option | Description |
|--------|-------------|
| `-p`, `--path` | Star Citizen installation folder (default: `SC_PATH` from `.env`, otherwise `C:\Program Files\Roberts Space Industries\StarCitizen\LIVE`) |
| `-l`, `--lang` | Interface language, e.g. `en`, `fr` (default: automatic) |
| `-h`, `--help` | Show the help |

`scripts\launch.bat` forwards its arguments, so `scripts\launch.bat -p "C:\StarCitizen\LIVE" -l fr` works too.

### Custom Star Citizen path

```
python src\autoupdate.py -p "C:/StarCitizen/LIVE"
```

## Languages

The language is chosen in this order:

1. `--lang` option
2. `APP_LANG` environment variable (can be set in `.env`, e.g. `APP_LANG=fr`)
3. System language
4. English (default and fallback)

Currently available: English (`en`), Français (`fr`).

### Add your language

No code change is needed:

1. Copy `src/locales/en.json` to `src/locales/<code>.json` (e.g. `de.json`, `pt_br.json`).
2. Translate the values. Keep the keys and the `{placeholders}` unchanged, and set `_language_name`.
3. Run `python src\autoupdate.py -l <code> -h` to check it. Missing keys fall back to English.
4. Run the tests (see below): they check that your file has the same keys and placeholders as `en.json`.
5. Open a pull request.

## Tests

```
python -m unittest discover -s tests
```

## Build a standalone executable

Run `scripts\build_exe.bat` (or `python scripts\build_exe.py` from the virtual environment). It installs PyInstaller if needed and produces `dist\AutoDLStarStrings.exe`, with the translations bundled.

The `.exe` uses the same `.env` as the project: it looks next to the `.exe` first, then in the parent folder (the project root when the exe is in `dist\`). A single `.env` is enough.

## Project layout

```
AutoDLStarStrings/
├── src/
│   ├── autoupdate.py     Main script and command-line interface
│   ├── githubapi.py      GitHub API fallback lookup of global.ini
│   ├── settings.py       Application folder and .env (GitHub token)
│   ├── i18n.py           Language detection and translation loading
│   └── locales/          One JSON translation file per language
├── scripts/
│   ├── launch.bat        Launcher (creates the virtual environment if needed)
│   ├── setup_venv.bat    Virtual environment and dependencies setup
│   ├── build_exe.bat     Builds the Windows executable
│   └── build_exe.py      PyInstaller build script
├── tests/                Unit tests (translations, download, atomic save, GitHub lookup)
├── requirements.txt
├── LICENSE               MIT
└── README.md
```

---

Released under the [MIT License](LICENSE). Inspired by [StarStrings](https://github.com/MrKraken/StarStrings).
