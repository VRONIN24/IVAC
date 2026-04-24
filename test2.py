import os
import requests
import json
import re
import datetime
from groq import Groq
from ddgs import DDGS 

class Tool_Box:
    @staticmethod
    def get_weather(location: str):
        try:
            response = requests.get(f"https://wttr.in/{location}?format=%C+%t")
            if response.status_code == 200:
                return f"Current weather in {location}: {response.text.strip()}"
            return "Weather service currently unavailable."
        except Exception as e:
            return f"Weather connection error: {e}"
            
    @staticmethod
    def web_search(query: str):
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

class IVAC:
    def __init__(self, api_key, model_name):
        self.client = Groq(api_key=api_key)
        self.model = model_name
        self.history = [
            {
                "role": "system", 
                "content": (
                    f"Your name is IVAC, a professional Agentic AI. Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}. "
                    "1. DO NOT use tools for simple greetings. "
                    "2. When using tools, do NOT explain yourself. Output the tool call immediately. "
                    "3. If a question involves future/historical dates or complex facts, use 'web_search'."
                )
            }
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get real-time weather for a city.",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for info, news, or long-term seasonal forecasts.",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"]
                    }
                }
            }
        ]

    def send_request(self):
        try:
            return self.client.chat.completions.create(
                model=self.model,
                messages=self.history,
                tools=self.tools,
                tool_choice="auto",
                temperature=0
            )
        except Exception as e:
            if "tool_use_failed" in str(e):
                repaired = self.repair_hallucination(str(e))
                if repaired: return repaired
            raise e

    def repair_hallucination(self, error_str):
        match = re.search(r'failed_generation\': \'(.*?)\'}', error_str)
        if not match: return None
        
        raw_gen = match.group(1)
        tag_match = re.search(r'<function=(\w+)\s*({.*?})', raw_gen)
        if tag_match:
            f_name, f_args = tag_match.groups()
            print(f"[!] System: Repaired hallucinated tag for {f_name}")
            
            class RepairedResponse:
                def __init__(self, name, args):
                    class Choice:
                        def __init__(self, n, a):
                            self.message = self.Msg(n, a)
                        class Msg:
                            def __init__(self, n, a):
                                self.content = None
                                self.tool_calls = [self.Tool(n, a)]
                            class Tool:
                                def __init__(self, n, a):
                                    self.id = f"repaired_{n}"
                                    self.function = type('F', (object,), {'name': n, 'arguments': a})
                    self.choices = [Choice(name, args)]
            return RepairedResponse(f_name, f_args)
        return None

    def chat(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        
        while True:
            response = self.send_request()
            if not response or not response.choices:
                return "I encountered an error I couldn't fix. Let's try another question."
                
            msg = response.choices[0].message
            self.history.append(msg)

            if not msg.tool_calls:
                return msg.content

            for tool in msg.tool_calls:
                name = tool.function.name
                args = json.loads(tool.function.arguments)
                print(f"[*] IVAC Acting: {name}({args})")

                if name == "get_weather":
                    result = Tool_Box.get_weather(args.get("location", ""))
                elif name == "web_search":
                    result = Tool_Box.web_search(args.get("query", ""))
                else:
                    result = "Tool not found."

                self.history.append({
                    "tool_call_id": tool.id,
                    "role": "tool",
                    "name": name,
                    "content": result
                })

if __name__ == "__main__":
    KEY = "<<YOUR API KEY>>" 
    agent = IVAC(KEY, "llama-3.3-70b-versatile")
    
    print("--- IVAC Terminal Activated ---")
    while True:
        try:
            query = input(">> ")
            if query.lower() in ["exit", "quit"]: 
                break
            print(f"IVAC: {agent.chat(query)}")
        except KeyboardInterrupt:
            break