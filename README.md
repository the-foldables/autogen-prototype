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

Install packages: # TODO change to requirements.txt
```
python -m pip install openai
python -m pip install scikit-learn
python -m pip install autogen-agentchat~=0.2
python -m pip install flaml[automl]
python -m pip install -U matplotlib
python -m pip install llama-index llama-index-tools-wikipedia llama-index-readers-wikipedia wikipedia
python -m pip install llama-index-llms-litellm
python -m pip install llama-index-embeddings-litellm
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

## Known Issues

Apply the following patches:

```
.../autogen_env/lib/python3.12/site-packages/litellm/cost_calculator.py

Line 808:
    except Exception as e:
        return 0
        # raise e
```

```
.../autogen_env/lib/python3.12/site-packages/autogen/oai/client.py
Line 454:
            self._initialize_rate_limiters(self._config_list)
```

## Resources

[AutoGen tutorial](https://microsoft.github.io/autogen/docs/tutorial/introduction)
[LlamaIndex](https://docs.llamaindex.ai/en/stable/)
[How to Create a Web UI for AutoGen](https://yeyu.substack.com/p/how-to-create-a-web-ui-for-autogen)