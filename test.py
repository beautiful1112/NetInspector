#complete the imort module
from tools.network_tools import GetHostsTool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from operation.ai_operator import AIOperator


agent = initialize_agent(
    tools=[GetHostsTool()],
    llm=AIOperator().llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
result = agent.run("How many network devices are there?")
print(result)