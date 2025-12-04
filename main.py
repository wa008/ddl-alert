import os
import glob
from dotenv import load_dotenv
from ddl_parser import parse_ddl_file
from utils import should_notify
from notifier import send_discord_notification

def main():
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    try:
        alert_days = int(os.getenv("ALERT_DAYS", 3))
    except ValueError:
        print("Invalid ALERT_DAYS in .env, defaulting to 3.")
        alert_days = 3
        
    ddl_dir = os.getenv("DDL_DIR", "data")
    
    print(f"Checking for DDLs {alert_days} business days from today in '{ddl_dir}'...")
    
    if not os.path.exists(ddl_dir):
        print(f"Directory '{ddl_dir}' not found. Please create it and add DDL files.")
        return

    # Process all files in the directory
    for filepath in glob.glob(os.path.join(ddl_dir, "*")):
        if not os.path.isfile(filepath):
            continue
            
        print(f"Processing file: {filepath}")
        ddls = parse_ddl_file(filepath)
        
        for ddl in ddls:
            if should_notify(ddl['date'], days_ahead=alert_days):
                # Format message: replace | with \t
                original_line = ddl['original_line']
                message = original_line.replace('|', '\t')
                
                print(f"Sending notification for: {message}")
                send_discord_notification(message)

if __name__ == "__main__":
    main()
