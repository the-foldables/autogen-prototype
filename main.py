import os
import autogen

from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.tools.wikipedia import WikipediaToolSpec

from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent

import agent_system_prompts

api_key = os.environ["API_KEY"] # do not insert API key in plaintext!
cborg = True

if cborg:
    base_url = "https://api.cborg.lbl.gov"
    model = "openai/lbl/cborg-chat:latest"
    embedding_model = "openai/lbl/nomic-embed-text"
else:
    base_url = "https://api.openai.com/v1"
    model = "gpt-3.5-turbo"
    embedding_model = "text-embedding-3-small"


config_list = [{"model": model, "api_key": api_key, 
              "base_url": base_url,
              "api_rate_limit":60.0, "price" : [0, 0]}]

llm = LiteLLM(model=model,
              api_key=api_key, 
              api_base=base_url,
              )

embedding = LiteLLMEmbedding(model_name=embedding_model,
              api_key=api_key,
              api_base=base_url,
              )


Settings.llm = llm
Settings.embed_model = embedding

# create a react agent to use wikipedia tool
wiki_spec = WikipediaToolSpec()

# Get the search wikipedia tool
wikipedia_tool = wiki_spec.to_tool_list()[1]

location_specialist = ReActAgent.from_tools(tools=[wikipedia_tool], llm=llm, max_iterations=10, verbose=True)

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

trip_assistant = LLamaIndexConversableAgent(
    "trip_specialist",
    llama_index_agent=location_specialist,
    system_message=agent_system_prompts.trip_assistant,
    description=agent_system_prompts.trip_assistant_description,
    
)

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    human_input_mode="ALWAYS",
    code_execution_config=False,
)

groupchat = autogen.GroupChat(
    agents=[trip_assistant, user_proxy],
    messages=[],
    max_round=500,
    speaker_selection_method="round_robin",
    enable_clear_history=True,
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

chat_result = user_proxy.initiate_chat(
    manager,
    message="What can i find in Tokyo related to Hayao Miyazaki and its moveis like Spirited Away?",
)