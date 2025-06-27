import os

class CodeEditor:
    def __init__(self, base_path):
        self.base_path = base_path

    def read_file(self, relative_path):
        file_path = os.path.join(self.base_path, relative_path)
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def write_file(self, relative_path, content):
        file_path = os.path.join(self.base_path, relative_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        return True

    def append_to_file(self, relative_path, content):
        file_path = os.path.join(self.base_path, relative_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'a') as f:
            f.write(content)
        return True

    def replace_in_file(self, relative_path, old_str, new_str):
        file_path = os.path.join(self.base_path, relative_path)
        content = self.read_file(relative_path)
        if content is None:
            return False
        if old_str not in content:
            return False
        new_content = content.replace(old_str, new_str, 1) # Replace only first occurrence
        self.write_file(relative_path, new_content)
        return True


