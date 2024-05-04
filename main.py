import fetch_data
import manage_info
import yaml

def main():

    with open('config.yaml', encoding='UTF-8') as f:
        _cfg = yaml.load(f, Loader=yaml.FullLoader)
        APP_KEY = _cfg['APP_KEY']
        APP_SECRET = _cfg['APP_SECRET']
        ACCESS_TOKEN = ""
        CANO = _cfg['CANO']
        ACNT_PRDT_CD = _cfg['ACNT_PRDT_CD']
        DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']
        URL_BASE = _cfg['URL_BASE']

    symbols = fetch_data.load_symbols()
    for symbol in symbols:
        fetch_data.fetch_and_save_stock_data(symbol)
        manage_info.update_info(symbol)


if __name__ == "__main__":
    main()
