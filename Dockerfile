# Dockerfile para Sistema de Produção
FROM python:3.9-slim

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de requisitos
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY . .

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 production && chown -R production:production /app
USER production

# Expõe porta (se necessário para futuras extensões)
EXPOSE 8000

# Comando padrão
CMD ["python", "SisProd.py"]