from workbench.types import Scenario, MonthlyRecord
from workbench.month import Month
from typing import List


def simulate(scenario: Scenario) -> List[MonthlyRecord]:
    monthly_records = []
    cash = scenario.initial_state.starting_cash

    for curr_month in Month.iterate(scenario.start_month, scenario.horizon_months):
        active_ongoing_events = [
            event for event in scenario.events 
            if event.start_month <= curr_month and event.duration_months is None
            ]
        active_finite_events = [
            event for event in scenario.events 
            if event.duration_months is not None 
            and event.start_month <= curr_month < event.start_month.add(event.duration_months)
            ]

        active_events = active_ongoing_events + active_finite_events
        
        base_income = scenario.base_monthly.takehome_salary
        base_outflows = scenario.base_monthly.outflows
        total_inflows = base_income + sum([event.amount for event in active_events if event.amount>0])
        total_outflows = base_outflows + sum([event.amount for event in active_events if event.amount<0])

        ending_cash = cash + total_inflows + total_outflows
        
        monthly_records.append(MonthlyRecord(month=curr_month, starting_cash=cash, base_takehome_salary=base_income, base_outflows=base_outflows, total_inflows=total_inflows, total_outflows=total_outflows, events_applied=active_events, ending_cash=ending_cash))
        
        cash = ending_cash
    return monthly_records