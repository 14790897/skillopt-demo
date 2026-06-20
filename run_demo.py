# -*- coding: utf-8 -*-
"""SkillOpt Demo - run SearchQA training with DeepSeek API.

Usage:
    1. Clone SkillOpt into this directory: git clone https://github.com/microsoft/SkillOpt.git
    2. Install: cd SkillOpt && python -m venv .venv && .venv\\Scripts\\pip install -e .
    3. Set your API key below or via environment variable DEEPSEEK_API_KEY
    4. Run: python run_demo.py
"""
import os
import sys
import shutil
import subprocess

# ===== Fix Windows GBK encoding issue =====
os.environ["PYTHONUTF8"] = "1"

# ===== API Configuration =====
API_KEY = "sk-your-key-here"  # <-- Replace with your DeepSeek API key

os.environ["AZURE_OPENAI_ENDPOINT"] = "https://api.deepseek.com/v1"
os.environ["AZURE_OPENAI_API_KEY"] = os.environ.get("DEEPSEEK_API_KEY", API_KEY)
os.environ["AZURE_OPENAI_AUTH_MODE"] = "openai_compatible"

# ===== Paths =====
ROOT = os.path.dirname(os.path.abspath(__file__))
SKILLOPT_DIR = os.path.join(ROOT, "SkillOpt")
PYTHON = os.path.join(SKILLOPT_DIR, ".venv", "Scripts", "python.exe")
TRAIN_SCRIPT = os.path.join(SKILLOPT_DIR, "scripts", "train.py")
CONFIG = os.path.join(SKILLOPT_DIR, "configs", "searchqa", "demo_deepseek.yaml")

# ===== Verify setup =====
if not os.path.isdir(SKILLOPT_DIR):
    print("ERROR: SkillOpt/ not found. Run: git clone https://github.com/microsoft/SkillOpt.git")
    sys.exit(1)
if not os.path.isfile(PYTHON):
    print("ERROR: .venv not found. Run: cd SkillOpt && python -m venv .venv && .venv\\Scripts\\pip install -e .")
    sys.exit(1)

# Copy config if not already there
config_dest = os.path.join(SKILLOPT_DIR, "configs", "searchqa")
os.makedirs(config_dest, exist_ok=True)
local_config = os.path.join(ROOT, "configs", "demo_deepseek.yaml")
if os.path.isfile(local_config):
    shutil.copy2(local_config, CONFIG)

# Copy dataset if not already there
data_dest = os.path.join(SKILLOPT_DIR, "data", "searchqa_demo_split")
local_data = os.path.join(ROOT, "data", "searchqa_demo_split")
if not os.path.isdir(data_dest) and os.path.isdir(local_data):
    shutil.copytree(local_data, data_dest)

print("=" * 50)
print("  SkillOpt Demo - SearchQA + DeepSeek")
print("=" * 50)
print(f"  Optimizer: deepseek-chat")
print(f"  Target:    deepseek-chat")
print(f"  Dataset:   30 train / 15 val / 20 test (HARD)")
print(f"  Config:    {CONFIG}")
print("=" * 50)
print()

# Clean previous output
OUT_DIR = os.path.join(SKILLOPT_DIR, "outputs", "demo_searchqa_deepseek")
if os.path.exists(OUT_DIR):
    print(f"  [cleanup] Removing previous output: {OUT_DIR}")
    shutil.rmtree(OUT_DIR)
    print()

# Run training
cmd = [PYTHON, TRAIN_SCRIPT, "--config", CONFIG]
result = subprocess.run(cmd, cwd=SKILLOPT_DIR)
sys.exit(result.returncode)
