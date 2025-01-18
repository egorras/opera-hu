import requests
import json
import os

class OperaTicketMonitor:
    def __init__(self):
        self.base_url = 'https://opera.jegy.hu/auditview/ticketcount'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Load events from JSON file
        with open('events.json', 'r', encoding='utf-8') as f:
            self.events = json.load(f)
        self.bot_token = os.environ['BOT_TOKEN']
        self.chat_id = os.environ['CHAT_ID']

    def check_event_prices(self, event):
        data = {'event_id': event['event_id']}
        response = requests.post(self.base_url, data=data, headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            if result['success'] and result['prices']:
                lowest_price = min(int(price) for price in result['prices'].keys())
                if lowest_price <= event['price_threshold']:
                    return self.create_notification_message(event, lowest_price)
        return None

    def create_notification_message(self, event, price):
        return (f"🎭 Билеты доступны!\n\n"
                f"{event['name']}\n"
                f"{event['date']}\n"
                f"Цена от: {price} HUF\n"
                f"{event['purchase_url']}")

    def send_telegram_notification(self, message):
        telegram_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        requests.post(telegram_url, data=data)

    def monitor_events(self):
        for event in self.events:
            try:
                notification = self.check_event_prices(event)
                if notification:
                    self.send_telegram_notification(notification)
            except Exception as e:
                print(f"Error checking event {event['event_id']}: {str(e)}")

if __name__ == "__main__":
    monitor = OperaTicketMonitor()
    monitor.monitor_events() 