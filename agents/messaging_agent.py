import os
from agents.deals import Opportunity
import http.client
import urllib
from agents.agent import Agent
from config_deploy import PUSHOVER_USER, PUSHOVER_TOKEN



DO_PUSH = True

class MessagingAgent(Agent):

    name = "Messaging Agent"
    color = Agent.WHITE

    def __init__(self):
        """
        Set up this object to do push notifications via Pushover
        """
        self.log(f"Messaging Agent is initializing")
        if DO_PUSH:
            self.pushover_user = PUSHOVER_USER
            self.pushover_token = PUSHOVER_TOKEN
            self.log("Messaging Agent has initialized Pushover")

    
    def push(self, text):
        """
        Send a Push Notification using the Pushover API
        """
        self.log("Messaging Agent is sending a push notification")
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
          urllib.parse.urlencode({
            "token": self.pushover_token,
            "user": self.pushover_user,
            "message": text,
            "sound": "cashregister"
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()

    def alert(self, opportunity: Opportunity):
        """
        Make an alert about the specified Opportunity
        """
        text = f"Deal Alert! Price=${opportunity.deal.price:.2f}, "
        text += f"Estimate=${opportunity.estimate:.2f}, "
        text += f"Discount=${opportunity.discount:.2f} :"
        text += opportunity.deal.product_description[:10]+'... '
        text += opportunity.deal.url
        if DO_PUSH:
            self.push(text)
        self.log("Messaging Agent has completed")
        
    
        