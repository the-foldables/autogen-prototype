import autogen

# AgentBuilder uses the 'builder' pattern to assist with the creation of
# multiple agents (of varying types).
class AgentBuilder:
  def __init__(self, human_input_mode='NEVER', llm_config=None):
    self.human_input_mode = human_input_mode
    self.llm_config = llm_config
    self.agent_names = []
    self.assistant_agents = []
    self.conversable_agents = []
    self.other_agents = []
    self.avatars = {}

  def AddOtherAgent(self, name=None, agent=None, avatar=None):
    if (name == None or agent == None or avatar == None):
      raise 'missing required arguments'

    self.agent_names.append(name)
    self.avatars[name] = avatar
    self.other_agents.append(agent)
    return agent

  def AddAssistantAgent(self, name=None, system_message=None, avatar=None, description='an assistant agent'):
    if (name == None or system_message == None or avatar == None):
      raise 'missing required arguments'

    self.agent_names.append(name)
    self.avatars[name] = avatar
    agent = autogen.AssistantAgent(
      name=name,
      human_input_mode=self.human_input_mode,
      llm_config=self.llm_config,
      system_message=system_message,
      description=description
    )
    self.assistant_agents.append(agent)
    print(f'Added assistant agent "{name}" {avatar}')
    return agent

  def AddConversableAgent(self, name=None, system_message=None, code_execution_config={}, avatar=None,
                          llm_config=False, is_termination_msg=None, human_input_mode=None,
                          description='a conversable agent'):
    if (name == None or avatar == None):
      raise 'missing required arguments'

    self.agent_names.append(name)
    self.avatars[name] = avatar
    agent = autogen.ConversableAgent(
      name=name,
      human_input_mode=human_input_mode,
      code_execution_config=code_execution_config,
      system_message=system_message,
      llm_config=llm_config,
      is_termination_msg=is_termination_msg,
      description=description
    )
    self.conversable_agents.append(agent)
    print(f'Added conversable agent "{name}" {avatar}')
    return agent

  def GroupChat(self, messages=[], max_round=20):
    names = []
    for name in self.agent_names: names.append(name)
    agents = []
    for agent in self.assistant_agents: agents.append(agent)
    for agent in self.conversable_agents: agents.append(agent)
    for agent in self.other_agents: agents.append(agent)
    if len(names) != len(agents):
      raise f'Programming error: {len(agents)} != {len(names)}'
    print(f'Creating group chat with {len(agents)} agents: {names}')
    return autogen.GroupChat(agents=agents, messages=messages, max_round=max_round)

  def Avatars(self):
    return self.avatars

  def RegisterReply(self, reply_func=None):
    names = []
    for name in self.agent_names: names.append(name)
    agents = []
    for agent in self.assistant_agents: agents.append(agent)
    for agent in self.conversable_agents: agents.append(agent)
    for agent in self.other_agents: agents.append(agent)
    if len(names) != len(agents):
      raise f'programming error: {len(agents)} != {len(names)}'
    print(f'Registering reply for {len(agents)} agents: {names}')
    for agent in agents:
      agent.register_reply(
        [autogen.Agent, None],
        reply_func=reply_func,
        config={'callback': None},
      )
