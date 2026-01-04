# Financial Reasoning Evaluation Framework

I built this framework to get hands-on with applied model reliability work. Specifically, I wanted to test whether models can accurately hold domain-specific invariants implicitly while reasoning through increasingly complex scenarios.

I started in finance because the invariants are extremely clear (cash conservation, liquidity floors, temporal consistency). This let me systematically test how various model configurations and evaluation choices affect the ability to maintain these constraints—and where these patterns might generalize.

The core mechanism: deterministic financial simulation as ground truth, enabling isolation of model reasoning failures from evaluation failures.

**The task**: Given a natural language financial scenario (e.g., "I have $1000 cash, earn $2000/month, but need to buy a $3000 car next month"), models must generate a structured JSON scenario, determine if it's feasible within constraints (liquidity floors, money conservation), and if infeasible, propose a specific repair (timing shifts, amount adjustments, baseline changes).

## Experimental Framework

![Framework Diagram](framework_diagram.png)

The diagram shows the complete experimental pipeline: natural language financial tasks are processed by agents under different configurations (model, tools, ledger requirements, task complexity), then evaluated against deterministic ground truth simulation to isolate model reasoning failures from evaluation artifacts.

The most interesting findings:

- **Task complexity dominates everything**: The 8.9-point gap between v4-advanced and v2-intermediate tasks is larger than all other factors combined. This has profound implications for how agentic systems should be scoped in production—the scenario design choice becomes more critical than model or infrastructure optimization.
- **Tools barely help despite seeming obvious**: Only -0.7pp average effect, with high variability masking large task-specific benefits and failures. Tool integration creates unpredictable performance patterns rather than consistent improvements, challenging assumptions about computational assistance.
- **Ledger requirements hurt across all conditions**: Requiring intermediate reasoning artifacts caused -8.4pp performance drop, contradicting my intuition about the beneifts of asking models to articulate their reasoning. My mechanistic analysis revealed this transforms the cognitive task from scenario design to arithmetic computation which seems to have distracted the model and it got more of its core cognitive work wrong.

## Key Findings

From 696 task executions across factorial comparison (2×2×2×3 design):

**Effect Size Hierarchy** (what actually matters for performance):

1. **Task Complexity**: -8.9pp (v4 vs v2) - largest effect
2. **Ledger Requirement**: -8.4pp - strong negative effect
3. **Model Choice**: +5.2pp (Sonnet vs Haiku) - moderate positive effect
4. **Tool Access**: -0.7pp - minimal effect

**Critical Insights for Production Systems**:

- **Scenario scoping trumps model optimization**: The 8.9pp complexity gap exceeds all infrastructure choices combined. For reliable agentic systems, constraining task scope matters and ensuring clarity of input context matters more than model/tool selection.

- **Tool integration creates brittleness**: Tools show 22.3 std dev vs 19.0 for no-tools, with task-specific benefits (+13.4pp on some tasks) offset by computational bottlenecks (-18.6pp on others). Current tool designs amplify variance rather than improving consistency.

- **Cognitive overhead from structured outputs**: Ledger requirements fundamentally change task demands from scenario reasoning to arithmetic computation, causing systematic performance degradation across all conditions.

- **Model differences emerge under tool stress**: Haiku shows 100% of JSON parsing errors and higher tool-induced brittleness, suggesting tools amplify existing capability gaps rather than compensating for them.

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

## Implications for Long-Running Agents & Trust

**What this means for agentic system design**:

- **Invariant maintenance degrades predictably**: Models can hold financial constraints through simple scenarios (90% success) but fail systematically on complex ones (60% success). This suggests **scope-limited deployment** rather than general-purpose financial agents.

- **Tool overhead vs. verification benefits**: Tools help with repairs (+29.6pp reduction in REPAIR_FAILED) but introduce computational bottlenecks that create stochastic behavior. For trustworthy systems, this suggests **verification-focused** rather than generation-focused tool integration.

- **Cognitive load management**: The ledger finding reveals that requiring structured intermediate outputs can fundamentally change cognitive demands, potentially degrading rather than improving reliability. UX design should **minimize rather than maximize** explicit reasoning requirements.

- **Guardrail design**: Since task complexity dominates all model configuration choices, the most effective reliability strategy is **constraining scenario complexity** rather than optimizing infrastructure. This has profound implications for how agentic systems should be scoped in production.

**System Architecture Implications**:

The findings suggest specific design patterns for reliable long-running agents:

- **Context specification interfaces**: Since task complexity is the dominant factor, UX should help users naturally constrain scenario scope rather than encouraging comprehensive descriptions. The 8.9pp complexity penalty suggests systems should actively guide toward simpler, well-specified inputs.

- **Subagent orchestration with clarification loops**: The high tool variability (22.3 vs 19.0 std dev) indicates agents should delegate uncertain computations to specialized subagents rather than attempting everything inline. This reduces cognitive load while enabling focused verification.

- **Introspection and intervention points**: The predictable degradation patterns (90% → 60% success across complexity) suggest systems can detect when they're approaching reliability boundaries and proactively request human oversight or task decomposition.

- **Review/queue systems for cognitive overhead**: The ledger finding shows that requiring structured outputs fundamentally changes cognitive demands. Systems should queue complex reasoning for review rather than demanding immediate structured responses.

**Open questions for generalization**:

- Do these patterns (complexity >> tools >> model) hold across other structured reasoning domains?
- Can tool integration or intermediate artifacts be redesigned to reduce rather than amplify performance variance?
- What level of task complexity enables reliable invariant maintenance for different applications?
- How should agent systems detect and communicate when they're approaching their reliability boundaries?

The framework methodology—factorial comparison with deterministic ground truth—felt like the right way to get empirical answers to these reliability questions.

---

Detailed analysis: [FINDINGS.md](./FINDINGS.md)
