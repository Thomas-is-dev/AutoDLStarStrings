import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env is looked up next to the executable, then in its parent folder (the project root for dist/),
# or at the project root when run from source
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
    ENV_CANDIDATES = [APP_DIR / '.env', APP_DIR.parent / '.env']
else:
    APP_DIR = Path(__file__).resolve().parent.parent
    ENV_CANDIDATES = [APP_DIR / '.env']

for env_file in ENV_CANDIDATES:
    if env_file.is_file():
        load_dotenv(env_file)
        break

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
SC_PATH = os.getenv('SC_PATH') or r'C:\Program Files\Roberts Space Industries\StarCitizen\LIVE'
