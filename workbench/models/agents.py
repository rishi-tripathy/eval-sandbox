from workbench.types import Scenario
import json
import os
from anthropic import Anthropic
from workbench.models.format_utils import format_eval_failure

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
        
        # Load prompts from files
        prompts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "v1")
        with open(os.path.join(prompts_dir, "draft_system.txt"), "r") as f:
            self.draft_system_prompt = f.read()
        with open(os.path.join(prompts_dir, "repair_system.txt"), "r") as f:
            self.repair_system_prompt = f.read()
    
    def draft(self, prompt: str, mode: str) -> str:
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system=self.draft_system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            # Extract text from Claude's response
            return response.content[0].text
        except Exception as e:
            # Let the runner handle errors
            raise e
    
    def repair(self, scenario_json: str, eval_result: dict) -> str:
        try:
            # Format the failure information
            failure_msg = format_eval_failure(eval_result)
            
            # Create the user message with scenario and failure info
            user_message = f"Original scenario that failed:\n{scenario_json}\n\n"
            user_message += f"Failure details:\n{failure_msg}"
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                system=self.repair_system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Extract text from Claude's response
            return response.content[0].text
        except Exception as e:
            # Let the runner handle errors
            raise e

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
