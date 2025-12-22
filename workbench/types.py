from workbench.month import Month
from pydantic import BaseModel, field_validator as validator, model_validator
from typing import Optional, List
from enum import Enum

class Event(BaseModel):
    label: str
    start_month: Month
    amount: float
    duration_months: Optional[int] = None # if None, the event occurs monthly until the end of the scenario
    

class BaseMonthly(BaseModel):
    takehome_salary: float
    outflows: float
    
    @validator('takehome_salary')
    def validate_takehome_salary(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"{v} specified is not a valid monthly takehome salary, takehome must be non-negative")
        return v
    
    @validator('outflows')
    def validate_outflows(cls, v: float) -> float:
        if v > 0:
            raise ValueError(f"{v} specified is not a valid baseline outflow amount, outflows must be non-positive")
        return v

class InitialState(BaseModel):
    starting_cash: float

    @validator('starting_cash')
    def validate_starting_cash(cls, v: float) -> float:
        if v < 0:
            raise ValueError(f"{v} specified is not a valid starting cash, starting cash must be non-negative")
        return v

class Scenario(BaseModel):
    id: str
    title: str
    start_month: Month
    horizon_months: int
    initial_state: InitialState
    base_monthly: BaseMonthly
    events: List[Event]

    @model_validator(mode='after')
    def validate_events(self) -> 'Scenario':
        start_month = self.start_month
        if start_month:
            for event in self.events:
                if event.start_month < start_month:
                    raise ValueError(f"Event {event.label} starts before scenario start")
        return self

class MonthlyRecord(BaseModel):
    month: Month
    starting_cash: float
    base_takehome_salary: float
    base_outflows: float
    total_inflows: float
    total_outflows: float
    events_applied: List[Event]
    ending_cash: float

class InvariantType(Enum):
    LIQUIDITY_FLOOR = "LIQUIDITY_FLOOR"
    MONEY_CONSERVATION = "MONEY_CONSERVATION"
    TEMPORAL_CONSISTENCY = "TEMPORAL_CONSISTENCY"

    def get_precedence(self) -> int:
        if self == InvariantType.MONEY_CONSERVATION:
            return 0
        elif self == InvariantType.TEMPORAL_CONSISTENCY:
            return 1
        elif self == InvariantType.LIQUIDITY_FLOOR:
            return 2
        return 3
  
class Violation(BaseModel):
    invariant: InvariantType
    month: Month
    record: MonthlyRecord
    magnitude: Optional[float] = None
    details: Optional[str] = None