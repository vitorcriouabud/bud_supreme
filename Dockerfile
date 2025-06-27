# Usa imagem oficial do Python
FROM python:3.10

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . .

# Instala as dependências listadas no requirements.txt
RUN pip install --upgrade pip && pip install -r requisitos.txt

# Executa o sistema
CMD ["python", "essencial/main.py"]
