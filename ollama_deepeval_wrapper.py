from deepeval.models import DeepEvalBaseLLM
import ollama
import json

class OllamaDeepEvalWrapper(DeepEvalBaseLLM):
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def load_model(self):
        return ollama.chat

    def generate(self, prompt: str) -> str:
        # DeepTeam passes the conversation history as a JSON string in 'prompt'
        try:
            messages = json.loads(prompt)
            # Ensure it's a list of dicts with 'role' and 'content'
            if not isinstance(messages, list):
                # Fallback if it's not a list (maybe just a single prompt string)
                messages = [{'role': 'user', 'content': prompt}]
            else:
                # Fix for when content is a dict (DeepTeam passes dicts in some prompts)
                for msg in messages:
                    if 'content' in msg and not isinstance(msg['content'], str):
                        msg['content'] = json.dumps(msg['content'])

        except json.JSONDecodeError:
            # Fallback for plain text prompts
            messages = [{'role': 'user', 'content': prompt}]

        # print(f"DEBUG MESSAGES: {messages}")

        response = ollama.chat(
            model=self.model_name, 
            messages=messages,
            format='json' # Force JSON output
        )
        content = response['message']['content']
        # print(f"DEBUG RESPONSE: {content}")
        return content

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return self.model_name