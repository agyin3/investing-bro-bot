import requests
import sys
import os
from dotenv import load_dotenv

# Add the project root to Python's module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """
    Send trade alerts via Telegram.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Telegram alert sent!")
        else:
            print(f"Telegram alert failed: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

# Example usage
if __name__ == "__main__":
    send_telegram_alert("🚀 Bot Started: Monitoring stock trades!")
