from pydantic import BaseModel, field_validator as validator
from workbench.month import Month
from typing import Optional, List

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
        
    @validator('events')
    def validate_events(cls, v: List[Event], values: dict) -> List[Event]:
        start_month = values.get('start_month')
        if start_month:
            for event in v:
                if event.start_month < start_month:
                    raise ValueError(f"Event {event.label} starts before scenario start")
        return v