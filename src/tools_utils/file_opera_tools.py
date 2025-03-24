from pathlib import Path
from typing import Optional
import os

# Correct the import path or provide an alternative if 'tool' is not in 'smolagents'
from ..smolagents import tool
import json
import csv
import openpyxl
import pandas as pd

@tool
def list_folders(directory: str) -> str:
    """
    List all folders in a given directory.

    Args:
        directory: The path to the directory to list folders from.

    Returns:
        A string containing a newline-separated list of folder names,
        or an error message if the directory does not exist or is not a directory.
    """
    path = Path(directory)
    if not path.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return f"Error: Directory '{directory}' does not exist."
    if not path.is_dir():

        print(f"Error: '{directory}' is not a directory.")
        return f"Error: '{directory}' is not a directory."
    folders = [item.name for item in path.iterdir() if item.is_dir()]
    if not folders:
        print(f"No folders found in this directory.")
        return "No folders found in this directory."
    
    print("Folders:\n" + "\n".join(folders))
    return "Folders:\n" + "\n".join(folders)

@tool
def list_files(directory: str) -> str:
    """
    List all files in a given directory.

    Args:
        directory: The path to the directory to list files from.

    Returns:
        A string containing a newline-separated list of file names,
        or an error message if the directory does not exist or is not a directory.
    """
    path = Path(directory)
    if not path.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return f"Error: Directory '{directory}' does not exist."
    if not path.is_dir():

        print(f"Error: '{directory}' is not a directory.")
        return f"Error: '{directory}' is not a directory."
    files = [item.name for item in path.iterdir() if item.is_file()]
    if not files:
        print(f"No files found in this directory.")
        return "No files found in this directory."
    
    print("Files:\n" + "\n".join(files))
    return "Files:\n" + "\n".join(files)

@tool
def read_file(file_path: str) -> str:
    """
    Reads the content of a file. Note: If the file is too large, it may cause memory issues.

    This function attempts to read the content of the file at the specified path and returns a dictionary 
    containing The content of the file.

    Example: ``` Content = read_file_content('example.txt') ```

    Args:
        file_path (str): The path to the file to read.

    Returns:
        "Content": The content of the file or None.

    """
 
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File {file_path} does not exist.")
        return None
    if not path.is_file():
        print(f"Error: {file_path} is not a file.")
        return  None

    file_size = path.stat().st_size  # Get file size in bytes

    try:
        if file_path.endswith(".txt") or file_path.endswith(".py"):
            with open(path, "r") as f:
                content = f.read()
        elif file_path.endswith(".json"):
            with open(path, "r") as f:
                content = json.load(f)
                content = json.dumps(content, indent=4)  # Pretty-print JSON
        elif file_path.endswith(".csv"):
            try:
                df = pd.read_csv(path)
                content = df.to_csv(index=False)  # Convert DataFrame back to CSV format as a string
            except Exception as e:
                print(f"Error: Could not read CSV file {file_path}.")
                return None
        else:
            print(f"Error: Unsupported file format for {file_path}")
            return  None

        print(f"Success: read file  {file_path}, size: {file_size}")
        return content

    except Exception as e:
        print(f"Error: Could not read file '{file_path}'")
        return None

@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file. Overwrites existing files.

    Args:
        file_path: The path to the file to write to.
        content: The content to write to the file.

    Returns:
        A success message or an error message if writing fails.
    """
    path = Path(file_path)
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote content to file '{file_path}'."
    except Exception as e:
        return f"Error: Could not write to file '{file_path}'. Reason: {e}"

@tool
def delete_file(file_path: str) -> str:
    """
    Delete a file.

    Args:
        file_path: The path to the file to delete.

    Returns:
        A success message or an error message if deletion fails.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File '{file_path}' does not exist."
    if not path.is_file():
        return f"Error: '{file_path}' is not a file."
    try:
        path.unlink()  # Delete the file
        return f"Successfully deleted file '{file_path}'."
    except Exception as e:
        return f"Error: Could not delete file '{file_path}'. Reason: {e}"

@tool
def clear_directory(directory: str = "tmp") -> str:
    """
    Clear all files and subdirectories in the specified directory.

    Args:
        directory: The path to the directory to clear. Defaults to 'tmp'.

    Returns:
        A success message or an error message if the operation fails.
    """
    path = Path(directory)
    if not path.exists():
        return f"Error: Directory '{directory}' does not exist."
    if not path.is_dir():
        return f"Error: '{directory}' is not a directory."

    try:
        for item in path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                for sub_item in item.rglob('*'):
                    if sub_item.is_file():
                        sub_item.unlink()
                    elif sub_item.is_dir():
                        sub_item.rmdir()
                item.rmdir()
        return f"Successfully cleared directory '{directory}'."
    except Exception as e:
        return f"Error: Could not clear directory '{directory}'. Reason: {e}"

@tool
def find_python_files(directory: str) -> str:
    """
    Find all Python files (.py) within a directory and its subdirectories.

    Args:
        directory: The path to the directory to search in.

    Returns:
        A string containing a newline-separated list of Python file paths,
        or an error message if the directory does not exist or is not a directory.
    """
    path = Path(directory)
    if not path.exists():
        return f"Error: Directory '{directory}' does not exist."
    if not path.is_dir():
        return f"Error: '{directory}' is not a directory."

    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(str(Path(root) / file)) # Use Path to create platform-independent paths

    if not python_files:
        return "No Python files found in this directory and its subdirectories."
    return "Python files found:\n" + "\n".join(python_files)

@tool
def save_codebase_to_file(directory: str, output_file_path: str = "codebase.txt") -> str:
    """
    Saves the content of all .py files in a directory and its subdirectories
    into a single text file. Files are separated by '==== FILE: <filepath> ===='.

    Args:
        directory: The path to the root directory of the codebase.
        output_file_path: The path to the file where the combined codebase will be saved.
                         Defaults to 'codebase.txt' in the current directory.

    Returns:
        A success message or an error message if the operation fails.
    """
    path = Path(directory)
    output_path = Path(output_file_path)

    if not path.exists():
        return f"Error: Directory '{directory}' does not exist."
    if not path.is_dir():
        return f"Error: '{directory}' is not a directory."

    all_code = ""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    with open(file_path, "r") as f:
                        code_content = f.read()
                    all_code += f"==== FILE: {str(file_path)} ====\n{code_content}\n\n"
                except Exception as e:
                    return f"Error: Could not read file '{file_path}'. Reason: {e}"

    try:
        with open(output_path, "w") as outfile:
            outfile.write(all_code)
        return f"Successfully saved codebase from '{directory}' to '{output_file_path}'."
    except Exception as e:
        return f"Error: Could not write codebase to '{output_file_path}'. Reason: {e}"


# 2- search related tools:(needs research, Do not implement these yet!)
@tool
def search_codebase(query: str, codebase_file_path: str = "codebase.txt") -> str:
    """
    [RESEARCH - NOT IMPLEMENTED YET]
    Search for a query string within the codebase file.

    Args:
        query: The string to search for.
        codebase_file_path: Path to the codebase file generated by save_codebase_to_file.
                             Defaults to 'codebase.txt'.

    Returns:
        [RESEARCH - NOT IMPLEMENTED YET]
        A string containing search results, including file names and code snippets.
    """
    return "[RESEARCH - NOT IMPLEMENTED YET] Codebase search is not yet implemented.  " \
           "This tool should search the codebase file and return relevant code snippets and file names."

# 3-1 extract the patch(in diff format) from the models output(this will not be the agent tool.)
# This is not implemented as a tool, because it's meant for post-processing the agent's output, not for the agent to use directly.
def extract_patch_from_output(model_output: str) -> Optional[str]:
    """
    [NOT AN AGENT TOOL]
    Extracts a patch (assuming diff format) from the model's output string.
    This is a utility function for processing the agent's output, not an agent tool itself.

    Args:
        model_output: The string output from the LLM agent, potentially containing a patch.

    Returns:
        The extracted patch string if found, otherwise None.
    """
    # Simple example: Assuming the patch starts with "<====STARTPATCH====>" and ends with "<====ENDPATCH====>".
    start_marker = "<====STARTPATCH====>"
    end_marker = "<====ENDPATCH====>"

    start_index = model_output.find(start_marker)
    if start_index != -1:
        # **Adjust start_index to be after the start marker itself**
        start_index += len(start_marker)
        end_index = model_output.find(end_marker, start_index) # find end marker starting from after start marker
        if end_index == -1: # if no end marker, consider rest of the string as patch (less robust but might be needed if agent forgets end marker)
            end_index = len(model_output)

        patch_content = model_output[start_index:end_index].strip() # extract content between markers and strip spaces.
        if patch_content:
            return patch_content
    return None


if __name__ == "__main__":
    print(list_folders("./"))