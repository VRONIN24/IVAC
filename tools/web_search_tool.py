import json
from ddgs import DDGS


def tool(description):
	def decorator(func):
		func.is_tool = True
		func.description = description
		return func
	return decorator


class Web_Search_Tool:
	def __init__(self):
		pass

	@tool("Search the web for info, news, or long-term seasonal forecasts.")
	def web_search(self, query: str):
		try:
			with DDGS() as ddgs:
				results = ddgs.text(query, max_results=3)
				if not results:
					return "No relevant search results found."
				
				output = []
				for r in results:
					output.append(f"Title: {r['title']}\nSnippet: {r['body']}")
				return "\n\n".join(output)
		except Exception as e:
			return f"Search engine error: {e}"
