from agapi.agents import AGAPIAgent
import os
api_key=os.environ.get('ATOMGPT_API_KEY')
agent = AGAPIAgent(api_key=api_key)

def test_ag1():
   ag1=agent.query_sync("Whats the capital of US?",render_html=True)
   print(ag1)
def test_ag2a():
   ag1=agent.query_sync("Find all Al2O3 materials",render_html=True,use_tools=False)
   print(ag1)
def test_ag2b():
   ag1=agent.query_sync("Find all Al2O3 materials",render_html=True,use_tools=True)
   print(ag1)
