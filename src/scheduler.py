"""
Meal schedule configuration for EagleEye People Counting System.

Defines meal timing windows when the system should be active.
"""

from datetime import datetime, time
from typing import Optional, Tuple

# Meal schedule configuration
MEAL_SCHEDULE = {
    'breakfast': (time(7, 30), time(10, 0)),
    'lunch': (time(12, 0), time(14, 0)),
    'snacks': (time(17, 30), time(18, 30)),
    'dinner': (time(19, 30), time(22, 0)),
}


def get_current_meal() -> Optional[str]:
    """
    Get the current meal period based on system time.
    
    Returns:
        Meal name ('breakfast', 'lunch', 'snacks', 'dinner') 
        or None if outside meal hours
    """
    now = datetime.now().time()
    
    for meal, (start, end) in MEAL_SCHEDULE.items():
        if start <= now <= end:
            return meal
    
    return None


def is_meal_time() -> bool:
    """
    Check if current time is within any meal period.
    
    Returns:
        True if within meal hours, False otherwise
    """
    return get_current_meal() is not None


def get_next_meal() -> Tuple[str, time]:
    """
    Get the next upcoming meal period.
    
    Returns:
        Tuple of (meal_name, start_time)
    """
    now = datetime.now().time()
    
    # Sort meals by start time
    meals_sorted = sorted(MEAL_SCHEDULE.items(), key=lambda x: x[1][0])
    
    # Find next meal
    for meal, (start, end) in meals_sorted:
        if now < start:
            return (meal, start)
    
    # If after all meals today, return first meal tomorrow
    return (meals_sorted[0][0], meals_sorted[0][1][0])


def get_meal_info() -> dict:
    """
    Get comprehensive meal schedule information.
    
    Returns:
        Dictionary with current meal status and schedule info
    """
    current_meal = get_current_meal()
    
    if current_meal:
        start, end = MEAL_SCHEDULE[current_meal]
        return {
            'active': True,
            'current_meal': current_meal,
            'start_time': start.strftime('%I:%M %p'),
            'end_time': end.strftime('%I:%M %p'),
            'message': f"🍽️ {current_meal.upper()} in progress"
        }
    else:
        next_meal, next_start = get_next_meal()
        return {
            'active': False,
            'current_meal': None,
            'next_meal': next_meal,
            'next_start': next_start.strftime('%I:%M %p'),
            'message': f"⏳ Next: {next_meal.capitalize()} at {next_start.strftime('%I:%M %p')}"
        }


def print_schedule():
    """Print the meal schedule."""
    print("\n" + "=" * 50)
    print("📅 MEAL SCHEDULE")
    print("=" * 50)
    for meal, (start, end) in MEAL_SCHEDULE.items():
        print(f"  {meal.capitalize():12} {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    # Test the scheduler
    print_schedule()
    info = get_meal_info()
    print(f"Current status: {info['message']}")
