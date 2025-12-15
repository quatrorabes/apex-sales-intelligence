# apps/backend/intelligence/utils.py
"""
Apex Intelligence - Utility Functions
"""

from typing import Optional


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    if denominator == 0:
        return default
    return numerator / denominator


def normalize_score(value: float, min_val: float = 0, max_val: float = 100) -> float:
    """Normalize a score to a range"""
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


def calculate_days_between(date1, date2) -> int:
    """Calculate days between two dates"""
    try:
        if isinstance(date1, str):
            from datetime import datetime
            date1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
        if isinstance(date2, str):
            from datetime import datetime
            date2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
        
        return abs((date2 - date1).days)
    except:
        return 0
