# Factorial Analysis Results for FINDINGS.md

This document provides the proper factorial analysis tables to replace the misleading mean±std tables in FINDINGS.md. The analysis is based on the actual 2×2×2×3 experimental design with 3 runs per condition.

## 1. Base Factorial Table (2×2×2×3)

Complete breakdown of all 24 experimental conditions:

| Agent    | Model  | Ledger | Task Set | Avg Score | N Tasks | Success % | Std Dev |
|----------|--------|--------|----------|-----------|---------|-----------|---------|
| no-tools | haiku  | no     | v2       | 90.8%     | 42      | 76.2%     | 21.9    |
| no-tools | haiku  | yes    | v2       | 80.8%     | 42      | 76.2%     | 14.9    |
| no-tools | sonnet | no     | v2       | 98.2%     | 42      | 92.9%     | 6.8     |
| no-tools | sonnet | yes    | v2       | 89.9%     | 42      | 100.0%    | 7.6     |
| tools    | haiku  | no     | v2       | 88.9%     | 42      | 83.3%     | 28.4    |
| tools    | haiku  | yes    | v2       | 82.2%     | 42      | 76.2%     | 20.0    |
| tools    | sonnet | no     | v2       | 97.3%     | 42      | 85.7%     | 7.2     |
| tools    | sonnet | yes    | v2       | 85.4%     | 42      | 76.2%     | 7.6     |
| no-tools | haiku  | no     | v3       | 94.8%     | 15      | 80.0%     | 10.7    |
| no-tools | haiku  | yes    | v3       | 79.3%     | 15      | 80.0%     | 8.1     |
| no-tools | sonnet | no     | v3       | 98.3%     | 15      | 93.3%     | 6.7     |
| no-tools | sonnet | yes    | v3       | 77.9%     | 15      | 80.0%     | 10.1    |
| tools    | haiku  | no     | v3       | 98.8%     | 15      | 93.3%     | 4.5     |
| tools    | haiku  | yes    | v3       | 82.3%     | 15      | 100.0%    | 6.7     |
| tools    | sonnet | no     | v3       | 96.5%     | 15      | 86.7%     | 9.1     |
| tools    | sonnet | yes    | v3       | 82.3%     | 15      | 100.0%    | 6.7     |
| no-tools | haiku  | no     | v4       | 82.9%     | 30      | 60.0%     | 25.4    |
| no-tools | haiku  | yes    | v4       | 78.1%     | 30      | 60.0%     | 23.9    |
| no-tools | sonnet | no     | v4       | 82.9%     | 30      | 60.0%     | 25.4    |
| no-tools | sonnet | yes    | v4       | 79.5%     | 30      | 60.0%     | 23.1    |
| tools    | haiku  | no     | v4       | 75.3%     | 30      | 56.7%     | 35.4    |
| tools    | haiku  | yes    | v4       | 74.3%     | 30      | 53.3%     | 30.4    |
| tools    | sonnet | no     | v4       | 86.2%     | 30      | 70.0%     | 25.0    |
| tools    | sonnet | yes    | v4       | 82.8%     | 30      | 70.0%     | 23.8    |

## 2. Main Effects Analysis

### Agent Effect (Tools vs No-Tools)
- **no-tools**: 86.4% avg score (n=348, success=76.7%, std=19.0)
- **tools**: 85.7% avg score (n=348, success=76.7%, std=22.3)
- **Tools Effect**: **-0.7 percentage points** (minimal impact)

### Model Effect (Haiku vs Sonnet)
- **haiku**: 83.5% avg score (n=348, success=72.7%, std=23.7)
- **sonnet**: 88.6% avg score (n=348, success=80.7%, std=16.8)
- **Sonnet Effect**: **+5.2 percentage points** (moderate positive impact)

### Ledger Effect (Yes vs No)
- **no**: 90.2% avg score (n=348, success=77.3%, std=22.2)
- **yes**: 81.8% avg score (n=348, success=76.1%, std=18.2)
- **Ledger Effect**: **-8.4 percentage points** (strong negative impact)

### Task Complexity Effect (v2 vs v3 vs v4)
- **v2**: 89.2% avg score (n=336, success=83.3%, std=17.2)
- **v3**: 88.8% avg score (n=120, success=89.2%, std=11.6)
- **v4**: 80.2% avg score (n=240, success=61.3%, std=26.7)
- **v4 vs v2**: **-8.9 percentage points** (strong negative impact)

## 3. Interaction Effects

### AGENT × MODEL Interaction
| Agent    | Model  | Avg Score | Success Rate |
|----------|--------|-----------|--------------|
| no-tools | haiku  | 84.2%     | 71.3%        |
| no-tools | sonnet | 88.6%     | 82.2%        |
| tools    | haiku  | 82.7%     | 74.1%        |
| tools    | sonnet | 88.7%     | 79.3%        |

**Interaction strength**: 1.6 percentage points (weak interaction)

### AGENT × LEDGER Interaction
| Agent    | Ledger | Avg Score | Success Rate |
|----------|--------|-----------|--------------|
| no-tools | no     | 90.8%     | 76.4%        |
| no-tools | yes    | 81.9%     | 77.0%        |
| tools    | no     | 89.6%     | 78.2%        |
| tools    | yes    | 81.7%     | 75.3%        |

### MODEL × LEDGER Interaction  
| Model  | Ledger | Avg Score | Success Rate |
|--------|--------|-----------|--------------|
| haiku  | no     | 87.4%     | 73.6%        |
| haiku  | yes    | 79.6%     | 71.8%        |
| sonnet | no     | 93.1%     | 81.0%        |
| sonnet | yes    | 84.1%     | 80.5%        |

### AGENT × TASK_SET Interaction
| Agent    | Task Set | Avg Score | Success Rate |
|----------|----------|-----------|--------------|
| no-tools | v2       | 89.9%     | 86.3%        |
| no-tools | v3       | 87.6%     | 83.3%        |
| no-tools | v4       | 80.9%     | 60.0%        |
| tools    | v2       | 88.5%     | 80.4%        |
| tools    | v3       | 90.0%     | 95.0%        |
| tools    | v4       | 79.6%     | 62.5%        |

## 4. Individual Task Consistency

### High Consistency Tasks (std dev < 5.0)
Found **195** highly consistent task-condition combinations where runs show nearly identical scores.

**Examples of perfect consistency (std=0.0)**:
- apartment_overlap (no-tools + haiku + no + v2): [17.6%, 17.6%, 17.6%]
- bonus_splurge (no-tools + haiku + no + v2): [100%, 100%, 100%]
- car_replacement (no-tools + haiku + no + v2): [82.4%, 82.4%, 82.4%]

### High Variance Tasks (std dev > 20.0)
Found **7** highly variable task-condition combinations:

1. **apartment_overlap** (no-tools + haiku + yes + v2): [91.7%, 30.0%, 30.0%] (std=35.6)
2. **seasonal_business** (tools + haiku + no + v2): [35.3%, 0.0%, 100.0%] (std=50.7)
3. **job_transition** (tools + haiku + yes + v2): [75.0%, 0.0%, 75.0%] (std=43.3)
4. **seasonal_business** (tools + haiku + yes + v2): [91.7%, 75.0%, 0.0%] (std=48.8)
5. **freelance_irregular** (tools + haiku + no + v4): [100%, 0%, 100%] (std=57.7)
6. **medical_emergency** (tools + haiku + no + v4): [0%, 0%, 76.5%] (std=44.2)
7. **home_office_setup** (tools + haiku + yes + v4): [91.7%, 0%, 0%] (std=52.9)

### Task-Specific Failure Patterns

**Tasks with <50% success rate across all conditions**:
- **apartment_move_complex**: 0.0% success rate
- **graduate_school_prep**: 0.0% success rate  
- **sabbatical_complex**: 0.0% success rate
- **tuition_payment**: 33.3% success rate
- **medical_emergency**: 45.8% success rate
- **ledger_02_simple_infeasible**: 45.8% success rate

### Tasks Most Sensitive to Agent Type (Tools vs No-Tools)

1. **seasonal_business**: 18.6pp difference (tools=73.1%, no-tools=91.7%)
2. **home_office_setup**: 13.9pp difference (tools=80.6%, no-tools=94.5%)
3. **apartment_move_complex**: 13.4pp difference (tools=71.9%, no-tools=58.5%)
4. **ledger_02_simple_infeasible**: 12.1pp difference (tools=86.7%, no-tools=74.6%)
5. **freelance_irregular**: 8.3pp difference (tools=87.5%, no-tools=95.8%)

## 5. Key Insights & Summary

### Overall Statistics
- **Total task executions**: 696
- **Overall success rate**: 76.7%
- **Overall average score**: 86.0%

### Key Factor Effects (in order of impact)
1. **Task Complexity (v4 vs v2)**: **-8.9 percentage points** (largest effect)
2. **Ledger (Yes vs No)**: **-8.4 percentage points** (strong negative effect)
3. **Model (Sonnet vs Haiku)**: **+5.2 percentage points** (moderate positive effect)
4. **Agent (Tools vs No-Tools)**: **-0.7 percentage points** (minimal effect)

### Best vs Worst Performing Configurations
- **Best**: tools + sonnet + ledger=no: **93.4%** avg score
- **Worst**: tools + haiku + ledger=yes: **79.5%** avg score
- **Performance gap**: **13.8 percentage points**

## Key Takeaways for FINDINGS.md

1. **Tools provide minimal benefit**: The agent effect is only -0.7pp, contradicting claims about tools helping significantly.

2. **Ledger information hurts performance**: Providing ledger context reduces scores by 8.4pp across all conditions.

3. **Sonnet outperforms Haiku**: +5.2pp advantage, consistent across conditions.

4. **Task complexity matters most**: v4 tasks are 8.9pp harder than v2 tasks.

5. **High consistency in most conditions**: 195/235 task-condition combinations show low variance, indicating deterministic behavior.

6. **Specific problematic tasks**: 6 tasks have systemic issues with <50% success rates.

7. **Interaction effects are weak**: No strong interactions between factors, suggesting independent effects.

This factorial analysis reveals the true structure of the evaluation results and should replace any mean±std summary tables that don't account for the experimental design.