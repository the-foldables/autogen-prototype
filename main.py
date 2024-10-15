import asyncio
import argparse
import tempfile

from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.tools.wikipedia import WikipediaToolSpec

import autogen
from autogen.agentchat.contrib.llamaindex_conversable_agent import LLamaIndexConversableAgent
from autogen.coding import DockerCommandLineCodeExecutor
from autogen import register_function

import panel as pn

import prompts
from tools.calculator import calculator
from tools.esm3 import esm_generate, save_protein
from api_config import get_api_config
from agent_builder import AgentBuilder


parser = argparse.ArgumentParser()
parser.add_argument('--cborg', action='store_true', help='Running with LBNL credentials')
args = parser.parse_args()

# Create a temporary directory to store code files created by the code_executor_agent_using_docker
temp_dir = tempfile.TemporaryDirectory()

llm_config, llm, embedding = get_api_config(args.cborg)

Settings.llm = llm
Settings.embed_model = embedding

# create a react agent to use wikipedia tool
wiki_spec = WikipediaToolSpec()

# Get the search wikipedia tool
wikipedia_tool = wiki_spec.to_tool_list()[1]

llamaindex_specialist = ReActAgent.from_tools(
    tools=[wikipedia_tool], llm=llm, max_iterations=20, verbose=True
)

llamaindex_assistant = LLamaIndexConversableAgent(
    name='llamaindex_assistant',
    llama_index_agent=llamaindex_specialist,
    system_message=prompts.llamaindex_assistant,
    description=prompts.llamaindex_assistant_description,
)

input_future = None

class MyConversableAgent(autogen.ConversableAgent):

    async def a_get_human_input(self, prompt: str) -> str:
        global input_future
        print('Getting human input!')
        chat_interface.send(prompt, user='System', respond=False)
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
   name='Admin',
   is_termination_msg=lambda x: x.get('content', '').rstrip().endswith('exit'),
   system_message=prompts.user_proxy,
   #Only say APPROVED in most cases, and say exit when nothing to be done further. Do not say others.
   code_execution_config=False,
   #default_auto_reply='Approved',
   human_input_mode='ALWAYS',
)

builder = AgentBuilder(
    human_input_mode='NEVER',
    llm_config=llm_config,
)

builder.AddOtherAgent(
    name='Admin',
    agent=user_proxy,
    avatar='👨‍💼',
)

builder.AddOtherAgent(
    name='llamaindex_assistant',
    agent=llamaindex_assistant,
    avatar='🦙',
)

builder.AddAssistantAgent(
    name='Engineer',
    system_message=prompts.engineer,
    avatar='👩‍💻',
)

builder.AddAssistantAgent(
    name='Scientist',
    system_message=prompts.scientist,
    avatar='👩‍🔬',
)

builder.AddAssistantAgent(
    name='Medicinal_Chemist',
    system_message=prompts.medicinal_chemist,
    avatar='💊',
)

builder.AddAssistantAgent(
    name='Planner',
    system_message=prompts.planner,
    avatar='🗓',
)

# Create a Docker command line code executor.
code_executor = DockerCommandLineCodeExecutor(
    image='python:3.12-slim',  # Execute code using the given docker image name.
    timeout=10,  # Timeout for each code execution in seconds.
    work_dir=temp_dir.name,  # Use the temporary directory to store the code files.
)

# Create an agent with code executor configuration that uses docker.
builder.AddConversableAgent(
    name='Executor',
    system_message=prompts.executor,
    code_execution_config={'executor': code_executor},  # Use the docker command line code executor.
    avatar='🛠',
    human_input_mode='NEVER',
)

builder.AddAssistantAgent(
    name='Critic',
    system_message=prompts.critic,
    avatar='📝',
)

# Suggests use of the calculator
calculator_assistant = builder.AddConversableAgent(
    name='Calculator_Assistant',
    system_message=prompts.calculator,
    llm_config=llm_config,
    avatar='🔢',
)

# Executes the calculator tool
calculator_executor = builder.AddConversableAgent(
    name='Calculator_Executor',
    llm_config=False,
    # is_termination_msg=lambda msg: msg.get('content') is not None and 'TERMINATE' in msg['content'],
    avatar='🔢',
    human_input_mode='NEVER',
)

# Register the calculator function to the two agents.
register_function(
    calculator,
    caller=calculator_assistant,  # The assistant agent can suggest calls to the calculator.
    executor=calculator_executor,  # The executor agent can execute the calculator calls.
    name='calculator',  # By default, the function name is used as the tool name.
    description='A simple calculator',  # A description of the tool.
)


# Suggests use of esm_generate
protein_generator_assistant = builder.AddConversableAgent(
    name='ESM3_Assistant',
    system_message=prompts.protein_generator,
    llm_config=llm_config,
    avatar='🧬',
)

# Executes the esm_generate tool
protein_generator_executor = builder.AddConversableAgent(
    name='ESM3_Executor',
    llm_config=False,
    avatar='🧬',
    human_input_mode='NEVER',
)

# Register the calculator function to the two agents.
register_function(
    esm_generate,
    caller=protein_generator_assistant,  # The assistant agent can suggest calls.
    executor=calculator_executor,  # The executor agent can execute the call.
    name='esm_generate',  # By default, the function name is used as the tool name.
    description=prompts.esm_generate_description,  # A description of the tool.
)


groupchat = builder.GroupChat(messages=[], max_round=20)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)

avatar = builder.Avatars()

def print_messages(recipient, messages, sender, config):
    print(f'Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}')

    content = messages[-1]['content']
    user = messages[-1]['name']
    if len(messages)>1 and content != '' and user != 'Admin':
        chat_interface.send(content, user=user, avatar=avatar[user], respond=False)

    return False, None  # required to ensure the agent communication flow continues

builder.RegisterReply(reply_func=print_messages)

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