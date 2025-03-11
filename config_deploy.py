from dotenv import load_dotenv
import os

# load environment variables from .env
load_dotenv()

# API keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Deploy constants
GPU = 'T4'
PROJECT_NAME = "pricer"
HF_USER = "aaron-childress"
DATASET_NAME = f"{HF_USER}/car-data"
MAX_NEW_TOKENS = 9 # six plus any padding tokens
SEED = 42

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
BASE_MODEL = 'Qwen/Qwen2.5-7B'
FINETUNED_MODEL = f"{HF_USER}/{CHOSEN_PROJECT_RUN_NAME}"
MODEL_DIR = "hf-cache/"
BASE_DIR = MODEL_DIR + BASE_MODEL
FINETUNED_DIR = MODEL_DIR + FINETUNED_MODEL

# chroma db and memory
DB = 'vectorstore'
COLLECTION = 'cars'
EMBEDDING = 'sentence-transformers/all-MiniLM-L6-v2'
TOP_K = 5
MEMORY_FILENAME = 'memory.json'

# RAG model
MODEL = "gpt-4o-mini"

# Random Forest Model
RF_PATH = 'models/random_forest_tfidf_model.pkl'
TFIDF_PATH = 'models/tfidf_vectorizer.pkl'
MAX_DF = 0.8 # present in no more then 80% of docs
MIN_DF = 5 # present at least 5 docs
NGRAM_RANGE = (1,3)
N_ESTIMATORS = 100
N_FEATURES = 20 # n most important features to show

# Ensemble Model
ENSEMBLE_PATH = 'models/ensemble_model.pkl'

# Pushover
PUSHOVER_USER = os.getenv('PUSHOVER_USER')
PUSHOVER_TOKEN = os.getenv('PUSHOVER_TOKEN')

# Planning Agent
DEAL_THRESHOLD = 0.20

# Classic Car Pricer
FREQUENCY = 60 * 60 * 24 * 7 # weekly run