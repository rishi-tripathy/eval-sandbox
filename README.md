# Financial Reasoning Evaluation Framework

**Building reliable AI systems through deterministic evaluation**

## Purpose

I rolled my own eval harness to get hands-on with how Anthropic thinks about reliability. There's a deterministic financial sim as ground truth, failure taxonomy, invariant-based scoring, and constrained repair loops. I also explored whether requesting intermediate artifacts (model-generated ledgers) improves reasoning accuracy.

## Methodology

This evaluation framework tests AI financial reasoning through:

- **Deterministic ledger simulation** with mathematical invariant validation
- **Two-turn agent workflow**: draft scenario → validate → repair if needed
- **Tool-calling integration**: calculator, validation, and advisory tools for mathematical precision
- **Systematic comparison framework**: factorial A/B testing across models, task sets, and configurations
- **Multi-complexity task progression**: simple structured prompts → complex natural language scenarios
- **Comprehensive scoring** across scenario generation, mathematical precision, and constraint satisfaction

## What I Learned

**Key Model Insights:**

- **Tool integration complexity**: Counter-intuitively, tool-enabled models initially showed worse performance due to JSON parsing failures from explanatory text, resolved through enhanced extraction logic  
- **Mathematical precision bottleneck**: ~0% accuracy on ledger calculations despite logical reasoning ability - addressed through calculator tool integration
- **JSON generation brittleness**: INVALID_JSON was dominant failure mode (45% of tool-enabled runs), but reduced to 3% through enhanced extraction with brace counting
- **Duration modeling systematic errors**: Models consistently omit `duration_months: 1` for one-time expenses, causing simulation engine to treat bonuses/costs as ongoing monthly events
- **Expected verdict validation critical**: Manual verification revealed 2/4 consistently failing tasks had incorrect expected verdicts, penalizing models for correct mathematical reasoning
- **Natural language complexity correlation**: 51.9% accuracy on conversational prompts vs 77%+ on structured tasks

**Evaluation Framework Insights:**

- **Systematic comparison reveals non-obvious patterns**: A/B testing infrastructure uncovered that tool integration can initially hurt performance, leading to root cause analysis and fixes
- **Partial scoring prevents information loss**: Enhanced scoring captures diagnostic value from failures, showing 16.7% average partial scores on wrong verdicts vs complete loss
- **Expected verdict validation essential**: Manual verification of "consistently failing" tasks revealed ground truth errors, highlighting need for mathematical validation of test cases  
- **Intermediate artifacts don't always help**: Requesting detailed calculations sometimes hurts vs helps performance  
- **Constraint-based repair is learnable**: Models can improve scenarios when given specific violation feedback
- **Statistical rigor essential**: Single-run evaluations miss important performance variations; multiple runs with aggregation provide reliable insights
- **Infrastructure enables discovery**: Comprehensive tracing revealed systematic vs random error patterns invisible in manual testing

## Execution Milestones

• **M0**: Core simulation engine + golden test fixtures  
• **M1**: Task runner, traces, error taxonomy, CLI infrastructure  
• **M2**: Claude integration with constraint-based repair system  
• **M3**: Advanced scoring, parallel task evaluation, enhanced UX  
• **M4**: Tool calling integration with calculator, validation, and advisory tools  
• **M4.5**: Systematic comparison framework for A/B testing across models and configurations  
• **Future**: Prompt optimization for tool integration, expanded task complexity, multi-domain evaluation

## Task Structure

**8 Task Folders** (4 pairs) enabling systematic evaluation - each has a version with and without ledger generation to see if asking the model to generate intermediate artifacts changes its accuracy.

### With Ledger Generation 📊

- **v1-simple-with-ledger**: 16 basic scenarios + detailed calculations
- **v2-intermediate**: 14 medium-complexity scenarios + ledger generation
- **v3-tasks-with-ledger**: 5 ledger-focused test cases
- **v4-advanced**: 10 complex natural language scenarios + calculations

### Without Ledger Generation 🎯

- **v1-simple**: 16 basic scenarios, JSON-only output
- **v2-intermediate-no-ledger**: 14 medium scenarios, JSON-only
- **v3-tasks-no-ledger**: 5 test cases, JSON-only
- **v4-advanced-no-ledger**: 10 complex scenarios, JSON-only

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here

# Run a single task
python -m workbench run-single tasks/v2-intermediate/apartment_overlap.json --model claude

# Run an entire suite
python -m workbench run-suite tasks/v1-simple --model claude --session-id my_test

# Run systematic A/B comparison
python -m workbench run-comparison --models claude,claude-tools --task-sets tasks/v3-tasks-with-ledger --runs 3

# Compare ledger vs non-ledger impact
python -m workbench run-comparison --models claude --task-sets tasks/v3-tasks-with-ledger,tasks/v3-tasks-no-ledger --runs 2
```

## Architecture Overview

### Core Components

**Scenario Schema** (`workbench/types.py`): Pydantic models enforcing sign conventions and temporal constraints

**Simulation Engine** (`workbench/simulate.py`): Monthly cash flow calculation with deterministic ledger generation

**Invariant System** (`workbench/invariants.py`):

- `LIQUIDITY_FLOOR`: Cash never goes below threshold
- `MONEY_CONSERVATION`: Ledger arithmetic validation
- `TEMPORAL_CONSISTENCY`: Event timing validity

**Evaluation Pipeline** (`workbench/eval.py`): Main entry point returning verdict + detailed violations

**Agent System** (`workbench/models/agents.py`): Two-turn loop with constrained repair strategies, tool-calling integration

**Comparison Framework** (`workbench/comparison.py`): Systematic A/B testing infrastructure with statistical analysis and reporting

### Key Workflows

**Single Task**: `python -m workbench run-task tasks/v2/apartment_overlap.json --model claude`

**Suite Execution**: `python -m workbench run-suite tasks/v1 --model claude --session-id my_session`

**A/B Comparison**: `python -m workbench run-comparison --models claude,claude-tools --task-sets tasks/v3-tasks-with-ledger --runs 3`

**Analysis**: Rich traces in `traces/<session_id>/` with task names in filenames, comparison reports in `reports/`

## Scoring System

**Comprehensive evaluation** across multiple dimensions:

- **Scenario Generation** (20 pts): Valid JSON, schema compliance, sign conventions
- **Verdict Accuracy** (25 pts): Correct feasible/infeasible determination
- **Violation Detection** (20 pts): Identifying first violation month and invariant
- **Repair Capability** (20 pts): Successful constraint satisfaction improvements
- **Mathematical Precision** (15 pts): Ledger calculation accuracy vs ground truth

**Variable point totals** based on task complexity - repair tasks have more possible points than generation-only tasks.

**Partial Scoring Benefits**: Enhanced scoring system extracts diagnostic value even from failed runs:
- Component-level analysis (scenario generation vs mathematical calculation vs repair)  
- Error-tolerant scoring prevents complete information loss on edge cases
- Statistical significance through multiple runs with partial credit aggregation

## Evaluation Quality Lessons

**Task Validation Protocol**: Our investigation revealed critical evaluation quality issues:

1. **Ground Truth Verification**: 2 out of 4 "consistently failing" tasks had incorrect expected verdicts
   - vacation_fund: Expected infeasible → Actually feasible (ends July with $200 cash)
   - home_repair_cascade: Expected infeasible → Actually feasible (ends July with $1700 cash) 
   - Models were being penalized for correct mathematical reasoning

2. **Model Error vs Test Error**: Distinguishing systematic model failures from evaluation framework bugs requires manual verification of edge cases

3. **Duration Semantics**: Clear specification essential but insufficient - models consistently omit `duration_months: 1` despite explicit prompt warnings

4. **Failure Pattern Analysis**: Consistent cross-model failures warrant ground truth investigation, not model capability assumptions

## Current Status

**M4.5 Complete**: Full evaluation infrastructure with tool calling integration, systematic A/B testing framework, and comprehensive statistical analysis.

## Conclusions & Future Directions

This framework successfully demonstrates systematic AI evaluation methodology with deterministic ground truth. The infrastructure is production-ready and reveals important insights about model behavior under structured evaluation.

**Key open questions for future work:**
- **Tool integration optimization**: Enhanced JSON extraction resolved initial performance degradation - further prompt engineering refinements may unlock additional gains
- **Task complexity thresholds**: Understanding when tools become beneficial vs harmful across difficulty scales  
- **Duration specification improvements**: Despite explicit prompt warnings, models consistently omit `duration_months: 1` - exploring alternative specification approaches
- **Evaluation quality assurance**: Systematic protocols for validating ground truth correctness as task complexity increases
- **Multi-domain generalization**: Expanding beyond financial scenarios to test framework robustness

**Methodology Contributions**: This framework demonstrates several eval reliability patterns:
- **Comprehensive tracing enables root cause analysis** of unexpected performance patterns
- **Partial scoring preserves diagnostic value** from edge cases that would otherwise be discarded  
- **A/B comparison infrastructure** rapidly identifies regression vs progression across model/prompt combinations
- **Manual verification protocols** essential for distinguishing model limitations from evaluation framework errors

The comparison infrastructure enables rapid iteration on these questions through systematic A/B testing methodology.

---

_This framework demonstrates hands-on exploration of AI reliability patterns through systematic evaluation design._
