from dotenv import load_dotenv
import os
# Base url for the scraper
BASE_URL = 'https://classiccars.com/'

# load environment variables from .env
load_dotenv()

# API keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# search criteria for cars to gather data for
CARS = [
    {'YearFrom': 1965, 'YearTo': 1971, 'Make': 'Ford', 'Model': 'Mustang'},
    {'YearFrom': 1968, 'YearTo': 1970, 'Make': 'Dodge', 'Model': 'Charger'},
    {'YearFrom': 1966, 'YearTo': 1977, 'Make': 'Ford', 'Model': 'Bronco'},
    {'YearFrom': 1967, 'YearTo': 1969, 'Make': 'Chevrolet', 'Model': 'Camaro'}
]

# File paths
DATA_FOLDER = 'data'
LISTING_IDS_FOLDER = 'listing_ids'
RECORDS_FOLDER = 'records'
DATASET_FOLDER = 'train_test_sets'

# Scraper constants
WAIT_TIME = 10 # number of secs to wait for page elemet to appear
MIN_SCROLL, MAX_SCROLL = 250, 350 # num px to scroll down (scroll_page function)
MIN_PAUSE, MAX_PAUSE = 0.8, 1.2 # pause to mimic human reading time (scroll_page function)
MIN_MARGIN, MAX_MARGIN = 2000, 3000 # stop scrolling when distance from bottom of page reached (scroll_page function)
MIN_DELAY, MAX_DELAY = 2, 5 # randomized delay for get_all_listings and process_ids functions

# processing script that get records from ids
CHUNK_SIZE = 50 # number of ids to process in each chunk
SECS_PER_HR = 3600
SECS_PER_MIN = 60
SLEEP = 30 # sleep before processing next chunk

# Items config
BASE_MODEL = 'Qwen/Qwen2.5-7B'
MIN_TOKENS = 80 # Any less than this, not enough useful content
MAX_TOKENS = 1500 # Truncate after this many tokens

MIN_CHARS = 300
CEILING_CHARS = MAX_TOKENS * 7

# Database connection parameters
DB_NAME = "cars"
USER = "postgres"
PASSWORD = os.getenv('POSTGRES_PW')
HOST = "localhost"
PORT = "5432"

# train-test split
SEED = 42
TEST_SIZE = 0.2

# HF Hub upload
HF_USER = "aaron-childress"
DATASET_NAME = f"{HF_USER}/car-data"

# Deploy constants
GPU = 'T4'
PROJECT_NAME = "pricer"
HF_USER = "aaron-childress"
DATASET_NAME = f"{HF_USER}/car-data"
MAX_NEW_TOKENS = 9 # six plus any padding tokens

# Available checkpoints

runs = {
    'qwen_4bit': '2025-02-21_08.50.50',
    'qwen_8bit': '2025-02-23_06.12.29'
}

# Chosen run for inference
QUANT_4_BIT = False # set this to true if chosen run is 4 bit model
CHOSEN_RUN_NAME = runs['qwen_8bit']
CHOSEN_PROJECT_RUN_NAME = f"{PROJECT_NAME}-{CHOSEN_RUN_NAME}"
REVISION = None
FINETUNED_MODEL = f"{HF_USER}/{CHOSEN_PROJECT_RUN_NAME}"
MODEL_DIR = "hf-cache/"
BASE_DIR = MODEL_DIR + BASE_MODEL
FINETUNED_DIR = MODEL_DIR + FINETUNED_MODEL

# Tester Class
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"

GOOD_PRED = 0.1 # within x% of actual price
OK_PRED = 0.2

# mapping states to regions
REGIONS = {
    'alabama': 'south',
    'alaska': 'west',
    'arizona': 'west',
    'arkansas': 'south',
    'california': 'west',
    'colorado': 'west',
    'connecticut': 'northeast',
    'delaware': 'northeast',
    'florida': 'south',
    'georgia': 'south',
    'hawaii': 'west',
    'idaho': 'west',
    'illinois': 'midwest',
    'indiana': 'midwest',
    'iowa': 'midwest',
    'kansas': 'midwest',
    'kentucky': 'south',
    'louisiana': 'south',
    'maine': 'northeast',
    'maryland': 'northeast',
    'massachusetts': 'northeast',
    'michigan': 'midwest',
    'minnesota': 'midwest',
    'mississippi': 'south',
    'missouri': 'midwest',
    'montana': 'west',
    'nebraska': 'midwest',
    'nevada': 'west',
    'new hampshire': 'northeast',
    'new jersey': 'northeast',
    'new mexico': 'west',
    'new york': 'northeast',
    'north carolina': 'south',
    'north dakota': 'midwest',
    'ohio': 'midwest',
    'oklahoma': 'south',
    'oregon': 'west',
    'pennsylvania': 'northeast',
    'rhode island': 'northeast',
    'south carolina': 'south',
    'south dakota': 'midwest',
    'tennessee': 'south',
    'texas': 'south',
    'utah': 'west',
    'vermont': 'northeast',
    'virginia': 'south',
    'washington': 'west',
    'west virginia': 'south',
    'wisconsin': 'midwest',
    'wyoming': 'west'
}