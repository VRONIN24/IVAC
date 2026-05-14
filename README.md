# IVAC

IVAC is a Agentic AI system built on the Groq Cloud API. It features dynamic tool discovery, automated hallucination repair and multi-model failover capabilities.

---

## 🛠 Features

* **Dynamic Tool Registry:** Automatically discovers and registers tools from the `/tools` directory at runtime.
* **Hallucination Repair:** Automatically detects and fixes malformed tool calls (common in smaller LLMs).
* **Model Failover:** Automatically switches to the next available model if rate limits (429 errors) are hit.
* **Currently Built-in available Tools:** Web search, weather reporting, file management and shell command execution.

---

## 📂 Project Structure

```text
.
├── ivac.py              # The core IVAC agent logic
├── tool_registry.py     # Logic for automatic tool discovery
├── tools/               # Directory where all custom tools reside
│   └── additional_tools.py  # Example file for your tool classes
└── README.md

```

---

## 🚀 Installation

### 1. Prerequisites

Ensure you have **Python 3.8+** installed. You will also need a Groq API Key.

### 2. Install Dependencies

Run the following command to install the required libraries:

```bash
pip install requests groq ddgs

```

### 3. Setup API Key

Open `main.py` and replace the placeholder variables with your actual data:

```python
KEY = "<your_groq_api_key_here>" 
model_list = ["
   <A_LIST_OF_YOUR_PREFERRED_MODEL_NAMES_IN_ORDER_OF_PREFERENCE>
   "]

```

---

## 🔧 How to Add New Tools

IVAC uses an automated discovery system. You can add new capabilities simply by dropping a Python file into the `/tools` folder.

### 1. Create a tool file

Create a new `.py` file inside the `/tools` directory (e.g., `communication_tools.py`) or just paste if you already have one.

### 2. The `@tool` Decorator

Every method you want IVAC to use must be decorated with `@tool("description")`. This helps the AI figure out what the tool does. You can copy this decorator into your tool file:

```python
def tool(description):
    def decorator(func):
        func.is_tool = True
        func.description = description
        return func
    return decorator

```

### 3. Define your Tool Class

1. The class name **must** end with `Tool` (e.g., `GmailTool`).
2. Methods should be regular instance methods (always include `self` as the first argument).

**Example:**

```python
class GmailTool:
    def __init__(self):
        # Setup your API clients here
        pass

    @tool("Search for emails using Gmail query syntax.")
    def search_emails(self, query: str):
        # The registry handles the 'self' argument automatically
        #YOUR_CODE
        return f"Found emails for {query}"

    @tool("Send a plain text email to a recipient.")
    def send_email(self, to: str, subject: str, body: str):
        #YOUR_CODE
        return f"Email sent to {to}"

```

### 💡 Pro-Tips for Tool Creation

* **Arguments:** Give your arguments clear names (like `query`, `location`, or `filename`). IVAC uses these names to understand what data to send.
* **Return Values:** Always return a string. If the tool fails, return a string describing the error so the AI can try to fix its mistake.
* **Class Names:** Ensure your class ends in `Tool` (e.g., `FileTool`, not `FileHelper`), otherwise the registry will ignore the class.

---

---

## 🛑 CAUTION: System Access & Security

**IVAC is a powerful Agentic AI with the capability to interact directly with your operating system.** By using the `system_access_tool`, you are granting the AI permission to:

* **Execute Terminal Commands:** The AI can run any command available to your user profile (e.g., `rm -rf`, `format`, or installing unverified packages).
* **File System Manipulation:** The AI can read, write, append, and delete files across any directory it has permission to access.

### 🛡️ Recommended Safety Practices:

1. **Sandbox Environment:** It is recommended to run IVAC inside a **safe environment** or a **Virtual Machine (VM)** to isolate your sensitive data from the AI's reach.
2. **Sensitive Data:** Ensure that no sensitive files (passwords, private keys, financial records) are located in the working directory or accessible via the terminal path where the agent is running.
3. **Human-in-the-Loop:** Monitor the terminal output. If you see the agent preparing a destructive command, terminate the process immediately ($Ctrl+C$).

**Disclaimer:** *The creators of IVAC are not responsible for any data loss, system instability, or security breaches caused by the AI's execution of system commands. Use at your own risk.*

---
