from functools import total_ordering
from typing import Iterator
from pydantic_core import core_schema

@total_ordering
class Month:
    index: int

    def __init__(self, year: int, month: int):
        if year < 0:
            raise ValueError(f"{year} specified is not a valid year")
        if month < 1 or month > 12:
            raise ValueError(f"{month} specified is not a valid month")
        self._index = (year*12) + (month-1)
    
    @property
    def year(self) -> int:
        return self._index // 12

    @property
    def month(self) -> int:
        return self._index % 12 + 1

    @classmethod
    def from_string(cls, string: str) -> 'Month':
        year, month = string.split('-')
        return Month(int(year), int(month))

    @classmethod
    def from_index(cls, index: int) -> 'Month':
        year = index // 12
        month = (index % 12) + 1
        return Month(year, month)
        
    def __json__(self):
        """For JSON serialization"""
        return self.to_string()
    
    def model_dump(self):
        """For Pydantic serialization"""
        return self.to_string()
    
    @classmethod
    def iterate(cls, start: 'Month', count: int) -> Iterator['Month']:
        for i in range(count):
            yield start.add(i)


    def to_string(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"
    
    def __eq__(self, other: 'Month') -> bool:
        return self._index == other._index

    def __lt__(self, other: 'Month') -> bool:
        return self._index < other._index

    def add(self, months: int) -> 'Month':
        return Month.from_index(self._index + months)
    


    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):

        def validate_month(v):
            if isinstance(v, cls):
                return v
            if isinstance(v, str):
                return cls.from_string(v)
            raise ValueError(f"Cannot convert {type(v)} to Month")

        return core_schema.no_info_plain_validator_function(validate_month)