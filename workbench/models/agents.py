from workbench.types import Scenario
import json
import os
from anthropic import Anthropic
from workbench.models.format_utils import format_eval_failure

class BaseAgent:
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
        raise NotImplementedError
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
        raise NotImplementedError

class StubAgent(BaseAgent):
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
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
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
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
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
        return "This is not JSON at all!"
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
        return "Still not JSON"

class BadSchemaAgent(BaseAgent):
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
        return json.dumps({
            "id": "bad_scenario",
            "title": "Missing required fields"
            # Missing all other required fields!
        })
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = None, max_tool_calls: int = 10) -> str:
        return json.dumps({"id": "still_bad"})

class ClaudeAgent(BaseAgent):
    def __init__(self):
        # Get API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize the Anthropic client
        self.client = Anthropic(api_key=api_key)
        
    
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = "claude-3-haiku-20240307", max_tool_calls: int = 10):
        self.load_prompts(generate_ledger, prompt_dir)
        # Use default model if None is passed
        if model is None:
            model = "claude-3-haiku-20240307"
        
        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=2500,
                system=self.draft_system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            # Extract text from Claude's response
            return response.content[0].text
        except Exception as e:
            # Let the runner handle errors
            raise e
    
    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = "claude-3-haiku-20240307", max_tool_calls: int = 10) -> str:
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


class ClaudeToolsAgent(BaseAgent):
    def __init__(self):
        # Get API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        # Initialize the Anthropic client
        self.client = Anthropic(api_key=api_key)
        self.tools = [
            {
            "name": "calculate",
            "description": "Perform arithmetic calculations using (e.g., '1000 + 2000 - 1500'). Returns the numeric result.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
                }
            },
            {
            "name": "validate_monthly_record",
            "description": "Check if a monthly ledger record has correct arithmetic and base monthly semantics. Validates: starting_cash + total_inflows + total_outflows = ending_cash. Also validates that base_takehome_salary and base_outflows match the scenario's base_monthly (if scenario_context provided).",
            "input_schema": {
                "type": "object",
                "properties": {
                    "monthly_record_json": {"type": "string"},
                    "scenario_context_json": {"type": "string", "description": "Optional: the full scenario JSON to validate base monthly semantics against"}
                },
                "required": ["monthly_record_json"]
                }   
            },
            {
            "name": "duration_advisor",
            "description": "Analyze an event description to determine if it appears to be a one-time occurrence (suggesting duration_months: 1). Returns boolean and reasoning.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "event_description": {"type": "string"}
                },
                "required": ["event_description"]
                }   
            },
            {
            "name": "check_json",
            "description": "Check if a string is valid JSON. Returns true if valid, false if invalid. Use this to verify your JSON before submitting.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "response_text": {"type": "string", "description": "The JSON text to validate"}
                },
                "required": ["response_text"]
                }   
            }
        ]    
    
    def draft(self, prompt: str, mode: str, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = "claude-3-haiku-20240307", max_tool_calls: int = 10):
        self.load_prompts(generate_ledger, prompt_dir)
        
        if model is None:
            model = "claude-3-haiku-20240307"
        
        # Keep user prompt clean - tool awareness already in system prompt
        enhanced_prompt = prompt
        
        messages = [{"role": "user", "content": enhanced_prompt}]
        tool_calls_used = 0
        tool_usage = {"calculate": 0, "validate_monthly_record": 0, "duration_advisor": 0, "check_json": 0}
        
        try:
            while tool_calls_used < max_tool_calls:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=3000,
                    system=self.draft_system_prompt,
                    messages=messages,
                    tools=self.tools
                )
                
                # Check if Claude used tools
                if response.stop_reason == "tool_use":
                    # Process tool calls
                    for content_block in response.content:
                        if content_block.type == "tool_use":
                            tool_calls_used += 1
                            if tool_calls_used > max_tool_calls:
                                # Exceed limit - return what we have
                                break
                            
                            # Execute the tool and track usage
                            tool_result = self._execute_tool(content_block.name, content_block.input)
                            tool_usage[content_block.name] += 1
                            
                            # Add assistant's response and tool result to conversation
                            messages.append({"role": "assistant", "content": response.content})
                            messages.append({
                                "role": "user", 
                                "content": [{"type": "tool_result", "tool_use_id": content_block.id, "content": str(tool_result)}]
                            })
                    
                    # Add tool usage reminder if getting close to limit
                    if tool_calls_used >= max_tool_calls - 2:
                        messages.append({
                            "role": "user",
                            "content": f"You've used {tool_calls_used}/{max_tool_calls} tool calls. Please finalize your scenario JSON now."
                        })
                else:
                    # Claude finished without more tools - extract final response
                    final_text = ""
                    for content_block in response.content:
                        if content_block.type == "text":
                            final_text += content_block.text
                    return final_text.strip(), tool_calls_used, tool_usage
            
            # If we hit max tool calls, ask for final answer
            messages.append({
                "role": "user", 
                "content": "You've reached your tool call limit. Please provide your final scenario JSON now."
            })
            
            final_response = self.client.messages.create(
                model=model,
                max_tokens=3000,
                system=self.draft_system_prompt,
                messages=messages
            )
            
            final_text = ""
            for content_block in final_response.content:
                if content_block.type == "text":
                    final_text += content_block.text
            return final_text.strip(), tool_calls_used
            
        except Exception as e:
            raise e

    def repair(self, scenario_json: str, eval_result: dict, generate_ledger: bool = False, prompt_dir: str = "prompts/v2", model: str = "claude-3-haiku-20240307", max_tool_calls: int = 10):
        self.load_prompts(generate_ledger, prompt_dir)
        
        if model is None:
            model = "claude-3-haiku-20240307"
        
        # Format the failure information
        from workbench.models.format_utils import format_eval_failure
        failure_msg = format_eval_failure(eval_result)
        
        # Create the user message with scenario and failure info
        user_message = f"Original scenario that failed:\n{scenario_json}\n\n"
        user_message += f"Failure details:\n{failure_msg}\n\n"
        # Tool awareness already in system prompt - keep user message clean
        
        messages = [{"role": "user", "content": user_message}]
        tool_calls_used = 0
        tool_usage = {"calculate": 0, "validate_monthly_record": 0, "duration_advisor": 0, "check_json": 0}
        
        try:
            while tool_calls_used < max_tool_calls:
                response = self.client.messages.create(
                    model=model,
                    max_tokens=3000,
                    system=self.repair_system_prompt,
                    messages=messages,
                    tools=self.tools
                )
                
                # Check if Claude used tools
                if response.stop_reason == "tool_use":
                    # Process tool calls
                    for content_block in response.content:
                        if content_block.type == "tool_use":
                            tool_calls_used += 1
                            if tool_calls_used > max_tool_calls:
                                # Exceed limit - return what we have
                                break
                            
                            # Execute the tool and track usage
                            tool_result = self._execute_tool(content_block.name, content_block.input)
                            tool_usage[content_block.name] += 1
                            
                            # Add assistant's response and tool result to conversation
                            messages.append({"role": "assistant", "content": response.content})
                            messages.append({
                                "role": "user", 
                                "content": [{"type": "tool_result", "tool_use_id": content_block.id, "content": str(tool_result)}]
                            })
                    
                    # Add tool usage reminder if getting close to limit
                    if tool_calls_used >= max_tool_calls - 2:
                        messages.append({
                            "role": "user",
                            "content": f"You've used {tool_calls_used}/{max_tool_calls} tool calls. Please finalize your repair JSON now."
                        })
                else:
                    # Claude finished without more tools - extract final response
                    final_text = ""
                    for content_block in response.content:
                        if content_block.type == "text":
                            final_text += content_block.text
                    return final_text.strip(), tool_calls_used, tool_usage
            
            # If we hit max tool calls, ask for final answer
            messages.append({
                "role": "user", 
                "content": "You've reached your tool call limit. Please provide your final repair JSON now."
            })
            
            final_response = self.client.messages.create(
                model=model,
                max_tokens=3000,
                system=self.repair_system_prompt,
                messages=messages
            )
            
            final_text = ""
            for content_block in final_response.content:
                if content_block.type == "text":
                    final_text += content_block.text
            return final_text.strip(), tool_calls_used
            
        except Exception as e:
            raise e
    
    def _execute_tool(self, tool_name: str, args: dict):
        """Execute a tool call and return the result."""
        if tool_name == "calculate":
            from workbench.models.tools.calculate import calculate
            return calculate(args["expression"])
        elif tool_name == "validate_monthly_record":
            from workbench.models.tools.validate_monthly_record import validate_monthly_record
            scenario_context = args.get("scenario_context_json")
            return validate_monthly_record(args["monthly_record_json"], scenario_context)
        elif tool_name == "duration_advisor":
            from workbench.models.tools.duration_advisor import duration_advisor
            return duration_advisor(args["event_description"])
        elif tool_name == "check_json":
            from workbench.models.tools.check_json import check_json
            return check_json(args["response_text"])
        else:
            raise ValueError(f"Unknown tool: {tool_name}")




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
        
        # Enhance prompts with tool-aware guidance
        tool_guidance = "\n\nTools available: calculate, validate_monthly_record, duration_advisor, check_json. Use as needed, then return only JSON."
        
        self.draft_system_prompt += tool_guidance
        self.repair_system_prompt += tool_guidance


def get_agent(model: str) -> BaseAgent:
    if model == "stub":
        return StubAgent()
    elif model == "bad_json":
        return BadJSONAgent()
    elif model == "bad_schema":
        return BadSchemaAgent()
    elif model == "claude":
        return ClaudeAgent()
    elif model == "claude-tools":
        return ClaudeToolsAgent()
    else:
        raise ValueError(f"Unknown model: {model}")
