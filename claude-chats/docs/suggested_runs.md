Here are the key commands to test the framework, organized by complexity:

Basic Single Task Testing

# Test basic functionality

python -m workbench run-single tasks/v3-tasks-with-ledger/ledger_01_simple_feasible.json --model claude --verbose

# Test tool-enabled model

python -m workbench run-single tasks/v3-tasks-with-ledger/ledger_02_simple_infeasible.json --model claude-tools --verbose

# Test repair scenario

python -m workbench run-single tasks/v3-tasks-with-ledger/ledger_05_repair_scenario.json --model claude-tools

Suite Testing

# Run small task set with regular claude

python -m workbench run-suite tasks/v3-tasks-with-ledger --model claude

# Run with tools model for comparison

python -m workbench run-suite tasks/v3-tasks-with-ledger --model claude-tools

# Run larger intermediate set

python -m workbench run-suite tasks/v2-intermediate-with-ledger --model claude-tools

Comparison Framework Testing

# Quick comparison (2 models × 1 task set × 1 run = 10 total tasks)

python -m workbench run-comparison --models claude,claude-tools --task-sets tasks/v3-tasks-with-ledger --runs 1

# Medium comparison for statistical significance

python -m workbench run-comparison --models claude,claude-tools --task-sets tasks/v3-tasks-with-ledger --runs 3

# Multi-task-set comparison

python -m workbench run-comparison --models claude,claude-tools --task-sets tasks/v3-tasks-with-ledger,tasks/v2-intermediate-with-ledger --runs 2

# Full evaluation (warning: 50+ tasks)

python -m workbench run-comparison --models claude,claude-tools --task-sets tasks/v3-tasks-with-ledger,tasks/v2-intermediate-with-ledger,tasks/v4-advanced-with-ledger --runs 3

Validation & Debugging

# Validate a scenario file

python -m workbench validate fixtures/scenarios/simple_feasible.json

# Test prompt engineering directly

python -m workbench run-prompt "I earn $3000/month, spend $2500/month, start with $1000 cash, and need to pay a $4000 emergency expense in month 1. Can I afford this over 3 months?" --model claude-tools --verbose

# Test with custom defaults

python -m workbench run-prompt "Bonus of $1000 in month 2" --starting-cash 500 --horizon 4 --model claude-tools

Results Analysis Commands

# Check recent traces

ls -la traces/ | head -10

# View comparison results

ls reports/comparison*\*/
cat reports/comparison*\*/comparison_report.md

# Examine specific trace

cat traces/session\_\*/summary.txt
