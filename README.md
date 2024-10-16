# autogen-prototype
Prototype of the Foldables platform with AutoGen

## Install Instructions

### Get the repository

Clone the repository:

```
export WORKING_DIR={your-working-directory}
cd $WORKING_DIR
git clone https://github.com/the-foldables/autogen-prototype.git
cd autogen-prototype
```

### Secrets

Create a file `.env.development.local` at the base (root) of this repo
that contains secrets that should NEVER be checked into GitHub:

```
export API_KEY={your-openai-api-key}
export GROQ_API_KEY=abc...123
# more keys...
# ...
```

Make sure `.env.development.local` is in you `.gitignore`!

### Conda environment

Create conda environment and install dependencies
```
./scripts/conda-create.sh
```

Can deactivate the conda environment:
```
conda deactivate
```


### Docker

Install [Docker](https://docs.docker.com/engine/install/).


## Startup Instructions

After installation, you can startup in a new terminal with the following instructions:

```
export WORKING_DIR={your-working-directory}
cd $WORKING_DIR
conda activate autogen_env
```

Open Docker in the background.

## Run the code

Simple test:
```
./scripts/panel-test.sh
```

AutoGen with panel example:
```
./scripts/serve.sh
```

## Resources

- [AutoGen tutorial](https://microsoft.github.io/autogen/docs/tutorial/introduction)
- [LlamaIndex](https://docs.llamaindex.ai/en/stable/)
- [How to Create a Web UI for AutoGen](https://yeyu.substack.com/p/how-to-create-a-web-ui-for-autogen)
- [AutoGen’s Full Function UI Powered by Panel](https://levelup.gitconnected.com/autogens-full-function-ui-powered-by-panel-d00ddecc98ee)
- [AutoGen + Panel Tutorials](https://github.com/yeyu2/Youtube_demos)
- [AutoGen + Panel Code](https://github.com/yeyu2/Youtube_demos/blob/main/panel_autogen_2.py)
