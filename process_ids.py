from scraper import Scraper
from utils import Utils
from config import RECORDS_FOLDER, CHUNK_SIZE, MIN_DELAY, \
    MAX_DELAY, SECS_PER_HR, SECS_PER_MIN, SLEEP, BASE_URL
import time
import random

utils_instance = Utils()

def process_ids(new_id_chunk: list) -> dict[str, list]:
    """
    Scrapes listing id page and returns listing records.
    """
    start_time = time.perf_counter()

    scraper = Scraper(BASE_URL)

    for new_id in new_id_chunk:
        scraper.get_listing_page(new_id)
        scraper.get_description()
        scraper.get_details()
        # Add randomized delay (in seconds)
        delay = random.uniform(MIN_DELAY, MAX_DELAY) 
        time.sleep(delay)

    scraper.quit()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    # Convert to hours, minutes, seconds
    hours, remainder = divmod(elapsed_time, SECS_PER_HR)
    minutes, seconds = divmod(remainder, SECS_PER_MIN)

    print(f"Elapsed time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    return scraper.listings


def run(file_prefix: str) -> None:
    """
    Runs script to process new listing ids into records \
        until there are no new listing ids left.
    """
    
    while True:
        # get a chunk of new ids for processing
        new_ids = utils_instance.get_new_ids(record_file_name=f'{file_prefix}.json', 
                                    id_file_name=f'{file_prefix}.txt')
        if not new_ids:
            break
        chunk = utils_instance.get_chunk(new_ids=new_ids, chunk_size=CHUNK_SIZE)

        # process chunk
        try:
            records = process_ids(chunk)
            utils_instance.save_records(folder_name=RECORDS_FOLDER, file_name=f'{file_prefix}.json', data=records)
        except Exception as e:
            print(f'Error processing chunk: {e}')
            break
        
        time.sleep(SLEEP) # sleep before processing next chunk 
        
if __name__ == '__main__':
    run('Ford_Bronco_1966_1977')