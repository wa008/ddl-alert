import datetime

def is_business_day(date):
    """
    Checks if a date is a business day (Mon-Fri).
    Returns True if Mon-Fri, False if Sat-Sun.
    """
    # weekday(): Monday is 0, Sunday is 6
    return date.weekday() < 5

def get_business_days_difference(start_date, end_date):
    """
    Calculates the number of business days between start_date and end_date.
    start_date is excluded, end_date is included? 
    Let's define it as: how many business days are there from start_date to end_date.
    If start_date is today, and end_date is 3 business days away.
    
    Example:
    Fri (Today) -> Mon (1 BD away) -> Tue (2 BD away) -> Wed (3 BD away)
    
    We want to find if end_date is exactly N business days after start_date.
    """
    if start_date > end_date:
        return -1 # Or handle appropriately
    
    current_date = start_date
    business_days = 0
    while current_date < end_date:
        current_date += datetime.timedelta(days=1)
        if is_business_day(current_date):
            business_days += 1
            
    return business_days

def should_notify(ddl_date, days_ahead=3):
    """
    Determines if a notification should be sent.
    Checks if ddl_date is exactly days_ahead business days from today.
    """
    today = datetime.date.today()
    
    # If DDL is in the past, don't notify
    if ddl_date < today:
        return False
        
    diff = get_business_days_difference(today, ddl_date)
    return diff == days_ahead
