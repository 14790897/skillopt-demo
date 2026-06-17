# -*- coding: utf-8 -*-
"""SkillOpt Demo - run SearchQA training with DeepSeek API.

Usage:
    1. Clone SkillOpt: git clone https://github.com/microsoft/SkillOpt.git
    2. Install: cd SkillOpt && python -m venv .venv && .venv/Scripts/pip install -e .
    3. Copy this file and configs/ into SkillOpt/
    4. Set your API key below or via environment variable
    5. Run: .venv/Scripts/python run_demo.py
"""
import os
import sys
import shutil
import subprocess

# ===== Fix Windows GBK encoding issue =====
os.environ["PYTHONUTF8"] = "1"

# ===== API Configuration =====
# Option 1: Set directly here
API_KEY = "sk-your-key-here"  # <-- Replace with your DeepSeek API key

# Option 2: Read from environment variable (higher priority)
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://api.deepseek.com/v1"
os.environ["AZURE_OPENAI_API_KEY"] = os.environ.get("DEEPSEEK_API_KEY", API_KEY)
os.environ["AZURE_OPENAI_AUTH_MODE"] = "openai_compatible"

# ===== Paths =====
ROOT = os.path.dirname(os.path.abspath(__file__))
PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
TRAIN_SCRIPT = os.path.join(ROOT, "scripts", "train.py")
CONFIG = os.path.join(ROOT, "configs", "searchqa", "demo_deepseek.yaml")

print("=" * 50)
print("  SkillOpt Demo - SearchQA + DeepSeek")
print("=" * 50)
print(f"  Optimizer: deepseek-chat")
print(f"  Target:    deepseek-chat")
print(f"  Dataset:   30 train / 15 val / 20 test (HARD)")
print(f"  Config:    {CONFIG}")
print("=" * 50)
print()

# Clean previous output (auto-resume would skip if exists)
OUT_DIR = os.path.join(ROOT, "outputs", "demo_searchqa_deepseek")
if os.path.exists(OUT_DIR):
    print(f"  [cleanup] Removing previous output: {OUT_DIR}")
    shutil.rmtree(OUT_DIR)
    print()

# Run training
cmd = [PYTHON, TRAIN_SCRIPT, "--config", CONFIG]
result = subprocess.run(cmd, cwd=ROOT)
sys.exit(result.returncode)
