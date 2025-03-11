from pathlib import Path
from items import Item
import json
import pandas as pd
from config import DATA_FOLDER, LISTING_IDS_FOLDER, RECORDS_FOLDER
import openai
import re

class Utils:
    
    def __init__(self):
        pass
        
    def load_ids(self, folder_name: str, file_name: str) -> list:
        file_path = Path(DATA_FOLDER) / folder_name / file_name
        # Read back the file
        with open(file_path, 'r') as f:
            loaded_list = f.read().splitlines()
        print(f'Loaded {len(loaded_list)} ids from {file_name}')    
        return loaded_list
    
    def save_records(self, folder_name: str, file_name: str, data: dict[str, list]) -> None:
        """
            Saves all key-value pairs of first batch. 
            Extends only existing keys with new values of subsequent batches for consistency. 
        """
        file_path = Path(DATA_FOLDER) / folder_name / file_name
        
        # Ensure the directory exists before saving
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data if file exists and is not empty
        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = data  # If no existing data, use the new data as is

        # Append new data only to existing keys
        if file_path.exists() and file_path.stat().st_size > 0:
            for key, value in data.items():
                if key in existing_data:
                    existing_data[key].extend(value)

        # Save the updated data back to the file
        with open(file_path, "w") as f:
            json.dump(existing_data, f, indent=4)

    def load_records(self, folder_name: str, file_name: str) -> dict[str, list]:
        file_path = Path(DATA_FOLDER) / folder_name / file_name
        
        # Check if the folder exists, return empty dict if not
        if not file_path.exists():
            return {}
        
        # Load from a file
        try:
            with open(file_path, "r", encoding='utf-8') as f:
                loaded_data = json.load(f)
            return loaded_data
        except Exception as e:
            return {}
    
    def make_jsonl(self, items: list[Item], prompt):
        """
        Convert items into a list of json objects (helper for write_jsonl)
        """
        result = ""
        for item in items:
            messages = prompt(item)
            messages_str = json.dumps(messages)
            result += '{"messages": ' + messages_str +'}\n'
        return result.strip()

    def write_jsonl(self, items: list[Item], prompt, folder_name: str, file_name: str):
        """
        Convert the items into jsonl and write them to a file
        """
        folder_path = Path(DATA_FOLDER) / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)  # Ensure the folder exists
    
        file_path = folder_path / file_name
        
        with open(file_path, "w") as f:
            jsonl = self.make_jsonl(items, prompt)
            f.write(jsonl)
    
    def load_jsonl(self, folder_name: str, file_name: str):
        """
        Loads jsonl as openai fine-tuning file
        """
        file_path = Path(DATA_FOLDER) / folder_name / file_name
        with open(file_path, "rb") as f:
            return openai.files.create(file=f, purpose="fine-tune")
    
    def get_new_ids(self, record_file_name: str, id_file_name: str, 
                    record_folder_name: str = RECORDS_FOLDER, id_folder_name: str = LISTING_IDS_FOLDER) -> list:
        """ 
        Filters for the listing ids without saved records.
        """
        saved_records = self.load_records(folder_name=record_folder_name, file_name=record_file_name)
        all_ids = self.load_ids(folder_name=id_folder_name, file_name=id_file_name)
        if saved_records:
            saved_ids = [record.split('-')[1].strip() for record in saved_records['listing_id']]
            new_ids = [id for id in all_ids if id not in saved_ids]  
            print(f'There are {len(new_ids)} new records')
            return new_ids
        else:
            print(f'There are {len(all_ids)} new records')
            return all_ids
    
    def get_chunk(self, new_ids: list, chunk_size: int) -> list:
        """
        Gets the next chunk to process.
        """
        chunk = min(len(new_ids), chunk_size)
        return new_ids[:chunk]
    
    def list_to_dataframe(self, items: list) -> pd.DataFrame:
        """
            Extracts features from list of items objects and makes df.
        """
        features = [item.features for item in items]
        df = pd.DataFrame(features)
        df['price'] = [item.price for item in items]
        return df
    
    def get_price(self, s: str) -> float:
        """
        Gets price from a string and returns a float.
        """
        s = s.replace('$','').replace(',','')
        match = re.search(r"[-+]?\d*\.\d+|\d+", s)
        return float(match.group()) if match else 0
