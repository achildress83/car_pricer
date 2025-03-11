from typing import Optional
from transformers import AutoTokenizer
import re
from config import BASE_MODEL, MIN_TOKENS, MAX_TOKENS, MIN_CHARS, CEILING_CHARS, REGIONS


class Item:
    """
    An Item is a cleaned, curated datapoint of a car listing with a price
    """
    
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    PREFIX = "Price is $"
    QUESTION = "How much does this cost to the nearest dollar?"
    
    title: str
    price: float
    category: str # year_make_model
    token_count: int = 0
    prompt: Optional[str] = None
    include = False

    def __init__(self, row):
        self.title = row['title']
        self.price = row['price']
        self.category = row['category']
        self.features = self.get_features(row)
        self.parse(row)

    def get_features(self, row):
        state = row['state']
        region = REGIONS.get(state)
        make = row['make']
        model = row['model']
        year = row['year']
        desc_length = len(row['description'].split())
        # if transmission type is missing, assume automatic
        if row['transmission'] in ['manual','automatic']:
            transmission = row['transmission']
        else:
            transmission = 'automatic'  
        
        return {'state': state, 'region': region, 'make': make, 'model': model, 
                    'year': year, 'word_count': desc_length, 'transmission': transmission}
        
    def scrub(self, stuff):
        """
        Clean up the provided text by removing unnecessary characters and whitespace
        Also remove words that are 7+ chars and contain numbers, as these are likely irrelevant product numbers
        """
        stuff = re.sub(r'[:\[\]"{}【】\s]+', ' ', stuff).strip()
        stuff = stuff.replace(" ,", ",").replace(",,,",",").replace(",,",",")
        # Remove email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        stuff = re.sub(email_pattern, '', stuff)
        return stuff
    
    def parse(self, row):
        """
        Parse this datapoint. If it has a price and fits within the allowed Token range,
        then set include to True.
        """
        try:
            self.price = float(self.price)
            contents = row['description']
            if contents:
                contents += '\n'
            
            if self.category:
                contents += f'Category: {self.category}' + '\n'
            
            if len(contents) > MIN_CHARS:
                contents = contents[:CEILING_CHARS]
                text = f"{self.scrub(self.title)}\n{self.scrub(contents)}"
                tokens = self.tokenizer.encode(text, add_special_tokens=False)
                if len(tokens) > MIN_TOKENS and self.price:
                    tokens = tokens[:MAX_TOKENS]
                    text = self.tokenizer.decode(tokens)
                    self.make_prompt(text)
                    self.include = True
        except Exception as e:
            print(f'Failed to create item: {e}')
            

    def make_prompt(self, text):
        """
        Set the prompt instance variable to be a prompt appropriate for training
        """
        self.prompt = f"{self.QUESTION}\n\n{text}\n\n"
        self.prompt += f"{self.PREFIX}{str(round(self.price))}.00"
        self.token_count = len(self.tokenizer.encode(self.prompt, add_special_tokens=False))

    def test_prompt(self):
        """
        Return a prompt suitable for testing, with the actual price removed
        """
        return self.prompt.split(self.PREFIX)[0] + self.PREFIX

    def __repr__(self):
        """
        Return a String version of this Item
        """
        return f"<{self.title} = ${self.price}>"

        

    
    