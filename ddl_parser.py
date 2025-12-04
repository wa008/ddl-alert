import os
import datetime
import re

def parse_date(date_str):
    """
    Parses a date string like "April 9-10, 2026", "April 3, 2026", "December 24, 2025 - January 2, 2026", or "October 25 - November 2, 2025".
    Returns a datetime.date object representing the START date.
    """
    date_str = date_str.strip()
    
    # Clean up trailing hyphens or extra spaces
    if date_str.endswith('-'):
        date_str = date_str[:-1].strip()

    # Regex patterns
    # 1. "Month Day-Day, Year" (e.g., April 9-10, 2026)
    match_range_simple = re.match(r"([A-Za-z]+)\s+(\d+)-(\d+),\s+(\d{4})", date_str)
    if match_range_simple:
        month, start_day, end_day, year = match_range_simple.groups()
        date_str_clean = f"{month} {start_day}, {year}"
        try:
            return datetime.datetime.strptime(date_str_clean, "%B %d, %Y").date()
        except ValueError:
            pass

    # 2. "Month Day - Month Day, Year" (e.g., October 25 - November 2, 2025)
    match_range_complex = re.match(r"([A-Za-z]+)\s+(\d+)\s*-\s*([A-Za-z]+)\s+(\d+),\s+(\d{4})", date_str)
    if match_range_complex:
        start_month, start_day, end_month, end_day, year = match_range_complex.groups()
        
        # Check if months are in order
        try:
            start_month_num = datetime.datetime.strptime(start_month, "%B").month
            end_month_num = datetime.datetime.strptime(end_month, "%B").month
        except ValueError:
            return None 

        start_year = int(year)
        if start_month_num > end_month_num:
            start_year -= 1
        
        date_str_clean = f"{start_month} {start_day}, {start_year}"
        try:
            return datetime.datetime.strptime(date_str_clean, "%B %d, %Y").date()
        except ValueError:
            pass

    # 3. "Month Day, Year - Month Day, Year" (e.g., December 24, 2025 - January 2, 2026)
    match_range_full = re.match(r"([A-Za-z]+)\s+(\d+),\s+(\d{4})\s*-\s*([A-Za-z]+)\s+(\d+),\s+(\d{4})", date_str)
    if match_range_full:
        start_month, start_day, start_year, end_month, end_day, end_year = match_range_full.groups()
        date_str_clean = f"{start_month} {start_day}, {start_year}"
        try:
            return datetime.datetime.strptime(date_str_clean, "%B %d, %Y").date()
        except ValueError:
            pass

    # 4. Simple single date: "April 3, 2026"
    try:
        return datetime.datetime.strptime(date_str, "%B %d, %Y").date()
    except ValueError:
        pass
        
    # 4. "Month Day -" (Start of a split range, e.g. "October 25 -")
    # If we see this, we might need to look ahead, but parse_date takes a string.
    # The caller should handle combining lines if possible, or we handle it here if passed "October 25"
    # But "October 25" is incomplete without year.
    # If the input is just "October 25", we can't parse it fully without year.
    # However, if the caller passes "October 25 - November 2, 2025", we handled it above.
    
    return None

def parse_ddl_file(filepath):
    """
    Reads a file and returns a list of dictionaries with 'date' and 'description'.
    Handles multi-line entries where date and description are on separate lines.
    """
    ddls = []
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return ddls

    with open(filepath, 'r') as f:
        lines = f.readlines()

    current_date_str = None
    current_desc_lines = []
    
    # We need to iterate and maintain state
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            # Empty line usually separates entries
            if current_date_str:
                # We have a pending entry, let's save it
                # Check if the next line is a continuation of the date (rare but possible if split)
                # Actually, looking at the file, empty lines separate entries.
                # So if we hit empty line, we finalize the previous entry.
                
                # But wait, sometimes description is multiple lines?
                # "September 2, 2025
                # Academic orientation ...
                # Orientation for ...
                # Class and laboratory ..."
                # Then empty line.
                
                # So:
                # 1. If we have a date and description, and hit empty line -> Save.
                # 2. If we have a date and NO description yet -> Continue (next lines are desc).
                # 3. If we have no date -> This line must be a date (or garbage).
                
                if current_desc_lines:
                    # Save current entry
                    full_desc = " ".join(current_desc_lines)
                    ddl_date = parse_date(current_date_str)
                    if ddl_date:
                        ddls.append({
                            'date': ddl_date,
                            'description': full_desc,
                            'original_line': f"{current_date_str} | {full_desc}" # Approximation
                        })
                    # Reset
                    current_date_str = None
                    current_desc_lines = []
            
            i += 1
            continue

        # Non-empty line
        if current_date_str is None:
            # This line should be a date
            # Check if it looks like a date
            # "May 22, 2025" or "October 25 -"
            
            # Special handling for split date ranges:
            # "October 25 -"
            # "November 2, 2025"
            # If the line ends with '-', it might be continued on the next line?
            # Looking at file:
            # 80: October 25 -
            # 81: 
            # 82: November 2, 2025
            # 83: Final examinations ...
            # This implies "October 25 - November 2, 2025" is the date range for the event described in 83?
            # Or are they two separate events?
            # Line 80 "October 25 -" followed by empty line 81.
            # Then 82 "November 2, 2025".
            # Then 83 Description.
            # This looks like "October 25 - November 2, 2025: Final examinations..."
            # BUT there is an empty line in between.
            
            # Let's look at another one:
            # 132: December 24, 2025 -
            # 133: 
            # 134: January 2, 2026
            # 135: University closed.
            
            # It seems "Date Part 1" -> Empty -> "Date Part 2" -> Description.
            # This is tricky.
            
            if line.endswith('-') or line.endswith(' -'):
                # It's a split date range.
                part1 = line
                # Look ahead for part 2
                j = i + 1
                part2 = None
                while j < len(lines):
                    next_l = lines[j].strip()
                    if next_l:
                        part2 = next_l
                        break
                    j += 1
                
                if part2:
                    # Combine
                    combined_date = f"{part1} {part2}"
                    current_date_str = combined_date
                    # Skip to the line after part2
                    i = j + 1
                    continue
                else:
                    # Could not find part 2, treat as is
                    current_date_str = line
            else:
                # Normal date line
                current_date_str = line
        else:
            # We already have a date, so this must be part of the description
            current_desc_lines.append(line)
            
        i += 1

    # End of file, save last entry if exists
    if current_date_str and current_desc_lines:
        full_desc = " ".join(current_desc_lines)
        ddl_date = parse_date(current_date_str)
        if ddl_date:
            ddls.append({
                'date': ddl_date,
                'description': full_desc,
                'original_line': f"{current_date_str} | {full_desc}"
            })

    return ddls
