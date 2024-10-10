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

from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent


import prompts
from api_config import get_api_config

parser = argparse.ArgumentParser()
parser.add_argument('--cborg', action='store_true', help='Running with LBNL credentials')
args = parser.parse_args()

llm_config, llm_config_gpt, llm, embedding = get_api_config(args.cborg)

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
    system_message=prompts.llamaindex_assistant,
    description=prompts.llamaindex_assistant_description,
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
   system_message=prompts.user_proxy,
   #Only say APPROVED in most cases, and say exit when nothing to be done further. Do not say others.
   code_execution_config=False,
   #default_auto_reply="Approved", 
   human_input_mode="ALWAYS",
)

engineer = autogen.AssistantAgent(
    name="Engineer",
    human_input_mode="NEVER",
    llm_config=llm_config,
    system_message=prompts.engineer,
)
scientist = autogen.AssistantAgent(
    name="Scientist",
    human_input_mode="NEVER",
    llm_config=llm_config,
    system_message=prompts.scientist
)
planner = autogen.AssistantAgent(
    name="Planner",
    human_input_mode="NEVER",
    system_message=prompts.planner,
    llm_config=llm_config,
)
executor = autogen.UserProxyAgent(
    name="Executor",
    system_message=prompts.executor,
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper", "use_docker": False},
)
critic = autogen.AssistantAgent(
    name="Critic",
    system_message=prompts.critic,
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