from workbench.types import Scenario
import json
import os
from anthropic import Anthropic

class BaseAgent:
    def draft(self, prompt: str, mode: str) -> str:
        raise NotImplementedError
    
    def repair(self, scenario_json: str, eval_result: dict) -> str:
        raise NotImplementedError

class StubAgent(BaseAgent):
    def draft(self, prompt: str, mode: str) -> str:
        return json.dumps({
            "id": "stub_scenario",
            "title": "Stub scenario",
            "start_month": "2024-01",
            "horizon_months": 12,
            "initial_state": {
                "starting_cash": 5000
            },
            "base_monthly": {
                "takehome_salary": 2000,
                "outflows": -4000
            },
            "events": []
        })
    
    def repair(self, scenario_json: str, eval_result: dict) -> str:
        return json.dumps({
            "id": "stub_scenario",
            "title": "Stub scenario",
            "start_month": "2024-01",
            "horizon_months": 12,
            "initial_state": {
                "starting_cash": 5000
            },
            "base_monthly": {
                "takehome_salary": 2000,
                "outflows": -1000
            },
            "events": []
        })



class BadJSONAgent(BaseAgent):
    def draft(self, prompt: str, mode: str) -> str:
        return "This is not JSON at all!"
    
    def repair(self, scenario_json: str, eval_result: dict) -> str:
        return "Still not JSON"

class BadSchemaAgent(BaseAgent):
    def draft(self, prompt: str, mode: str) -> str:
        return json.dumps({
            "id": "bad_scenario",
            "title": "Missing required fields"
            # Missing all other required fields!
        })
    
    def repair(self, scenario_json: str, eval_result: dict) -> str:
        return json.dumps({"id": "still_bad"})

class ClaudeAgent(BaseAgent):
    def __init__(self):
        # Get API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize the Anthropic client
        self.client = Anthropic(api_key=api_key)
        
        # We'll define the system prompt later
        self.system_prompt = "You are a financial scenario generator."
    
    def draft(self, prompt: str, mode: str) -> str:
        # TODO: Make actual API call but return stub for now
        try:
            # This is where we'll call Claude
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            # For now, ignore response and return stub
            return json.dumps({
                "id": "stub_scenario",
                "title": "Stub scenario",
                "start_month": "2024-01",
                "horizon_months": 12,
                "initial_state": {
                    "starting_cash": 5000
                },
                "base_monthly": {
                    "takehome_salary": 2000,
                    "outflows": -4000
                },
                "events": []
            })
        except Exception as e:
            # Let the runner handle errors
            raise e
    
    def repair(self, scenario_json: str, eval_result: dict) -> str:
        # TODO: Implement repair with wrapped response
        return json.dumps({
            "repaired_scenario": {
                "id": "stub_scenario",
                "title": "Stub scenario",
                "start_month": "2024-01",
                "horizon_months": 12,
                "initial_state": {
                    "starting_cash": 5000
                },
                "base_monthly": {
                    "takehome_salary": 2000,
                    "outflows": -1000
                },
                "events": []
            },
            "repair_applied": {
                "type": "baseline_reduction",
                "changes": "Reduced outflows from -4000 to -1000"
            }
        })

def get_agent(model: str) -> BaseAgent:
    if model == "stub":
        return StubAgent()
    elif model == "bad_json":
        return BadJSONAgent()
    elif model == "bad_schema":
        return BadSchemaAgent()
    elif model == "claude":
        return ClaudeAgent()
    else:
        raise ValueError(f"Unknown model: {model}")
