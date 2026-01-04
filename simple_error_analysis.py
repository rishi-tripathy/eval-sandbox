import csv
from collections import defaultdict, Counter

# Load the data
data = []
with open('/Users/rishi/Documents/Workspace/eval-sandbox/reports/results_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

print("=== ERROR TYPE ANALYSIS ===\n")

print("Dataset Overview:")
print(f"Total rows: {len(data)}")

# Filter for error cases only
error_data = [row for row in data if row['FEASIBLE'] == 'error']
feasible_data = [row for row in data if row['FEASIBLE'] == 'feasible']

print(f"Feasible outcomes: {len(feasible_data)}")
print(f"Error outcomes: {len(error_data)}")
print(f"Error rate: {len(error_data)/len(data)*100:.1f}%")

if len(error_data) == 0:
    print("No errors found!")
    exit()

# 1. Overall error type distribution
print("\n1. MOST COMMON ERROR TYPES OVERALL")
print("=" * 50)
all_errors = [row['ERROR_TYPE'] for row in error_data if row['ERROR_TYPE']]
error_counts = Counter(all_errors)
for error, count in error_counts.most_common():
    pct = (count / len(error_data)) * 100
    print(f"{error:<35} {count:>4} ({pct:>5.1f}%)")

# 2. Error types by AGENT (tools vs no-tools)
print("\n2. ERROR TYPES BY AGENT CONDITION")
print("=" * 50)

agent_errors = defaultdict(lambda: defaultdict(int))
agent_totals = defaultdict(int)

for row in error_data:
    if row['ERROR_TYPE']:
        agent_errors[row['AGENT']][row['ERROR_TYPE']] += 1
        agent_totals[row['AGENT']] += 1

print(f"no-tools agent: {agent_totals['no-tools']} total errors")
print(f"tools agent: {agent_totals['tools']} total errors")

print(f"\nno-tools error breakdown:")
if 'no-tools' in agent_errors:
    no_tools_total = agent_totals['no-tools']
    sorted_errors = sorted(agent_errors['no-tools'].items(), key=lambda x: x[1], reverse=True)
    for error, count in sorted_errors:
        if count > 0:
            pct = (count / no_tools_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

print(f"\ntools error breakdown:")
if 'tools' in agent_errors:
    tools_total = agent_totals['tools']
    sorted_errors = sorted(agent_errors['tools'].items(), key=lambda x: x[1], reverse=True)
    for error, count in sorted_errors:
        if count > 0:
            pct = (count / tools_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 3. Error types by MODEL (haiku vs sonnet)
print("\n3. ERROR TYPES BY MODEL")
print("=" * 50)

model_errors = defaultdict(lambda: defaultdict(int))
model_totals = defaultdict(int)

for row in error_data:
    if row['ERROR_TYPE']:
        model_errors[row['MODEL']][row['ERROR_TYPE']] += 1
        model_totals[row['MODEL']] += 1

print(f"haiku model: {model_totals['haiku']} total errors")
print(f"sonnet model: {model_totals['sonnet']} total errors")

print(f"\nhaiku error breakdown:")
if 'haiku' in model_errors:
    haiku_total = model_totals['haiku']
    sorted_errors = sorted(model_errors['haiku'].items(), key=lambda x: x[1], reverse=True)
    for error, count in sorted_errors:
        if count > 0:
            pct = (count / haiku_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

print(f"\nsonnet error breakdown:")
if 'sonnet' in model_errors:
    sonnet_total = model_totals['sonnet']
    sorted_errors = sorted(model_errors['sonnet'].items(), key=lambda x: x[1], reverse=True)
    for error, count in sorted_errors:
        if count > 0:
            pct = (count / sonnet_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 4. Error types by LEDGER (yes vs no)
print("\n4. ERROR TYPES BY LEDGER CONDITION")
print("=" * 50)

ledger_errors = defaultdict(lambda: defaultdict(int))
ledger_totals = defaultdict(int)

for row in error_data:
    if row['ERROR_TYPE']:
        ledger_errors[row['LEDGER']][row['ERROR_TYPE']] += 1
        ledger_totals[row['LEDGER']] += 1

print(f"no ledger: {ledger_totals['no']} total errors")
print(f"yes ledger: {ledger_totals['yes']} total errors")

print(f"\nno ledger error breakdown:")
if 'no' in ledger_errors:
    no_ledger_total = ledger_totals['no']
    sorted_errors = sorted(ledger_errors['no'].items(), key=lambda x: x[1], reverse=True)
    for error, count in sorted_errors:
        if count > 0:
            pct = (count / no_ledger_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

print(f"\nyes ledger error breakdown:")
if 'yes' in ledger_errors:
    yes_ledger_total = ledger_totals['yes']
    sorted_errors = sorted(ledger_errors['yes'].items(), key=lambda x: x[1], reverse=True)
    for error, count in sorted_errors:
        if count > 0:
            pct = (count / yes_ledger_total) * 100
            print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 5. Error types by TASK_SET (complexity analysis)
print("\n5. ERROR TYPES BY TASK COMPLEXITY (TASK_SET)")
print("=" * 50)

taskset_errors = defaultdict(lambda: defaultdict(int))
taskset_totals = defaultdict(int)

for row in error_data:
    if row['ERROR_TYPE']:
        taskset_errors[row['TASK_SET']][row['ERROR_TYPE']] += 1
        taskset_totals[row['TASK_SET']] += 1

for taskset in ['v2-intermediate', 'v3-tasks', 'v4-advanced']:
    if taskset in taskset_totals:
        print(f"\n{taskset}: {taskset_totals[taskset]} total errors")
        if taskset in taskset_errors:
            taskset_total = taskset_totals[taskset]
            sorted_errors = sorted(taskset_errors[taskset].items(), key=lambda x: x[1], reverse=True)
            for error, count in sorted_errors:
                if count > 0:
                    pct = (count / taskset_total) * 100
                    print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

# 6. Specific pattern analysis
print("\n6. SPECIFIC ERROR PATTERN ANALYSIS")
print("=" * 50)

# EXCEEDED_MAX_TOOL_CALLS analysis
print(f"\nEXCEEDED_MAX_TOOL_CALLS analysis:")
tool_calls_errors = [row for row in error_data if row['ERROR_TYPE'] == 'EXCEEDED_MAX_TOOL_CALLS']
print(f"Total EXCEEDED_MAX_TOOL_CALLS: {len(tool_calls_errors)}")
if len(tool_calls_errors) > 0:
    by_agent = Counter([row['AGENT'] for row in tool_calls_errors])
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  → Confirms tools-only occurrence: {by_agent.get('no-tools', 0) == 0}")

# JSON parsing errors
print(f"\nINVALID_JSON analysis:")
json_errors = [row for row in error_data if row['ERROR_TYPE'] == 'INVALID_JSON']
print(f"Total INVALID_JSON: {len(json_errors)}")
if len(json_errors) > 0:
    by_agent = Counter([row['AGENT'] for row in json_errors])
    by_model = Counter([row['MODEL'] for row in json_errors])
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  haiku: {by_model.get('haiku', 0)}")
    print(f"  sonnet: {by_model.get('sonnet', 0)}")

# REPAIR_FAILED patterns
print(f"\nREPAIR_FAILED analysis:")
repair_errors = [row for row in error_data if row['ERROR_TYPE'] == 'REPAIR_FAILED']
print(f"Total REPAIR_FAILED: {len(repair_errors)}")
if len(repair_errors) > 0:
    by_agent = Counter([row['AGENT'] for row in repair_errors])
    by_model = Counter([row['MODEL'] for row in repair_errors])
    by_taskset = Counter([row['TASK_SET'] for row in repair_errors])
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  haiku: {by_model.get('haiku', 0)}")
    print(f"  sonnet: {by_model.get('sonnet', 0)}")
    print(f"  v2-intermediate: {by_taskset.get('v2-intermediate', 0)}")
    print(f"  v3-tasks: {by_taskset.get('v3-tasks', 0)}")
    print(f"  v4-advanced: {by_taskset.get('v4-advanced', 0)}")

# WRONG_VERDICT patterns
print(f"\nWRONG_VERDICT analysis:")
verdict_errors = [row for row in error_data if row['ERROR_TYPE'] == 'WRONG_VERDICT']
print(f"Total WRONG_VERDICT: {len(verdict_errors)}")
if len(verdict_errors) > 0:
    by_agent = Counter([row['AGENT'] for row in verdict_errors])
    by_model = Counter([row['MODEL'] for row in verdict_errors])
    by_taskset = Counter([row['TASK_SET'] for row in verdict_errors])
    print(f"  no-tools: {by_agent.get('no-tools', 0)}")
    print(f"  tools: {by_agent.get('tools', 0)}")
    print(f"  haiku: {by_model.get('haiku', 0)}")
    print(f"  sonnet: {by_model.get('sonnet', 0)}")
    print(f"  v2-intermediate: {by_taskset.get('v2-intermediate', 0)}")
    print(f"  v3-tasks: {by_taskset.get('v3-tasks', 0)}")
    print(f"  v4-advanced: {by_taskset.get('v4-advanced', 0)}")

# 7. Agent × Model error interaction analysis
print("\n7. AGENT × MODEL ERROR INTERACTION")
print("=" * 50)

combo_errors = defaultdict(lambda: defaultdict(int))
for row in error_data:
    if row['ERROR_TYPE']:
        combo_key = f"{row['AGENT']}-{row['MODEL']}"
        combo_errors[combo_key][row['ERROR_TYPE']] += 1

for combo in ['no-tools-haiku', 'no-tools-sonnet', 'tools-haiku', 'tools-sonnet']:
    if combo in combo_errors:
        total = sum(combo_errors[combo].values())
        print(f"\n{combo}: {total} total errors")
        sorted_errors = sorted(combo_errors[combo].items(), key=lambda x: x[1], reverse=True)
        for error, count in sorted_errors[:3]:  # Top 3 errors for each combo
            if count > 0:
                pct = (count / total) * 100
                print(f"  {error:<33} {count:>4} ({pct:>5.1f}%)")

print("\n=== ANALYSIS COMPLETE ===")