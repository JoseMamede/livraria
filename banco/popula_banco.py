import json
from pymongo import MongoClient
from bson.decimal128 import Decimal128
from decimal import Decimal
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Caminho do arquivo JSON
json_path = os.path.join("banco", "livros.json")
with open(json_path, "r", encoding="utf-8") as file:
    livros = json.load(file)

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("Variável de ambiente MONGO_URI não encontrada!")

client = MongoClient(MONGO_URI)
db = client.livraria

# AJUSTE: Usando 'books' que é onde vimos que os dados funcionam no seu Atlas
livros_collection = db.books

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

# AJUSTE: Limpa a coleção antes de inserir para garantir que o banco fique "cheio" apenas com o JSON atual
print(f"Limpando a coleção '{livros_collection.name}'...")
livros_collection.delete_many({})

print(f"Iniciando a inserção de {len(livros)} livros...")

for livro in livros:
    livro_doc = {
        "titulo": livro["titulo"],
        "preco": Decimal128(Decimal(str(livro["preco"]))),
        "categoria": livro["categoria"],
        "tags": livro["tags"],
        "autores": livro["autores"],
        "mais_recente_edicao": livro.get("mais_recente_edicao", False),
        "data_publicacao": parse_date(livro["data_publicacao"]),
        "editora": livro["editora"],
        "descricao": livro["descricao"],
        "isbn": livro["isbn"],
        "estoque": livro["estoque"],
        "imagem_capa": livro.get("imagem_capa", "static/img/default.jpg") # Garante que a imagem apareça
    }
    livros_collection.insert_one(livro_doc)

client.close()
print("✅ Banco de dados populado com sucesso!")