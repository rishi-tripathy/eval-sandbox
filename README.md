# Financial Reasoning Evaluation Framework

I built this framework to get hands-on with applied model reliability work. Specifically, I wanted to test whether models can accurately hold domain-specific invariants implicitly while reasoning through increasingly complex scenarios.

I started in finance because the invariants are extremely clear (cash conservation, liquidity floors, temporal consistency). This let me systematically test how various model configurations and evaluation choices affect the ability to maintain these constraints—and where these patterns might generalize.

The core mechanism: deterministic financial simulation as ground truth, enabling isolation of model reasoning failures from evaluation failures.

The most interesting findings:

- the choice of evaluation scenario (in this example, the complexity of the task description) matters much more than any model configuration/agent infrastructure choices made. This has a huge impact on how agentic systems might more reliably and effectively be packaged in applications fit to purpose when expected to do this kind of reasoning.
- tools barely help despite seeming like an obvious improvement, while intermediate reasoning artifacts work consistently across all conditions. I don't know if this generalizes beyond financial reasoning, but it made me rethink assumptions about the benefits of integrating tools for deterministic thought.

## Key Findings

From 696 task executions across factorial comparison:

- **Task complexity dominates everything else**: The 11.7-point performance gap between easiest and hardest tasks dwarfs model differences (2.5 points) or tool effects. This suggests evaluation design choices matter more than model configuration optimization. I wanted to see how the model responded to differentiatlly harder tasks, as this might impact the kinds of UXs this agent might be pacakged into for (hypothetical) productization.

- **Tools provide minimal benefit, against expectations**: Comprehensive analysis shows tools improved performance by only 0.5 points (+2.8% success rate), with Haiku actually harmed (-0.2 pts) and Sonnet barely helped (+0.7 pts). Even with optimized limits, current tool designs don't match model reasoning patterns effectively.

- **Intermediate reasoning artifacts work consistently**: Requesting ledger generation improved performance by 5.5 points (+5.0% success rate) across all models and conditions. This is the most reliable improvement strategy I found.

## What I Was Trying to Learn

I designed this framework to get hands-on with questions like:

1. Can models maintain domain-specific invariants while reasoning through increasingly complex scenarios? I started with a domain (finance) where the invariants are extremely clear.
2. How do you distinguish model limitations from evaluation failures?
3. When do tools help vs. hurt reasoning accuracy? What other factors can help?
4. What interaction effects emerge across model × tool × task complexity?

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

- Can models reliably hold domain-specific invariants across increasing scenario complexity, and what breaks first?
- Why do tools provide so little benefit when they seem obviously useful for mathematical reasoning?
- What makes intermediate reasoning artifacts consistently effective while external tools aren't?
- How do you distinguish "model can't do X" from "evaluation is measuring the wrong thing" in systematic ways?
- When does evaluation design choice (task complexity) become more important than model configuration for real applications?

I don't have definitive answers—but building this gave me a clearer sense of why these questions matter for packaging reliable AI systems.

---

Built to understand evaluation methodology through hands-on experimentation.  
Detailed analysis: [FINDINGS.md](./FINDINGS.md)
