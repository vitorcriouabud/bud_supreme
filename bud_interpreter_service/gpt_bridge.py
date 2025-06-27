import openai
from dotenv import load_dotenv
import os

class GPTBridge:
    def __init__(self):
        load_dotenv() # Carrega as variáveis de ambiente do arquivo .env
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            print("Erro: OPENAI_API_KEY não encontrada nas variáveis de ambiente.")

    def generate_code_from_prompt(self, prompt, model="gpt-3.5-turbo"):
        if not openai.api_key:
            return None
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Você é um assistente de IA que gera código Python com base em instruções em linguagem natural. O código deve ser modular, seguro e seguir as melhores práticas."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Erro ao gerar código com GPT: {e}")
            return None

    def process_command(self, command_text):
        print(f"GPTBridge processando comando para geração de código: {command_text}")
        generated_code = self.generate_code_from_prompt(
            f"Gere um trecho de código Python para implementar a seguinte ideia: {command_text}. O código deve ser adicionado ao arquivo bud_logic/strategy.py."
        )
        return {"action": "generate_code", "code": generated_code, "target_file": "bud_logic/strategy.py"}


