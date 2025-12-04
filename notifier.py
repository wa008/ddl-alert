import os
import requests
import json

def send_discord_notification(message):
    """
    Sends a message to the Discord Webhook URL defined in environment variables.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Error: DISCORD_WEBHOOK_URL not found in environment variables.")
        return False

    payload = {
        "content": message
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Notification sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending notification: {e}")
        return False
