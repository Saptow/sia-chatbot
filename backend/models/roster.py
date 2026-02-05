from pydantic import BaseModel
from enum import StrEnum
from datetime import datetime, time, timedelta
from typing import Union, Optional, List

## Roster Schedule Mappings ## TODO: These can be expanded or modified as per actual shift definitions, but we take this as ground truth for now. 
MAPPING_EIGHT_HOURS_SHIFT = {
    'N': {'start_time': time(0, 0), 'end_time': time(9,15), 'total_hours': 9.25, 'breaks': [{'start_time': time(6,0), 'end_time': time(6,45), 'total_hours': 0.75}]},
    'M': {'start_time': time(8,0), 'end_time': time(17,15), 'total_hours': 9.25, 'breaks': [{'start_time': time(12,0), 'end_time': time(12,45), 'total_hours': 0.75}]},
    'A': {'start_time': time(15,15), 'end_time': time(0,0), 'total_hours': 9.25, 'breaks': [{'start_time': time(18,00), 'end_time': time(18,45), 'total_hours': 0.75}]},
    'OH': {'start_time': time(8,30), 'end_time': time(17,30), 'total_hours': 9.0, 'breaks': [{'start_time': time(12,0), 'end_time': time(12,45), 'total_hours': 0.75}]}
    }

MAPPING_TWELVE_HOURS_SHIFT = {
    'A': {'start_time': time(8,0), 'end_time': time(19,30), 'total_hours': 11.5, 'breaks': [{'start_time': time(12,0), 'end_time': time(12,45), 'total_hours': 0.75}]},
    'B/D': {'start_time': time(19,00), 'end_time': time(8,30), 'total_hours': 13.5, 'breaks': [{'start_time': time(0,30), 'end_time': time(1,15), 'total_hours': 0.75}, {'start_time': time(6,0), 'end_time': time(6,45), 'total_hours': 0.75}]},
    'C': {'start_time': time(10,0), 'end_time': time(19,0), 'total_hours': 9.0, 'breaks': [{'start_time': time(12,0), 'end_time': time(12,45), 'total_hours': 0.75}]},
    'L': {'start_time': time(13,00), 'end_time': time(22,0), 'total_hours': 9.0, 'breaks': [{'start_time': time(18,0), 'end_time': time(18,45), 'total_hours': 0.75}]}
    }

## Enums ##
class EightHourShiftType(StrEnum):
    N='N' # Night Shift
    M='M' # Morning Shift
    A='A' # Afternoon Shift
    OH='OH' # Off-Hours Shift

class TwelveHourShiftType(StrEnum):
    A='A' # day shift
    B_D='B/D' # evening shift
    C='C' # night shift
    L = 'L' # late night shift

class RosterType(StrEnum):
    EIGHT_HOUR = '8-hour'
    TWELVE_HOUR = '12-hour'

## Data Models ##
class TimePeriod(BaseModel):
    start_time: time
    end_time: time
    total_hours: float

class Shift(BaseModel):
    duration: List[TimePeriod] # start time, end time
    breaks: List[TimePeriod] # break start time, break end time

class RosterDay(BaseModel):
    date: str  # YYYY-MM-DD for that current day 
    shifts: List[Shift]

class Roster(BaseModel):
    type: RosterType
    start: str  # YYYY-MM-DD for the start date of the roster
    end: str    # YYYY-MM-DD for the end date of the roster
    roster_days: List[RosterDay]

    @classmethod
    #TODO: this is a temporary method to generate synthetic roster data for demo purposes
    def generate(cls, start_date: str, end_date: str, roster_type: RosterType, shift_sequence: List[str]) -> "Roster":
        """
        Factory method to create a Roster object from a start date, end date, and shift pattern.
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if roster_type == RosterType.EIGHT_HOUR:
            mapping = MAPPING_EIGHT_HOURS_SHIFT
            enum_cls = EightHourShiftType
        else:
            mapping = MAPPING_TWELVE_HOURS_SHIFT
            enum_cls = TwelveHourShiftType

        roster_days_list = []
        current_dt = start_dt
        seq_index = 0
        
        while current_dt <= end_dt:
            # Cycle through the provided sequence using modulo
            shift_key = shift_sequence[seq_index % len(shift_sequence)]
            
            # Fetch data from mapping
            shift_data = mapping.get(shift_key)
            
            day_shifts = []
            if shift_data:
                new_shift = Shift(
                    type=enum_cls(shift_key),
                    duration=[TimePeriod(
                        start_time=shift_data['start_time'],
                        end_time=shift_data['end_time'],
                        total_hours=shift_data['total_hours']
                    )],
                    breaks=[TimePeriod(**b) for b in shift_data['breaks']]
                )
                day_shifts.append(new_shift)
            
            roster_day = RosterDay(
                type=roster_type,
                date=current_dt.strftime("%Y-%m-%d"),
                shifts=day_shifts
            )
            
            roster_days_list.append(roster_day)
            
            current_dt += timedelta(days=1)
            seq_index += 1

        return cls(start=start_date, end=end_date, roster_days=roster_days_list)
    
