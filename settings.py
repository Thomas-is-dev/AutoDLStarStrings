import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
