
"""
Utility functions that can be used multiple places.
"""

from datetime import datetime, timedelta

def weekdaystr(day):
    """
    Convert an int day to a string representation of the day.
    For example, 0 returns "Monday" and 6 returns "Sunday".  This
    mirrors the way datetime.weekday() works.
    """
    if day < 0 or day > 6:
        raise ValueError("day is out of range")
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[day]

def tdtosecs(td):
    """Convert a timedelta to seconds."""
    return (td.days * 24 * 60 * 60) + td.seconds + (td.microseconds * 0.000001)

def get_current_time():
    """
    Returns a tuple of the current date and the current time.
    """
    curdate = datetime.today()
    curtime = curdate.time()
    return curdate, curtime
