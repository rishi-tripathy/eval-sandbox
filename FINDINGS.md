# Detailed Findings

## Summary

This document contains the comprehensive technical analysis supporting the findings presented in [README.md](./README.md). Through factorial comparison across 696 task executions, I explored whether models can reliably maintain domain-specific invariants while discovering that evaluation design choices matter more than model configuration for practical applications.

**Key Numbers**:

- 696 total task executions across 2×2×3×2 factorial design
- Task complexity dominates: 11.7-point gap between easiest and hardest task sets
- Invariant maintenance degrades with complexity: 90% success on simple tasks → 61% on complex tasks
- Tool effects minimal: +0.5 points overall (+2.8% success rate)  
- Intermediate reasoning artifacts consistently effective: +5.5 points (+5.0% success rate) across all conditions
- Ground truth errors: 2/2 investigated "consistently failing" tasks had incorrect expected verdicts

## Methodology

### Factorial Design

**Design Matrix**: 2 models (Haiku-4-5, Sonnet-4-5) × 2 tool configurations (claude, claude-tools) × 3 task sets (v2-intermediate, v3-tasks, v4-advanced) × 2 ledger conditions (with-ledger, no-ledger) × 3 runs per condition

**Why This Design Enables Attribution**:

- Single-condition evaluations mask interaction effects
- Factorial comparison isolates model effects from tool effects from task complexity
- Multiple runs capture performance variance and statistical significance
- Systematic A/B testing reveals patterns invisible in manual testing

**Total Executions**: 696 individual task runs producing comprehensive trace data across conditions

### Ground Truth System

**Deterministic Ledger Simulation**: Monthly cash flow calculation with mathematical invariant validation enables isolation of reasoning failures from evaluation framework bugs.

**Three Core Invariants**:

1. **LIQUIDITY_FLOOR**: Cash balance must never fall below threshold (typically $0)
2. **MONEY_CONSERVATION**: Ledger arithmetic must balance exactly (income - outflows = change in cash)
3. **TEMPORAL_CONSISTENCY**: Event timing must respect scenario start/end dates and duration constraints

**Sign Conventions**: Income ≥ 0, outflows ≤ 0, with strict schema validation preventing common modeling errors.

**Temporal Constraints**: Events have start_month and optional duration_months, enabling complex overlapping scenario modeling.

### Scoring System

**5 Dimensions with Variable Point Allocations**:

- **Scenario Generation** (20 pts): Valid JSON, schema compliance, sign conventions
- **Verdict Accuracy** (25 pts): Correct feasible/infeasible determination
- **Violation Detection** (20 pts): Identifying first violation month and invariant type
- **Repair Capability** (20 pts): Successful constraint satisfaction improvements
- **Mathematical Precision** (15 pts): Ledger calculation accuracy vs ground truth

**Why Partial Scoring Matters**: Traditional binary success/failure discards diagnostic value from edge cases. Enhanced scoring captures 16.7% average partial scores on wrong verdicts vs complete information loss, enabling statistical significance through aggregation.

**Variable Totals by Task Type**: Repair tasks have higher possible scores than generation-only tasks, reflecting additional complexity requirements.

## Results: Exploring the Core Questions

### 1. Can Models Maintain Domain-Specific Invariants Across Complexity?

| Task Set | Score | Success Rate | Invariant Violations | What Breaks |
|----------|-------|--------------|---------------------|-------------|
| **v3-tasks (simple)** | 59.8 ± 16.8 | 90.0% | Minimal | Clean constraint satisfaction |
| **v2-intermediate** | 56.9 ± 17.3 | 82.8% | Moderate | Repair loops, timing errors |
| **v4-advanced (complex)** | 48.1 ± 17.0 | 61.3% | High | WRONG_VERDICT (22), REPAIR_FAILED (28) |

**Key Finding**: **Invariant maintenance degrades predictably with complexity**. Models can hold financial constraints (cash conservation, liquidity floors) consistently on simple scenarios but struggle as overlapping events and temporal complexity increase.

**What Breaks First**: The repair mechanisms fail before basic invariant detection. Models correctly identify violations but can't effectively fix them in complex scenarios.

### 2. Model Differences in Invariant Maintenance

| Model | Combined Score | Success Rate | Consistency |
|-------|----------------|--------------|-------------|
| **Sonnet-4-5** | 56.2 ± 17.0 | 81.2% | **More reliable** |
| **Haiku-4-5** | 53.7 ± 17.6 | 74.6% | Higher variance |
| **Difference** | +2.5 pts | +6.6% | Sonnet more stable |

**Key Insight**: Sonnet maintains invariants more consistently across complexity levels, suggesting better systematic reasoning rather than just higher capability.

### 3. Why Do Tools Provide So Little Benefit?

**Overall Tool Impact (Surprising Results)**:

| Condition | Haiku | Sonnet | Combined Effect |
|-----------|-------|--------|-----------------|
| **With Tools** | 53.8 ± 19.7 (77.1%) | 56.5 ± 17.2 (81.4%) | 55.2 ± 18.5 (79.3%) |
| **No Tools** | 53.6 ± 15.5 (72.1%) | 55.8 ± 16.9 (81.0%) | 54.7 ± 16.3 (76.5%) |
| **Tool Effect** | -0.2 pts (-5.0%) | +0.7 pts (+0.4%) | **+0.5 pts (+2.8%)** |

**Tool Usage Pattern Analysis**:
- **Sonnet heavily favors calculator**: 534/938 calls (57%) to `calculate` tool
- **Haiku uses tools evenly**: Balanced across validation, calculation, and advisory tools
- **Tool call bottleneck persists**: 26 EXCEEDED_MAX_TOOL_CALLS despite 20-call limit
- **Critical insight**: Current tool designs don't match model reasoning patterns effectively

**Task Complexity × Tool Interactions**:
| Task Set | Tool Benefit | Interpretation |
|----------|--------------|----------------|
| v3-tasks | +1.5 pts (+6.6%) | **Tools help only on easiest tasks** |
| v2-intermediate | -0.8 pts (-3.5%) | **Tools hurt on medium complexity** |
| v4-advanced | -0.3 pts (+2.5%) | **Tools neutral on hardest tasks** |

### 4. What Makes Intermediate Reasoning Artifacts Effective?

**Ledger Effects Analysis (The Consistent Winner)**:

| Condition | With-Ledger | No-Ledger | Ledger Benefit |
|-----------|-------------|-----------|----------------|
| **v2-intermediate** | 60.7 ± 17.8 (88.1%) | 53.1 ± 17.9 (77.0%) | **+7.6 pts (+11.1%)** |
| **v3-tasks** | 60.4 ± 16.4 (90.0%) | 57.5 ± 17.2 (86.7%) | **+2.9 pts (+3.3%)** |
| **v4-advanced** | 51.2 ± 17.8 (61.7%) | 45.0 ± 16.2 (61.0%) | **+6.2 pts (+0.7%)** |
| **Combined** | 57.4 ± 17.4 (79.9%) | 51.9 ± 17.6 (74.9%) | **+5.5 pts (+5.0%)** |

**Why Ledgers Work Where Tools Don't**:
- **Forces structured thinking**: Intermediate calculations make reasoning explicit
- **Error detection**: Computational mistakes become visible and correctable  
- **Independent of complexity**: Benefits across all task difficulty levels
- **Model-agnostic**: Works equally well for Haiku (+5.4 pts) and Sonnet (+5.6 pts)

**Critical Insight**: Explicit intermediate steps consistently improve performance while external tool access doesn't. This suggests internal reasoning structure matters more than external computation access.

### 5. Task Complexity as Dominant Factor

**Evaluation Design Choice Impact**:

| Task Set | Combined Score | Success Rate | Difficulty Rank |
|----------|----------------|--------------|-----------------|
| **v3-tasks** | 59.8 ± 16.8 (90.0%) | 90.0% | 1 (Easiest) |
| **v2-intermediate** | 56.9 ± 17.3 (82.8%) | 82.8% | 2 (Medium) |
| **v4-advanced** | 48.1 ± 17.0 (61.3%) | 61.3% | 3 (Hardest) |
| **Performance Gap** | **11.7 points** | **28.7%** | **Large effect** |

**Complexity Dominance**: Task difficulty is the strongest predictor of performance, with an 11.7-point gap that dwarfs model differences (2.5 points) or tool effects (0.5 points).

**Error Pattern Correlation**: More complex tasks show higher rates of WRONG_VERDICT (22 instances in v4) and REPAIR_FAILED (28 instances in v4) compared to simpler task sets.

### 6. Distinguishing Model vs Evaluation Framework Limitations

**The Humbling Discovery**: Manual verification of "consistently failing" tasks revealed evaluation framework errors, not model limitations.

**Specific Cases**:
1. **graduate_school_prep**: Expected "feasible" but Claude consistently returned "infeasible" across all 24 conditions
   - **Investigation**: Manual calculation confirmed Claude was correct - expenses exceed income capacity  
   - **Fix**: Updated expected verdict to match mathematical reality

2. **sabbatical_complex**: Expected "infeasible" but missing first_violation_month specification
   - **Investigation**: Task definition incomplete despite expecting violation
   - **Fix**: Added missing first_violation_month field

**What I Learned**: Systematic cross-model agreement against expected results warrants ground truth investigation before assuming model capability limitations. Models were being penalized for correct mathematical reasoning.

**Protocol Developed**:
- **Systematic vs random failure analysis**: Consistent patterns warrant investigation
- **Cross-model validation**: Agreement against expected results suggests evaluation bugs  
- **Manual verification**: Mathematical validation against deterministic simulation
- **Trace-driven debugging**: Comprehensive logging enables retrospective analysis

### 7. Effect Size Hierarchy and Practical Implications

**What Matters Most for Applications**:
1. **Task Complexity**: 11.7-point range (dominant factor)
2. **Intermediate Reasoning Artifacts**: 5.5-point average benefit (reliable improvement)  
3. **Model Choice**: 2.5-point difference (consistent but smaller)
4. **Tool Access**: 0.5-point benefit (minimal/inconsistent effect)

**For Practical Applications**: Focus on task design and intermediate artifacts over tool integration or model optimization.

### 8. Updated Failure Mode Analysis

**Error Distribution by Tool Condition**:

**With Tools (348 executions)**:
- EXCEEDED_MAX_TOOL_CALLS: 26 (7.5%) - persistent bottleneck
- REPAIR_FAILED: 17 (4.9%)  
- WRONG_VERDICT: 16 (4.6%)

**No Tools (348 executions)**:
- REPAIR_FAILED: 41 (11.8%) - dominant failure mode
- WRONG_VERDICT: 17 (4.9%)
- WRONG_FIRST_VIOLATION_MONTH: 12 (3.4%)

**Key Insight**: Tools reduce repair failures but introduce tool call limitations, with minimal net benefit overall.

## Lessons About Evaluation Quality

### Ground Truth Verification

**The Humbling Discovery**: Manual verification of "consistently failing" tasks revealed evaluation framework errors, not model limitations.

**Specific Cases**:

1. **graduate_school_prep**: Expected "feasible" but Claude consistently returned "infeasible" across all 24 conditions
   - **Investigation**: Manual calculation confirmed Claude was correct - expenses exceed income capacity
   - **Fix**: Updated expected verdict to match mathematical reality
2. **sabbatical_complex**: Expected "infeasible" but missing first_violation_month specification
   - **Investigation**: Task definition incomplete despite expecting violation
   - **Fix**: Added missing first_violation_month field

**What I Learned**: Systematic cross-model agreement against expected results warrants ground truth investigation before assuming model capability limitations. Models were being penalized for correct mathematical reasoning.

### Specification Ambiguity

**Duration Semantics Challenge**: Despite explicit prompt warnings, models consistently omit `duration_months: 1` for one-time expenses. This appears to be a limitation of natural language specification rather than model capability.

**Limits of Prompt Engineering**: Some edge cases resist prompt-based solutions and require schema-level constraints or alternative specification approaches.

**Protocol for Distinguishing Failures**: Implemented systematic analysis of consistent vs random failures to distinguish model limitations from evaluation framework bugs.

## System Improvements Made

### Changes Based on Data

**Tool Call Limit Optimization (10→20)**:

- **Evidence**: 55 violations across initial comparison runs
- **Analysis**: Complex mathematical reasoning chains require more tool calls than estimated
- **Impact**: Expected elimination of constraint-based failures in subsequent runs

**JSON Extraction Enhancement**:

- **Before**: 45% INVALID_JSON rate due to mixed explanatory text
- **After**: 3% failure rate through brace counting and enhanced parsing
- **Method**: Structured extraction logic resilient to model output variations

**Task Definition Corrections**:

- Fixed expected verdicts based on manual mathematical verification
- Added missing constraint specifications (first_violation_month)
- Established protocol for ground truth validation

**Enhanced Reporting Attribution**:

- Separated agent architecture (claude vs claude-tools) from model specification (haiku vs sonnet)
- Enables precise performance attribution across factorial design
- Resolved ambiguity in comparison analysis

## Milestones

**M0**: Core simulation engine + golden test fixtures  
**M1**: Task runner, traces, error taxonomy, CLI infrastructure  
**M2**: Claude integration with constraint-based repair system  
**M3**: Advanced scoring, parallel task evaluation, enhanced UX  
**M4**: Tool calling integration with calculator, validation, and advisory tools  
**M4.5**: Systematic comparison framework for A/B testing across models and configurations  
**M5**: Multivariate analysis, constraint optimization, evaluation quality improvements

## Open Questions

**Why Do Tools Provide So Little Benefit**: Despite seeming obviously useful for mathematical reasoning, tools improved performance by only 0.5 points overall. Is this a fundamental limitation of current tool designs, or specific to financial reasoning tasks?

**What Makes Intermediate Artifacts Effective**: Ledger provision consistently improved performance by 5.5 points across all conditions. What cognitive mechanisms make explicit intermediate steps more beneficial than tool access?

**Generalizability Beyond Financial Reasoning**: Do these patterns (minimal tool benefit, strong intermediate artifact effects, task complexity dominance) hold across other structured reasoning domains?

**Tool Call Efficiency Problem**: Models still hit 20-call limits on complex tasks. Is this a fundamental mismatch between tool interaction patterns and model reasoning strategies?

**Evaluation Framework Generalization**: The factorial design revealed interaction effects invisible in single-condition evaluations. When do infrastructure constraints masquerade as capability limitations in other evaluation contexts?

## Appendix

### Task Set Descriptions

**v1-simple (16 tasks)**: Basic feasibility scenarios with clear constraints, both with and without ledger generation requirements.

**v2-intermediate (14 tasks)**: Medium complexity scenarios with overlapping events and temporal constraints, designed to test multi-step reasoning.

**v3-tasks (5 tasks)**: Ledger-focused validation tests specifically designed to assess calculation accuracy and constraint detection.

**v4-advanced (10 tasks)**: Complex natural language scenarios with multiple events, duration modeling, and realistic financial planning complexity.

### Task Folder Structure

**With Ledger Generation**: v1-simple-with-ledger, v2-intermediate-with-ledger, v3-tasks-with-ledger, v4-advanced-with-ledger

**Without Ledger Generation**: v1-simple-no-ledger, v2-intermediate-no-ledger, v3-tasks-no-ledger, v4-advanced-no-ledger

**Design Intent**: Systematic evaluation of whether requesting intermediate artifacts (detailed calculations) improves reasoning accuracy across complexity levels.

### Full Results Summary

Complete statistical analysis available in comparison reports at `reports/comparison_*`. Key aggregate findings confirm interaction effects and support tool effectiveness reversal conclusions across all measured dimensions.
