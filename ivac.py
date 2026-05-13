import os
import requests
import json
import re
import datetime
from groq import Groq
from ddgs import DDGS 
import subprocess
from tool_registry import Tool_Registry

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

    @staticmethod
    def execute_command(command: str):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return "STDOUT: " + str(result.stdout) + "\nSTDERR: " + str(result.stderr)
        except Exception as e:
            return "Execution error: " + str(e)

    @staticmethod
    def read_file(location: str):
        try:
            with open(location, "r") as file:
                content = file.read()
                return content
        except Exception as e:
            return "file read error: " + str(e)

    @staticmethod
    def write_file(location: str, content: str):
        try:
            with open(location, "w") as file:
                file.write(content)
                return "writing complete"
        except Exception as e:
            return "writing error: " + str(e)

    @staticmethod
    def append_file(location: str, content: str):
        try:
            with open(location, "a") as file:
                file.write(content)
                return "appending complete"
        except Exception as e:
            return "appending error: " + str(e)



class IVAC:
    def __init__(self, api_key, model_list):
        self.client = Groq(api_key=api_key)
        self.model_list = model_list
        self.current_model = None
        self.select_model()
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
        self.registry = Tool_Registry()
        self.registry.find_tools()
        self.tools = self.registry.tool_metadata


    def select_model(self):
        if self.current_model is None:
            self.current_model = self.model_list[0]
        else:
            try:
                current_model_index = self.model_list.index(self.current_model)
                next_model_index = (current_model_index + 1) % len(self.model_list)
                self.current_model = self.model_list[next_model_index]
            except ValueError:
                self.current_model = self.model_list[0]
        print("[!]System model: " + str(self.current_model))

    def send_request(self):
        try:
            return self.client.chat.completions.create(
                model=self.current_model,
                messages=self.history,
                tools=self.tools,
                tool_choice="auto",
                temperature=0
            )
        except Exception as e:
            error_str = str(e).lower()
            
            if "tool_use_failed" in str(e):
                repaired = self.repair_hallucination(str(e))
                if repaired: 
                    return repaired
            
            if "rate_limit_reached" in error_str or "429" in error_str:
                print("[!] Rate limit reached on " + self.model + ", switching to next model")
                self.select_model()

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
                if name in self.registry.tool_map:
                    result = self.registry.tool_map[name](**args)
                else:
                    result = "Tool not found"

                self.history.append({
                    "tool_call_id": tool.id,
                    "role": "tool",
                    "name": name,
                    "content": result
                })


if __name__ == "__main__":
    KEY = "<YOUR_API_KEY>" #PLACE_HOLDER
    model_list = [
        "<A_LIST_OF_YOUR_PREFERRED_MODEL_NAMES_IN_ORDER_OF_PREFERENCE>" #PLACE_HOLDER
        ]
    agent = IVAC(KEY, model_list)

    print("--- IVAC Terminal Activated ---")
    while True:
        try:
            query = input(">> ")
            if query.lower() in ["exit", "quit"]: 
                break
            print(f"IVAC: {agent.chat(query)}")
        except KeyboardInterrupt:
            break
