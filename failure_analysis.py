#!/usr/bin/env python3
"""
Analysis of consistent failures across all agent types and conditions.
"""

import json
from collections import defaultdict

def load_results(file_path):
    """Load NDJSON results."""
    results = []
    with open(file_path, 'r') as f:
        for line in f:
            results.append(json.loads(line.strip()))
    return results

def analyze_failures():
    """Analyze failure patterns across both agent types."""
    
    # Load results from both agent types
    tools_results = load_results('/Users/rishi/Documents/Workspace/eval-sandbox/reports/comparison_20251229_1216/raw_results.ndjson')
    no_tools_results = load_results('/Users/rishi/Documents/Workspace/eval-sandbox/reports/comparison_20251229_1217/raw_results.ndjson')
    
    all_results = tools_results + no_tools_results
    
    # Track failures by task
    task_stats = defaultdict(lambda: {
        'total_runs': 0,
        'wrong_verdict': 0,
        'wrong_violation_month': 0,
        'conditions': set(),
        'agent_failures': defaultdict(int)
    })
    
    for result in all_results:
        task_id = result['task_id']
        agent_type = result.get('condition_model', 'unknown')
        model_name = result['condition_model_name']
        task_set = result['condition_task_set']
        
        condition_key = f"{agent_type}_{model_name}_{task_set}"
        
        task_stats[task_id]['total_runs'] += 1
        task_stats[task_id]['conditions'].add(condition_key)
        
        if result.get('verdict_correct') == False:
            task_stats[task_id]['wrong_verdict'] += 1
            task_stats[task_id]['agent_failures'][agent_type] += 1
            
        if result.get('first_violation_month_correct') == False:
            task_stats[task_id]['wrong_violation_month'] += 1
    
    # Identify consistently failing tasks
    print("=== FAILURE ANALYSIS ACROSS ALL CONDITIONS ===\n")
    
    verdict_failures = []
    violation_failures = []
    
    for task_id, stats in sorted(task_stats.items()):
        total = stats['total_runs']
        wrong_verdict = stats['wrong_verdict']
        wrong_violation = stats['wrong_violation_month']
        
        verdict_rate = (wrong_verdict / total) * 100 if total > 0 else 0
        violation_rate = (wrong_violation / total) * 100 if total > 0 else 0
        
        if verdict_rate > 80:  # >80% failure rate on verdicts
            verdict_failures.append((task_id, verdict_rate, wrong_verdict, total))
            
        if violation_rate > 80:  # >80% failure rate on violation months
            violation_failures.append((task_id, violation_rate, wrong_violation, total))
    
    print("TASKS WITH >80% WRONG VERDICT FAILURES:")
    print("Task ID | Failure Rate | Failed/Total | Agent Type Distribution")
    print("-" * 70)
    for task_id, rate, failed, total in sorted(verdict_failures, key=lambda x: x[1], reverse=True):
        agent_dist = task_stats[task_id]['agent_failures']
        print(f"{task_id:<25} | {rate:5.1f}% | {failed:2d}/{total:2d} | tools:{agent_dist.get('claude-tools', 0)}, no-tools:{agent_dist.get('claude', 0)}")
    
    print("\nTASKS WITH >80% WRONG VIOLATION MONTH FAILURES:")
    print("Task ID | Failure Rate | Failed/Total")
    print("-" * 50)
    for task_id, rate, failed, total in sorted(violation_failures, key=lambda x: x[1], reverse=True):
        print(f"{task_id:<25} | {rate:5.1f}% | {failed:2d}/{total:2d}")
    
    print("\nCONDITION BREAKDOWN:")
    print("Each task should have been tested across:")
    print("- 2 agent types (tools vs no-tools)")  
    print("- 2 models (haiku vs sonnet)")
    print("- 2-3 task sets (with/without ledger, different versions)")
    print("- 3 runs each = ~24 total runs per task")
    
    # Check if any tasks fail consistently across ALL conditions
    consistently_failing = []
    for task_id, stats in task_stats.items():
        conditions = stats['conditions']
        if len(conditions) >= 8:  # Should have multiple conditions
            wrong_verdict = stats['wrong_verdict']
            total = stats['total_runs']
            if wrong_verdict / total > 0.8:  # >80% failure
                consistently_failing.append(task_id)
    
    print(f"\nTASKS FAILING CONSISTENTLY ACROSS ALL CONDITIONS:")
    for task in consistently_failing:
        print(f"- {task}")
    
    print(f"\nRECOMMENDATIONS:")
    print("Tasks requiring manual expected verdict verification:")
    all_suspicious = set([t[0] for t in verdict_failures] + [t[0] for t in violation_failures])
    for task in sorted(all_suspicious):
        print(f"- {task}")
    
    print(f"\nPATTERN ANALYSIS:")
    v4_advanced_tasks = [t for t in all_suspicious if any('v4-advanced' in c for c in task_stats[t]['conditions'])]
    print(f"- {len(v4_advanced_tasks)} suspicious tasks are in v4-advanced task sets")
    
    infeasible_candidates = ['graduate_school_prep', 'sabbatical_complex']
    print(f"- Tasks likely expected to be 'infeasible': {infeasible_candidates}")
    print(f"- These may have incorrect expected verdicts in task definitions")

if __name__ == "__main__":
    analyze_failures()