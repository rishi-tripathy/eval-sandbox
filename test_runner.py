#!/usr/bin/env python3
from workbench.runner import run_task

result = run_task("tasks/v1/test_stub.json")
print(f"Initial verdict: {result.initial_verdict}")
print(f"Final verdict: {result.final_verdict}")
print(f"Repair attempted: {result.repair_attempted}")
print(f"Tool calls: {result.tool_calls}")