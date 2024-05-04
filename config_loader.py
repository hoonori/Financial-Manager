import yaml

def load_config():
    with open('config.yaml', encoding='UTF-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
    """
    APP_KEY = config['APP_KEY']
    APP_SECRET = config['APP_SECRET']
    ACCESS_TOKEN = ""
    CANO = config['CANO']
    ACNT_PRDT_CD = config['ACNT_PRDT_CD']
    DISCORD_WEBHOOK_URL = config['DISCORD_WEBHOOK_URL']
    URL_BASE = config['URL_BASE']
    """

config = load_config()