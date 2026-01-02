# Individual Task Scores by Experimental Condition

Based on the results from `/Users/rishi/Documents/Workspace/eval-sandbox/reports/full-set-results.txt`, here are the individual task scores organized by experimental condition. The file contains results for both TOOLS and NO TOOLS conditions across 2 models × 6 task-sets × 3 runs = 36 total combinations each.

## TOOLS CONDITIONS

## HAIKU - v2-intermediate - with-ledger - tools

- apartment_overlap: 55,45,55
- bonus_splurge: 55,45,55
- car_replacement: 75(EXCEEDED_MAX_TOOL_CALLS),75(INACCURATE_REPAIR_LABEL),90
- commission_drought: 45,45,45
- freelance_ramp: 55,55,55
- home_repair_cascade: 55,55,55
- job_transition: 45,0(INVALID_JSON),45
- medical_emergency: 80(EXCEEDED_MAX_TOOL_CALLS),80(EXCEEDED_MAX_TOOL_CALLS),90
- pet_emergency: 95,85(EXCEEDED_MAX_TOOL_CALLS),80(INACCURATE_REPAIR_LABEL)
- seasonal_business: 55,45,0(INVALID_JSON)
- student_loan_payment: 55,55,55
- tuition_payment: 90(EXCEEDED_MAX_TOOL_CALLS),90,90(EXCEEDED_MAX_TOOL_CALLS)
- vacation_fund: 55,55,55
- wedding_guest_spree: 55,55,55

**Summary:**
- Mean Score (all): 59.3
- Success Rate: 67.9%
- Mean Score (successful only): 65.3
- Total runs: 42

---

## HAIKU - v2-intermediate - no-ledger - tools

- apartment_overlap: 10(WRONG_VERDICT),10(WRONG_VERDICT),10(WRONG_VERDICT)
- bonus_splurge: 45,45,45
- car_replacement: 85,70(INACCURATE_REPAIR_LABEL),85
- commission_drought: 45,45,45
- freelance_ramp: 45,45,45
- home_repair_cascade: 45,45,45
- job_transition: 45,45,45
- medical_emergency: 85,85,85
- pet_emergency: 85,85,85
- seasonal_business: 30(WRONG_VERDICT),0(INVALID_JSON),45
- student_loan_payment: 45,45,45
- tuition_payment: 70(INACCURATE_REPAIR_LABEL),85,85
- vacation_fund: 45,45,45
- wedding_guest_spree: 45,45,45

**Summary:**
- Mean Score (all): 53.2
- Success Rate: 83.3%
- Mean Score (successful only): 58.6
- Total runs: 42

---

## HAIKU - v3-tasks - with-ledger - tools

- ledger_01_simple_feasible: 55,55,55
- ledger_02_simple_infeasible: 85,85,85
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 63.0
- Success Rate: 100.0%
- Mean Score (successful only): 63.0
- Total runs: 15

---

## HAIKU - v3-tasks - no-ledger - tools

- ledger_01_simple_feasible: 45,45,45
- ledger_02_simple_infeasible: 85,70(INACCURATE_REPAIR_LABEL),85
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 61.3
- Success Rate: 93.3%
- Mean Score (successful only): 62.9
- Total runs: 15

---

## HAIKU - v4-advanced - with-ledger - tools

- apartment_move_complex: 80(EXCEEDED_MAX_TOOL_CALLS),75(EXCEEDED_MAX_TOOL_CALLS),75(EXCEEDED_MAX_TOOL_CALLS)
- car_lease_promotion: 45,45,45
- freelance_irregular: 55,55,55
- graduate_school_prep: 10(WRONG_VERDICT),10(WRONG_VERDICT),10(WRONG_VERDICT)
- home_office_setup: 55,0(INVALID_JSON),0(INVALID_JSON)
- medical_emergency: 65(WRONG_FIRST_VIOLATION_MONTH),65(WRONG_FIRST_VIOLATION_MONTH),65(WRONG_FIRST_VIOLATION_MONTH)
- sabbatical_complex: 60(EXCEEDED_MAX_TOOL_CALLS),70(EXCEEDED_MAX_TOOL_CALLS),55(EXCEEDED_MAX_TOOL_CALLS)
- side_hustle_growth: 55,55,55
- simple_bonus: 55,55,55
- wedding_season_chaos: 45,45,45

**Summary:**
- Mean Score (all): 46.5
- Success Rate: 40.0%
- Mean Score (successful only): 51.7
- Total runs: 30

---

## HAIKU - v4-advanced - no-ledger - tools

- apartment_move_complex: 63(REPAIR_FAILED),63(REPAIR_FAILED),63(REPAIR_FAILED)
- car_lease_promotion: 45,45,45
- freelance_irregular: 45,45,45
- graduate_school_prep: 45,45,45
- home_office_setup: 45,45,45
- medical_emergency: 85,85,85
- sabbatical_complex: 85,85,85
- side_hustle_growth: 45,45,45
- simple_bonus: 45,45,45
- wedding_season_chaos: 45,45,45

**Summary:**
- Mean Score (all): 53.1
- Success Rate: 90.0%
- Mean Score (successful only): 53.7
- Total runs: 30

---

## SONNET - v2-intermediate - with-ledger - tools

- apartment_overlap: 55,55,45
- bonus_splurge: 55,55,55
- car_replacement: 95,90,95
- commission_drought: 45,45,45
- freelance_ramp: 55,55,55
- home_repair_cascade: 45,45,45
- job_transition: 45,45,45
- medical_emergency: 90,95,80(EXCEEDED_MAX_TOOL_CALLS)
- pet_emergency: 95,95,95
- seasonal_business: 55,55,55
- student_loan_payment: 55,55,55
- tuition_payment: 90(EXCEEDED_MAX_TOOL_CALLS),90(EXCEEDED_MAX_TOOL_CALLS),90(EXCEEDED_MAX_TOOL_CALLS)
- vacation_fund: 55,55,55
- wedding_guest_spree: 55,55,55

**Summary:**
- Mean Score (all): 66.4
- Success Rate: 92.9%
- Mean Score (successful only): 67.8
- Total runs: 42

---

## SONNET - v2-intermediate - no-ledger - tools

- apartment_overlap: 45,45,45
- bonus_splurge: 45,45,45
- car_replacement: 85,85,85
- commission_drought: 45,45,45
- freelance_ramp: 45,45,45
- home_repair_cascade: 45,45,45
- job_transition: 45,45,45
- medical_emergency: 85,85,85
- pet_emergency: 75(EXCEEDED_MAX_TOOL_CALLS),75(EXCEEDED_MAX_TOOL_CALLS),75(EXCEEDED_MAX_TOOL_CALLS)
- seasonal_business: 45,45,45
- student_loan_payment: 45,45,45
- tuition_payment: 63(REPAIR_FAILED),63(REPAIR_FAILED),63(REPAIR_FAILED)
- vacation_fund: 45,45,45
- wedding_guest_spree: 45,45,45

**Summary:**
- Mean Score (all): 53.6
- Success Rate: 85.7%
- Mean Score (successful only): 58.3
- Total runs: 42

---

## SONNET - v3-tasks - with-ledger - tools

- ledger_01_simple_feasible: 55,55,55
- ledger_02_simple_infeasible: 85,85,85
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 63.0
- Success Rate: 100.0%
- Mean Score (successful only): 63.0
- Total runs: 15

---

## SONNET - v3-tasks - no-ledger - tools

- ledger_01_simple_feasible: 45,45,45
- ledger_02_simple_infeasible: 63(REPAIR_FAILED),85,63(REPAIR_FAILED)
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 58.0
- Success Rate: 86.7%
- Mean Score (successful only): 62.3
- Total runs: 15

---

## SONNET - v4-advanced - with-ledger - tools

- apartment_move_complex: 65(EXCEEDED_MAX_TOOL_CALLS),65(EXCEEDED_MAX_TOOL_CALLS),55(EXCEEDED_MAX_TOOL_CALLS)
- car_lease_promotion: 45,45,45
- freelance_irregular: 55,55,55
- graduate_school_prep: 10(WRONG_VERDICT),10(WRONG_VERDICT),10(WRONG_VERDICT)
- home_office_setup: 55,55,55
- medical_emergency: 85,85,85
- sabbatical_complex: 60(EXCEEDED_MAX_TOOL_CALLS),60(EXCEEDED_MAX_TOOL_CALLS),60(EXCEEDED_MAX_TOOL_CALLS)
- side_hustle_growth: 55,55,55
- simple_bonus: 55,55,55

**Summary:**
- Mean Score (all): 50.6
- Success Rate: 66.7%
- Mean Score (successful only): 54.2
- Total runs: 27

---

## SONNET - v4-advanced - no-ledger - tools

- apartment_move_complex: 63(REPAIR_FAILED),63(REPAIR_FAILED),63(REPAIR_FAILED)
- car_lease_promotion: 45,45,45
- freelance_irregular: 45,45,45
- graduate_school_prep: 45,45,45
- home_office_setup: 45,45,45
- medical_emergency: 85,85,85
- sabbatical_complex: 85,85,85
- side_hustle_growth: 45,45,45
- simple_bonus: 45,45,45

**Summary:**
- Mean Score (all): 53.0
- Success Rate: 88.9%
- Mean Score (successful only): 55.0
- Total runs: 27

---

## Key Insights

1. **Individual Task Performance**: Each task's scores across 3 runs are shown explicitly, revealing consistency patterns and specific failure modes.

2. **Model Comparison**: 
   - Sonnet generally outperforms Haiku, especially on v2-intermediate tasks
   - Both models struggle with v4-advanced tasks (lower success rates)

3. **Ledger Effect**: 
   - With-ledger conditions generally show higher scores when successful
   - No-ledger conditions sometimes have higher success rates but lower scores

4. **Task Set Difficulty**:
   - v3-tasks: Highest success rates (86-100%)
   - v2-intermediate: Moderate success rates (68-93%)
   - v4-advanced: Lowest success rates (40-89%)

5. **Error Patterns**:
   - EXCEEDED_MAX_TOOL_CALLS: Common across complex scenarios
   - REPAIR_FAILED: More frequent in no-ledger conditions
   - WRONG_VERDICT: Specific tasks (apartment_overlap, graduate_school_prep)
   - INVALID_JSON: Sporadic formatting failures

---

## NO TOOLS CONDITIONS

### HAIKU - v2-intermediate - with-ledger - no-tools

- apartment_overlap: 55,30(WRONG_VERDICT),55
- bonus_splurge: 45,45,45
- car_replacement: 70(INACCURATE_REPAIR_LABEL),75(INACCURATE_REPAIR_LABEL),70(INACCURATE_REPAIR_LABEL)
- commission_drought: 55,45,55
- freelance_ramp: 55,55,55
- home_repair_cascade: 55,55,55
- job_transition: 45,45,45
- medical_emergency: 63(REPAIR_FAILED),90,90
- pet_emergency: 95,85,85
- seasonal_business: 45,45,45
- student_loan_payment: 55,55,55
- tuition_payment: 73(REPAIR_FAILED),73(REPAIR_FAILED),73(REPAIR_FAILED)
- vacation_fund: 55,55,55
- wedding_guest_spree: 55,55,55

**Summary:**
- Mean Score (all): 58.8
- Success Rate: 80.9%
- Mean Score (successful only): 63.8
- Total runs: 42

---

### HAIKU - v2-intermediate - no-ledger - no-tools

- apartment_overlap: 15(WRONG_VERDICT),15(WRONG_VERDICT),15(WRONG_VERDICT)
- bonus_splurge: 45,45,45
- car_replacement: 85,70(INACCURATE_REPAIR_LABEL),70(INACCURATE_REPAIR_LABEL)
- commission_drought: 45,45,45
- freelance_ramp: 45,45,45
- home_repair_cascade: 45,45,45
- job_transition: 45,45,45
- medical_emergency: 85,85,85
- pet_emergency: 85,70(INACCURATE_REPAIR_LABEL),70(INACCURATE_REPAIR_LABEL)
- seasonal_business: 45,45,45
- student_loan_payment: 45,45,45
- tuition_payment: 63(REPAIR_FAILED),85,63(REPAIR_FAILED)
- vacation_fund: 45,45,45
- wedding_guest_spree: 45,45,45

**Summary:**
- Mean Score (all): 52.4
- Success Rate: 73.8%
- Mean Score (successful only): 59.7
- Total runs: 42

---

### HAIKU - v3-tasks - with-ledger - no-tools

- ledger_01_simple_feasible: 55,55,55
- ledger_02_simple_infeasible: 70(INACCURATE_REPAIR_LABEL),70(INACCURATE_REPAIR_LABEL),70(INACCURATE_REPAIR_LABEL)
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 58.0
- Success Rate: 80.0%
- Mean Score (successful only): 62.5
- Total runs: 15

---

### HAIKU - v3-tasks - no-ledger - no-tools

- ledger_01_simple_feasible: 45,45,45
- ledger_02_simple_infeasible: 63(REPAIR_FAILED),85,85
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 59.2
- Success Rate: 93.3%
- Mean Score (successful only): 60.7
- Total runs: 15

---

### HAIKU - v4-advanced - with-ledger - no-tools

- apartment_move_complex: 63(REPAIR_FAILED),70(REPAIR_FAILED),63(REPAIR_FAILED)
- car_lease_promotion: 45,45,45
- freelance_irregular: 45,45,45
- graduate_school_prep: 45,45,45
- home_office_setup: 45,45,45
- medical_emergency: 85,85,85
- sabbatical_complex: 85,85,85
- side_hustle_growth: 45,45,45
- simple_bonus: 45,45,45
- wedding_season_chaos: 45,45,45

**Summary:**
- Mean Score (all): 53.8
- Success Rate: 90.0%
- Mean Score (successful only): 54.4
- Total runs: 30

---

### HAIKU - v4-advanced - no-ledger - no-tools

- apartment_move_complex: 63(REPAIR_FAILED),63(REPAIR_FAILED),63(REPAIR_FAILED)
- car_lease_promotion: 45,45,45
- freelance_irregular: 45,45,45
- graduate_school_prep: 45,45,45
- home_office_setup: 45,45,45
- medical_emergency: 85,85,85
- sabbatical_complex: 85,85,85
- side_hustle_growth: 45,45,45
- simple_bonus: 45,45,45
- wedding_season_chaos: 45,45,45

**Summary:**
- Mean Score (all): 53.1
- Success Rate: 90.0%
- Mean Score (successful only): 53.7
- Total runs: 30

---

### SONNET - v2-intermediate - with-ledger - no-tools

- apartment_overlap: 55,55,55
- bonus_splurge: 45,45,45
- car_replacement: 90,90,90
- commission_drought: 55,55,55
- freelance_ramp: 55,55,55
- home_repair_cascade: 55,55,55
- job_transition: 45,45,45
- medical_emergency: 90,90,90
- pet_emergency: 95,95,95
- seasonal_business: 55,55,55
- student_loan_payment: 55,55,55
- tuition_payment: 90,90,90
- vacation_fund: 55,55,55
- wedding_guest_spree: 55,55,55

**Summary:**
- Mean Score (all): 66.8
- Success Rate: 100.0%
- Mean Score (successful only): 66.8
- Total runs: 42

---

### SONNET - v2-intermediate - no-ledger - no-tools

- apartment_overlap: 45,45,45
- bonus_splurge: 45,45,45
- car_replacement: 85,85,85
- commission_drought: 45,45,45
- freelance_ramp: 45,45,45
- home_repair_cascade: 45,45,45
- job_transition: 45,45,45
- medical_emergency: 85,85,85
- pet_emergency: 85,85,85
- seasonal_business: 45,45,45
- student_loan_payment: 45,45,45
- tuition_payment: 85,85,85
- vacation_fund: 45,45,45
- wedding_guest_spree: 45,45,45

**Summary:**
- Mean Score (all): 56.4
- Success Rate: 100.0%
- Mean Score (successful only): 56.4
- Total runs: 42

---

### SONNET - v3-tasks - with-ledger - no-tools

- ledger_01_simple_feasible: 55,55,55
- ledger_02_simple_infeasible: 85,85,85
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 63.0
- Success Rate: 100.0%
- Mean Score (successful only): 63.0
- Total runs: 15

---

### SONNET - v3-tasks - no-ledger - no-tools

- ledger_01_simple_feasible: 45,45,45
- ledger_02_simple_infeasible: 85,85,85
- ledger_03_multi_event: 45,45,45
- ledger_04_boundary_case: 45,45,45
- ledger_05_repair_scenario: 85,85,85

**Summary:**
- Mean Score (all): 61.0
- Success Rate: 100.0%
- Mean Score (successful only): 61.0
- Total runs: 15

---

### SONNET - v4-advanced - with-ledger - no-tools

- apartment_move_complex: 85,85,85
- car_lease_promotion: 45,45,45
- freelance_irregular: 45,45,45
- graduate_school_prep: 45,45,45
- home_office_setup: 45,45,45
- medical_emergency: 85,85,85
- sabbatical_complex: 85,85,85
- side_hustle_growth: 45,45,45
- simple_bonus: 45,45,45

**Summary:**
- Mean Score (all): 56.7
- Success Rate: 100.0%
- Mean Score (successful only): 56.7
- Total runs: 27

---

### SONNET - v4-advanced - no-ledger - no-tools

- apartment_move_complex: 85,85,85
- car_lease_promotion: 45,45,45
- freelance_irregular: 45,45,45
- graduate_school_prep: 45,45,45
- home_office_setup: 45,45,45
- medical_emergency: 85,85,85
- sabbatical_complex: 85,85,85
- side_hustle_growth: 45,45,45
- simple_bonus: 45,45,45

**Summary:**
- Mean Score (all): 56.7
- Success Rate: 100.0%
- Mean Score (successful only): 56.7
- Total runs: 27

---

## Updated Key Insights

### Tools vs No Tools Comparison

**Tools Conditions:**
- Higher complexity handling but more failure modes
- EXCEEDED_MAX_TOOL_CALLS errors common in complex scenarios
- Better performance on repair scenarios when successful

**No Tools Conditions:**
- More consistent performance, fewer error types
- Higher success rates overall (less failure modes)
- Simpler but more limited problem-solving approach

### Model Performance Patterns

**Haiku:**
- Tools: More variable performance, struggles with complex tasks
- No Tools: More consistent but limited ceiling

**Sonnet:**
- Tools: Better handling of complex scenarios when successful
- No Tools: Excellent consistency, very high success rates

### Task Set Analysis

**v2-intermediate:** Most shows largest performance gap between tools/no-tools
**v3-tasks:** Relatively consistent across conditions
**v4-advanced:** Tools show more failures but higher potential scores