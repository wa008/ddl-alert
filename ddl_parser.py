import os
import datetime
import re

def parse_date(date_str):
    """
    Parses a date string. Supported formats:
    1. "April 9-10, 2026" -> Start: April 9, 2026
    2. "April 3, 2026" -> Start: April 3, 2026
    3. "December 24, 2025 - January 2, 2026" -> Start: December 24, 2025
    4. "October 25 - November 2, 2025" -> Start: October 25, 2025
    
    Returns a datetime.date object representing the START date.
    """
    date_str = date_str.strip()
    
    # Clean up trailing hyphens or extra spaces
    if date_str.endswith('-'):
        date_str = date_str[:-1].strip()

    # 1. "Month Day-Day, Year" (e.g., April 9-10, 2026)
    match_range_simple = re.match(r"([A-Za-z]+)\s+(\d+)-(\d+),\s+(\d{4})", date_str)
    if match_range_simple:
        month, start_day, _, year = match_range_simple.groups()
        date_str_clean = f"{month} {start_day}, {year}"
        try:
            return datetime.datetime.strptime(date_str_clean, "%B %d, %Y").date()
        except ValueError:
            pass

    # 3. "Month Day, Year - Month Day, Year" (e.g., December 24, 2025 - January 2, 2026)
    match_range_full = re.match(r"([A-Za-z]+)\s+(\d+),\s+(\d{4})\s*-\s*([A-Za-z]+)\s+(\d+),\s+(\d{4})", date_str)
    if match_range_full:
        start_month, start_day, start_year, _, _, _ = match_range_full.groups()
        date_str_clean = f"{start_month} {start_day}, {start_year}"
        try:
            return datetime.datetime.strptime(date_str_clean, "%B %d, %Y").date()
        except ValueError:
            pass

    # 4. "Month Day - Month Day, Year" (e.g., October 25 - November 2, 2025)
    match_range_complex = re.match(r"([A-Za-z]+)\s+(\d+)\s*-\s*([A-Za-z]+)\s+(\d+),\s+(\d{4})", date_str)
    if match_range_complex:
        start_month, start_day, end_month, _, year = match_range_complex.groups()
        
        # Determine start year
        try:
            start_month_num = datetime.datetime.strptime(start_month, "%B").month
            end_month_num = datetime.datetime.strptime(end_month, "%B").month
        except ValueError:
            return None 

        start_year = int(year)
        if start_month_num > end_month_num:
            # e.g. December - January, and year is for end date
            start_year -= 1
        
        date_str_clean = f"{start_month} {start_day}, {start_year}"
        try:
            return datetime.datetime.strptime(date_str_clean, "%B %d, %Y").date()
        except ValueError:
            pass

    # 2. Simple single date: "April 3, 2026"
    try:
        return datetime.datetime.strptime(date_str, "%B %d, %Y").date()
    except ValueError:
        pass
    
    return None

def parse_ddl_file(filepath):
    """
    Reads a file and returns a list of dictionaries with 'date', and 'original_message'.
    Handles multi-line entries where date are on separate lines.
    """
    ddls = []
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return ddls

    # read file and split it by two \n 
    with open(filepath, 'r') as f:
        blocks = f.read().split('\n\n')

    for block in blocks:
        lines = block.split('\n')
        if len(lines) < 2:
            continue
        
        date_str = lines[0].strip()
        desc_lines = lines[1:]
        
        ddl_date = parse_date(date_str)
        if ddl_date:
            ddls.append({
                'date': ddl_date,
                'original_message': block
            })

    return ddls
