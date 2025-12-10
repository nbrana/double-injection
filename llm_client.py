import ollama

class LLMClient:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate(self, prompt, system_prompt=None, history=None):
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        if history:
            messages.extend(history)
            
        messages.append({'role': 'user', 'content': prompt})

        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']

    def generate_chat(self, messages):
        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']
