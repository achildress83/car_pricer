from typing import Optional, List
from agents.agent import Agent
from agents.deals import ScrapedDeal, DealSelection, Deal, Opportunity
from agents.screener_agent import ScreenerAgent
from agents.ensemble_agent import EnsembleAgent
from agents.messaging_agent import MessagingAgent
from config_deploy import DEAL_THRESHOLD


class PlanningAgent(Agent):

    name = "Planning Agent"
    color = Agent.GREEN
    deal_threshold = DEAL_THRESHOLD # percent

    def __init__(self, collection):
        """
        Create instances of the 3 Agents that this planner coordinates across
        """
        self.log("Planning Agent is initializing")
        self.screener = ScreenerAgent()
        self.ensemble = EnsembleAgent(collection)
        self.messenger = MessagingAgent()
        self.log("Planning Agent is ready")

    def run(self, deal: Deal) -> Opportunity:
        """
        Runs the workflow for a deal.
        """
        self.log("Planning Agent is pricing a potential deal")
        estimate = self.ensemble.price(deal.product_description)
        discount = estimate - deal.price
        self.log(f"Planning Agent has processed a deal with discount ${discount:.2f}")
        return Opportunity(deal=deal, estimate=estimate, discount=discount)

    def plan(self, memory: List[str] = []) -> Optional[List[Opportunity]]:
        """
        Run the full workflow:
        1. Use the ScreenerAgent to find deals from RSS feeds
        2. Use the EnsembleAgent to estimate them
        3. Use the MessagingAgent to send a notification of deals
        :param memory: a list of URLs that have been surfaced in the past
        :return: list of opportunities, otherwise None
        """
        qualified_opps = []
        self.log("Planning Agent is kicking off a run")
        selection = self.screener.screen(memory=memory)
        if selection:
            opportunities = [self.run(deal) for deal in selection.deals]
            opportunities.sort(key=lambda opp: opp.discount, reverse=True)
            self.log(f"Planning Agent has sorted {len(opportunities)}")
            for opp in opportunities:
                pct_discount = opp.discount / opp.deal.price
                if pct_discount > self.deal_threshold:
                    self.messenger.alert(opp)
                    qualified_opps.append(opp)
                else:
                    break
            self.log("Planning Agent has completed a run")
            return qualified_opps if qualified_opps else None
        return None