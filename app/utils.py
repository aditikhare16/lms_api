from datetime import date, timedelta
from .config import HOLIDAYS  # set of YYYY-MM-DD strings from .env

def business_days_between(start: date, end: date) -> int:
    """
    Count business days between two dates inclusive, excluding weekends and configured holidays.
    Returns 0 if end < start.
    """
    if end < start:
        return 0
    count, d = 0, start
    one = timedelta(days=1)
    while d <= end:
        if d.weekday() < 5 and d.isoformat() not in HOLIDAYS:  # Mon–Fri and not a holiday
            count += 1
        d += one
    return count
