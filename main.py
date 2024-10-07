"""
https://github.com/yeyu2/Youtube_demos/blob/main/panel_autogen_2.py
"""
# To install required packages:
# pip install pyautogen==0.2.9 panel==1.3.8
import autogen

import panel as pn
import openai
import os
import time
import asyncio
import argparse

from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.tools.wikipedia import WikipediaToolSpec

from llama_index.llms.litellm import LiteLLM
from llama_index.embeddings.litellm import LiteLLMEmbedding

from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent


parser = argparse.ArgumentParser()
parser.add_argument('--cborg', action='store_true', help='Running with LBNL credentials')
args = parser.parse_args()

api_key = os.environ["API_KEY"] # do not insert API key in plaintext!

if args.cborg:
    base_url = "https://api.cborg.lbl.gov"
    model = "openai/lbl/cborg-chat:latest"
    model_gpt = "openai/gpt-4o-mini"
    embedding_model = "openai/lbl/nomic-embed-text"
else:
    base_url = "https://api.openai.com/v1"
    model = "gpt-4o-mini"
    model_gpt = model
    embedding_model = "text-embedding-3-small"

config_list = [
    {
        "model": model, "api_key": api_key, 
              "base_url": base_url,
              "api_rate_limit":60.0, "price" : [0, 0]
    }
]

config_list_gpt = [
    {
        "model": model_gpt, "api_key": api_key, 
              "base_url": base_url,
              "api_rate_limit":60.0, "price" : [0, 0]
    }
]

llm_config = {
    "temperature": 0,
    "config_list": config_list,
}

llm_config_gpt = {
    "temperature": 0,
    "config_list": config_list_gpt,
}

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

llamaindex_specialist = ReActAgent.from_tools(
    tools=[wikipedia_tool], llm=llm, max_iterations=10, verbose=True
)

llamaindex_assistant = LLamaIndexConversableAgent(
    name="llamaindex_assistant",
    llama_index_agent=llamaindex_specialist,
    system_message="You can use Wikipedia to provide more details about any aspect of the plan.",
    description="This agent uses Wikipedia to provide more details about any aspect of the plan.",
)

input_future = None

class MyConversableAgent(autogen.ConversableAgent):

    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        print('Getting human input!')
        chat_interface.send(prompt, user="System", respond=False)
        # Create a new Future object for this input operation if none exists
        if input_future is None or input_future.done():
            input_future = asyncio.Future()

        # Wait for the callback to set a result on the future
        await input_future

        # Once the result is set, extract the value and reset the future for the next input operation
        input_value = input_future.result()
        input_future = None
        return input_value

user_proxy = MyConversableAgent(
   name="Admin",
   is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("exit"),
   system_message="""A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin. 
   
   """,
   #Only say APPROVED in most cases, and say exit when nothing to be done further. Do not say others.
   code_execution_config=False,
   #default_auto_reply="Approved", 
   human_input_mode="ALWAYS",
   #llm_config=gpt4_config,
)

engineer = autogen.AssistantAgent(
    name="Engineer",
    human_input_mode="NEVER",
    llm_config=llm_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)
scientist = autogen.AssistantAgent(
    name="Scientist",
    human_input_mode="NEVER",
    llm_config=llm_config,
    system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code."""
)
planner = autogen.AssistantAgent(
    name="Planner",
    human_input_mode="NEVER",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
    llm_config=llm_config,
)
executor = autogen.UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper", "use_docker": False},
)
critic = autogen.AssistantAgent(
    name="Critic",
    system_message="""Critic. Double check plan, claims, code from other agents and provide feedback. 
    Check whether the plan includes adding verifiable info such as source URL. 
    """,
    llm_config=llm_config,
    human_input_mode="NEVER",
)

groupchat = autogen.GroupChat(agents=[user_proxy, engineer, scientist, planner, executor, critic, llamaindex_assistant], messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_gpt)

avatar = {user_proxy.name:"👨‍💼", engineer.name:"👩‍💻", scientist.name:"👩‍🔬", planner.name:"🗓", executor.name:"🛠", critic.name:'📝', llamaindex_assistant.name:"🦙"}

def print_messages(recipient, messages, sender, config):
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")

    content = messages[-1]['content']
    
    print(all(key in messages[-1] for key in ['name']))
    if all(key in messages[-1] for key in ['name']):
        if messages[-1]['name'] != 'Admin':
            chat_interface.send(content, user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
    else:
        chat_interface.send(content, user=recipient.name, avatar=avatar[recipient.name], respond=False)
    
    return False, None  # required to ensure the agent communication flow continues

user_proxy.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

engineer.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 
scientist.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 
planner.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

executor.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 
critic.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 

llamaindex_assistant.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 

pn.extension(design="material")

initiate_chat_task_created = False

async def delayed_initiate_chat(agent, recipient, message):

    global initiate_chat_task_created
    # Indicate that the task has been created
    initiate_chat_task_created = True

    # Wait for 2 seconds
    await asyncio.sleep(2)

    # Now initiate the chat
    await agent.a_initiate_chat(recipient, message=message)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    
    global initiate_chat_task_created
    global input_future

    if not initiate_chat_task_created:
        asyncio.create_task(delayed_initiate_chat(user_proxy, manager, contents))

    else:
        if input_future and not input_future.done():
            input_future.set_result(contents)
        else:
            print("There is currently no input being awaited.")


chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send("Please describe a task you would like to complete.", user="System", respond=False)
chat_interface.servable()