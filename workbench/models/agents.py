from workbench.types import Scenario
import json

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

def get_agent(model: str) -> BaseAgent:
    if model == "stub":
        return StubAgent()
    elif model == "bad_json":
        return BadJSONAgent()
    elif model == "bad_schema":
        return BadSchemaAgent()
    else:
        raise ValueError(f"Unknown model: {model}")
