from pydantic import BaseModel
from enum import StrEnum
from typing import List, Optional
import statistics
from datetime import datetime, time, timedelta
import random

class SleepType(StrEnum):
    DEEP = 'Deep'
    LIGHT = 'Light'
    REM = 'REM'
    WAKE = 'Wake'

class SleepRecord(BaseModel):
    date: str  # YYYY-MM-DD
    sleep_type: SleepType
    start_time: str  # HH:MM
    end_time: str    # HH:MM
    duration_hours: float
    is_main_sleep: bool

class SleepSummary(BaseModel):
    summary_period: int # in days (should be 7 or 30)
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    total_sleep_hours: float
    average_sleep_hours: float
    sleep_hours_std_dev: float
    avg_main_sleep_hours: float

class SleepCollection(BaseModel):
    user_id: int
    sleep_records: List[SleepRecord]
    summary: Optional[SleepSummary] = None

    def summarise(self, lookback_period: int) -> SleepSummary:
        latest_date_str = max(record.date for record in self.sleep_records)
        latest_date_dt = datetime.strptime(latest_date_str, "%Y-%m-%d")
        cutoff_date_str = (latest_date_dt - timedelta(days=lookback_period)).strftime("%Y-%m-%d")
        records = [
            record for record in self.sleep_records 
            if record.date >= cutoff_date_str
        ]  

        relevant_sleeps = [record.duration_hours for record in records if record.sleep_type in [SleepType.DEEP, SleepType.LIGHT, SleepType.REM]]
        main_sleeps= [record.duration_hours for record in records if record.is_main_sleep]

        # Calculate summary statistics
        return SleepSummary(
            summary_period=lookback_period,  # or 30, depending on the context
            start_date=min(record.date for record in records),
            end_date=max(record.date for record in records),
            total_sleep_hours=sum(relevant_sleeps),
            average_sleep_hours=statistics.mean(relevant_sleeps) if relevant_sleeps else 0,
            sleep_hours_std_dev=statistics.stdev(relevant_sleeps) if len(relevant_sleeps) > 1 else 0,
            avg_main_sleep_hours=statistics.mean(main_sleeps) if main_sleeps else 0
        )
    
# TODO: This is a temporary function to generate synthetic sleep data for demo purposes
def generate_sleep_data(user_id: int, current_date: datetime, end_date: datetime) -> SleepCollection:
    records = []
    current_date = datetime(2025, 9, 1)
    end_date = datetime(2025, 9, 30)

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Determine Bedtime (22:30 to 01:30)
        start_hour_offset = random.uniform(22.5, 25.5) 
        current_time_pointer = datetime.combine(current_date, time(0,0)) + timedelta(hours=start_hour_offset)
        
        # Determine Sleep Duration Target (e.g., 6.5 to 8.5 hours)
        target_sleep = random.uniform(6.5, 8.5)
        accumulated_sleep = 0.0
        
        # Cycle Logic: We generate segments until we hit the target
        # A typical night is multiple cycles of Light -> Deep -> REM
        while accumulated_sleep < target_sleep:
            
            # 1. Light Sleep (Transition) - 15 to 45 mins
            light_dur = random.choice([0.25, 0.5, 0.75])
            
            # 2. Deep Sleep (Early night has more deep, late night has less)
            # Simple logic: Random 30 to 60 mins
            deep_dur = random.choice([0.5, 0.75, 1.0])
            
            # 3. REM Sleep (increases later in night, but we'll randomize for simplicity)
            rem_dur = random.choice([0.25, 0.5, 0.75])

            # 4. Random Wake (10-20% chance between cycles)
            wake_dur = 0.0
            if random.random() < 0.2:
                wake_dur = 0.25 # 15 min wake up
            
            # Build the sequence for this cycle
            cycle_stages = [
                (SleepType.LIGHT, light_dur),
                (SleepType.DEEP, deep_dur),
                (SleepType.REM, rem_dur)
            ]
            
            # Insert wake if it happened
            if wake_dur > 0:
                cycle_stages.append((SleepType.WAKE, wake_dur))

            # Create Records
            for s_type, dur in cycle_stages:
                # Stop adding if we exceeded target (unless it's wake)
                if accumulated_sleep >= target_sleep and s_type != SleepType.WAKE:
                    break
                
                start_str = current_time_pointer.strftime("%H:%M")
                current_time_pointer += timedelta(hours=dur)
                end_str = current_time_pointer.strftime("%H:%M")
                
                records.append(SleepRecord(
                    date=date_str,
                    sleep_type=s_type,
                    start_time=start_str,
                    end_time=end_str,
                    duration_hours=dur,
                    is_main_sleep=True
                ))
                
                if s_type != SleepType.WAKE:
                    accumulated_sleep += dur

        current_date += timedelta(days=1)

    return SleepCollection(user_id=user_id, sleep_records=records)