"""
Date utility functions
"""
from datetime import datetime, timedelta


def calculate_date_range(years):
    """
    Calculate start and end dates based on the number of years from today.
    
    Parameters:
    years (int): Number of years to look back from today.
    
    Returns:
    tuple: (start_date, end_date) as strings in 'YYYY-MM-DD' format.
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years * 365)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

