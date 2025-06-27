# Usa imagem oficial do Python
FROM python:3.10

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . .

# Instala as dependências listadas no requirements.txt
 && pip install -r requirements.txt

# Executa o sistema
CMD ["python", "essencial/main.py"]
