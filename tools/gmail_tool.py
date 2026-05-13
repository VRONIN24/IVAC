import json

def tool(description):
	def decorator(func):
		func.is_tool = True
		func.description = description
		return func
	return decorator


class Gmail_Tool:
	def __init__(self):
		pass

	@tool("Search for emails using Gmail query syntax (e.g., 'from:boss')")
	def search_emails(self, query: str):
		print("[!]Searching email for: " + str(query))
		return "2 emails found"

	@tool("Send an email to a specific address")
	def send_email(self, to: str, subject: str, body: str):
		print("[!]SENDING AN EMAIL TO: " + str(to) + "\n" + "subject: " + str(subject) + "\n" + str(body))
		return "Email has been sent to " + str(to)