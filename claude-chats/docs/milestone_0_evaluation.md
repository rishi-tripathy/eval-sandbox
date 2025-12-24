# Milestone 0 Evaluation: Deterministic Core

## Overview
Milestone 0 established the foundation of the eval system - a deterministic financial simulator with invariant checking. This milestone tested Rishi's ability to translate abstract concepts into concrete implementations.

## Key Accomplishments

### 1. Month Type Implementation
- **Decision**: Created a custom Month type with internal index representation (year*12 + month)
- **Quality**: Excellent design - supports arithmetic, comparison, string parsing, and iteration
- **Learning moment**: Struggled with Pydantic serialization, eventually solved with `__json__` and `model_dump` methods
- **Alternative considered**: Using datetime objects (rejected for unnecessary complexity)

### 2. Data Models (Pydantic v2)
- **Event**: Correctly enforced sign conventions on amounts
- **BaseMonthly**: Validated takehome_salary ≥ 0, outflows ≤ 0
- **Scenario**: Cross-validated event timing against scenario bounds
- **Challenge**: Pydantic v1 vs v2 syntax confusion - learned about `model_validator(mode='after')`

### 3. Simulation Engine
- **Key insight**: Events with `duration_months=None` run through horizon
- **Quality**: Clean separation between event activation logic and monthly calculation
- **Design choice**: All events apply simultaneously within a month (no ordering)

### 4. Invariant System
- **LIQUIDITY_FLOOR**: Cash must stay ≥ 0
- **MONEY_CONSERVATION**: Ledger arithmetic must balance
- **TEMPORAL_CONSISTENCY**: Events only apply within valid windows
- **Smart design**: Returns list of ALL violations, not just first
- **Precedence rules**: Clear ordering for tie-breaking

### 5. Integration (run_eval)
- **Clean API**: Single entry point returning structured EvalResult
- **First-violation logic**: Correctly implemented with precedence rules
- **Edge case handling**: Empty simulation returns sensible defaults

## Technical Growth Demonstrated

### Strengths
1. **Conceptual understanding**: Quickly grasped deterministic testing philosophy
2. **Problem decomposition**: Breaking complex system into clean modules
3. **Type system usage**: Leveraged Python's type hints effectively
4. **Test-driven approach**: Built comprehensive golden tests

### Areas Improved
1. **Pydantic mastery**: Learned v2 patterns through trial and error
2. **Custom type integration**: Solved Month serialization challenges
3. **Edge case thinking**: Handled None durations, empty scenarios

## Product Thinking

### Good Decisions
- Month arithmetic design enables intuitive date math
- Sign conventions prevent common financial modeling errors
- Returning all violations aids debugging
- Separating simulation from evaluation enables testing

### Questionable Choices
- Month serialization hack feels brittle
- No explicit handling of floating point precision
- Validation messages could be more user-friendly

## Learning Partnership Assessment

Rishi demonstrated:
- **Persistence**: Worked through Pydantic issues methodically
- **First principles thinking**: Questioned design choices appropriately
- **Implementation speed**: ~1 hour for complex system
- **Debugging skills**: Used error messages to guide solutions

## Overall Grade: A-

Strong foundation implementation with minor rough edges. The deterministic core is solid and will support the rest of the system well. Key learning: building reliable systems requires careful attention to data modeling and edge cases.