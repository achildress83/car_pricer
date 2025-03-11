import os
import sys
import logging
import json
from typing import List, Optional
from twilio.rest import Client
from dotenv import load_dotenv
import chromadb
from agents.planning_agent import PlanningAgent
from agents.deals import Opportunity
from sklearn.manifold import TSNE
import numpy as np
from config_deploy import DB, COLLECTION, MEMORY_FILENAME


# Colors for logging
BG_BLUE = '\033[44m'
WHITE = '\033[37m'
RESET = '\033[0m'


def init_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [Agents] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

class DealAgentFramework:

    db = DB
    collection_name = COLLECTION
    memory_filename = MEMORY_FILENAME

    def __init__(self):
        init_logging()
        self.log("Initializing Agent Framework")
        client = chromadb.PersistentClient(path=self.db)
        self.memory = self.read_memory()
        self.collection = client.get_or_create_collection(self.collection_name)
        self.planner = PlanningAgent(self.collection)
        self.log("Agent Framework is ready")
        
    def read_memory(self) -> List[Opportunity]:
        if os.path.exists(self.memory_filename):
            with open(self.memory_filename, "r") as file:
                data = json.load(file)
            opportunities = [Opportunity(**item) for item in data]
            return opportunities
        return []

    def write_memory(self) -> None:
        data = [opportunity.dict() for opportunity in self.memory]
        with open(self.memory_filename, "w") as file:
            json.dump(data, file, indent=2)

    def log(self, message: str):
        text = BG_BLUE + WHITE + "[Agent Framework] " + message + RESET
        logging.info(text)

    def run(self) -> List[Opportunity]:
        logging.info("Kicking off Planning Agent")
        result = self.planner.plan(memory=self.memory)
        logging.info(f"Planning Agent has completed and returned: {result}")
        if result:
            self.memory.extend(result)
            self.write_memory()
        return self.memory


if __name__=="__main__":
    DealAgentFramework().run()
    