from bud_editor_service.editor import CodeEditor
from bud_interpreter_service.gpt_bridge import GPTBridge
from bud_guardian_service.guardian import CodeGuardian

class CommandInterpreter:
    def __init__(self, base_path):
        self.code_editor = CodeEditor(base_path)
        self.gpt_bridge = GPTBridge() # Placeholder for GPT integration
        self.code_guardian = CodeGuardian(base_path)

    def interpret_and_modify(self, command_text):
        print(f"Interpretando comando: {command_text}")

        # Use GPTBridge to process the command and get modification instructions
        modification_instruction = self.gpt_bridge.process_command(command_text)

        action = modification_instruction.get("action")
        code_to_add = modification_instruction.get("code")
        target_file = modification_instruction.get("target_file")

        if action == "generate_code" and code_to_add and target_file:
            print(f"Recebido instrução para gerar código para {target_file}.")
            if self.code_editor.append_to_file(target_file, "\n" + code_to_add):
                print(f"Código gerado adicionado a {target_file} com sucesso.")
                
                # Trigger validation and testing after modification
                print("Iniciando validação e testes...")
                if self.code_guardian.validate_code(target_file) and self.code_guardian.run_tests():
                    print("Validação e testes concluídos com sucesso. Código pronto para deploy.")
                else:
                    print("Validação ou testes falharam. Reverter modificações ou revisar.")
            else:
                print(f"Falha ao adicionar código gerado a {target_file}.")
        else:
            print("Comando não resultou em uma instrução de modificação de código reconhecida.")


