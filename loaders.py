from pathlib import Path
from huggingface_hub import login
from datasets import load_dataset, Dataset, DatasetDict
from config import CHUNK_SIZE, SEED, HF_USER, HF_API_KEY, DATASET_NAME, TEST_SIZE, DATA_FOLDER
from database import init_connection
from items import Item
from collections import defaultdict, Counter
import math
import random
import pickle

class ItemLoader:
    """
        Uses Item Class. Loads records from database, transforms them to items. 
    """
    def __init__(self):
        self.items = []
        self.train = []
        self.test = []
        self.category_counts = defaultdict(int)
        
    def fetch_items(self, chunk_size=CHUNK_SIZE) -> None:
        """
            create Item objects from database listings
        """
        conn, cur = init_connection(load=False)

        offset = 0
        
        with cur as c:
            while True:
                c.execute(
                    "SELECT * FROM listings ORDER BY listing_id LIMIT %s OFFSET %s",
                    (chunk_size, offset)      
                )
                
                chunk = []
                count = defaultdict(int)
                for row in c:
                    try:
                        row_dict = dict(row)
                        item = Item(row_dict)
                        if item.include:
                            chunk.append(item)
                            count[item.category] += 1
                    except Exception as e:
                        print(f'Error creating Item object: {e}')
                    
                if not chunk: # No more records
                    break
                
                self.items.extend(chunk)
                self.category_counts = Counter(self.category_counts) + Counter(count)
                print(f"Processed {len(chunk):,} items (offset: {offset:,})")
                offset += chunk_size
                
        print(f'Total items processed: {len(self.items):,}')
    
    def train_test_split(self, test_size: float=TEST_SIZE) -> None:
        """
        Shuffles items list and creates a train-test split
        """
        # build dictionary with number of test items for each category
        test_split_dict = {category: math.floor(count * test_size) for category, count in self.category_counts.items()}
        if self.items:
            for item in self.items:
                if test_split_dict[item.category] > 0:
                    self.test.append(item)
                    test_split_dict[item.category] -= 1
                else:
                    self.train.append(item)
        # shuffle the train and test sets
        random.seed(SEED)
        random.shuffle(self.train)
        random.shuffle(self.test)
        
    def upload_prompts_to_HFhub(self) -> None:
        """
        Convert train and test set to prompts and upload to HF Hub.
        """
        login(HF_API_KEY)
        # Create prommpt and price lists
        train_prompts = [item.prompt for item in self.train]
        train_prices = [item.price for item in self.train]
        test_prompts = [item.test_prompt() for item in self.test]
        test_prices = [item.price for item in self.test]
        
        # Create a Dataset from the lists
        train_dataset = Dataset.from_dict({"text": train_prompts, "price": train_prices})
        test_dataset = Dataset.from_dict({"text": test_prompts, "price": test_prices})
        dataset = DatasetDict({
            "train": train_dataset,
            "test": test_dataset
        })
        
        dataset.push_to_hub(DATASET_NAME, private=True)
    
    # pickle the dataset
    def pickle(self, folder_name: str) -> None:
        
        file_path = Path(DATA_FOLDER) / folder_name
        
        # Ensure the directory exists before saving
        file_path.mkdir(parents=True, exist_ok=True)
        
        with open(file_path / 'train.pkl', 'wb') as file:
            pickle.dump(self.train, file)

        with open(file_path / 'test.pkl', 'wb') as file:
            pickle.dump(self.test, file)
            
    def load_pickle(self, folder_name: str, train_file: str='train.pkl', test_file: str='test.pkl') -> tuple:
        
        file_path = Path(DATA_FOLDER) / folder_name
        
        with open(file_path / train_file, 'rb') as file:
            train = pickle.load(file)

        with open(file_path / test_file, 'rb') as file:
            test = pickle.load(file)
            
        return train, test