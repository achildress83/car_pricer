from typing import Optional, List
from agents.deals import Deal, ScrapedDeal, DealSelection
from agents.agent import Agent

class ScreenerAgent(Agent):
    
    name = "Screener Agent"
    color = Agent.CYAN

    def __init__(self):
        pass
        
    def fetch_deals(self, memory) -> List[ScrapedDeal]:
        """
        Look up deals published on RSS feeds
        Return any new deals that are not already in the memory provided
        """
        self.log("Screener Agent is about to fetch deals from RSS feed")
        urls = [opp.deal.url for opp in memory]
        scraped = ScrapedDeal.fetch()
        result = [scrape for scrape in scraped if scrape.url not in urls]
        self.log(f"Screener Agent received {len(result)} deals not already scraped")
        return result
    
    def screen(self, memory: List[str]=[]) -> Optional[DealSelection]:
        """
        Filters new deals not already in memory and makes Deal objects from them. 
        """
        scraped = self.fetch_deals(memory)
        if scraped:
            self.log("Screener Agent is making Deal objects")
            
            result = DealSelection(deals=[Deal(product_description=car.description,
                        price=car.price,
                        url=car.url
                        ) for car in scraped])
        
            self.log(f"Screener Agent received {len(result.deals)} selected deals with price>0")
            return result
        return None