from config_loader import config
import datetime
import requests

DISCORD_WEBHOOK_URL = config['DISCORD_WEBHOOK_URL']

def discord_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)
    print(message)