import pandas as pd
import os
import json
from datetime import datetime

DEBUG = True

def log(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def read_json(filename):
    """Reads a JSON file saved with lines=True and returns a list of dictionaries."""
    with open(filename, 'r') as file:
        data = json.load(file)  # Load the complete JSON object)
    return data

def write_json(data, filename):
    """Utility function to write JSON data to a file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)

def update_file(raw_data_file, info_file):
    """Update the info data based on new raw data."""
    if not os.path.exists(info_file):
        print("Info file does not exist. Creating a new one.")
        info_data = []
    else:
        info_data = read_json(info_file)

    log(raw_data_file)

    raw_data = read_json(raw_data_file)
    updates = []
    updated = False

    # Assuming both data sets are lists of dictionaries
    for new_entry in raw_data:
        for existing_entry in info_data:
            if existing_entry['Date'] == new_entry['Date']:
                # Compare for any differences
                if existing_entry != new_entry:
                    updates.append((existing_entry, new_entry))
                    info_data.remove(existing_entry)
                    info_data.append(new_entry)
                    updated = True
                break
        else:
            # If no matching date is found, append new entry
            info_data.append(new_entry)
            updates.append((None, new_entry))
            updated = True

    if updated:
        write_json(info_data, info_file)
        if updates:
            for old, new in updates:
                print(f"Updated from {old} to {new}")
        else:
            print("No updates were made.")
    else:
        print("No updates were necessary.")

def update_info(symbol):
    info_path = f'info/{symbol}.json'

    if not os.path.exists('info'):
        os.makedirs('info')
    
    if not os.path.exists('raw_datas'):
        print(f'no raw data exists to process')
        return None

    raw_data_folders = [f'raw_datas/{folder}' for folder in sorted(os.listdir('raw_datas')) if os.path.isdir(f'raw_datas/{folder}')]
    
    #read data. file path is great. target file is saved as following:
    #orient='records', lines=True, date_format='iso', indent=2
    all_data = []
    for folder in raw_data_folders:
        file_path = f'{folder}/{symbol}/data.json'
        print(f'[info] trying to update{symbol}info. . .')
        update_file(file_path, f'info/{symbol}.json')
