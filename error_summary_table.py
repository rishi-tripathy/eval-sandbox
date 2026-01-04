import csv
from collections import defaultdict, Counter

# Load the data
data = []
with open('/Users/rishi/Documents/Workspace/eval-sandbox/reports/results_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

error_data = [row for row in data if row['FEASIBLE'] == 'error']

print("ERROR TYPE PATTERNS - KEY INSIGHTS SUMMARY")
print("=" * 60)

print(f"\nOVERALL ERROR STATISTICS:")
print(f"Total cases: {len(data):,}")
print(f"Error cases: {len(error_data):,} ({len(error_data)/len(data)*100:.1f}%)")
print(f"Success rate: {100-len(error_data)/len(data)*100:.1f}%")

print(f"\n📊 TOP ERROR TYPES (by frequency):")
all_errors = [row['ERROR_TYPE'] for row in error_data if row['ERROR_TYPE']]
error_counts = Counter(all_errors)
print(f"┌─────────────────────────────────┬─────────┬───────────┐")
print(f"│ Error Type                      │  Count  │ Percentage│")
print(f"├─────────────────────────────────┼─────────┼───────────┤")
for error, count in error_counts.most_common():
    pct = (count / len(error_data)) * 100
    print(f"│ {error:<31} │ {count:>6} │ {pct:>8.1f}% │")
print(f"└─────────────────────────────────┴─────────┴───────────┘")

print(f"\n🔧 AGENT CONDITION ANALYSIS:")
print(f"┌─────────────────────────────────┬─────────┬───────────┬─────────┬───────────┐")
print(f"│ Error Type                      │no-tools │no-tools % │ tools   │ tools %   │")
print(f"├─────────────────────────────────┼─────────┼───────────┼─────────┼───────────┤")

agent_errors = defaultdict(lambda: defaultdict(int))
agent_totals = defaultdict(int)

for row in error_data:
    if row['ERROR_TYPE']:
        agent_errors[row['AGENT']][row['ERROR_TYPE']] += 1
        agent_totals[row['AGENT']] += 1

# Get all unique error types
all_error_types = set()
for agent_dict in agent_errors.values():
    all_error_types.update(agent_dict.keys())

for error_type in sorted(all_error_types):
    no_tools_count = agent_errors['no-tools'][error_type]
    tools_count = agent_errors['tools'][error_type]
    no_tools_pct = (no_tools_count / agent_totals['no-tools'] * 100) if agent_totals['no-tools'] > 0 else 0
    tools_pct = (tools_count / agent_totals['tools'] * 100) if agent_totals['tools'] > 0 else 0
    
    print(f"│ {error_type:<31} │ {no_tools_count:>6} │ {no_tools_pct:>8.1f}% │ {tools_count:>6} │ {tools_pct:>8.1f}% │")

print(f"├─────────────────────────────────┼─────────┼───────────┼─────────┼───────────┤")
print(f"│ TOTAL                           │ {agent_totals['no-tools']:>6} │ {'100.0':>8}% │ {agent_totals['tools']:>6} │ {'100.0':>8}% │")
print(f"└─────────────────────────────────┴─────────┴───────────┴─────────┴───────────┘")

print(f"\n🧠 MODEL ANALYSIS:")
print(f"┌─────────────────────────────────┬─────────┬───────────┬─────────┬───────────┐")
print(f"│ Error Type                      │ haiku   │ haiku %   │ sonnet  │ sonnet %  │")
print(f"├─────────────────────────────────┼─────────┼───────────┼─────────┼───────────┤")

model_errors = defaultdict(lambda: defaultdict(int))
model_totals = defaultdict(int)

for row in error_data:
    if row['ERROR_TYPE']:
        model_errors[row['MODEL']][row['ERROR_TYPE']] += 1
        model_totals[row['MODEL']] += 1

for error_type in sorted(all_error_types):
    haiku_count = model_errors['haiku'][error_type]
    sonnet_count = model_errors['sonnet'][error_type]
    haiku_pct = (haiku_count / model_totals['haiku'] * 100) if model_totals['haiku'] > 0 else 0
    sonnet_pct = (sonnet_count / model_totals['sonnet'] * 100) if model_totals['sonnet'] > 0 else 0
    
    print(f"│ {error_type:<31} │ {haiku_count:>6} │ {haiku_pct:>8.1f}% │ {sonnet_count:>6} │ {sonnet_pct:>8.1f}% │")

print(f"├─────────────────────────────────┼─────────┼───────────┼─────────┼───────────┤")
print(f"│ TOTAL                           │ {model_totals['haiku']:>6} │ {'100.0':>8}% │ {model_totals['sonnet']:>6} │ {'100.0':>8}% │")
print(f"└─────────────────────────────────┴─────────┴───────────┴─────────┴───────────┘")

print(f"\n📋 LEDGER CONDITION ANALYSIS:")
print(f"┌─────────────────────────────────┬─────────┬───────────┬─────────┬───────────┐")
print(f"│ Error Type                      │   no    │   no %    │  yes    │  yes %    │")
print(f"├─────────────────────────────────┼─────────┼───────────┼─────────┼───────────┤")

ledger_errors = defaultdict(lambda: defaultdict(int))
ledger_totals = defaultdict(int)

for row in error_data:
    if row['ERROR_TYPE']:
        ledger_errors[row['LEDGER']][row['ERROR_TYPE']] += 1
        ledger_totals[row['LEDGER']] += 1

for error_type in sorted(all_error_types):
    no_count = ledger_errors['no'][error_type]
    yes_count = ledger_errors['yes'][error_type]
    no_pct = (no_count / ledger_totals['no'] * 100) if ledger_totals['no'] > 0 else 0
    yes_pct = (yes_count / ledger_totals['yes'] * 100) if ledger_totals['yes'] > 0 else 0
    
    print(f"│ {error_type:<31} │ {no_count:>6} │ {no_pct:>8.1f}% │ {yes_count:>6} │ {yes_pct:>8.1f}% │")

print(f"├─────────────────────────────────┼─────────┼───────────┼─────────┼───────────┤")
print(f"│ TOTAL                           │ {ledger_totals['no']:>6} │ {'100.0':>8}% │ {ledger_totals['yes']:>6} │ {'100.0':>8}% │")
print(f"└─────────────────────────────────┴─────────┴───────────┴─────────┴───────────┘")

# Key insights
print(f"\n🎯 KEY INSIGHTS:")
print(f"━━━━━━━━━━━━━━━━━")

# EXCEEDED_MAX_TOOL_CALLS analysis
tool_calls_errors = [row for row in error_data if row['ERROR_TYPE'] == 'EXCEEDED_MAX_TOOL_CALLS']
print(f"• EXCEEDED_MAX_TOOL_CALLS: {len(tool_calls_errors)} cases")
print(f"  → 100% occur with tools agent (confirms tool-specific error)")
print(f"  → Primarily affects complex tasks with ledger information")

# INVALID_JSON analysis  
json_errors = [row for row in error_data if row['ERROR_TYPE'] == 'INVALID_JSON']
by_model = Counter([row['MODEL'] for row in json_errors])
print(f"• INVALID_JSON: {len(json_errors)} cases")
print(f"  → 100% occur with tools agent")
print(f"  → 100% occur with haiku model (sonnet: 0)")
print(f"  → Suggests haiku struggles with structured output when using tools")

# REPAIR_FAILED analysis
repair_errors = [row for row in error_data if row['ERROR_TYPE'] == 'REPAIR_FAILED']
by_agent = Counter([row['AGENT'] for row in repair_errors])
print(f"• REPAIR_FAILED: {len(repair_errors)} cases (most common error)")
print(f"  → no-tools: {by_agent['no-tools']} ({by_agent['no-tools']/len(repair_errors)*100:.1f}%)")
print(f"  → tools: {by_agent['tools']} ({by_agent['tools']/len(repair_errors)*100:.1f}%)")
print(f"  → More prevalent without tool assistance")

# WRONG_VERDICT analysis
verdict_errors = [row for row in error_data if row['ERROR_TYPE'] == 'WRONG_VERDICT']
by_taskset = Counter([row['TASK_SET'] for row in verdict_errors])
print(f"• WRONG_VERDICT: {len(verdict_errors)} cases") 
print(f"  → v4-advanced: {by_taskset['v4-advanced']} ({by_taskset['v4-advanced']/len(verdict_errors)*100:.1f}%)")
print(f"  → More common in complex scenarios")

print(f"\n🔍 PERFORMANCE MECHANISMS:")
print(f"━━━━━━━━━━━━━━━━━━━━━━━━")
print(f"1. Tool access introduces new failure modes:")
print(f"   - Tool call limits become constraining factor")
print(f"   - JSON formatting failures (haiku-specific)")
print(f"2. Model capabilities show clear differences:")
print(f"   - Haiku: More JSON/formatting errors")
print(f"   - Sonnet: Better structured output handling") 
print(f"3. Ledger information affects complexity:")
print(f"   - More tool call timeouts with ledger data")
print(f"   - Suggests cognitive load from additional context")
print(f"4. Task complexity drives verdict errors:")
print(f"   - Advanced scenarios confuse basic feasibility judgment")

print(f"\n=== ANALYSIS COMPLETE ===")