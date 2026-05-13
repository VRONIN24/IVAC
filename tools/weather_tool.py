import json
import requests


def tool(description):
	def decorator(func):
		func.is_tool = True
		func.description = description
		return func
	return decorator


class Weather_Tool:
	def __init__(self):
		pass

	@tool("Get real-time weather for a city.")
	def get_weather(self, location: str):
		try:
			response = requests.get(f"https://wttr.in/{location}?format=%C+%t")
			if response.status_code == 200:
				return f"Current weather in {location}: {response.text.strip()}"
			return "Weather service currently unavailable."
		except Exception as e:
			return f"Weather connection error: {e}"

