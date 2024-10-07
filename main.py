import os
import autogen
import argparse

from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.tools.wikipedia import WikipediaToolSpec

from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent

import panel as pn
import agent_system_prompts

parser = argparse.ArgumentParser()
parser.add_argument('--cborg', action='store_true', help='Running with LBNL credentials')
args = parser.parse_args()

api_key = os.environ["API_KEY"] # do not insert API key in plaintext!

if args.cborg:
    base_url = "https://api.cborg.lbl.gov"
    model = "openai/lbl/cborg-chat:latest"
    embedding_model = "openai/lbl/nomic-embed-text"
else:
    base_url = "https://api.openai.com/v1"
    model = "gpt-3.5-turbo"
    embedding_model = "text-embedding-3-small"


config_list = [
    {
        "model": model, "api_key": api_key, 
              "base_url": base_url,
              "api_rate_limit":60.0, "price" : [0, 0]
    }
]

llm = LiteLLM(
    model=model,
    api_key=api_key, 
    api_base=base_url,
)

embedding = LiteLLMEmbedding(
    model_name=embedding_model,
    api_key=api_key,
    api_base=base_url,
)

Settings.llm = llm
Settings.embed_model = embedding

# create a react agent to use wikipedia tool
wiki_spec = WikipediaToolSpec()

# Get the search wikipedia tool
wikipedia_tool = wiki_spec.to_tool_list()[1]

location_specialist = ReActAgent.from_tools(
    tools=[wikipedia_tool], llm=llm, max_iterations=10, verbose=True
)

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
    human_input_mode="NEVER",
    code_execution_config=False,
)

groupchat = autogen.GroupChat(
    agents=[trip_assistant, user_proxy],
    messages=[],
    max_round=10,
    allow_repeat_speaker=False
)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

avatar = {user_proxy.name:"👨‍💼", trip_assistant.name:"🗓"}

def print_messages(recipient, messages, sender, config):
    chat_interface.send(
        messages[-1]['content'], user=messages[-1]['name'],
        avatar=avatar[messages[-1]['name']], respond=False
    )
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num_messages: {len(messages)} | message: {messages[-1]}")
    return False, None # required to ensure the agent communication flow continues

trip_assistant.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages,
    config={"callback": None}  
)

user_proxy.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages,
    config={"callback": None}
)

pn.extension(design="material")

def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    chat_result = user_proxy.initiate_chat(
        manager,
        message=contents,
    )

chat_interface = pn.chat.ChatInterface(callback=callback, callback_exception='verbose')
chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()