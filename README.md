# SkillOpt Demo

基于 [SkillOpt](https://github.com/microsoft/SkillOpt)（[论文](https://arxiv.org/abs/2605.23904)）的最小演示。通过优化自然语言 skill 文档提升 LLM 任务表现，无需微调模型权重。

## 快速开始

```bash
# 1. 克隆并安装
git clone https://github.com/microsoft/SkillOpt.git
cd SkillOpt
python -m venv .venv
.venv\Scripts\activate        # Windows（Linux/Mac: source .venv/bin/activate）
pip install -e .
cd ..

# 2. 设置 API Key（修改 run_demo.py 中的 API_KEY，或设置环境变量）
export DEEPSEEK_API_KEY=sk-your-key-here

# 3. 运行
python run_demo.py
```

训练约 2 分钟完成，消耗 ~152K tokens（约 ¥0.15）。

## 训练结果

```
Baseline → Best Skill:
  验证集 Hard Accuracy: 0.60 → 0.93 (+55.6%)
  测试集 Hard Accuracy: 0.65 → 0.75 (+15.4%)
```

优化器从空白模板自动学到了 7 条提取规则（见 `SkillOpt/outputs/demo_searchqa_deepseek/best_skill.md`）。

## 文件结构

```
├── run_demo.py                  # 入口脚本（自动复制 config 和数据到 SkillOpt/）
├── build_hard_data.py           # 数据集生成脚本（可重新生成或自定义数据）
├── configs/demo_deepseek.yaml   # 训练配置
├── data/searchqa_demo_split/    # 数据集（30 train / 15 val / 20 test）
└── SkillOpt/                    # 克隆的 SkillOpt 仓库（不提交到 git）
```

## 注意事项

- **Windows 用户**：`run_demo.py` 已设置 `PYTHONUTF8=1` 解决编码问题
- **重新训练**：删除 `SkillOpt/outputs/demo_searchqa_deepseek/` 后重新运行
- **数据集已包含**：`data/searchqa_demo_split/` 已在仓库中，无需额外生成
- **重新生成数据**：直接运行 `python build_hard_data.py`

## 参考

- [SkillOpt 官方仓库](https://github.com/microsoft/SkillOpt)
- [论文](https://arxiv.org/abs/2605.23904)
