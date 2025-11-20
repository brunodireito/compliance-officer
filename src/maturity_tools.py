import json
import time
from . import config

# --- 1. Import ADK Tooling ---
try:
    from google.adk.tools import FunctionTool
except ImportError:
    # Fallback for development
    class FunctionTool:
        def __init__(self, func): self.func = func

# --- 2. Helper: Load JSON ---
def _load_data():
    try:
        with open(config.DATA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"topics": {}}

# --- 3. The Tool Function (Now with Rate Limiting) ---
def get_maturity_criteria(topic: str) -> str:
    """
    Retrieves the maturity level definitions (Levels 1-5) for a specific compliance topic.
    The agent uses this tool to look up the grading rules.
    
    Args:
        topic (str): The name of the topic (e.g., "Access Control", "Incident Response").
    
    Returns:
        str: A formatted list of levels or a list of valid topics if not found.
    """
    # --- RATE LIMIT SAFEGUARD ---
    # The Free Tier limit is ~10-15 RPM. 
    # We pause for 5 seconds to prevent 429 RESOURCE_EXHAUSTED errors during loops.
    print(f"   ⏳ [Rate Limit] Pausing 5s before looking up '{topic}'...")
    time.sleep(5) 
    # ----------------------------

    data = _load_data()
    topics = data.get("topics", {})
    
    # Exact match check
    if topic in topics:
        levels = topics[topic]["levels"]
        output = f"--- Criteria for '{topic}' ---\n"
        for level, criteria in levels.items():
            output += f"Level {level}: {criteria}\n"
        return output
    
    # If topic not found, help the agent self-correct
    valid_keys = ", ".join(topics.keys())
    return f"Topic '{topic}' not found. Valid topics are: {valid_keys}"

# --- 4. Create Tool Object ---
maturity_tool = FunctionTool(func=get_maturity_criteria)