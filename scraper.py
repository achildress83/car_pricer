# imports for Selenium webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup

# other imports
from config import DATA_FOLDER, WAIT_TIME, MIN_SCROLL, MAX_SCROLL, \
    MIN_PAUSE, MAX_PAUSE, MIN_MARGIN, MAX_MARGIN
from collections import defaultdict
import re
import time
import random

class Scraper:
    '''
    Attrs: url, driver, criteria, soup, all_listing_ids, pages
    '''
    def __init__(self, url):
        self.url = url
        self.driver = self.web_driver()
        self.listings = defaultdict(list)
        
    
    def web_driver(self) -> object:

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            print(f'An error occurred: {e}')
        
        return driver
    
    def get_page(self, new_url) -> None:
        try:
            self.driver.get(new_url)
        except Exception as e:
            print(f'An error occurred {e}')
            
    def quit(self) -> None:
        if self.driver:
            self.driver.quit()
    
    def save_ids(self, folder_name) -> None:
        folder = Path(DATA_FOLDER) / folder_name
        if not folder.exists():
            folder.mkdir(parents=True)
            
        # Write to a file
        file_name = f"{self.criteria['Make']}_{self.criteria['Model']}_{self.criteria['YearFrom']}_{self.criteria['YearTo']}.txt"
        path = folder / file_name
        
        with open(path, 'w') as f:
            for i in self.all_listing_ids:
                f.write(f"{i}\n")

    

    ############################### COLLECT LISTING IDS #################################
    
    def populate_input_fields(self, from_yr: int, to_yr: int, make: str, model:str) -> None:
        '''
        Enters search criteria on the homepage and clicks search to return listings pages
        '''
        # navigate to main page with search fields
        self.driver.get(self.url)
        
        inputs = {
            'YearFrom': from_yr, # input id and desired value
            'YearTo': to_yr,
        }

        # Define dropdowns and their desired values
        dropdowns = {
            "Make": make,  # Dropdown id and desired value
            "Model": model
        }

        # expose search criteria as attrs
        self.criteria = {
            'YearFrom': inputs['YearFrom'],
            'YearTo': inputs['YearTo'],
            'Make': dropdowns['Make'],
            'Model': dropdowns['Model']
        }
        
        # Wait for the search button to be clickable
        search_button = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.element_to_be_clickable((By.ID, "main-search-button"))
        )

        # populate input fields
        for input_id, value in inputs.items():
            element = self.driver.find_element(By.ID, input_id)
            element.clear()
            element.send_keys(value)
            
        for dropdown_id, value in dropdowns.items():
            dropdown = Select(self.driver.find_element(By.ID, dropdown_id))
            dropdown.select_by_visible_text(value)
            
        search_button.click()
        
        

    def scroll_page(self):
        # Scroll the page gradually like a human
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            
            # scroll down by a random amount b/w 250 to 350 pixels
            scroll_amount = random.randint(MIN_SCROLL, MAX_SCROLL)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # random pause between 0.8-1.2 seconds
            time.sleep(random.uniform(MIN_PAUSE, MAX_PAUSE))  # Mimic human reading time

            # Get both current scroll position and new document height
            current_position = self.driver.execute_script("return window.scrollY")
            window_height = self.driver.execute_script("return window.innerHeight")
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Stop if we've reached the bottom (within 3000 px)
            bottom_margin = random.randint(MIN_MARGIN, MAX_MARGIN)
            if current_position + window_height >= last_height - bottom_margin:
                break
            
            # If the page height changed (due to dynamic loading) update it
            if new_height != last_height:
                last_height = new_height
                
   
    def get_page_listings(self) -> list:
        """
        Collects all unique listing IDs from the page while scrolling naturally.
        """
        try:
            wait = WebDriverWait(self.driver, WAIT_TIME)
            
            # Wait for the page to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'html')))

            self.scroll_page()
            
            # Get updated page source
            body = self.driver.page_source
            self.soup = BeautifulSoup(body, 'html.parser')

            try:    
                # first attempt regex search
                matching_divs = self.soup.find_all('div', string=re.compile(r"CC-\d+"))
                if not matching_divs:
                    # Backup: search for divs that might contain the id pattern
                    matching_divs = [
                        div for div in self.soup.find_all('div')
                        if div.text and re.search(r"CC-\d+", div.text)
                    ]

                # Get all listing IDs from the page
                listing_ids = [div.text.strip().split('-')[1] for div in matching_divs]
                return listing_ids
            
            except IndexError:
                print('could not parse listing ids from divs')
                return []
                
        except Exception as e:
            print(f'Error during page scraping: {e}')
            return []
        


    def get_all_listings(self) -> None:
        '''
        Iterates over all listings and stores list of ids using direct URL navigation,
        with detection for circular pagination
        '''
        self.all_listing_ids = []
        self.pages = 0
        current_page = 1
        seen_listings = set()  # Track listing IDs to detect duplicates
        
        while True:
            try:
                # Construct the URL for the current page
                page_url = f"{self.url}listings/find/{self.criteria['YearFrom']}-{self.criteria['YearTo']}/{self.criteria['Make']}/{self.criteria['Model']}"
                if current_page > 1:
                    page_url += f"?p={current_page}"
                    
                # Navigate directly to the page
                self.driver.get(page_url)
                
                # Wait for the search results to be present
                WebDriverWait(self.driver, WAIT_TIME).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "search-result-item"))
                )
                
                # Get listings from current page
                listing_ids = self.get_page_listings()
                
                # If no listings found, reached the end
                if not listing_ids:
                    break
                    
                # Check for duplicate listings (indicates end of loop)
                current_page_set = set(listing_ids)
                if current_page_set.intersection(seen_listings):
                    print(f"Detected pagination loop at page {current_page} - stopping")
                    break
                    
                # Add current listings to seen set
                seen_listings.update(current_page_set)
                
                self.all_listing_ids.extend(listing_ids)
                self.pages += 1
                current_page += 1
                
                # Add randomized delay (in seconds) to avoid detection
                delay = random.uniform(MIN_DELAY, MAX_DELAY) 
                time.sleep(delay)
                
            except TimeoutException:
                print("Page failed to load within timeout period")
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        
        print(f"{self.criteria['Make']} {self.criteria['Model']} ({self.criteria['YearFrom']}-{self.criteria['YearTo']})")
        print("==============================")
        print(f"Paginated {self.pages} pages.")
        print(f"Collected {len(self.all_listing_ids)} listing ids.\n")
    
    
    ################################# GET LISTING DESCRIPTION ##################################
    
    def clean_text(self, text: str) -> str:
        """
        Remove phone numbers and VIN numbers from text (Helper for get_description)
        """
        # Remove pattern
        text = text.replace('\xa0', '')
        
        # Pattern for phone numbers (handles various formats)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            
        # Remove phone numbers
        text = re.sub(phone_pattern, '', text)
        
        return text

    
    def get_listing_page(self, listing_id: str) -> None:
        '''
        Takes listing id and parses html of the listing page.
        '''
        # build soup for the listing page
        try:
            self.driver.get(f'{self.url}listings/view/{listing_id}/')
            
            # Wait until the listing number appears in the title
            wait = WebDriverWait(self.driver, WAIT_TIME)
            wait.until(EC.title_contains(listing_id))
            
            self.scroll_page()
            
            html_content = self.driver.page_source
            
            # soup passed to get_description and get_details functions
            self.soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            print(f'Failed to get listing page: {e}')

    
    def get_description(self) -> None:
        '''
        Gets description from listing page
        '''
        try:
            # Get text from div element where 'p-description' is in the class name
            text = self.soup.find('div', class_=lambda value: value and 'p-description' in value).get_text(separator='\n', strip=True)

            # remove vin numbers and phone numbers
            self.text = self.clean_text(text)
            
        except Exception as e:
            print(f'Failed to get description: {e}')
            self.text = None
        
    ################################# GET LISTING DETAILS #####################################
    
    def get_details(self):
        '''
        Gathers all list details from listing and adds description to the listing dictionary.
        '''
        import re

        def convert_to_int(value):
            """Extract numeric parts and convert to integer."""
            return int(re.sub(r"[^\d]", "", value)) if re.search(r"\d", value) else None

        details_div = []
        
        try:
            details_div = self.soup.find_all('div', class_=lambda value: value and 'vehicle-details' in value)
        except Exception as e:
            print(f'Failed to get details div: {e}')
            return

        if not details_div:
            return  # Exit if no details found

        ul = details_div[0].find('ul', class_=lambda value: value and 'details-list' in value)
        
        if not ul:
            return  # Exit if no <ul> is found

        # Get title and product ID
        title_li = ul.find('li', class_=lambda value: value and 'p-name' in value)
        product_li = ul.find('li', class_=lambda value: value and 'productID' in value)

        if not (title_li and product_li):
            return  # Exit if title or product ID is missing

        title = title_li.find_all('span')[0].text
        product_id = product_li.find_all('span')[1].text

        # Append basic listing details
        self.listings['listing_id'].append(product_id)
        self.listings['title'].append(title)
        self.listings['description'].append(self.text)  # Created by get_description

        # Process additional details
        following_li = product_li.find_next_siblings('li')
        seen_keys = set()  # Track keys that are found in this item

        for li in following_li:
            spans = li.find_all('span')
            if len(spans) == 2:
                try:
                    key = spans[0].text.replace(':', '').lower().strip().replace(' ', '_')
                    value = spans[1].text.lower()

                    if key == 'price':
                        value = convert_to_int(value)

                    elif key == 'location':
                        try:
                            city, state = map(str.strip, value.split(','))
                        except:
                            city, state = None, None
                        self.listings['city'].append(city)
                        self.listings['state'].append(state)

                    elif key == 'odometer':
                        value = convert_to_int(value)

                    self.listings[key].append(value)
                    seen_keys.add(key)

                except Exception as e:
                    print(f'Error processing key-value pair: {e}')

        # **Ensure all other keys (including missing ones like VIN) are aligned**
        all_keys = set(self.listings.keys())  # Get all existing keys
        for key in all_keys - seen_keys - {'listing_id', 'title', 'description', 'city', 'state'}:
            self.listings[key].append(None)

        # **Ensure new keys from this item are added to previous entries**
        for key in seen_keys:
            if len(self.listings[key]) < len(self.listings['listing_id']):
                while len(self.listings[key]) < len(self.listings['listing_id']):
                    self.listings[key].insert(-1, None)  # Add None to previous items where key was missing
