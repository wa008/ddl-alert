import datetime

def should_notify(ddl_date, days_ahead=7):
    """
    Determines if a notification should be sent.
    Checks if ddl_date is exactly days_ahead natural days from today.
    """
    today = datetime.date.today()
    
    # If DDL is in the past, don't notify
    if ddl_date < today:
        return False
        
    diff = (ddl_date - today).days
    return diff == days_ahead
