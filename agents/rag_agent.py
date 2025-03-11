import re
from agents.agent import Agent
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
from config_deploy import OPENAI_API_KEY, EMBEDDING, MODEL, TOP_K, SEED, MAX_NEW_TOKENS

class RagAgent(Agent):

    name = "RAG Agent"
    color = Agent.BLUE

    model_name = MODEL
    embedding = EMBEDDING
    top_k = TOP_K
    seed = SEED
    max_tokens = MAX_NEW_TOKENS
    
    def __init__(self, collection):
        """
        Set up this instance by connecting to OpenAI, the Chroma Datastore,
        And setting up the vector encoding model
        """
        self.log("Initializing RAG Agent")
        self.openai = OpenAI()
        self.openai.api_key = OPENAI_API_KEY
        self.collection = collection
        self.model = SentenceTransformer(self.embedding)
        self.log("RAG Agent is ready")
        
    def find_similars(self, description: str) -> Tuple[str, float]:
        """
        Fetches top_k similar cars from ChromaDB.

        Args:
            description (str): description of classic car for sale.

        Returns:
            Tuple[str, float]: description of similar classic cars with their prices.
        """
        self.log("Frontier Agent is performing a RAG search of the Chroma datastore to find 5 similar products")
        vector = self.model.encode([description])
        results = self.collection.query(query_embeddings=vector.astype(float).tolist(), n_results=self.top_k)
        documents = results['documents'][0][:]
        prices = [m['price'] for m in results['metadatas'][0][:]]
        self.log("Frontier Agent has found similar products")
        return documents, prices
    
    def make_context(self, similars: List[str], prices: List[float]) -> str:
        """
        Helper function creates context that can be inserted into the prompt. 
        Takes top_k similar descriptions w/ prices and packages as context for the query.

        Args:
            similars (List[str]): list of top_k car descriptions.
            prices (List[float]): list of top_k car prices.

        Returns:
            str: context for final prompt.
        """
        message = "To provide some context, here are some other cars that are similar to the car you need to estimate.\n\n"
        for similar, price in zip(similars, prices):
            message += f"Potentially related car:\n{similar}\nPrice is ${price:.2f}\n\n"
        return message
    
    def messages_for(self, description: str, similars: List[str], prices: List[float]) -> List[Dict[str, str]]:
        """
        Combines system and user prompt with context to create final prompt.

        Args:
            description (str): description of classic car for sale.
            similars (List[str]): list of top_k car descriptions.
            prices (List[float]): list of top_k car prices.

        Returns:
            List[Dict[str, str]]: system and user prompt formatted for OpenAI.
        """
        
        system_message = "You estimate prices of classic cars. Reply only with the price, no explanation"
        user_prompt = self.make_context(similars, prices)
        user_prompt += "And now the question for you:\n\n"
        user_prompt += "How much does this car cost?\n\n" + description
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": "Price is $"}
        ]
        
    def get_price(self, s: str) -> float:
        """
        A utility that pulls a floating point number out of a string
        """
        s = s.replace('$','').replace(',','')
        match = re.search(r"[-+]?\d*\.\d+|\d+", s)
        return float(match.group()) if match else 0.0
    
    def price(self, description: str) -> float:
        """
        Make a call to OpenAI to estimate the price of the described car,
        by looking up top_k similar cars and including them in the prompt to give context

        Args:
            description (str): description of classic car for sale.

        Returns:
            float: price estimate
        """
        documents, prices = self.find_similars(description)
        self.log(f"Frontier Agent is about to call OpenAI with context including {self.top_k} similar products")
        response = self.openai.chat.completions.create(
            model=self.model_name, 
            messages=self.messages_for(description, documents, prices),
            seed=self.seed,
            max_tokens=self.max_tokens
        )
        reply = response.choices[0].message.content
        result = self.get_price(reply)
        self.log(f"Frontier Agent completed - predicting ${result:.2f}")
        return result