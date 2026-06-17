# SkillOpt Demo - Agent Skill Optimization with DeepSeek API

> Based on paper: [SkillOpt: Executive Strategy for Self-Evolving Agent Skills](https://arxiv.org/abs/2605.23904) (Microsoft, 2026)

## What is SkillOpt?

SkillOpt is a **text-space optimizer** that treats external skill documents as trainable state for frozen LLM agents. Instead of fine-tuning model weights, it optimizes a **natural language skill document** (a markdown file injected into the system prompt) through a deep learning-style training loop:

```
Forward Pass (Rollout)  -->  Backward Pass (Reflection)  -->  Bounded Update (Edits)
     |                             |                              |
     v                             v                              v
Target model executes         Optimizer model analyzes       Apply add/delete/replace
tasks with current skill      success & failure traces       edits within budget (lr)
     |                                                            |
     v                                                            v
Validation Gate: accept only if score STRICTLY improves on held-out set
```

**Key insight**: The model weights never change. Only the skill document evolves.

## Quick Start

### 1. Install SkillOpt

```bash
git clone https://github.com/microsoft/SkillOpt.git
cd SkillOpt
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -e .
```

### 2. Configure API

Copy `.env.example` to `SkillOpt/.env` and fill in your API key:

```bash
AZURE_OPENAI_ENDPOINT=https://api.deepseek.com/v1
AZURE_OPENAI_API_KEY=sk-your-key-here
AZURE_OPENAI_AUTH_MODE=openai_compatible
```

### 3. Build Dataset & Run

```bash
# Build the hard dataset
python scripts/build_hard_data.py

# Run training
python run_demo.py
```

## Files in This Repo

| File | Purpose |
|------|---------|
| `run_demo.py` | Main entry script - sets env, cleans output, runs training |
| `build_hard_data.py` | Generates challenging QA dataset designed to trip up LLMs |
| `configs/demo_deepseek.yaml` | Training config (2 epochs, batch=15, lr=4, constant schedule) |
| `data/initial_skill.md` | Starting skill (empty placeholder) |
| `examples/best_skill_example.md` | Example of what SkillOpt learns |
| `.env.example` | API credential template |

## Training Results (Example Run)

```
Config: deepseek-chat as both optimizer and target
Dataset: 30 train / 15 val / 20 test (hard QA pairs)
Epochs: 2, Batch: 15, Edit Budget: 4

Step 1: Rollout 100% -> Learned from successes -> Validation 80% -> REJECTED
Step 2: Rollout 90%  -> Learned from 1 failure + 9 successes -> Validation 100% -> ACCEPTED

Test: 86.67% -> 93.33% (+6.67% improvement)
Tokens: ~35K total, 90 API calls, 37 seconds
```

## Key Experiences & Lessons

### 1. Windows GBK Encoding Fix (Critical)

SkillOpt is developed on Linux/Mac. On Chinese Windows, Python defaults to GBK encoding which crashes on UTF-8 YAML files.

**Solution**: Set `PYTHONUTF8=1` before spawning subprocess:
```python
os.environ["PYTHONUTF8"] = "1"
```

### 2. Auto-Resume Behavior

SkillOpt saves state to `runtime_state.json`. Re-running the same command resumes from the last checkpoint. **Delete the output directory for a fresh run.**

### 3. Validation Gate is STRICT

The gate requires `new_score > current_score` (strict inequality). If baseline is already 100%, no edit can pass. Design data that challenges the model.

### 4. Dataset Design Matters

Easy data -> model gets 100% baseline -> no room to improve -> all edits rejected.

**Hard data tricks that work:**
- Context conflicts with common knowledge (must follow context)
- Multiple candidate answers in one passage
- Strict format requirements (number only, no units)
- Ambiguous entity names (Apple Inc vs Apple Records)
- Dense context with distractors

### 5. DeepSeek API as OpenAI-compatible Backend

SkillOpt uses `AZURE_OPENAI_*` env vars for all backends. For DeepSeek:
```
AZURE_OPENAI_ENDPOINT=https://api.deepseek.com/v1
AZURE_OPENAI_AUTH_MODE=openai_compatible
model name: deepseek-chat
```

### 6. What SkillOpt Actually Learns

The optimized skills encode **procedural rules**, not instance-specific answers:
- "Use the shortest canonical entity name (Apple not Apple Inc.)"
- "Always follow the context even when it conflicts with general knowledge"
- "Extract the specific value asked for, not surrounding text"

These rules transfer across models and even across benchmarks.

### 7. Cost Efficiency

- Training cost: ~35K tokens for a minimal demo
- Deployment cost: 0 (just a markdown file in system prompt)
- The skill file is typically 300-2000 tokens

### 8. Relevance to Local Agent Systems (e.g., MiQi)

SkillOpt is directly applicable to local agent skill systems:
- Agent skills are already natural language documents -> perfect fit
- Use a cloud optimizer (GPT-5.5 / DeepSeek) to train skills offline
- Deploy optimized skills to local/weaker models at zero cost
- Sandbox isolation provides safe rollout environments
- Execution traces are natural feedback signals

## SkillOpt Architecture (Deep Learning Analogy)

| Deep Learning | SkillOpt Equivalent |
|---------------|---------------------|
| Forward Pass | Rollout batch execution |
| Backward Pass | Minibatch reflection (success/failure analysis) |
| Learning Rate | Edit budget Lt (max edits per step) |
| LR Scheduler | Cosine/constant/linear decay of edit budget |
| Validation Set | Held-out selection split (Dsel) |
| Momentum | Epoch-level slow/meta update |
| Regularization | Bounded updates + rejected-edit buffer |
| Model State | External skill document (markdown) |
| Gradient | Structured edits (append/insert/replace/delete) |

## Config Reference (Key Parameters)

```yaml
train:
  num_epochs: 2          # Training epochs
  batch_size: 15         # Rollout batch size per step
  
optimizer:
  learning_rate: 4       # Max edits per step
  lr_scheduler: constant # constant/cosine/linear
  use_slow_update: true  # Epoch-level longitudinal guidance
  use_meta_skill: true   # Cross-epoch optimizer memory

gradient:
  minibatch_size: 4      # Trajectories per reflection group
  analyst_workers: 4     # Parallel reflection workers

evaluation:
  use_gate: true         # Validation gate (required)
```

## References

- Paper: https://arxiv.org/abs/2605.23904
- Repo: https://github.com/microsoft/SkillOpt
- Docs: https://microsoft.github.io/SkillOpt/docs/guideline.html
