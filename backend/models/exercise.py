from pydantic import BaseModel
from enum import StrEnum
from typing import Optional
import statistics
from datetime import datetime, timedelta
import random

class ExerciseEntry(BaseModel):
    start: str  # YYYY-MM-DD
    end: str    # YYYY-MM-DD
    exercise_type: str  # e.g., 'Sedentary', 'Light'
    duration_hours: float
    calories_burned: int
    steps_taken: Optional[int] = None

class ExerciseSummary(BaseModel):
    summary_period: int # in days (should be 7 or 30)
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    average_exercise_hours: float
    exercise_hours_std_dev: float
    average_calories_burned: float
    calories_burned_std_dev: float
    average_steps_taken: Optional[float] = None
    steps_taken_std_dev: Optional[float] = None
    average_sedentary_duration: Optional[float] = None
    sedentary_duration_std_dev: Optional[float] = None


class ExerciseCollection(BaseModel):
    user_id: int
    exercise_entries: list[ExerciseEntry]
    exercise_summary: ExerciseSummary

    def summarise(self, lookback_period: int) -> ExerciseSummary:
        # (Your provided logic here, compacted for brevity)
        latest_date_str = max(e.start for e in self.exercise_entries)
        latest_date_dt = datetime.strptime(latest_date_str, "%Y-%m-%d")
        cutoff_date_str = (latest_date_dt - timedelta(days=lookback_period)).strftime("%Y-%m-%d")
        
        entries = [e for e in self.exercise_entries if e.start >= cutoff_date_str]
        
        # Helper to safely filter None values
        def get_valid_steps(ent_list):
            return [e.steps_taken for e in ent_list if e.steps_taken is not None]

        exercise_hours = [e.duration_hours for e in entries]
        calories_burned = [e.calories_burned for e in entries]
        steps_taken = get_valid_steps(entries)
        sedentary_durations = [e.duration_hours for e in entries if e.exercise_type == 'Sedentary']

        return ExerciseSummary(
            summary_period=lookback_period,
            start_date=min(e.start for e in entries),
            end_date=max(e.end for e in entries),
            average_exercise_hours=statistics.mean(exercise_hours) if exercise_hours else 0,
            exercise_hours_std_dev=statistics.stdev(exercise_hours) if len(exercise_hours) > 1 else 0,
            average_calories_burned=statistics.mean(calories_burned) if calories_burned else 0,
            calories_burned_std_dev=statistics.stdev(calories_burned) if len(calories_burned) > 1 else 0,
            average_steps_taken=statistics.mean(steps_taken) if steps_taken else None,
            steps_taken_std_dev=statistics.stdev(steps_taken) if len(steps_taken) > 1 else None,
            average_sedentary_duration=statistics.mean(sedentary_durations) if sedentary_durations else None,
            sedentary_duration_std_dev=statistics.stdev(sedentary_durations) if len(sedentary_durations) > 1 else None
        )



















# TODO: This is a temporary function to generate synthetic exercise data for demo purposes
ACTIVITY_CONFIG = {
    "Light": {"cals_per_hour": 200, "steps_per_hour": random.randint(3000, 7000)},  # Walking
    "Sedentary": {"cals_per_hour": 80,  "steps_per_hour": 0}     # Office work
}

def generate_exercise_data(user_id: int, start_date: datetime, end_date: datetime) -> ExerciseCollection:
    entries = []
    current_dt = start_date
    
    while current_dt <= end_date:
        date_str = current_dt.strftime("%Y-%m-%d")
        
        # 1. Always generate a "Sedentary" baseline
        sed_hours = random.uniform(6.0, 9.0)
        entries.append(ExerciseEntry(
            start=date_str, end=date_str,
            exercise_type="Sedentary",
            duration_hours=round(sed_hours, 2),
            calories_burned=int(sed_hours * ACTIVITY_CONFIG["Sedentary"]["cals_per_hour"]),
            steps_taken=0
        ))

        # 2. Determine "Day Type"
        rand_val = random.random()
        
        # -- SCENARIO A: Rest Day (20%) --
        if rand_val < 0.2:
            pass # No extra activity
            
        # -- SCENARIO B: Normal Active Day (40%) --
        # Short duration Light activity
        elif rand_val < 0.6:
            duration = random.uniform(0.5, 1.0) # 30 mins to 1 hour
            
            # Dynamic Step Count Logic
            steps_per_hour = random.randint(3000, 7000)
            cals_per_hour = ACTIVITY_CONFIG["Light"]["cals_per_hour"]
            
            # Add randomness to stats
            cals = int(duration * cals_per_hour * random.uniform(0.9, 1.1))
            steps = int(duration * steps_per_hour)
            
            entries.append(ExerciseEntry(
                start=date_str, end=date_str,
                exercise_type="Light",
                duration_hours=round(duration, 2),
                calories_burned=cals,
                steps_taken=steps
            ))

        # -- SCENARIO C: Very Active Day (40%) --
        # Same Type ("Light"), but Double Duration (Simulating a long hike or busy day)
        else:
            # Instead of changing type to Gym, we just increase duration significantly
            duration = random.uniform(1.5, 2.5) # 1.5 to 2.5 hours of Light activity
            
            steps_per_hour = random.randint(4000, 7500) # Slightly higher intensity
            cals_per_hour = ACTIVITY_CONFIG["Light"]["cals_per_hour"]
            
            cals = int(duration * cals_per_hour * random.uniform(0.9, 1.1))
            steps = int(duration * steps_per_hour)
            
            entries.append(ExerciseEntry(
                start=date_str, end=date_str,
                exercise_type="Light", # Still using Light
                duration_hours=round(duration, 2),
                calories_burned=cals,
                steps_taken=steps
            ))

        current_dt += timedelta(days=1)

    # 3. Initialization Logic
    dummy_summary = ExerciseSummary(
        summary_period=0, start_date="", end_date="",
        average_exercise_hours=0, exercise_hours_std_dev=0,
        average_calories_burned=0, calories_burned_std_dev=0
    )
    
    collection = ExerciseCollection(
        user_id=user_id,
        exercise_entries=entries,
        exercise_summary=dummy_summary
    )
    
    total_days = (end_date - start_date).days + 1
    collection.exercise_summary = collection.summarise(lookback_period=total_days)
    
    return collection