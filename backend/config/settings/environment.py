import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

environ.Env.read_env(ENV_PATH)
env = environ.Env()
