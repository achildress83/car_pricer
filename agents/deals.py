from pydantic import BaseModel
from typing import List, Dict, Tuple, Self, Optional
from bs4 import BeautifulSoup
import re
import feedparser
from tqdm import tqdm
import time
from config import CARS

feeds = ["https://www.admcars.com/rssfeed.php"]


def get_price(text: str) -> int:
    """Finds price from a text string."""
    # Find the line containing "Price:"
    for line in text.split("\n"):
        if "Price:" in line:
            raw_price = line.split("Price:")[-1].strip()  # Extract price value
            clean_price = re.sub(r"[^\d]", "", raw_price)  # Removes all non-digit characters
            if clean_price:
                clean_price = int(clean_price)
                return clean_price
            else:
                return None
            

def get_price_and_description(entry: feedparser.util.FeedParserDict) -> Tuple[Optional[str], Optional[int]]:
    """Combines the text from <h3><strong> and all <li> elements into a single string.
       Extracts price. 
    """
    soup = BeautifulSoup(entry.summary, 'html.parser')
    # extract all text
    text = soup.get_text(separator="\n")
    # get price
    price = get_price(text)
    if not price:
        return None
    # body of description is in h3 header
    h3_element = soup.find('h3')
    if h3_element:
        strong_element = h3_element.find('strong')
        if strong_element:
            h3_text = strong_element.get_text(separator='\n', strip=True)
        else:
            h3_text = ''
    else:
        h3_text = ''
    # Initialize the combined string with the h3_element text
    combined_string = h3_text + "\n" # Add a newline to seperate the h3 text and list items.

    # list elements contain more detailed info on repairs, build, etc.
    for line in soup.find_all('li'):
        combined_string += line.get_text(separator='\n', strip=True) + '\n'
        
    return combined_string.rstrip('\n'), price # remove last new line from combined string


def generate_year_pattern(start_year, end_year) -> str:
    """
    Generates a regex pattern to match any year between start_year and end_year (inclusive).
    """
    return rf"\b({'|'.join(str(year) for year in range(start_year, end_year + 1))})\b"


def contains_year_and_model(text: str, model: str, start_year: int, end_year: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts values for year and model from title text if exists.
    """
    # Regex pattern for a 4-digit year within range
    year_pattern = generate_year_pattern(start_year, end_year)
    
    # Check if model and year exist
    year_match = re.search(year_pattern, text)
    model_match = re.search(rf"\b{model}\b", text, re.IGNORECASE)  # Case-insensitive match
    
    found_year = year_match.group(0) if year_match else None
    found_model = model_match.group(0) if model_match else None 
    
    return found_year, found_model


def match_model_and_year(title: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Check title for match to make, model, and year from search criteria. 
    """
    make = None
    model = None
    year = None
    
    for car in CARS:
        start_year = car['YearFrom']
        end_year = car['YearTo']
        car_model = car['Model']
        car_make = car['Make']
        make = car_make
        
        year, model = contains_year_and_model(title, car_model, start_year, end_year)    
    
        if model:
            make = car_make
            break
              
    return make, model, year


class ScrapedDeal:
    """
    A class to represent a Deal retrieved from an RSS feed
    """
    category: str
    title: str
    make: str
    model: str
    year: str
    summary: str
    url: str
    details: str
    features: str
    
    def __init__(self, entry: Dict[str, str]):
        """
        Populate this instance based on the provided dict
        """
        self.title = entry['title']
        self.url = entry['url']   
        self.make = entry['make']
        self.model = entry['model']
        self.year = entry['year']
        self.price = entry['price']
        self.description = entry['description']
        self.category = self.get_category()
            
    def get_category(self):
        return f"{self.make}_{self.model}_{self.year}"
    
    def __repr__(self):
        """
        Return a string to describe this deal
        """
        return f"<{self.title}>"

    def describe(self):
        """
        Return a longer string to describe this deal
        """
        return f"Title: {self.title}\nCategory: {self.category}\nPrice: {self.price}\nURL: {self.url}"

    @classmethod
    def fetch(cls, show_progress : bool = False) -> List[Self]:
        """
        Retrieve all deals from the selected RSS feeds.
        Turn each entry in to an instance of ScrapedDeal
        """
        deals = []
        feed_iter = tqdm(feeds) if show_progress else feeds
        for feed_url in feed_iter:
            feed = feedparser.parse(feed_url)
        
            for entry in tqdm(feed.entries):
                title = entry.title
                url = entry.link
                make, model, year = match_model_and_year(title)
                if model and year:
                    result = get_price_and_description(entry)
                    if isinstance(result, tuple) and len(result) == 2:
                        description, price = result
                        deals.append(cls({
                            'title': title,
                            'url': url,
                            'make': make,
                            'model': model,
                            'year': year,
                            'price': price,
                            'description': description
                        }))
        return deals

class Deal(BaseModel):
    """
    A class to Represent a Deal with a summary description
    """
    product_description: str
    price: float
    url: str

class DealSelection(BaseModel):
    """
    A class to Represent a list of Deals
    """
    deals: List[Deal]

class Opportunity(BaseModel):
    """
    A class to represent a possible opportunity: a Deal where we estimate
    it should cost more than it's being offered
    """
    deal: Deal
    estimate: float
    discount: float