# TODO: THIS IS A STATIC DATA FILE FOR DEMO PURPOSES ONLY
# In production/a more rigorous POV, this data should be fetched from a secure database (can init some Firebase/MongoDB instance)

# Mock user info dictionary for demo purposes
import datetime
from backend.models.exercise import generate_exercise_data
from backend.models.personal import Personnel, Role
from backend.models.roster import Roster
from backend.models.sleep import SleepCollection, generate_sleep_data


USER_INFO_DICTIONARY = {
    1: {
        "position": "Air Traffic Controller",
        "age": 28,
        "gender": "F",
        "roster_info": {

        },

        "current_location": "Singapore",
        "favourite_activities": ["running", "photography", "travel blogging"]
    },
    2: {
        "position": "Air Traffic Controller",
        "age": 31,
        "gender": "M",
        "current_location": "Tokyo",
        "favourite_activities": ["surfing", "guitar", "cycling"]
    },
    3: {
        "position": "Air Traffic Controller",
        "age": 26,
        "gender": "F",
        "current_location": "Doha",
        "favourite_activities": ["painting", "baking", "yoga"]
    }
}

# Mock Personnels data for demo purposes
# Dictionary mapping (user_id -> Personnel instances)
PERSONNELS_DATA = {
    1: Personnel(
        user_id=1,
        position=Role.ATC,
        age=28,
        gender='F',
        roster_info=Roster.generate(
            start_date="2025-09-01",
            end_date="2025-09-30",
            roster_type="EIGHT_HOUR",
            shift_sequence=[
                "N", "M", "A", "OH", "N", "M", "A", "OH",
                "N", "M", "A", "OH", "N", "M", "A", "OH",
                "N", "M", "A", "OH", "N", "M", "A", "OH",
                "N", "M", "A", "OH", "N", "M"
            ]
        ),
        sleep_info=generate_sleep_data(
            user_id=1,
            current_date=datetime(2025, 9, 1),
            end_date=datetime(2025, 9, 30)
        ),
        exercise_info=generate_exercise_data(
            user_id=1,
            current_date=datetime(2025, 9, 1),
            end_date=datetime(2025, 9, 30)
        ), # add actual roster data here
    ),
    
    2: Personnel(
        user_id=2,
        position=Role.ATC,
        age=31,
        gender='M',
        roster_info=Roster.generate(
            start_date="2025-09-01",
            end_date="2025-09-30",
            roster_type="TWELVE_HOUR",
            shift_sequence=[
                "A", "B/D", "C", "L", "A", "B/D", "C", "L",
                "A", "B/D", "C", "L", "A", "B/D", "C", "L",
                "A", "B/D", "C", "L", "A", "B/D", "C", "L",
                "A", "B/D", "C", "L", "A", "B/D"
            ]
        ),
        sleep_info=generate_sleep_data(
            user_id=2,
            current_date=datetime(2025, 9, 1),
            end_date=datetime(2025, 9, 30)
        ),
        exercise_info=generate_exercise_data(
            user_id=2,
            current_date=datetime(2025, 9, 1),
            end_date=datetime(2025, 9, 30)
        )
    ),
    }