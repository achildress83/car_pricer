import gradio as gr
from deal_agent_framework import DealAgentFramework
from agents.deals import Opportunity, Deal
from config_deploy import FREQUENCY

class App:
    
    def __init__(self):
        self.agent_framework = DealAgentFramework()
        self.frequency = FREQUENCY
        
    def run(self):

        with gr.Blocks(title='Classic Car Pricer', fill_width=True) as ui:
            
            def table_for(opps=None):
                show_opps = opps
                if not opps:
                    show_opps = self.agent_framework.read_memory()
                    
                return [[opp.deal.product_description, 
                         f'${opp.deal.price:.2f}', 
                         f'${opp.estimate:.2f}', 
                         f'${opp.discount:.2f}', 
                         opp.deal.url] for opp in show_opps]
            
            def start():
                opportunities = self.agent_framework.memory
                
            def go():
                self.agent_framework.run()
                new_opportunities = self.agent_framework.memory
                table = table_for(new_opportunities)
                return table
            
            def do_select(selected_index: gr.SelectData):
                opportunities = self.agent_framework.memory
                row = selected_index.index[0]
                opportunity = opportunities[row]
                self.agent_framework.planner.messenger.alert(opportunity)
                
            with gr.Row():
                gr.Markdown('<div style="text-align: center;font-size:24px">Classic Car Pricer - Deal Hunting Agent</div>')
            with gr.Row():
                gr.Markdown('<div style="text-align: center;font-size:14px">Autonomous agent framework that finds online classic car deals by estimating price from desccriptions.</div>')
            with gr.Row():
                gr.Markdown('<div style="text-align: center;font-size:14px">Pricing model is a weighted ensemble comprised of a proprietary fine-tuned LLM deployed on Modal, a RAG pipeline with a frontier model and Chroma, and a Random Forest Regressor.</div>')
            with gr.Row():
                opportunities_dataframe = gr.Dataframe(
                    headers =['Description','Price','Estimate','Discount','URL'],
                    wrap=True,
                    column_widths=[4, 1, 1, 1, 2],
                    row_count = 10,
                    col_count = 5,
                    max_height = 400
                )
            ui.load(table_for, inputs=[], outputs=[opportunities_dataframe])
            timer = gr.Timer(value=self.frequency)
            timer.tick(go, inputs=[], outputs=[opportunities_dataframe])
            
            opportunities_dataframe.select(do_select)
            
        ui.launch(share=False, inbrowser=True)
        
if __name__ == '__main__':
    App().run()