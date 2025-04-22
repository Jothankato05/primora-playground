"""
primora_nl.py - Natural Language to Primora code converter
"""
import os
import requests

class PrimoraNL:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    def nl_to_primora(self, text):
        """Convert natural language to Primora code using OpenAI or simple rules."""
        if self.api_key:
            # Use OpenAI API for advanced NL to code
            try:
                prompt = f"Convert this instruction to Primora code (be concise):\nInstruction: {text}\nCode:"
                headers = {"Authorization": f"Bearer {self.api_key}"}
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an expert in the Primora programming language."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 128,
                    "temperature": 0.2
                }
                resp = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
                resp.raise_for_status()
                result = resp.json()
                code = result["choices"][0]["message"]["content"].strip()
                return code
            except Exception as e:
                return f"# Error: {e}\n# Fallback to simple rules."
        # Simple rules fallback
        text = text.lower()
        if "search" in text and "summarize" in text:
            import re
            query = re.findall(r'"(.*?)"', text)
            if query:
                return f'search "{query[0]}" as results\nsummarize results as summary\necho summary'
            else:
                return 'search "latest news" as results\nsummarize results as summary\necho summary'
        if "fetch" in text and "json" in text:
            return 'fetch url("https://jsonplaceholder.typicode.com/todos/1") as todo\necho todo'
        if "email" in text:
            return '# Email sending is not yet implemented.'
        return '# Sorry, could not parse instruction. Try rephrasing.'

primora_nl = PrimoraNL()
