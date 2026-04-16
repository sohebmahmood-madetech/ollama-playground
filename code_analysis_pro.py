import os
from pathlib import Path
from argparse import ArgumentParser

from ollama import chat, ChatResponse

DEFAULT_MODEL = "qwen3.5:4b"
#DEFAULT_MODEL = "glm-4.7-flash"


def list_files_and_dirs(path):
    """Returns a list of all files and subdirectories under the given path."""
    """
    Args:
        path: The path where the code project lives
    Returns:
        A list of all files and subdirectories under the given path
    """
    path = Path(path)
    return list(path.rglob('*'))


def read_file_content(file_path):
    """
    Reads the entire text content of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Content of the file.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_dir(path_to_read: str, thinking_mode: bool = False, model: str = DEFAULT_MODEL):
    available_functions = {
        'list_files_and_dirs': list_files_and_dirs,
        'read_file_content': read_file_content,
    }

    messages = [{'role': 'user', 'content': f'Can you explain to me what the code does under `{path_to_read}`?'}]
    while True:
        response: ChatResponse = chat(
            model=model,
            messages=messages,
            tools=[list_files_and_dirs, read_file_content],
            think=thinking_mode,
        )
        messages.append(response.message)
        if thinking_mode:
            print(f"\n\nThinking:\n{response.message.thinking}")
            input()
            print(f"\n\n============\n\nContent:\n{response.message.content}")
        if response.message.tool_calls:
            for tc in response.message.tool_calls:
                if tc.function.name in available_functions:
                    if thinking_mode:
                        print(f"Calling {tc.function.name} with arguments {tc.function.arguments}")
                    result = available_functions[tc.function.name](**tc.function.arguments)
                    if thinking_mode:
                        print(f"Result: {result}")
                        input()
                    # add the tool result to the messages
                    messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})
        else:
            # end the loop when there are no more tool calls
            if thinking_mode:
                print(f"### FINAL RESPONSE:\n{response.message.content}")
                input()
            else:
                print(response.message.content)
            break

def get_args():
    parser = ArgumentParser(prog='code_analysis_pro',
                            description="Get a clanker to do the heavy lifting for you",
                            epilog='The robot uprising is coming...')
    parser.add_argument('path', type=str, help="Path to the code project.")
    parser.add_argument('--think-goddamnit', action='store_true', help='Turn on thinking mode (be verbose about AI thoughts)')
    parser.add_argument('--model', type=str, default=DEFAULT_MODEL, help="Name of Ollama model to use")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    if not os.path.exists(args.path) or not os.path.isdir(args.path):
        print("Invalid path specified")
        exit(1)
    read_dir(args.path, args.think_goddamnit, args.model)