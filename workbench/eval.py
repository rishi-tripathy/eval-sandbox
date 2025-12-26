from workbench.types import Scenario, InvariantType, Violation, MonthlyRecord
from workbench.simulate import simulate
from workbench.invariants import check_invariants
from workbench.month import Month
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class EvalResult(BaseModel):
    verdict: str  # 'feasible' or 'infeasible'
    first_violation_month: Optional[str] = None 
    violated_invariant: Optional[InvariantType] = None
    ledger_summary: dict[str, Any]
    violations: List[Violation]
    ledger: List[MonthlyRecord]  # Full monthly records for validation
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            Month: lambda v: v.to_string()
        }

    
def run_eval(scenario: Scenario) -> EvalResult:

    records = simulate(scenario)
    if not records:
          return EvalResult(
              verdict='feasible',
              first_violation_month=None,
              violated_invariant=None,
              ledger_summary={'min_cash': 0, 'ending_cash': 0, 'months_simulated': 0},
              violations=[],
              ledger=[]
          )

    violations = check_invariants(scenario, records) or []

    summary = {
          'min_cash': min(r.ending_cash for r in records),
          'ending_cash': records[-1].ending_cash,
          'months_simulated': len(records)
      }

    # Determine verdict
    if violations:
        first_violation = min(violations, key=lambda v: (v.month._index, v.invariant.get_precedence()))

        return EvalResult(
        verdict='infeasible',
        first_violation_month=first_violation.month.to_string(),
        violated_invariant=first_violation.invariant,
        ledger_summary=summary,
        violations=violations,
        ledger=records
    )

    return EvalResult(
        verdict='feasible', 
        first_violation_month=None,
        violated_invariant=None,
        ledger_summary=summary,
        violations=violations,
        ledger=records
    )
    
