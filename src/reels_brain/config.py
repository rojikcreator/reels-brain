import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_DIR / ".env")

VAULT = Path(os.environ.get("VAULT_PATH", r"C:\Users\jakub\OneDrive\Počítač\Brain"))
BRAIN_SUBDIR = "3-Zdroje/Reels Brain"

IG_LOGIN = os.environ.get("IG_LOGIN", "")

DAYS = 30
TOP_N = 10

WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "large-v3-turbo")
WHISPER_DEVICE = "cpu"      # kto má NVIDIA GPU, prepne na "cuda"
WHISPER_COMPUTE = "int8"    # na CPU najrýchlejšie; na "cuda" daj "float16"

CLAUDE_FAST = "haiku"       # klasifikácia niche
CLAUDE_SMART = "sonnet"     # anatómia scenárov, playbook
CLAUDE_TIMEOUT = 600        # sekúnd na jedno claude -p volanie

DOWNLOADS = PROJECT_DIR / "downloads"
