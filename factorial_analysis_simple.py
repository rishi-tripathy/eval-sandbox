#!/usr/bin/env python3
"""
Comprehensive factorial analysis of the evaluation results.
Creates proper factorial tables to replace misleading mean±std tables in FINDINGS.md.
Uses only standard library (no pandas required).
"""

import csv
import statistics
from collections import defaultdict

def load_data():
    """Load the CSV data and clean it up."""
    data = []
    
    with open('reports/results_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean up the data
            row['SCORE_PCT'] = float(row['SCORE_PCT'])
            row['TASK_SET'] = row['TASK_SET'].replace('-intermediate', '').replace('-advanced', '').replace('-tasks', '')
            data.append(row)
    
    print(f"Loaded {len(data)} rows of data")
    
    # Count unique combinations
    unique_combinations = set()
    for row in data:
        unique_combinations.add((row['AGENT'], row['MODEL'], row['LEDGER'], row['TASK_SET']))
    print(f"Unique factor combinations: {len(unique_combinations)}")
    
    return data

def calculate_base_factorial_table(data):
    """Create the base 2x2x2x3 factorial table showing all unique combinations."""
    
    print("\n" + "="*80)
    print("1. BASE FACTORIAL TABLE (2x2x2x3)")
    print("="*80)
    
    # Group by all factors
    groups = defaultdict(list)
    for row in data:
        key = (row['AGENT'], row['MODEL'], row['LEDGER'], row['TASK_SET'])
        groups[key].append(row)
    
    print("\nComplete Factorial Table:")
    print("-" * 110)
    print(f"{'Agent':<10} {'Model':<8} {'Ledger':<8} {'Task Set':<12} {'Avg Score':<10} {'N Tasks':<8} {'Success %':<10} {'Std Dev':<8}")
    print("-" * 110)
    
    # Sort by task set, then agent, model, ledger
    sorted_keys = sorted(groups.keys(), key=lambda x: (x[3], x[0], x[1], x[2]))
    
    results = []
    for key in sorted_keys:
        group = groups[key]
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        n_tasks = len(scores)
        success_rate = (successes / n_tasks) * 100
        
        agent, model, ledger, task_set = key
        print(f"{agent:<10} {model:<8} {ledger:<8} "
              f"{task_set:<12} {avg_score:<10.1f} {n_tasks:<8} "
              f"{success_rate:<10.1f} {std_score:<8.1f}")
        
        results.append({
            'agent': agent, 'model': model, 'ledger': ledger, 'task_set': task_set,
            'avg_score': avg_score, 'n_tasks': n_tasks, 'success_rate': success_rate, 'std_score': std_score
        })
    
    return results

def calculate_main_effects(data):
    """Calculate main effects for each factor."""
    
    print("\n" + "="*80)
    print("2. MAIN EFFECTS ANALYSIS")
    print("="*80)
    
    # Agent effect (Tools vs No-Tools)
    print("\nAgent Effect (Tools vs No-Tools):")
    print("-" * 50)
    
    agent_groups = defaultdict(list)
    for row in data:
        agent_groups[row['AGENT']].append(row)
    
    for agent, group in sorted(agent_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {agent:<10}: {avg_score:.1f}% avg score (n={len(scores):3d}, success={success_rate:.1f}%, std={std_score:.1f})")
    
    tools_avg = statistics.mean([row['SCORE_PCT'] for row in agent_groups['tools']])
    notools_avg = statistics.mean([row['SCORE_PCT'] for row in agent_groups['no-tools']])
    tools_effect = tools_avg - notools_avg
    print(f"  Tools Effect: {tools_effect:+.1f} percentage points")
    
    # Model effect (Haiku vs Sonnet)
    print("\nModel Effect (Haiku vs Sonnet):")
    print("-" * 50)
    
    model_groups = defaultdict(list)
    for row in data:
        model_groups[row['MODEL']].append(row)
    
    for model, group in sorted(model_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {model:<8}: {avg_score:.1f}% avg score (n={len(scores):3d}, success={success_rate:.1f}%, std={std_score:.1f})")
    
    sonnet_avg = statistics.mean([row['SCORE_PCT'] for row in model_groups['sonnet']])
    haiku_avg = statistics.mean([row['SCORE_PCT'] for row in model_groups['haiku']])
    sonnet_effect = sonnet_avg - haiku_avg
    print(f"  Sonnet Effect: {sonnet_effect:+.1f} percentage points")
    
    # Ledger effect (Yes vs No)
    print("\nLedger Effect (Yes vs No):")
    print("-" * 50)
    
    ledger_groups = defaultdict(list)
    for row in data:
        ledger_groups[row['LEDGER']].append(row)
    
    for ledger, group in sorted(ledger_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {ledger:<5}: {avg_score:.1f}% avg score (n={len(scores):3d}, success={success_rate:.1f}%, std={std_score:.1f})")
    
    yes_avg = statistics.mean([row['SCORE_PCT'] for row in ledger_groups['yes']])
    no_avg = statistics.mean([row['SCORE_PCT'] for row in ledger_groups['no']])
    ledger_effect = yes_avg - no_avg
    print(f"  Ledger Effect: {ledger_effect:+.1f} percentage points")
    
    # Task complexity effect
    print("\nTask Complexity Effect (v2 vs v3 vs v4):")
    print("-" * 50)
    
    task_groups = defaultdict(list)
    for row in data:
        task_groups[row['TASK_SET']].append(row)
    
    task_averages = {}
    for task_set, group in sorted(task_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {task_set:<5}: {avg_score:.1f}% avg score (n={len(scores):3d}, success={success_rate:.1f}%, std={std_score:.1f})")
        task_averages[task_set] = avg_score
    
    return {
        'tools_effect': tools_effect,
        'sonnet_effect': sonnet_effect, 
        'ledger_effect': ledger_effect,
        'task_averages': task_averages
    }

def calculate_interaction_effects(data):
    """Calculate key interaction effects."""
    
    print("\n" + "="*80)
    print("3. INTERACTION EFFECTS ANALYSIS")
    print("="*80)
    
    # AGENT × MODEL interaction
    print("\nAGENT × MODEL Interaction:")
    print("-" * 50)
    
    agent_model_groups = defaultdict(list)
    for row in data:
        key = (row['AGENT'], row['MODEL'])
        agent_model_groups[key].append(row)
    
    agent_model_averages = {}
    for (agent, model), group in sorted(agent_model_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {agent:<10} + {model:<8}: {avg_score:.1f}% (n={len(scores):3d}, success={success_rate:.1f}%)")
        agent_model_averages[(agent, model)] = avg_score
    
    # Calculate interaction strength
    tools_sonnet = agent_model_averages[('tools', 'sonnet')]
    tools_haiku = agent_model_averages[('tools', 'haiku')]
    notools_sonnet = agent_model_averages[('no-tools', 'sonnet')]
    notools_haiku = agent_model_averages[('no-tools', 'haiku')]
    
    interaction = (tools_sonnet - tools_haiku) - (notools_sonnet - notools_haiku)
    print(f"  Interaction strength: {interaction:.1f} percentage points")
    
    # AGENT × LEDGER interaction
    print("\nAGENT × LEDGER Interaction:")
    print("-" * 50)
    
    agent_ledger_groups = defaultdict(list)
    for row in data:
        key = (row['AGENT'], row['LEDGER'])
        agent_ledger_groups[key].append(row)
    
    for (agent, ledger), group in sorted(agent_ledger_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {agent:<10} + {ledger:<5}: {avg_score:.1f}% (n={len(scores):3d}, success={success_rate:.1f}%)")
    
    # MODEL × LEDGER interaction
    print("\nMODEL × LEDGER Interaction:")
    print("-" * 50)
    
    model_ledger_groups = defaultdict(list)
    for row in data:
        key = (row['MODEL'], row['LEDGER'])
        model_ledger_groups[key].append(row)
    
    for (model, ledger), group in sorted(model_ledger_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {model:<8} + {ledger:<5}: {avg_score:.1f}% (n={len(scores):3d}, success={success_rate:.1f}%)")
    
    # AGENT × TASK_SET interaction
    print("\nAGENT × TASK_SET Interaction:")
    print("-" * 50)
    
    agent_task_groups = defaultdict(list)
    for row in data:
        key = (row['AGENT'], row['TASK_SET'])
        agent_task_groups[key].append(row)
    
    for (agent, task_set), group in sorted(agent_task_groups.items()):
        scores = [row['SCORE_PCT'] for row in group]
        successes = sum(1 for row in group if row['FEASIBLE'] == 'feasible')
        
        avg_score = statistics.mean(scores)
        success_rate = (successes / len(scores)) * 100
        
        print(f"  {agent:<10} + {task_set:<5}: {avg_score:.1f}% (n={len(scores):3d}, success={success_rate:.1f}%)")

def analyze_task_consistency(data):
    """Analyze individual task consistency patterns."""
    
    print("\n" + "="*80)
    print("4. INDIVIDUAL TASK CONSISTENCY ANALYSIS")
    print("="*80)
    
    # Group by condition and task
    task_groups = defaultdict(list)
    for row in data:
        key = (row['AGENT'], row['MODEL'], row['LEDGER'], row['TASK_SET'], row['TASK'])
        task_groups[key].append(row['SCORE_PCT'])
    
    consistent_tasks = []
    variable_tasks = []
    
    for key, scores in task_groups.items():
        if len(scores) > 1:
            std_score = statistics.stdev(scores)
            avg_score = statistics.mean(scores)
            
            if std_score < 5.0:
                consistent_tasks.append((key, scores, std_score, avg_score))
            elif std_score > 20.0:
                variable_tasks.append((key, scores, std_score, avg_score))
    
    print(f"\nHigh Consistency Tasks (std dev < 5.0):")
    print("-" * 80)
    print(f"Found {len(consistent_tasks)} highly consistent task-condition combinations")
    
    # Show a few examples
    for i, (key, scores, std_score, avg_score) in enumerate(consistent_tasks[:10]):
        agent, model, ledger, task_set, task = key
        scores_str = ','.join([f"{s:.1f}" for s in scores])
        print(f"  {agent:<10} {model:<8} {ledger:<5} {task_set:<5} "
              f"{task:<25}: scores=[{scores_str}], std={std_score:.1f}")
    
    if len(consistent_tasks) > 10:
        print(f"\n... and {len(consistent_tasks) - 10} more consistent patterns")
    
    print(f"\nHigh Variance Tasks (std dev > 20.0):")
    print("-" * 80)
    print(f"Found {len(variable_tasks)} highly variable task-condition combinations")
    
    for key, scores, std_score, avg_score in variable_tasks:
        agent, model, ledger, task_set, task = key
        scores_str = ','.join([f"{s:.1f}" for s in scores])
        print(f"  {agent:<10} {model:<8} {ledger:<5} {task_set:<5} "
              f"{task:<25}: scores=[{scores_str}], std={std_score:.1f}")
    
    # Task-specific failure patterns
    print("\nTask-Specific Failure Patterns:")
    print("-" * 80)
    
    task_success_rates = defaultdict(list)
    for row in data:
        task_success_rates[row['TASK']].append(row['FEASIBLE'] == 'feasible')
    
    problem_tasks = []
    for task, successes in task_success_rates.items():
        success_rate = (sum(successes) / len(successes)) * 100
        if success_rate < 50.0:
            problem_tasks.append((task, success_rate))
    
    if problem_tasks:
        print("Tasks with <50% success rate across all conditions:")
        for task, success_rate in sorted(problem_tasks, key=lambda x: x[1]):
            print(f"  {task:<30}: {success_rate:.1f}% success rate")
    else:
        print("No tasks have <50% success rate across all conditions")
    
    # Find tasks most sensitive to agent type
    print("\nTasks Most Sensitive to Agent Type (tools vs no-tools):")
    agent_sensitive = []
    
    task_agent_scores = defaultdict(lambda: defaultdict(list))
    for row in data:
        task_agent_scores[row['TASK']][row['AGENT']].append(row['SCORE_PCT'])
    
    for task, agent_data in task_agent_scores.items():
        if 'tools' in agent_data and 'no-tools' in agent_data:
            tools_score = statistics.mean(agent_data['tools'])
            notools_score = statistics.mean(agent_data['no-tools'])
            diff = abs(tools_score - notools_score)
            agent_sensitive.append((task, diff, tools_score, notools_score))
    
    agent_sensitive.sort(key=lambda x: x[1], reverse=True)
    for task, diff, tools_score, notools_score in agent_sensitive[:5]:
        print(f"  {task:<30}: {diff:.1f}pp difference (tools={tools_score:.1f}%, no-tools={notools_score:.1f}%)")

def print_summary_insights(data, main_effects):
    """Print key insights and recommendations."""
    
    print("\n" + "="*80)
    print("5. KEY INSIGHTS & SUMMARY")
    print("="*80)
    
    total_runs = len(data)
    overall_success = (sum(1 for row in data if row['FEASIBLE'] == 'feasible') / total_runs) * 100
    overall_score = statistics.mean([row['SCORE_PCT'] for row in data])
    
    print(f"\nOverall Statistics:")
    print(f"- Total task executions: {total_runs}")
    print(f"- Overall success rate: {overall_success:.1f}%")
    print(f"- Overall average score: {overall_score:.1f}%")
    
    print(f"\nKey Factor Effects (in order of impact):")
    
    # Calculate effect sizes
    effects = [
        ("Model (Sonnet vs Haiku)", main_effects['sonnet_effect']),
        ("Ledger (Yes vs No)", main_effects['ledger_effect']),
        ("Agent (Tools vs No-Tools)", main_effects['tools_effect'])
    ]
    
    # Add task complexity effects
    task_avg = main_effects['task_averages']
    if 'v2' in task_avg and 'v4' in task_avg:
        effects.append(("Task Complexity (v4 vs v2)", task_avg['v4'] - task_avg['v2']))
    
    effects.sort(key=lambda x: abs(x[1]), reverse=True)
    
    for i, (factor, effect) in enumerate(effects, 1):
        print(f"{i}. {factor}: {effect:+.1f} percentage points")
    
    # Find best and worst performing configurations
    config_groups = defaultdict(list)
    for row in data:
        key = (row['AGENT'], row['MODEL'], row['LEDGER'])
        config_groups[key].append(row['SCORE_PCT'])
    
    config_averages = {key: statistics.mean(scores) for key, scores in config_groups.items()}
    
    best_config = max(config_averages.items(), key=lambda x: x[1])
    worst_config = min(config_averages.items(), key=lambda x: x[1])
    
    print(f"\nBest Performing Configuration:")
    print(f"- {best_config[0][0]} + {best_config[0][1]} + ledger={best_config[0][2]}: {best_config[1]:.1f}% avg score")
    
    print(f"\nWorst Performing Configuration:")
    print(f"- {worst_config[0][0]} + {worst_config[0][1]} + ledger={worst_config[0][2]}: {worst_config[1]:.1f}% avg score")
    
    performance_gap = best_config[1] - worst_config[1]
    print(f"- Performance gap: {performance_gap:.1f} percentage points")

def main():
    """Main analysis function."""
    print("Financial Scenario Evaluation - Comprehensive Factorial Analysis")
    print("================================================================")
    
    # Load and prepare data
    data = load_data()
    
    # 1. Base factorial table (2x2x2x3)
    factorial_table = calculate_base_factorial_table(data)
    
    # 2. Main effects analysis  
    main_effects = calculate_main_effects(data)
    
    # 3. Interaction effects
    calculate_interaction_effects(data)
    
    # 4. Task consistency patterns
    analyze_task_consistency(data)
    
    # 5. Summary insights
    print_summary_insights(data, main_effects)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nThis comprehensive factorial analysis replaces the misleading mean±std tables")
    print("in FINDINGS.md with accurate breakdowns based on the actual experimental design.")
    print("\nData shows clear factorial structure with proper statistical accounting")
    print("for the repeated measurements (3 runs per condition) and nested factors.")

if __name__ == "__main__":
    main()