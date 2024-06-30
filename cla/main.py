import argparse
import json
import time
import sys
import os

from anthropic import Anthropic
from colors import red, green, blue, yellow, magenta

# constants
INITIAL_PROMPT = (
    "You are a helpful assistant who keeps your response short and to the point"
)
MULTI_LINE_SEND = "END"
MULI_LINE_MODE_TEXT = "!m"
CLEAR_HISTORY_TEXT = "!c"
SAVE_CHAT_HISTORY = "!s"
EXIT_STRING_KEY = "!e"

# global variables
CURRENT_CHAT_HISTORY = [{"time": time.time(), "user": INITIAL_PROMPT, "bot": ""}]

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


# NOTE: this is not great but Anthropic does not have an API endpoint for this
def get_models():
    from bs4 import BeautifulSoup
    import requests

    url = "https://docs.anthropic.com/en/docs/about-claude/models"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    data_dict = []
    tables = soup.find_all("table")
    for table in tables:
        headers = [header.get_text().strip() for header in table.find_all("th")]
        rows = table.find_all("tr")[1:]
        for row in rows:
            cells = row.find_all("td")
            if cells:
                row_data = [cell.get_text().strip() for cell in cells]
                data_dict.append(dict(zip(headers, row_data)))

    data_dict = data_dict[:6]

    for d in data_dict:
        keys_to_remove = [
            key for key, value in d.items() if "coming soon" in value.lower()
        ]
        for key in keys_to_remove:
            del d[key]
    data_dict = [d for d in data_dict[:6] if not (len(d) == 1 and "Model" in d)]

    output = []
    for entry in data_dict:
        model = entry.get("Model")
        model_id = entry.get("Latest 1P API model name")
        if model and model_id:
            output.append({"name": model, "model": model_id})

    return output


def title_print(selected_model):
    print(
        yellow(
            f"""
Chatting With Anthropic's '{selected_model}' Model
 - '{EXIT_STRING_KEY}' to exit
 - '{MULI_LINE_MODE_TEXT}' for multi-line mode
 - '{MULTI_LINE_SEND}' to end in multi-line mode
 - '{CLEAR_HISTORY_TEXT}' to clear chat history
 - '{SAVE_CHAT_HISTORY}' to save chat history
    """.strip()
        )
    )


def chatbot(selected_model, print_title=True):
    messages = []
    multi_line_input = False
    first_loop = True

    if print_title:
        title_print(selected_model)

    line_mode = False
    last_line = ""
    while True:
        if not first_loop:
            print()

        if not last_line.endswith("\n"):
            print()

        user_input_string = blue("User: ")
        if line_mode:
            print(
                yellow(
                    f"Entered multi-line input mode. Type '{MULTI_LINE_SEND}' to send message"
                )
            )
            user_input_string = red("[M] ") + blue("User: ")
        print(user_input_string, end="", flush=True)

        first_loop = False

        if not multi_line_input:
            message = sys.stdin.readline().rstrip("\n")

            if message == MULI_LINE_MODE_TEXT:
                multi_line_input = True
                line_mode = True
                last_line = "\n"
                continue
            elif message.replace(" ", "") == EXIT_STRING_KEY:
                break
            elif message.replace(" ", "") == CLEAR_HISTORY_TEXT:
                messages = []
                print(yellow("\n\nChat history cleared.\n"))
                first_loop = True
                continue

        if multi_line_input:
            message_lines = []
            while True:
                line = sys.stdin.readline().rstrip("\n")
                if line == MULTI_LINE_SEND:
                    break
                elif line.replace(" ", "") == CLEAR_HISTORY_TEXT:
                    messages = []
                    print(yellow("\nChat history cleared.\n"))
                    first_loop = True
                    break
                message_lines.append(line)
            message = "\n".join(message_lines)
            line_mode = False
            multi_line_input = False

        print()

        if message == SAVE_CHAT_HISTORY:
            cha_filepath = f"cha_{int(time.time())}.json"
            with open(cha_filepath, "w") as f:
                json.dump(CURRENT_CHAT_HISTORY, f)
            print(red(f"\nSaved current chat history to {cha_filepath}"))
            continue

        if len(message) == 0:
            raise KeyboardInterrupt

        messages.append({"role": "user", "content": message})

        obj_chat_history = {"time": time.time(), "user": message, "bot": ""}
        try:
            response = client.messages.create(
                model=selected_model,
                max_tokens=1024,
                messages=messages,
                system=INITIAL_PROMPT,
                stream=True,
            )

            print(green("Claude:"), end=" ", flush=True)
            for chunk in response:
                if chunk.type == "content_block_delta":
                    last_line = chunk.delta.text
                    sys.stdout.write(green(chunk.delta.text))
                    obj_chat_history["bot"] += chunk.delta.text
                    sys.stdout.flush()

            messages.append({"role": "assistant", "content": obj_chat_history["bot"]})
        except Exception as e:
            print(red(f"Error during chat: {e}"))
            break

        CURRENT_CHAT_HISTORY.append(obj_chat_history)


def basic_chat(filepath, model, just_string=None):
    try:
        print_padding = False

        if just_string is None:
            if "/" not in filepath:
                filepath = os.path.join(os.getcwd(), filepath)

            if not os.path.exists(filepath):
                print(red(f"The following file does not exist: {filepath}"))
                return

            print(blue(f"Feeding the following file content to {model}:\n{filepath}\n"))

            with open(filepath, "r") as file:
                content = file.read()
        else:
            content = just_string
            print_padding = True

        if print_padding:
            print()

        response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": content}],
            system=INITIAL_PROMPT,
            stream=True,
        )

        last_line = ""
        complete_output = ""
        for chunk in response:
            if chunk.type == "content_block_delta":
                last_line = chunk.delta.text
                complete_output += chunk.delta.text
                sys.stdout.write(green(chunk.delta.text))
                sys.stdout.flush()

        CURRENT_CHAT_HISTORY.append(
            {"time": time.time(), "user": content, "bot": complete_output}
        )

        if not last_line.startswith("\n"):
            print()

        if print_padding:
            print()
    except Exception as e:
        print(red(f"Error during chat: {e}"))


def cli():
    try:
        parser = argparse.ArgumentParser(
            description="Chat with an Anthropic Claude model."
        )
        parser.add_argument(
            "-tp", "--titleprint", help="Print initial title during interactive mode"
        )
        parser.add_argument(
            "-m", "--model", help="Model to use for chatting", required=False
        )
        parser.add_argument(
            "-f",
            "--file",
            help="Filepath to file that will be sent to the model (text only)",
            required=False,
        )
        parser.add_argument(
            "-s",
            "--string",
            help="Non-interactive mode, just feed a string into the model",
        )

        args = parser.parse_args()

        title_print_value = True
        if str(args.titleprint).lower() == "false":
            title_print_value = False

        anthropic_models = get_models()

        if args.model and any(
            model["model"] == args.model for model in anthropic_models
        ):
            selected_model = args.model
        else:
            print(yellow("Available Anthropic Models:"))
            for i, model in enumerate(anthropic_models, 1):
                print(yellow(f"   {i}) {model['name']} ({model['model']})"))
            print()

            try:
                model_choice = int(input(blue("Model (Enter the number): ")))
                if 1 <= model_choice <= len(anthropic_models):
                    selected_model = anthropic_models[model_choice - 1]["model"]
                else:
                    print(red("Invalid model selected. Exiting."))
                    return
            except ValueError:
                print(red("Invalid input. Exiting."))
                return
            except KeyboardInterrupt:
                return
            print()

        if args.string and args.file:
            print(red("You can't use the string and file option at the same time!"))
        elif args.string:
            basic_chat(None, selected_model, str(args.string))
        elif args.file:
            basic_chat(args.file, selected_model)
        else:
            try:
                label_text = red("✶ Anthropic")
                if title_print_value == True:
                    label_text += "\n"
                print(label_text)
                chatbot(selected_model, title_print_value)
            except KeyboardInterrupt:
                print()
                sys.exit(0)

    except Exception as err:
        print(red(f"An error occurred: {err}"))


if __name__ == "__main__":
    cli()
