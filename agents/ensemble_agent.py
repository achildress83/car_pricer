import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

from agents.agent import Agent
from agents.specialist_agent import SpecialistAgent
from agents.rag_agent import RagAgent
from agents.rf_agent import RandomForestAgent
from config_deploy import ENSEMBLE_PATH

class EnsembleAgent(Agent):

    name = "Ensemble Agent"
    color = Agent.YELLOW
    model_path = ENSEMBLE_PATH
    
    def __init__(self, collection):
        """
        Create an instance of Ensemble, by creating each of the models
        And loading the weights of the Ensemble
        """
        self.log("Initializing Ensemble Agent")
        self.specialist = SpecialistAgent()
        self.rag = RagAgent(collection)
        self.random_forest = RandomForestAgent()
        self.model = joblib.load(self.model_path)
        self.log("Ensemble Agent is ready")

    def price(self, description: str) -> float:
        """
        Runs ensemble model. Asks each of the models to price the car.
        Then uses the Linear Regression model to return the weighted price

        Args:
            description (str): description of listed car.

        Returns:
            float: weigted price estimate
        """
        self.log("Running Ensemble Agent - collaborating with specialist, rag and random forest agents")
        specialist = self.specialist.price(description)
        rag = self.rag.price(description)
        random_forest = self.random_forest.price(description)
        X = pd.DataFrame({
            'Specialist': [specialist],
            'Rag': [rag],
            'RandomForest': [random_forest]
        })
        y = self.model.predict(X)[0]
        self.log(f"Ensemble Agent complete - returning ${y:.2f}")
        return y