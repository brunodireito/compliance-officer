import os
import pathlib

# --- 🔑 API KEY CONFIGURATION ---
# Paste your key inside the quotes below.
# This sets it for the entire application session.
os.environ["GEMINI_API_KEY"] = "AIzaSyAwlaKnxgwmgx1dVpL3xFCb7htOewNxgic"

# --- PATHS ---
# Defines where the project root and data files are located
PROJECT_ROOT = pathlib.Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "maturity_model.json"

# --- MODEL ---
MODEL_NAME = "gemini-2.5-flash"

INPUT_FILENAME = "input_policy.txt"
OUTPUT_FILENAME = "compliance_report.md"