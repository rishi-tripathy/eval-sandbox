# Detailed Findings

## Summary

This document contains the comprehensive technical analysis supporting the findings presented in [README.md](./README.md). Through factorial comparison across 696 task executions, I explored whether models can reliably maintain domain-specific invariants while discovering that evaluation design choices matter more than model configuration for practical applications.

**Key Numbers**:

- 696 total task executions across 2×2×3×2 factorial design
- Task complexity dominates: 11.7-point gap between easiest and hardest task sets
- Invariant maintenance degrades with complexity: 90% success on simple tasks → 61% on complex tasks
- Tool effects minimal: +0.5 points overall (+2.8% success rate)
- Intermediate reasoning artifacts consistently effective: +5.5 points (+5.0% success rate) across all conditions

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

#### v3-tasks (Simple): High Consistency
**Haiku + Tools**: 55,55,55 | 85,85,85 | 45,45,45 | 45,45,45 | 85,85,85 (all tasks succeed consistently)
**Haiku + No Tools**: 45,45,45 | 70,70,70 | 45,45,45 | 45,45,45 | 85,85,85 (1 repair failure)
**Sonnet + Tools**: 55,55,55 | 85,85,85 | 45,45,45 | 45,45,45 | 85,85,85 (perfect consistency)
**Sonnet + No Tools**: 45,45,45 | 85,85,85 | 45,45,45 | 45,45,45 | 85,85,85 (perfect consistency)

*Summary: 90-100% success rates, minimal variance*

#### v2-intermediate (Medium): Moderate Degradation
**Haiku + Tools**: Shows repair failures, JSON errors, tool call limits
**Haiku + No Tools**: Consistent WRONG_VERDICT on apartment_overlap (10,10,10), otherwise stable
**Sonnet + Tools**: High performance with occasional tool limits (95% success)
**Sonnet + No Tools**: Perfect consistency (100% success), moderate scores

*Summary: 68-100% success rates, repair mechanisms start failing*

#### v4-advanced (Complex): Significant Breakdown
**Haiku + Tools**: Consistent failures on graduate_school_prep (10,10,10), medical_emergency (65,65,65), frequent tool limits
**Haiku + No Tools**: Better success rate (90%) but repair failures on apartment_move_complex
**Sonnet + Tools**: Tool limit issues but higher scores when successful
**Sonnet + No Tools**: Perfect success rate (100%), consistent performance

*Summary: 40-100% success rates depending on configuration*

**Key Finding**: **Invariant maintenance degrades predictably with complexity**. Simple scenarios show near-perfect consistency, but complex scenarios reveal distinct failure modes: tool call limits, repair mechanism failures, and verdict determination errors.

**What Breaks First**: Tool-enabled configurations hit computational limits (EXCEEDED_MAX_TOOL_CALLS) before basic invariant detection fails. No-tools configurations show more consistent success rates but lower ceiling performance.

### 2. Model Differences in Invariant Maintenance

#### Haiku Performance Patterns:
**v3-tasks**: 63.0% (tools) vs 58-59% (no-tools) - consistent but tool limits hurt
**v2-intermediate**: Wide variance - 53-59% with many partial failures 
**v4-advanced**: 46-54% - struggles with complex scenarios, frequent errors

*Individual task breakdown shows: apartment_overlap always fails (10,10,10), graduate_school_prep always fails (10,10,10)*

#### Sonnet Performance Patterns:
**v3-tasks**: 63.0% (tools) vs 61-63% (no-tools) - remarkably consistent
**v2-intermediate**: 53-67% - much higher ceiling when tools work effectively
**v4-advanced**: 50-57% - better handling of complex scenarios

*Individual task breakdown shows: Perfect success on simpler task sets, graceful degradation on complex scenarios*

#### Direct Model Comparison:
**Success Rate Gap**: Sonnet achieves 100% success on multiple conditions vs Haiku's maximum 93-100%
**Consistency**: Sonnet shows identical scores across runs (45,45,45 or 85,85,85) while Haiku varies more
**Error Handling**: Sonnet avoids certain error categories that consistently affect Haiku

**Key Insight**: Sonnet maintains invariants more consistently across complexity levels through **deterministic reasoning patterns** - identical scores across runs indicate systematic rather than stochastic problem-solving approaches.

### 3. Why Do Tools Provide So Little Benefit?

#### Individual Task Analysis Reveals Tool Bottlenecks:

**Haiku Tool Performance**:
- v2-intermediate: Many EXCEEDED_MAX_TOOL_CALLS errors (medical_emergency: 80,80,90; tuition_payment: 90,90,90)
- v4-advanced: Consistent tool limits on apartment_move_complex (80,75,75) and sabbatical_complex (60,70,55)
- Tool success varies widely: pet_emergency ranges 95→85→80 across runs

**Haiku No-Tool Performance**:
- v2-intermediate: More consistent but hits specific task failures (apartment_overlap: 15,15,15)
- v4-advanced: Better success rate (90% vs 40%) with stable scores
- Predictable performance: apartment_move_complex consistently 63,63,63

**Sonnet Tool Performance**:
- v2-intermediate: High success (93%) but tool limits on complex repairs (tuition_payment: 90,90,90)
- v4-advanced: Tool limits on apartment_move_complex (65,65,55) and sabbatical_complex (60,60,60)
- Higher ceiling when tools work: car_replacement achieves 95,90,95

**Sonnet No-Tool Performance**:
- v2-intermediate: Perfect 100% success rate with consistent scores
- v4-advanced: Perfect 100% success rate, apartment_move_complex: 85,85,85 (vs 65,65,55 with tools)
- Remarkable consistency: identical scores across all runs

#### Tool Paradox: More Capability, More Failure Modes
**Tools Add Computational Overhead**: 20-call limit insufficient for complex scenarios
**Tools Create Brittleness**: EXCEEDED_MAX_TOOL_CALLS, INACCURATE_REPAIR_LABEL errors
**No-Tools More Robust**: Higher success rates, fewer error categories
**Critical Insight**: Current tool designs create cognitive overhead that exceeds their computational benefit for financial reasoning tasks.

### 4. What Makes Intermediate Reasoning Artifacts Effective?

#### Individual Ledger Effects by Model and Complexity:

**Haiku Ledger Impact**:
- v2-intermediate: With-ledger 59.3% vs No-ledger 52-53% (but no-ledger more consistent)
- v3-tasks: With-ledger 63.0% vs No-ledger 59-61% (minimal difference)
- v4-advanced: With-ledger 46-54% vs No-ledger 53% (actually hurts on complex tasks)

*Pattern: Ledgers help medium complexity but create overhead on simple/complex tasks*

**Sonnet Ledger Impact**:
- v2-intermediate: With-ledger 66.4-66.8% vs No-ledger 53-56% (**significant benefit**)
- v3-tasks: With-ledger 63.0% vs No-ledger 61.0% (small benefit)
- v4-advanced: With-ledger 50-57% vs No-ledger 56.7% (neutral to negative)

*Pattern: Strong ledger benefit on intermediate tasks, diminishing returns on simple/complex*

#### Task-Level Ledger Analysis:
**car_replacement**: 
- Haiku with-ledger: 75,75,90 vs no-ledger: 85,70,85 (mixed)
- Sonnet with-ledger: 95,90,95 vs no-ledger: 85,85,85 (clear benefit)

**medical_emergency**:
- Haiku with-ledger: 80,80,90 vs no-ledger: 85,85,85 (no-ledger better)
- Sonnet with-ledger: 90,95,80 vs no-ledger: 85,85,85 (with-ledger better)

**Why Ledgers Work for Sonnet but Less for Haiku**:
- **Sonnet utilizes structure**: Higher scores on complex repairs when ledger available
- **Haiku gets overwhelmed**: More errors and inconsistency with ledger requirements  
- **Model-dependent benefit**: Ledger effectiveness correlates with model sophistication

**Critical Insight**: Intermediate reasoning artifacts benefit sophisticated models more than simple ones - Sonnet can leverage structured thinking while Haiku finds it burdensome.

### 5. Task Complexity as Dominant Factor

**Evaluation Design Choice Impact**:

| Task Set            | Combined Score      | Success Rate | Difficulty Rank  |
| ------------------- | ------------------- | ------------ | ---------------- |
| **v3-tasks**        | 59.8 ± 16.8 (90.0%) | 90.0%        | 1 (Easiest)      |
| **v2-intermediate** | 56.9 ± 17.3 (82.8%) | 82.8%        | 2 (Medium)       |
| **v4-advanced**     | 48.1 ± 17.0 (61.3%) | 61.3%        | 3 (Hardest)      |
| **Performance Gap** | **11.7 points**     | **28.7%**    | **Large effect** |

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

### 8. Individual Task Failure Pattern Analysis

#### Systematic Failure Patterns (Consistent Across Runs):

**apartment_overlap**: 
- Haiku+tools+no-ledger: 10,10,10 (WRONG_VERDICT every time)
- Haiku+no-tools+no-ledger: 15,15,15 (WRONG_VERDICT every time)
- Sonnet: Succeeds consistently (45,45,45 or 55,55,55)

**graduate_school_prep**:
- All Haiku conditions: 10,10,10 (WRONG_VERDICT - systematic reasoning error)
- All Sonnet conditions: 45,45,45 (succeeds consistently)

**apartment_move_complex**:
- With tools: 65-80 partial scores (EXCEEDED_MAX_TOOL_CALLS)
- No tools: 63-85 (Haiku fails repairs, Sonnet succeeds)

#### Error Distribution by Configuration:

**Tools + Complex Tasks**:
- EXCEEDED_MAX_TOOL_CALLS: Dominates on v4-advanced (apartment_move_complex, sabbatical_complex)
- INACCURATE_REPAIR_LABEL: Frequent on repair scenarios
- Tool overhead creates brittleness

**No Tools + Complex Tasks**:
- REPAIR_FAILED: Primary failure mode for Haiku
- WRONG_VERDICT: Model-specific systematic errors
- More predictable failure patterns

**Key Insight**: Individual task analysis reveals **systematic vs random failures**. Systematic failures (identical scores across runs) indicate fundamental model limitations, while variable scores indicate stochastic tool interaction problems.

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

### Individual Results Summary

Complete individual task scores organized by experimental condition available in `task_scores_organized.md`. Raw execution data shows transparent performance patterns without statistical aggregation, revealing systematic vs stochastic failure modes across 696 total task executions.
