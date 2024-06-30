<p align="center">
    <img width="300" src="./assets/logo.png">
</p>

## About

A simple CLI chat tool designed for easy interaction with Anthropic's LLM models. Cla is based off of the [Cha](https://github.com/MehmetMHY/cla) project.

## Setup

1. Get your Anthropic API key. Follow [this](https://docs.anthropic.com/en/docs/quickstart) tutorial.
    - Check out your Anthropic console [HERE](https://docs.anthropic.com/en/docs/console.anthropic.com)
    - Check out/get your API key(s) [HERE](https://console.anthropic.com/settings/keys)

2. After getting your API key, create a .env file and add the following to it:
    ```
    export ANTHROPIC_API_KEY="sk-ant..."
    ```

3. Make sure you have python and pip installed. Then install the tool's dependencies:
    ```
    pip3 install --upgrade .
    ```

4. Source your environment variable(s):
    ```
    source .env
    ```

5. Use it!
    ```
    cla
    # or 
    python3 main.py
    ```

## How To Set Up?

### 1. Install `cla`

Clone this repository, navigate to its directory, and run the following command to install or upgrade `cla`:

```bash
pip3 install --upgrade .
```

### 2. Configure API Key

1. Create a `.env` file in the root directory.

2. Obtain your OpenAI API key [HERE](https://platform.openai.com/api-keys). If you want to use Answer-Search, obtain your Brave API key [HERE](https://brave.com/search/api/).

3. Add your keys to the `.env` file, using this format:

    ```env
    # Replace YOUR_KEY_HERE with your OpenAI API key
    OPENAI_API_KEY="YOUR_KEY_HERE"

    # (Optional) Replace YOUR_KEY_HERE with your Brave API key
    BRAVE_API_KEY="YOUR_KEY_HERE"
    ```

4. To activate the environment variables, run:

```bash
source .env
```

### 3. Run `cla`

To start the tool, execute:

```bash
cla
```

### 4. (Optional) Setup an Alias/Command for `cla`

For easier use of `cla`, consider setting up an alias or command. To add the preferred alias/command for cla, run the appropriate command for your shell:

```bash
# if using a zsh shell
echo 'alias cla="path/to/cla"' >> $HOME/.zshrc

# if using a bash shell
echo 'alias cla="path/to/cla"' >> $HOME/.bashrc
```

You're now ready to go!

## Develop Mode

For developing cla, you can do the following:

### 1. Install `cla` in editable mode so that pip points to the source files of the cloned code:

```bash
pip install -e .
```

### 2. Make clanges to the code, then run `cla` to try out your clanges

### 3. If you add a new dependency, you will have to do step 1 again

## Other Notes

- To see and/or clange hard-coded config variables/logic in cla, checkout the `config.py` file.

## Credits

- [OpenAI Documentation](https://platform.openai.com/docs/introduction)
- [clatGPT (GPT-4)](https://clat.openai.com/)
- [Ollama's CLI](https://ollama.com/)

