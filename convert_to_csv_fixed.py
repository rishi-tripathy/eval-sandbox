#!/usr/bin/env python3
"""
Convert full-set-results.txt to CSV format with robust regex parsing
"""
import re
import csv

def parse_full_results_to_csv(input_file, output_file):
    """Parse full-set-results.txt and convert to CSV format."""
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Split into TOOLS and NO TOOLS sections
    sections = content.split('NO TOOLS')
    tools_section = sections[0].replace('TOOLS\n', '')
    no_tools_section = sections[1] if len(sections) > 1 else ""
    
    csv_data = []
    
    def parse_section(section, has_tools):
        """Parse a single section and add to csv_data."""
        
        # Match the main pattern first
        pattern = r'\[\d+/\d+\] ([^(]+)\(([^)]+)\)\+([^(]+) \(run (\d)/\d\): ([^.]+)\.+\s*(feasible|infeasible|error)\s*\(([^)]+)\)'
        
        for match in re.finditer(pattern, section):
            agent_type = match.group(1).strip()  # claude-tools or claude
            full_model = match.group(2).strip()  # claude-haiku-4-5 or claude-sonnet-4-5
            task_set_full = match.group(3).strip()  # v2-intermediate-with-ledger
            run_idx = int(match.group(4))  # 1, 2, or 3
            task_name = match.group(5).strip()  # apartment_overlap
            verdict = match.group(6).strip()  # feasible, infeasible, or error
            score_info = match.group(7).strip()  # "Score: 55/60" or "EXCEEDED_MAX_TOOL_CALLS, 75/100"
            
            # Extract model name (haiku or sonnet)
            if 'haiku' in full_model:
                model = 'haiku'
            elif 'sonnet' in full_model:
                model = 'sonnet'
            else:
                model = 'unknown'
            
            # Extract task set name and ledger info
            if 'with-ledger' in task_set_full:
                ledger = 'yes'
                task_set = task_set_full.replace('-with-ledger', '')
            elif 'no-ledger' in task_set_full:
                ledger = 'no'
                task_set = task_set_full.replace('-no-ledger', '')
            else:
                ledger = 'unknown'
                task_set = task_set_full
            
            # Parse score info
            error_type = None
            if verdict == 'error':
                # Format: "EXCEEDED_MAX_TOOL_CALLS, 75/100"
                if ', ' in score_info:
                    error_type, score_part = score_info.split(', ', 1)
                    score_match = re.search(r'(\d+)/(\d+)', score_part)
                    if score_match:
                        score = int(score_match.group(1))
                        max_score = int(score_match.group(2))
                    else:
                        score, max_score = 0, 100
                else:
                    error_type = 'UNKNOWN_ERROR'
                    score, max_score = 0, 100
            else:
                # Format: "Score: 55/60"
                score_match = re.search(r'(?:Score: )?(\d+)/(\d+)', score_info)
                if score_match:
                    score = int(score_match.group(1))
                    max_score = int(score_match.group(2))
                else:
                    score, max_score = 0, 100
            
            # Convert to percentage
            score_pct = (score / max_score * 100) if max_score > 0 else 0
            
            # Agent type (tools vs no-tools)
            agent = 'tools' if has_tools else 'no-tools'
            
            csv_data.append({
                'AGENT': agent,
                'MODEL': model,
                'TASK': task_name,
                'TASK_SET': task_set,
                'LEDGER': ledger,
                'POINTS_SCORED': score,
                'POINTS_POSSIBLE': max_score,
                'SCORE_PCT': round(score_pct, 1),
                'FEASIBLE': verdict,
                'RUN_IDX': run_idx,
                'ERROR_TYPE': error_type
            })
    
    # Parse both sections
    parse_section(tools_section, True)
    parse_section(no_tools_section, False)
    
    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['AGENT', 'MODEL', 'TASK', 'TASK_SET', 'LEDGER', 'POINTS_SCORED', 'POINTS_POSSIBLE', 'SCORE_PCT', 'FEASIBLE', 'RUN_IDX', 'ERROR_TYPE']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in sorted(csv_data, key=lambda x: (x['AGENT'], x['MODEL'], x['TASK_SET'], x['LEDGER'], x['TASK'], x['RUN_IDX'])):
            writer.writerow(row)
    
    print(f"Converted {len(csv_data)} records to {output_file}")
    
    # Print sample of data for verification
    print("\nSample of converted data:")
    for row in csv_data[:5]:
        print(f"  {row}")
    
    return len(csv_data)

def main():
    input_file = "reports/full-set-results.txt"
    output_file = "results_data.csv"
    
    try:
        count = parse_full_results_to_csv(input_file, output_file)
        print(f"\nSuccessfully converted {count} records from {input_file} to {output_file}")
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()