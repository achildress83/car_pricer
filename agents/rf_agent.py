from sentence_transformers import SentenceTransformer
import joblib
from agents.agent import Agent
from config_deploy import RF_PATH, TFIDF_PATH

class RandomForestAgent(Agent):

    name = "Random Forest Agent"
    color = Agent.MAGENTA
    rf_path = RF_PATH
    tfidf_path = TFIDF_PATH

    def __init__(self):
        """
        Initialize this object by loading in the saved model weights
        and the SentenceTransformer vector encoding model
        """
        self.log("Random Forest Agent is initializing")
        self.vectorizer = joblib.load(self.tfidf_path)
        self.model = joblib.load(self.rf_path)
        self.log("Random Forest Agent is ready")

    def price(self, description: str) -> float:
        """
        Use a Random Forest model to estimate the price of the described car
        
        Args:
            description (str): description of classic car for sale.

        Returns:
            float: price estimate
        """  
        self.log("Random Forest Agent is starting a prediction")
        vector = self.vectorizer.transform([description])
        result = max(0, self.model.predict(vector)[0])
        self.log(f"Random Forest Agent completed - predicting ${result:.2f}")
        return result