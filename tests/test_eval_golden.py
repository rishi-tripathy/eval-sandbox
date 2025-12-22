from workbench.month import Month
from workbench.types import Scenario, Event, BaseMonthly, InitialState, InvariantType
from workbench.eval import run_eval
import pytest

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
    # horizon_months=3 means simulate 3 months total starting from start_month
    # Month 1: starting=1000, net=+500, ending=1500
    # Month 2: starting=1500, net=+500, ending=2000
    # Month 3: starting=2000, net=+500, ending=2500
    assert result.ledger_summary["ending_cash"] == 2500
    assert result.ledger_summary["min_cash"] == 1500  # Min is after month 1
    assert result.ledger_summary["months_simulated"] == 3
    assert result.first_violation_month is None
    assert result.violated_invariant is None
    assert len(result.violations) == 0


def test_liquidity_floor_violation_immediate():
    """Test immediate liquidity floor violation in first month"""
    scenario = Scenario(
        id="test2",
        title="Immediate liquidity floor violation",
        start_month=Month(2024, 1),
        horizon_months=3,
        initial_state=InitialState(starting_cash=100),
        base_monthly=BaseMonthly(takehome_salary=1000, outflows=-2000),
        events=[]
    )

    result = run_eval(scenario)
    assert result.verdict == "infeasible"
    assert result.first_violation_month == "2024-01"  
    assert result.violated_invariant == InvariantType.LIQUIDITY_FLOOR
    assert result.ledger_summary["min_cash"] == -2900 


def test_liquidity_floor_violation_later():
    """Test liquidity floor violation in a later month"""
    scenario = Scenario(
        id="test3",
        title="Later liquidity floor violation",
        start_month=Month(2024, 1),
        horizon_months=6,
        initial_state=InitialState(starting_cash=2000),
        base_monthly=BaseMonthly(takehome_salary=3000, outflows=-3500),
        events=[]
    )

    result = run_eval(scenario)
    assert result.verdict == "infeasible"
    assert result.first_violation_month == "2024-05"
    assert result.violated_invariant == InvariantType.LIQUIDITY_FLOOR

def test_move_scenario_with_overlap():
    """Test classic move scenario with overlap, deposit, and broker fee"""
    scenario = Scenario(
        id="test4",
        title="Move with overlap + deposit + broker fee",
        start_month=Month(2024, 1),
        horizon_months=12,
        initial_state=InitialState(starting_cash=20000),
        base_monthly=BaseMonthly(takehome_salary=8000, outflows=-2500),
        events=[
            Event(label="old_rent", start_month=Month(2024, 1), amount=-3200, duration_months=2),
            Event(label="new_rent", start_month=Month(2024, 2), amount=-3800),  # Starts in Feb, continues
            Event(label="new_deposit", start_month=Month(2024, 2), amount=-3800, duration_months=1),
            Event(label="broker_fee", start_month=Month(2024, 2), amount=-3800, duration_months=1),
        ]
    )

    result = run_eval(scenario)
    # Check February specifically - the crunch month
    # Income: 8000
    # Baseline outflows: -2500
    # Old rent: -3200
    # New rent: -3800
    # Deposit: -3800
    # Broker: -3800
    # Total outflows in Feb: -17100
    # Net in Feb: 8000 - 17100 = -9100
    # Cash end of Jan: 20000 + 8000 - 2500 - 3200 = 22300
    # Cash end of Feb: 22300 - 9100 = 13200
    
    assert result.verdict == "feasible"
    assert result.ledger_summary["min_cash"] == 13200  # February is the tightest month


def test_single_event_duration():
    """Test event with specific duration"""
    scenario = Scenario(
        id="test5",
        title="Temporary expense",
        start_month=Month(2024, 1),
        horizon_months=6,
        initial_state=InitialState(starting_cash=5000),
        base_monthly=BaseMonthly(takehome_salary=3000, outflows=-2000),
        events=[
            Event(label="moving_costs", start_month=Month(2024, 2), amount=-1500, duration_months=2),
        ]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    # Month 1: 5000 + 3000 - 2000 = 6000
    # Month 2: 6000 + 3000 - 2000 - 1500 = 5500
    # Month 3: 5500 + 3000 - 2000 - 1500 = 5000
    # Month 4: 5000 + 3000 - 2000 = 6000 (event ended)
    # Month 5: 6000 + 3000 - 2000 = 7000
    # Month 6: 7000 + 3000 - 2000 = 8000
    assert result.ledger_summary["ending_cash"] == 8000


def test_event_beyond_horizon():
    """Test that events starting after horizon don't affect simulation"""
    scenario = Scenario(
        id="test6",
        title="Event beyond horizon",
        start_month=Month(2024, 1),
        horizon_months=3,
        initial_state=InitialState(starting_cash=1000),
        base_monthly=BaseMonthly(takehome_salary=2000, outflows=-1000),
        events=[
            Event(label="future_expense", start_month=Month(2024, 5), amount=-5000, duration_months=1),
        ]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    assert result.ledger_summary["ending_cash"] == 4000  # Event never applies


def test_zero_cash_exactly():
    """Test scenario that ends exactly at zero (boundary condition)"""
    scenario = Scenario(
        id="test7",
        title="Zero cash boundary",
        start_month=Month(2024, 1),
        horizon_months=2,
        initial_state=InitialState(starting_cash=1000),
        base_monthly=BaseMonthly(takehome_salary=2000, outflows=-2500),
        events=[]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"  # Zero is allowed
    assert result.ledger_summary["min_cash"] == 0
    assert result.ledger_summary["ending_cash"] == 0


def test_complex_overlapping_events():
    """Test multiple overlapping events with different durations"""
    scenario = Scenario(
        id="test8",
        title="Complex overlapping events",
        start_month=Month(2024, 1),
        horizon_months=6,
        initial_state=InitialState(starting_cash=10000),
        base_monthly=BaseMonthly(takehome_salary=5000, outflows=-2000),
        events=[
            Event(label="rent", start_month=Month(2024, 1), amount=-2000),  # Ongoing
            Event(label="bonus", start_month=Month(2024, 3), amount=5000, duration_months=1),  # One-time
            Event(label="medical", start_month=Month(2024, 2), amount=-1000, duration_months=3),  # 3 months
        ]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    # Month 1: 10000 + 5000 - 2000 - 2000 = 11000
    # Month 2: 11000 + 5000 - 2000 - 2000 - 1000 = 11000
    # Month 3: 11000 + 5000 - 2000 - 2000 - 1000 + 5000 = 17000 (bonus!)
    # Month 4: 17000 + 5000 - 2000 - 2000 - 1000 = 17000
    # Month 5: 10000 + 5000 - 2000 - 2000 = 17000 (medical ended)
    # Month 6: 11000 + 5000 - 2000 - 2000 = 18000
    assert result.ledger_summary["ending_cash"] == 18000


def test_positive_outflow_validation_error():
    """Test that positive outflows are rejected by validation"""
    with pytest.raises(ValueError, match="must be non-positive"):
        Scenario(
            id="test9",
            title="Invalid positive outflows",
            start_month=Month(2024, 1),
            horizon_months=3,
            initial_state=InitialState(starting_cash=1000),
            base_monthly=BaseMonthly(takehome_salary=2000, outflows=500),  # Invalid!
            events=[]
        )


def test_negative_income_validation_error():
    """Test that negative income is rejected by validation"""
    with pytest.raises(ValueError, match="must be non-negative"):
        Scenario(
            id="test10",
            title="Invalid negative income",
            start_month=Month(2024, 1),
            horizon_months=3,
            initial_state=InitialState(starting_cash=1000),
            base_monthly=BaseMonthly(takehome_salary=-2000, outflows=-1000),  # Invalid!
            events=[]
        )


def test_event_before_scenario_start_validation_error():
    """Test that events before scenario start are rejected"""
    with pytest.raises(ValueError, match="starts before scenario start"):
        Scenario(
            id="test11",
            title="Event before start",
            start_month=Month(2024, 3),
            horizon_months=3,
            initial_state=InitialState(starting_cash=1000),
            base_monthly=BaseMonthly(takehome_salary=2000, outflows=-1000),
            events=[
                Event(label="early_event", start_month=Month(2024, 1), amount=-500)  # Before March!
            ]
        )


def test_negative_starting_cash_validation_error():
    """Test that negative starting cash is rejected"""
    with pytest.raises(ValueError, match="must be non-negative"):
        Scenario(
            id="test12",
            title="Invalid negative starting cash",
            start_month=Month(2024, 1),
            horizon_months=3,
            initial_state=InitialState(starting_cash=-1000),  # Invalid!
            base_monthly=BaseMonthly(takehome_salary=2000, outflows=-1000),
            events=[]
        )


def test_very_tight_but_feasible():
    """Test a scenario that barely stays above zero"""
    scenario = Scenario(
        id="test13",
        title="Very tight but feasible",
        start_month=Month(2024, 1),
        horizon_months=4,
        initial_state=InitialState(starting_cash=1500),
        base_monthly=BaseMonthly(takehome_salary=4000, outflows=-3500),
        events=[
            Event(label="one_time_expense", start_month=Month(2024, 2), amount=-1900, duration_months=1),
        ]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    # Month 1: 1500 + 4000 - 3500 = 2000
    # Month 2: 2000 + 4000 - 3500 - 1900 = 600  # Tight!
    # Month 3: 600 + 4000 - 3500 = 1100
    # Month 4: 1100 + 4000 - 3500 = 1600
    assert result.ledger_summary["min_cash"] == 600


def test_year_boundary_crossing():
    """Test simulation crossing year boundaries"""
    scenario = Scenario(
        id="test14",
        title="Year boundary crossing",
        start_month=Month(2024, 11),
        horizon_months=4,
        initial_state=InitialState(starting_cash=5000),
        base_monthly=BaseMonthly(takehome_salary=3000, outflows=-2000), 
        events=[
            Event(label="holiday_bonus", start_month=Month(2024, 12), amount=5000, duration_months=1),
            Event(label="new_year_expense", start_month=Month(2025, 1), amount=-2000, duration_months=1),
        ]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    assert result.ledger_summary["ending_cash"] == 12000


def test_no_events_negative_net_flow():
    """Test simple scenario with negative net monthly flow"""
    scenario = Scenario(
        id="test15",
        title="Burn rate scenario",
        start_month=Month(2024, 1),
        horizon_months=12,
        initial_state=InitialState(starting_cash=10000),
        base_monthly=BaseMonthly(takehome_salary=3000, outflows=-4000),
        events=[]
    )

    result = run_eval(scenario)
    assert result.verdict == "infeasible"
    assert result.first_violation_month == "2024-11"  # String format
    assert result.violated_invariant == InvariantType.LIQUIDITY_FLOOR


def test_all_positive_inflows():
    """Test scenario with only positive event amounts (bonuses)"""
    scenario = Scenario(
        id="test16",
        title="Multiple bonuses",
        start_month=Month(2024, 1),
        horizon_months=6,
        initial_state=InitialState(starting_cash=1000),
        base_monthly=BaseMonthly(takehome_salary=3000, outflows=-2900),
        events=[
            Event(label="q1_bonus", start_month=Month(2024, 3), amount=5000, duration_months=1),
            Event(label="q2_bonus", start_month=Month(2024, 6), amount=5000, duration_months=1),
        ]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    assert result.ledger_summary["ending_cash"] == 11600


def test_exact_zero_net_monthly():
    """Test scenario where monthly income exactly equals outflows"""
    scenario = Scenario(
        id="test17",
        title="Zero net monthly",
        start_month=Month(2024, 1),
        horizon_months=12,
        initial_state=InitialState(starting_cash=5000),
        base_monthly=BaseMonthly(takehome_salary=4000, outflows=-4000),
        events=[]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    assert result.ledger_summary["ending_cash"] == 5000  # No change
    assert result.ledger_summary["min_cash"] == 5000


def test_large_horizon():
    """Test with a large horizon (5 years)"""
    scenario = Scenario(
        id="test18",
        title="Five year plan",
        start_month=Month(2024, 1),
        horizon_months=60,  # 5 years
        initial_state=InitialState(starting_cash=10000),
        base_monthly=BaseMonthly(takehome_salary=5000, outflows=-4500),
        events=[
            Event(label="annual_raise", start_month=Month(2025, 1), amount=500),  # Ongoing raise
        ]
    )

    result = run_eval(scenario)
    assert result.verdict == "feasible"
    # First 12 months: +500/month = +6000
    # Remaining 48 months: +1000/month = +48000
    # Total: 10000 + 6000 + 48000 = 64000
    assert result.ledger_summary["ending_cash"] == 64000