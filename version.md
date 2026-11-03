# Versions

## 2.0.0

**Project**
- Reorganized into `src/`, `scripts/` and `tests/`
- Added `scripts/build_exe.bat` / `build_exe.py` to build a standalone `AutoDLStarStrings.exe`
- Added `requirements.txt`, `setup_venv.bat` and a launcher that uses its own `.venv`
- Added a full README and an MIT `LICENSE`
- Removed `repo_url.json`, `Roadmap.txt`, the `.spec` file, the committed `.exe` and dead code

**Features**
- Multi-language interface (English, French) with community translations in `src/locales/*.json`
- New `-l` / `--lang` option, system language detection and `APP_LANG`
- Star Citizen folder configurable with `SC_PATH` in `.env` (a single `.env`, also used by the exe)
- The exe stays open until Enter is pressed; launcher messages are translated

**Reliability**
- Atomic write of `global.ini`, and validation of the downloaded file
- Known file URL used first, with a GitHub API fallback (single request instead of recursive calls)
- Clear error when the game folder does not exist (no more prompt or stray folders)
- Network timeouts and precise error handling
- Console no longer crashes on emojis

**Quality**
- Simplified `autoupdate.py`
- 13 unit tests (translations, download, save, update flow, GitHub lookup)

## 1.0.0

Initial version: downloads the StarStrings `global.ini` and installs it in the Star Citizen folder.
