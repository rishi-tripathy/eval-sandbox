# Financial Reasoning Evaluation Framework

I built this framework to understand how evaluation design affects reliability claims. The core mechanism: deterministic financial simulation as ground truth, enabling isolation of model reasoning failures from evaluation failures.

The most interesting finding: tools barely help despite seeming like an obvious improvement, and what does help (intermediate reasoning artifacts) works consistently across all conditions. I don't know if this generalizes beyond financial reasoning, but it made me rethink assumptions about tool integration benefits.

## Key Findings

From 696 task executions across factorial comparison:

- **Tools provide minimal benefit despite expectations**: Comprehensive analysis shows tools improved performance by only 0.5 points (+2.8% success rate), with Haiku actually harmed (-0.2 pts) and Sonnet barely helped (+0.7 pts). Even with optimized limits, current tool designs don't match model reasoning patterns effectively.

- **Task complexity dominates everything else**: The 11.7-point performance gap between easiest and hardest tasks dwarfs model differences (2.5 points) or tool effects. This suggests evaluation design choices matter more than model configuration optimization.

- **Intermediate reasoning artifacts work consistently**: Requesting ledger generation improved performance by 5.5 points (+5.0% success rate) across all models and conditions. This is the most reliable improvement strategy I found.

- **Ground truth validation was critical**: Manual verification revealed 2/2 investigated "consistently failing" tasks had incorrect expected verdicts. I was debugging model behavior when the evaluation framework was wrong.

## What I Was Trying to Learn

I designed this framework to get hands-on with questions like:

1. How do you distinguish model limitations from evaluation failures?
2. When do tools help vs. hurt reasoning accuracy?
3. What interaction effects emerge across model × tool × task complexity?

The factorial design (2 models × 2 tool configurations × 4 task sets × 3 runs) enables attribution that single-condition evaluations miss. Whether these specific findings generalize, I'm not sure—but the methodology felt like the right way to ask the questions.

## Quick Start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key

# Run systematic comparison
python -m workbench run-comparison \
  --models claude,claude-tools \
  --task-sets tasks/v3-tasks-with-ledger \
  --runs 3

# Single task for debugging
python -m workbench run-single tasks/v2-intermediate/apartment_overlap.json --model claude
```

See [FINDINGS.md](./FINDINGS.md) for detailed methodology and results.

## Architecture

| Component       | Purpose                                                   |
| --------------- | --------------------------------------------------------- |
| `simulate.py`   | Deterministic ledger engine (ground truth)                |
| `invariants.py` | LIQUIDITY_FLOOR, MONEY_CONSERVATION, TEMPORAL_CONSISTENCY |
| `agents.py`     | Two-turn loop: generate → validate → repair               |
| `comparison.py` | Factorial A/B testing infrastructure                      |
| `scoring.py`    | Partial credit scoring across 5 dimensions                |

Traces written to `traces/<session_id>/`, comparison reports to `reports/`.

## Questions This Raised

- Why do tools provide so little benefit when they seem obviously useful for mathematical reasoning?
- What makes intermediate artifacts (ledgers) consistently effective while tools aren't?
- When does task complexity become the dominant factor overwhelming configuration choices?
- What's the right protocol for distinguishing "model can't do X" from "evaluation is measuring the wrong thing"?

I don't have answers—but building this gave me a clearer sense of why these questions are hard to answer well.

---

Built to understand evaluation methodology through hands-on experimentation.  
Detailed analysis: [FINDINGS.md](./FINDINGS.md)
