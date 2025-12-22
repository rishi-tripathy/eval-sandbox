from workbench.month import Month
from workbench.types import Scenario, Event, BaseMonthly, InitialState
from workbench.eval import run_eval

def test_simple_feasible_scenario():
    scenario = Scenario(
        id="test1",
        title="Simple feasible test",
        start_month=Month(2024, 1),
        horizon_months=3,
        initial_state=InitialState(starting_cash=1000),
        base_monthly=BaseMonthly(takehome_salary=2000, outflows=-1500),
        events=[]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    assert result.ledger_summary["ending_cash"] == 2500  # 1000 + 3*(500)