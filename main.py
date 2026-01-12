import schedule
import requests
from bs4 import BeautifulSoup
import time
import os

GOTIFY_URL = os.getenv('GOTIFY_URL', 'http://localhost')
GOTIFY_TOKEN = os.getenv('GOTIFY_TOKEN')
URL = os.getenv('URL')

def send_notification(message):
    if not GOTIFY_TOKEN:
        print("Kein Gotify Token gesetzt!")
        return
    
    try:
        requests.post(
            f'{GOTIFY_URL}/message',
            json={
                'title': 'Job Alert',
                'message': message,
                'priority': 5
            },
            headers={'X-Gotify-Key': GOTIFY_TOKEN}
        )
        print("Notification gesendet")
    except Exception as e:
        print(f"Fehler beim Senden: {e}")

def check_job(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for script in soup(['script', 'style']):
        script.decompose()
    
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    text = '\n'.join(line for line in lines if line)
    
    file_path = '/app/data/last_content.txt'
    
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Initiale Version gespeichert")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        old_content = f.read()
    
    if old_content != text:
        print("ÄNDERUNG GEFUNDEN!")
        send_notification(f'Änderung auf {url} erkannt!')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        print("Keine Änderung")
        send_notification(f'Keine Änderung auf {url} erkannt!')

schedule.every().day.at("08:00").do(check_job, url)
schedule.every().day.at("20:00").do(check_job, url)

while True:
    schedule.run_pending()
    time.sleep(60)