from workbench.types import Scenario
import json
import os
from anthropic import Anthropic
from workbench.models.format_utils import format_eval_failure

class BaseAgent:
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        raise NotImplementedError
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        raise NotImplementedError

class StubAgent(BaseAgent):
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        scenario = {
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
        }
        
        if generate_ledger:
            return json.dumps({
                "scenario": scenario,
                "ledger": [
                    {
                        "month": "2024-01",
                        "starting_cash": 5000,
                        "base_takehome_salary": 2000,
                        "base_outflows": -4000,
                        "total_inflows": 2000,
                        "total_outflows": -4000,
                        "events_applied": [],
                        "ending_cash": 3000
                    }
                ]
            })
        else:
            return json.dumps(scenario)
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        if generate_ledger:
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
                    "changes": "Reduced baseline outflows from -4000 to -1000"
                },
                "ledger": [
                    {
                        "month": "2024-01",
                        "starting_cash": 5000,
                        "base_takehome_salary": 2000,
                        "base_outflows": -1000,
                        "total_inflows": 2000,
                        "total_outflows": -1000,
                        "events_applied": [],
                        "ending_cash": 6000
                    }
                ]
            })
        else:
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
                    "changes": "Reduced baseline outflows from -4000 to -1000"
                }
            })



class BadJSONAgent(BaseAgent):
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        return "This is not JSON at all!"
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        return "Still not JSON"

class BadSchemaAgent(BaseAgent):
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        return json.dumps({
            "id": "bad_scenario",
            "title": "Missing required fields"
            # Missing all other required fields!
        })
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None) -> str:
        return json.dumps({"id": "still_bad"})

class ClaudeAgent(BaseAgent):
    def __init__(self):
        # Get API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize the Anthropic client
        self.client = Anthropic(api_key=api_key)
        
    
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = "claude-3-haiku-20240307"):
        self.load_prompts(generate_ledger, prompt_dir)
        # Use default model if None is passed
        if model is None:
            model = "claude-3-haiku-20240307"
        
        print(f"DEBUG ClaudeAgent.draft: received model='{model}', generate_ledger={generate_ledger}")
        try:
            print(f"DEBUG ClaudeAgent.draft: calling anthropic API with model='{model}'")
            response = self.client.messages.create(
                model=model,
                max_tokens=2500,
                system=self.draft_system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            # Extract text from Claude's response
            result = response.content[0].text
            print(f"DEBUG ClaudeAgent.draft: API response length = {len(result)}")
            print(f"DEBUG ClaudeAgent.draft: API response preview = {result[:100]}...")
            return result
        except Exception as e:
            print(f"DEBUG ClaudeAgent.draft: API call failed with error: {e}")
            # Let the runner handle errors
            raise e
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = "claude-3-haiku-20240307") -> str:
        self.load_prompts(generate_ledger, prompt_dir)
        # Use default model if None is passed
        if model is None:
            model = "claude-3-haiku-20240307"
        try:
            # Format the failure information
            failure_msg = format_eval_failure(eval_result)
            
            # Create the user message with scenario and failure info
            user_message = f"Original scenario that failed:\n{scenario_json}\n\n"
            user_message += f"Failure details:\n{failure_msg}"
            
            response = self.client.messages.create(
                model=model,
                max_tokens=2500,
                system=self.repair_system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Extract text from Claude's response
            return response.content[0].text
        except Exception as e:
            # Let the runner handle errors
            raise e
    # Load prompts from files
    def load_prompts(self, generate_ledger: bool = False, prompt_dir: str = "prompts/v2"):
        if generate_ledger:
            with open(os.path.join(prompt_dir, "draft_with_ledger_system.txt"), "r") as f:
                self.draft_system_prompt = f.read()
            with open(os.path.join(prompt_dir, "repair_with_ledger_system.txt"), "r") as f:
                self.repair_system_prompt = f.read()
        else:
            with open(os.path.join(prompt_dir, "draft_system.txt"), "r") as f:
                self.draft_system_prompt = f.read()
            with open(os.path.join(prompt_dir, "repair_system.txt"), "r") as f:
                self.repair_system_prompt = f.read()


def get_agent(model: str) -> BaseAgent:
    print(f"DEBUG get_agent: called with model='{model}'")
    if model == "stub":
        print("DEBUG get_agent: returning StubAgent")
        return StubAgent()
    elif model == "bad_json":
        print("DEBUG get_agent: returning BadJSONAgent")
        return BadJSONAgent()
    elif model == "bad_schema":
        print("DEBUG get_agent: returning BadSchemaAgent")
        return BadSchemaAgent()
    elif model == "claude":
        print("DEBUG get_agent: returning ClaudeAgent")
        return ClaudeAgent()
    else:
        print(f"DEBUG get_agent: unknown model '{model}', raising ValueError")
        raise ValueError(f"Unknown model: {model}")
