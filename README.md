## IVAC: Agentic AI with Self-Healing Tool Calls

**IVAC** is an agentic AI assistant powered by the **Llama 3.3 70B** model via Groq. It is designed to handle real-world tasks through tool integration while maintaining high reliability in structured outputs.

---

### Key Features

* **Self-Healing Architecture:** Includes a specialized "Repair Shield" that intercepts common LLM hallucinations (like malformed function tags) and surgically repairs them into valid API objects without interrupting the user experience.
* **Real-Time Capabilities:**
    * **Live Weather:** Fetches current atmospheric conditions using the `wttr.in` service.
    * **Web Search:** Browses the internet via DuckDuckGo (DDGS) for up-to-date facts, news, and 2026 forecasts.
* **Stateful Conversation:** Maintains a structured history that supports multi-turn reasoning and complex tool-calling loops.
* **High Performance:** Optimized for the Groq LPU™ Inference Engine for near-instantaneous response times.

---

### 🛠️ Technical Setup

#### Prerequisites
* Python 3.10+
* A Groq API Key

#### Installation
```bash
pip install groq ddgs requests
```

#### Configuration
1. Clone this repository.
2. Replace `<<YOUR API KEY>>` in the script with your actual Groq API key.
3. Run the terminal:
```bash
python main.py
```

---

### 🧠 How It Works

IVAC operates on a **Try-Catch-Repair** logic. When the model attempts to call a tool but fails to follow the strict JSON schema required by the API, the system:
1.  **Intercepts** the `BadRequestError`.
2.  **Extracts** the intended function and arguments using Regex.
3.  **Injects** a repaired response object into the processing loop.
4.  **Executes** the tool and returns the data to the AI for final synthesis.

---

### 📝 License
This project is open-source and available under the MIT License. The project is still in development.
