import json
import os
import subprocess

def tool(description):
	def decorator(func):
		func.is_tool = True
		func.description = description
		return func
	return decorator


class System_Access_Tool:
	def __init__(self):
		pass

	@tool("Execute terminal commands. Use this to run scripts, install dependencies, find files or run any necessary system commands")
	def execute_command(self, command: str):
		try:
			result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
			return "STDOUT: " + str(result.stdout) + "\nSTDERR: " + str(result.stderr)
		except Exception as e:
			return "Execution error: " + str(e)

	@tool("Read the text content of a local file")
	def read_file(self, location: str):
		try:
			with open(location, "r") as file:
				content = file.read()
				return content
		except Exception as e:
			return "file read error: " + str(e)

	@tool("Create a new file or overwrite an existing file with new content")
	def write_file(self, location: str, content: str):
		try:
			with open(location, "w") as file:
				file.write(content)
				return "writing complete"
		except Exception as e:
			return "writing error: " + str(e)

	@tool("Add content to the end of an existing file")
	def append_file(self, location: str, content: str):
		try:
			with open(location, "a") as file:
				file.write(content)
				return "appending complete"
		except Exception as e:
			return "appending error: " + str(e)

	@tool("Change working directory")
	def change_directory(self, destination: str):
		try:
			os.chdir(destination)
		except Exception as e:
			return "failed to change directory error: " + str(e)