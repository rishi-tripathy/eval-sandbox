from typing import List, Optional, Tuple
from workbench.types import MonthlyRecord, Scenario, Violation, InvariantType

def check_liquidity_floor(records: List[MonthlyRecord], floor: float=0.0) -> Tuple[Optional[MonthlyRecord], Optional[float], Optional[str]]:
    for record in records:
        if record.ending_cash < floor:
            magnitude = floor - record.ending_cash
            description = f"Cash fell below {floor} to {record.ending_cash} at {record.month.to_string()}"
            return (record, magnitude, description)
    return (None, None, None)


def check_money_conservation(scenario: Scenario, records: List[MonthlyRecord]) -> Tuple[Optional[MonthlyRecord], Optional[float], Optional[str]]:
    for i in range(len(records)-1):
        record = records[i]
        if i == 0: # check starting cash mismatch against scenario initial state
            if record.starting_cash != scenario.initial_state.starting_cash:
                magnitude = scenario.initial_state.starting_cash - record.starting_cash
                description = f"Starting cash mismatch: {scenario.initial_state.starting_cash} != {record.starting_cash} at {record.month.to_string()}"
                return (record, magnitude, description)
        
        if record.ending_cash != record.starting_cash + record.total_inflows + record.total_outflows: # check intramonth conservation
            magnitude = record.ending_cash - record.starting_cash - record.total_inflows - record.total_outflows
            description = f"Intramonth conservation violation: {record.ending_cash} != {record.starting_cash} + {record.total_inflows} + {record.total_outflows} at {record.month.to_string()}"
            return (record, magnitude, description)

        if record.ending_cash != records[i+1].starting_cash: # check ending cash of previous month to starting cash of next month conservation
            magnitude = records[i+1].starting_cash - record.ending_cash
            description = f"Month to month conservation violation: Starting cash {records[i+1].starting_cash} in {records[i+1].month.to_string()} != ending cash {record.ending_cash} from {record.month.to_string()}"
            return (records[i+1], magnitude, description)
    
    return (None, None, None)


def check_temporal_consistency(records: List[MonthlyRecord]) -> Tuple[Optional[MonthlyRecord], Optional[float], Optional[str]]:
    for record in records:
        for event in record.events_applied:
            if event.start_month > record.month:
                description = f"Event {event.label} applied in {record.month.to_string()} but starts in {event.start_month.to_string()}"
                return (record, None, description)
            if event.duration_months is not None: 
                end_month = event.start_month.add(event.duration_months-1)
                if record.month > end_month:
                    description = f"Event {event.label} applied in {record.month.to_string()} but ends in {end_month.to_string()}"
                    return (record, None, description)
    return None, None, None




def check_invariants(scenario: Scenario, records: List[MonthlyRecord]) -> Optional[List[Violation]]:

    violations = []
    lf_record, lf_magnitude, lf_description = check_liquidity_floor(records)
    if lf_record:
        violations.append(
            Violation(
                invariant=InvariantType.LIQUIDITY_FLOOR, 
                month=lf_record.month, 
                record=lf_record, 
                magnitude=lf_magnitude, 
                details=lf_description
            )
        )
    mc_record, mc_magnitude, mc_description = check_money_conservation(scenario, records)
    if mc_record:
        violations.append(
            Violation(
                invariant=InvariantType.MONEY_CONSERVATION, 
                month=mc_record.month, 
                record=mc_record, 
                magnitude=mc_magnitude, 
                details=mc_description
            )
        )
    
    tc_record, tc_magnitude, tc_description = check_temporal_consistency(records)
    if tc_record:
        violations.append(
            Violation(
                invariant=InvariantType.TEMPORAL_CONSISTENCY, 
                month=tc_record.month, 
                record=tc_record, 
                magnitude=tc_magnitude, 
                details=tc_description
            )
        )

    if len(violations) > 0:
        return violations
    return None