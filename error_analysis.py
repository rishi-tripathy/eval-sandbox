import pandas as pd
import numpy as np
from collections import Counter

# Load the data
df = pd.read_csv('/Users/rishi/Documents/Workspace/eval-sandbox/reports/results_data.csv')

print("=== ERROR TYPE ANALYSIS ===\n")

print("Dataset Overview:")
print(f"Total rows: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nFeasible outcomes: {sum(df['FEASIBLE'] == 'feasible')}")
print(f"Error outcomes: {sum(df['FEASIBLE'] == 'error')}")

# Filter for error cases only
error_df = df[df['FEASIBLE'] == 'error'].copy()
print(f"\nTotal error cases: {len(error_df)}")

# 1. Overall error type distribution
print("\n1. MOST COMMON ERROR TYPES OVERALL")
print("=" * 50)
overall_errors = error_df['ERROR_TYPE'].value_counts()
for error, count in overall_errors.items():
    pct = (count / len(error_df)) * 100
    print(f"{error:<35} {count:>4} ({pct:>5.1f}%)")

# 2. Error types by AGENT (tools vs no-tools)
print("\n2. ERROR TYPES BY AGENT CONDITION")
print("=" * 50)
agent_error_analysis = error_df.groupby(['AGENT', 'ERROR_TYPE']).size().unstack(fill_value=0)
agent_totals = error_df['AGENT'].value_counts()

print(f"\nno-tools agent: {agent_totals.get('no-tools', 0)} total errors")
print(f"tools agent: {agent_totals.get('tools', 0)} total errors")

print(f"\nno-tools error breakdown:")
if 'no-tools' in agent_error_analysis.index:
    no_tools_errors = agent_error_analysis.loc['no-tools']
    no_tools_total = no_tools_errors.sum()
    for error, count in no_tools_errors.sort_values(ascending=False).items():
        if count > 0:
            pct = (count / no_tools_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

print(f"\ntools error breakdown:")
if 'tools' in agent_error_analysis.index:
    tools_errors = agent_error_analysis.loc['tools']
    tools_total = tools_errors.sum()
    for error, count in tools_errors.sort_values(ascending=False).items():
        if count > 0:
            pct = (count / tools_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 3. Error types by MODEL (haiku vs sonnet)
print("\n\n3. ERROR TYPES BY MODEL")
print("=" * 50)
model_error_analysis = error_df.groupby(['MODEL', 'ERROR_TYPE']).size().unstack(fill_value=0)
model_totals = error_df['MODEL'].value_counts()

print(f"\nhaiku model: {model_totals.get('haiku', 0)} total errors")
print(f"sonnet model: {model_totals.get('sonnet', 0)} total errors")

print(f"\nhaiku error breakdown:")
if 'haiku' in model_error_analysis.index:
    haiku_errors = model_error_analysis.loc['haiku']
    haiku_total = haiku_errors.sum()
    for error, count in haiku_errors.sort_values(ascending=False).items():
        if count > 0:
            pct = (count / haiku_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

print(f"\nsonnet error breakdown:")
if 'sonnet' in model_error_analysis.index:
    sonnet_errors = model_error_analysis.loc['sonnet']
    sonnet_total = sonnet_errors.sum()
    for error, count in sonnet_errors.sort_values(ascending=False).items():
        if count > 0:
            pct = (count / sonnet_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 4. Error types by LEDGER (yes vs no)
print("\n\n4. ERROR TYPES BY LEDGER CONDITION")
print("=" * 50)
ledger_error_analysis = error_df.groupby(['LEDGER', 'ERROR_TYPE']).size().unstack(fill_value=0)
ledger_totals = error_df['LEDGER'].value_counts()

print(f"\nno ledger: {ledger_totals.get('no', 0)} total errors")
print(f"yes ledger: {ledger_totals.get('yes', 0)} total errors")

print(f"\nno ledger error breakdown:")
if 'no' in ledger_error_analysis.index:
    no_ledger_errors = ledger_error_analysis.loc['no']
    no_ledger_total = no_ledger_errors.sum()
    for error, count in no_ledger_errors.sort_values(ascending=False).items():
        if count > 0:
            pct = (count / no_ledger_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

print(f"\nyes ledger error breakdown:")
if 'yes' in ledger_error_analysis.index:
    yes_ledger_errors = ledger_error_analysis.loc['yes']
    yes_ledger_total = yes_ledger_errors.sum()
    for error, count in yes_ledger_errors.sort_values(ascending=False).items():
        if count > 0:
            pct = (count / yes_ledger_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 5. Error types by TASK_SET (complexity analysis)
print("\n\n5. ERROR TYPES BY TASK COMPLEXITY (TASK_SET)")
print("=" * 50)
taskset_error_analysis = error_df.groupby(['TASK_SET', 'ERROR_TYPE']).size().unstack(fill_value=0)
taskset_totals = error_df['TASK_SET'].value_counts()

for taskset in ['v2-intermediate', 'v3-tasks', 'v4-advanced']:
    if taskset in taskset_totals.index:
        print(f"\n{taskset}: {taskset_totals[taskset]} total errors")
        if taskset in taskset_error_analysis.index:
            taskset_errors = taskset_error_analysis.loc[taskset]
            taskset_total = taskset_errors.sum()
            for error, count in taskset_errors.sort_values(ascending=False).items():
                if count > 0:
                    pct = (count / taskset_total) * 100
                    print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 6. Specific pattern analysis
print("\n\n6. SPECIFIC ERROR PATTERN ANALYSIS")
print("=" * 50)

# EXCEEDED_MAX_TOOL_CALLS analysis
print(f"\nEXCEEDED_MAX_TOOL_CALLS analysis:")
tool_calls_errors = error_df[error_df['ERROR_TYPE'] == 'EXCEEDED_MAX_TOOL_CALLS']
print(f"Total EXCEEDED_MAX_TOOL_CALLS: {len(tool_calls_errors)}")
if len(tool_calls_errors) > 0:
    by_agent = tool_calls_errors['AGENT'].value_counts()
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  → Confirms tools-only occurrence: {by_agent.get('no-tools', 0) == 0}")

# JSON parsing errors
print(f"\nINVALID_JSON analysis:")
json_errors = error_df[error_df['ERROR_TYPE'] == 'INVALID_JSON']
print(f"Total INVALID_JSON: {len(json_errors)}")
if len(json_errors) > 0:
    by_agent = json_errors['AGENT'].value_counts()
    by_model = json_errors['MODEL'].value_counts()
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  haiku: {by_model.get('haiku', 0)}")
    print(f"  sonnet: {by_model.get('sonnet', 0)}")

# REPAIR_FAILED patterns
print(f"\nREPAIR_FAILED analysis:")
repair_errors = error_df[error_df['ERROR_TYPE'] == 'REPAIR_FAILED']
print(f"Total REPAIR_FAILED: {len(repair_errors)}")
if len(repair_errors) > 0:
    by_agent = repair_errors['AGENT'].value_counts()
    by_model = repair_errors['MODEL'].value_counts()
    by_taskset = repair_errors['TASK_SET'].value_counts()
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  haiku: {by_model.get('haiku', 0)}")
    print(f"  sonnet: {by_model.get('sonnet', 0)}")
    print(f"  v2-intermediate: {by_taskset.get('v2-intermediate', 0)}")
    print(f"  v3-tasks: {by_taskset.get('v3-tasks', 0)}")
    print(f"  v4-advanced: {by_taskset.get('v4-advanced', 0)}")

# WRONG_VERDICT patterns
print(f"\nWRONG_VERDICT analysis:")
verdict_errors = error_df[error_df['ERROR_TYPE'] == 'WRONG_VERDICT']
print(f"Total WRONG_VERDICT: {len(verdict_errors)}")
if len(verdict_errors) > 0:
    by_agent = verdict_errors['AGENT'].value_counts()
    by_model = verdict_errors['MODEL'].value_counts()
    by_taskset = verdict_errors['TASK_SET'].value_counts()
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  haiku: {by_model.get('haiku', 0)}")
    print(f"  sonnet: {by_model.get('sonnet', 0)}")
    print(f"  v2-intermediate: {by_taskset.get('v2-intermediate', 0)}")
    print(f"  v3-tasks: {by_taskset.get('v3-tasks', 0)}")
    print(f"  v4-advanced: {by_taskset.get('v4-advanced', 0)}")

# 7. Cross-tabulation summary
print("\n\n7. CROSS-TABULATION: AGENT × MODEL ERROR PATTERNS")
print("=" * 50)
cross_tab = pd.crosstab([error_df['AGENT'], error_df['MODEL']], error_df['ERROR_TYPE'])
print(cross_tab)

print("\n=== ANALYSIS COMPLETE ===")