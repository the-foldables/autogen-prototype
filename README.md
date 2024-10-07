# autogen-prototype
Prototype of the Foldables platform with AutoGen

## Install Instructions

Clone the repository:

```
export WORKING_DIR={your-working-directory}
cd $WORKING_DIR
git clone https://github.com/the-foldables/autogen-prototype.git
cd autogen-prototype
```

Create a conda environment:
```
conda create --name autogen_env python=3.12
conda activate autogen_env
```

Install packages:
```
python -m pip install -r requirements.txt
brew install libomp
```

Deactivate environment:
```
conda deactivate
```

## Startup Instructions

After installation, you can startup in a new terminal with the following instructions:

```
export WORKING_DIR={your-working-directory}
cd $WORKING_DIR
conda activate autogen_env
export API_KEY={your-openai-api-key} 
```

## Run the code

### OpenAI API key

Simple test:
```
panel serve test_panel.py
```

AutoGen example:
```
panel serve main.py 
```

### If using LBNL credentials for the API key

Simple test:
```
panel serve test_panel.py --args --cborg
```

AutoGen example:
```
panel serve main.py --args --cborg
```
### AutoGen Patch

Use the terminal to find where your AutoGen package code lives:
```
python -m pip show autogen-agentchat
```

## Resources

- [AutoGen tutorial](https://microsoft.github.io/autogen/docs/tutorial/introduction)
- [LlamaIndex](https://docs.llamaindex.ai/en/stable/)
- [How to Create a Web UI for AutoGen](https://yeyu.substack.com/p/how-to-create-a-web-ui-for-autogen)
- [AutoGen’s Full Function UI Powered by Panel](https://levelup.gitconnected.com/autogens-full-function-ui-powered-by-panel-d00ddecc98ee)