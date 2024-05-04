import fetch_data
import manage_info

def main():
    symbols = fetch_data.load_symbols()
    for symbol in symbols:
        fetch_data.fetch_and_save_stock_data(symbol)
        manage_info.update_info(symbol)


if __name__ == "__main__":
    main()
