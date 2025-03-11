from config import CARS, BASE_URL
from scraper import Scraper

def scrape_ids(cars: list[dict]) -> None:
    """"Takes records of car criteria, scrapes unique id and saves as .txt in listing_ids folder"""
    # instantiate scraper class with url to scrape
    scraper = Scraper(BASE_URL)

    # get listing ids for all car specs 
    for car in cars:
        # fill in search criteria to return listings
        scraper.populate_input_fields(car['YearFrom'], car['YearTo'], car['Make'], car['Model'])
        # paginate through listing pages and collect all listing ids
        scraper.get_all_listings()
        # save listing ids to folder
        scraper.save_ids('listing_ids')
        
        
if __name__ == "__main__":
    scrape_ids(CARS)