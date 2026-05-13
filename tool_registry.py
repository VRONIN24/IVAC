import inspect
import importlib
import os

class Tool_Registry:
    def __init__(self):
        self.tool_metadata = []
        self.tool_map = {}

    def find_tools(self, folder="tools"):
        if not os.path.exists(folder):
            print(f"[!] Folder {folder} not found.")
            return

        for file_name in os.listdir(folder):
            if file_name.endswith(".py") and file_name != "__init__.py":
                module_name = f"{folder}.{file_name[:-3]}"
                module_path = module_name.replace("/", ".").replace("\\", ".")
                
                try:
                    module = importlib.import_module(module_path)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and name.endswith("Tool"): 
                            instance = obj()
                            self.extract_tools(instance)
                except Exception as e:
                    print(f"[!] Error loading {module_path}: {e}")

    def extract_tools(self, instance):
        for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
            if hasattr(method, "is_tool"):
                sig = inspect.signature(method)
                properties = {}
                required = []

                for param_name, param in sig.parameters.items():
                    properties[param_name] = {"type": "string"}
                    if param.default is inspect.Parameter.empty:
                        required.append(param_name)

                tools_schema = {
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": getattr(method, "description", "No description provided"),
                        "parameters": {
                            "type": "object",
                            "properties": properties,
                            "required": required
                        }
                    }
                }
                self.tool_metadata.append(tools_schema)
                self.tool_map[name] = method
                print(f"[*] Registered tool: {name}")